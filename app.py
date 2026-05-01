"""
app.py
Main Flask application for Online Leave Application System.
All routes are defined here with role-based access control.
"""

from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from config import Config
from datetime import date

APPROVAL_STATUSES = ("pending", "hod_approved", "approved", "rejected")

STATUS_LABELS = {
    "pending": "Pending HOD",
    "hod_approved": "Pending Faculty",
    "approved": "Approved",
    "rejected": "Rejected",
}

STATUS_BADGES = {
    "pending": "bg-warning text-dark",
    "hod_approved": "bg-info text-dark",
    "approved": "bg-success",
    "rejected": "bg-danger",
}

_schema_checked = False

# ──────────────────────────────────────────────
# App Setup
# ──────────────────────────────────────────────
app = Flask(__name__)
app.config.from_object(Config)

mysql = MySQL(app)

# ──────────────────────────────────────────────
# Decorators for Role-Based Route Protection
# ──────────────────────────────────────────────

def login_required(f):
    """Redirect to login if user is not logged in."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            flash("Please login to access this page.", "warning")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated


def role_required(*roles):
    """Allow access only if the logged-in user has one of the given roles."""
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if "user_id" not in session:
                flash("Please login first.", "warning")
                return redirect(url_for("login"))
            if session.get("role") not in roles:
                flash("Access denied. You are not authorized to view this page.", "danger")
                return redirect(url_for("dashboard"))
            return f(*args, **kwargs)
        return decorated
    return decorator


# ──────────────────────────────────────────────
# Helper: DB cursor
# ──────────────────────────────────────────────
def get_cursor():
    return mysql.connection.cursor()


def ensure_approval_schema():
    """Keep older local databases compatible with the HOD -> faculty flow."""
    global _schema_checked
    if _schema_checked:
        return

    cur = get_cursor()
    cur.execute(
        "ALTER TABLE users MODIFY role ENUM('student', 'faculty', 'hod', 'admin') NOT NULL"
    )
    cur.execute(
        """ALTER TABLE leave_applications
           MODIFY status ENUM('pending', 'hod_approved', 'approved', 'rejected') DEFAULT 'pending'"""
    )
    cur.execute("SHOW COLUMNS FROM leave_applications LIKE 'hod_remarks'")
    if not cur.fetchone():
        cur.execute("ALTER TABLE leave_applications ADD COLUMN hod_remarks TEXT AFTER status")

    mysql.connection.commit()
    cur.close()
    _schema_checked = True


@app.before_request
def before_request():
    if request.endpoint != "static" and "user_id" in session:
        ensure_approval_schema()


@app.context_processor
def approval_status_helpers():
    return dict(status_labels=STATUS_LABELS, status_badges=STATUS_BADGES)


# ──────────────────────────────────────────────
# GENERAL ROUTES
# ──────────────────────────────────────────────

@app.route("/")
def index():
    """Professional landing page."""
    if "user_id" in session:
        return redirect(url_for("dashboard"))
    return render_template("landing.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Login page for all roles."""
    if "user_id" in session:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        email    = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()

        if not email or not password:
            flash("Email and password are required.", "danger")
            return render_template("login.html")

        cur = get_cursor()
        cur.execute("SELECT * FROM users WHERE email = %s AND status = 'active'", (email,))
        user = cur.fetchone()
        cur.close()

        if user and check_password_hash(user["password"], password):
            # Store user info in session
            session["user_id"]   = user["id"]
            session["full_name"] = user["full_name"]
            session["role"]      = user["role"]
            session["email"]     = user["email"]
            session["dept"]      = user["department"]

            flash(f"Welcome, {user['full_name']}!", "success")
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid email or password.", "danger")

    return render_template("login.html")






@app.route("/logout")
@login_required
def logout():
    """Clear session and redirect to login."""
    session.clear()
    flash("You have been logged out successfully.", "info")
    return redirect(url_for("login"))


@app.route("/dashboard")
@login_required
def dashboard():
    """Smart redirect to the correct dashboard based on role."""
    role = session.get("role")
    if role == "student":
        return redirect(url_for("student_dashboard"))
    elif role == "faculty":
        return redirect(url_for("faculty_dashboard"))
    elif role == "hod":
        return redirect(url_for("faculty_dashboard"))
    elif role == "admin":
        return redirect(url_for("admin_dashboard"))
    else:
        session.clear()
        flash("Unknown role. Please contact admin.", "danger")
        return redirect(url_for("login"))


# ──────────────────────────────────────────────
# STUDENT ROUTES
# ──────────────────────────────────────────────

@app.route("/student/dashboard")
@role_required("student")
def student_dashboard():
    """Student dashboard with stats and recent leaves."""
    cur  = get_cursor()
    uid  = session["user_id"]

    cur.execute("SELECT COUNT(*) AS total    FROM leave_applications WHERE student_id = %s", (uid,))
    total = cur.fetchone()["total"]

    cur.execute(
        """SELECT COUNT(*) AS cnt FROM leave_applications
           WHERE student_id = %s AND status IN ('pending', 'hod_approved')""",
        (uid,)
    )
    pending = cur.fetchone()["cnt"]

    cur.execute("SELECT COUNT(*) AS cnt FROM leave_applications WHERE student_id = %s AND status='approved'",  (uid,))
    approved = cur.fetchone()["cnt"]

    cur.execute("SELECT COUNT(*) AS cnt FROM leave_applications WHERE student_id = %s AND status='rejected'",  (uid,))
    rejected = cur.fetchone()["cnt"]

    cur.execute(
        "SELECT * FROM leave_applications WHERE student_id = %s ORDER BY applied_at DESC LIMIT 5", (uid,)
    )
    recent = cur.fetchall()
    cur.close()

    return render_template(
        "student/dashboard.html",
        total=total, pending=pending, approved=approved, rejected=rejected, recent=recent
    )


@app.route("/student/apply", methods=["GET", "POST"])
@role_required("student")
def student_apply():
    """Student: apply for leave."""
    if request.method == "POST":
        title      = request.form.get("title", "").strip()
        leave_type = request.form.get("leave_type", "").strip()
        from_date  = request.form.get("from_date", "").strip()
        to_date    = request.form.get("to_date", "").strip()
        reason     = request.form.get("reason", "").strip()

        # Validation
        if not all([title, leave_type, from_date, to_date, reason]):
            flash("All fields are required.", "danger")
            return render_template("student/apply_leave.html")

        if from_date > to_date:
            flash("End date cannot be before start date.", "danger")
            return render_template("student/apply_leave.html")

        valid_types = ("sick_leave", "personal_leave", "emergency", "others")
        if leave_type not in valid_types:
            flash("Invalid leave type.", "danger")
            return render_template("student/apply_leave.html")

        cur = get_cursor()
        cur.execute(
            """INSERT INTO leave_applications
               (student_id, title, leave_type, from_date, to_date, reason, status)
               VALUES (%s, %s, %s, %s, %s, %s, 'pending')""",
            (session["user_id"], title, leave_type, from_date, to_date, reason)
        )
        mysql.connection.commit()
        cur.close()

        flash("Leave application submitted successfully! It is now pending HOD approval.", "success")
        return redirect(url_for("student_my_leaves"))

    return render_template("student/apply_leave.html")


@app.route("/student/my-leaves")
@role_required("student")
def student_my_leaves():
    """Student: view all their leave applications."""
    cur = get_cursor()
    cur.execute(
        "SELECT * FROM leave_applications WHERE student_id = %s ORDER BY applied_at DESC",
        (session["user_id"],)
    )
    leaves = cur.fetchall()
    cur.close()
    return render_template("student/my_leaves.html", leaves=leaves)


@app.route("/student/edit/<int:leave_id>", methods=["GET", "POST"])
@role_required("student")
def student_edit_leave(leave_id):
    """Student: edit a pending leave application."""
    cur = get_cursor()
    cur.execute(
        "SELECT * FROM leave_applications WHERE id = %s AND student_id = %s",
        (leave_id, session["user_id"])
    )
    leave = cur.fetchone()

    if not leave:
        cur.close()
        flash("Leave application not found.", "danger")
        return redirect(url_for("student_my_leaves"))

    if leave["status"] != "pending":
        cur.close()
        flash("Only pending applications can be edited.", "warning")
        return redirect(url_for("student_my_leaves"))

    if request.method == "POST":
        title      = request.form.get("title", "").strip()
        leave_type = request.form.get("leave_type", "").strip()
        from_date  = request.form.get("from_date", "").strip()
        to_date    = request.form.get("to_date", "").strip()
        reason     = request.form.get("reason", "").strip()

        if not all([title, leave_type, from_date, to_date, reason]):
            flash("All fields are required.", "danger")
            return render_template("student/apply_leave.html", leave=leave, edit=True)

        if from_date > to_date:
            flash("End date cannot be before start date.", "danger")
            return render_template("student/apply_leave.html", leave=leave, edit=True)

        cur.execute(
            """UPDATE leave_applications
               SET title=%s, leave_type=%s, from_date=%s, to_date=%s, reason=%s
               WHERE id=%s AND student_id=%s""",
            (title, leave_type, from_date, to_date, reason, leave_id, session["user_id"])
        )
        mysql.connection.commit()
        cur.close()
        flash("Leave application updated successfully!", "success")
        return redirect(url_for("student_my_leaves"))

    cur.close()
    return render_template("student/apply_leave.html", leave=leave, edit=True)


@app.route("/student/delete/<int:leave_id>", methods=["POST"])
@role_required("student")
def student_delete_leave(leave_id):
    """Student: delete a pending leave application."""
    cur = get_cursor()
    cur.execute(
        "SELECT * FROM leave_applications WHERE id = %s AND student_id = %s AND status = 'pending'",
        (leave_id, session["user_id"])
    )
    leave = cur.fetchone()

    if not leave:
        flash("Cannot delete this application.", "danger")
    else:
        cur.execute("DELETE FROM leave_applications WHERE id = %s", (leave_id,))
        mysql.connection.commit()
        flash("Leave application deleted.", "info")

    cur.close()
    return redirect(url_for("student_my_leaves"))


@app.route("/student/profile")
@role_required("student")
def student_profile():
    """Student: view their profile."""
    cur = get_cursor()
    cur.execute("SELECT * FROM users WHERE id = %s", (session["user_id"],))
    user = cur.fetchone()
    cur.close()
    return render_template("student/profile.html", user=user)


# ──────────────────────────────────────────────
# FACULTY ROUTES
# ──────────────────────────────────────────────

@app.route("/faculty/dashboard")
@app.route("/hod/dashboard")
@role_required("faculty", "hod")
def faculty_dashboard():
    """Faculty/HOD dashboard with department-scoped leave stats."""
    cur = get_cursor()
    faculty_dept = session.get("dept")
    role = session.get("role")
    review_status = "pending" if role == "hod" else "hod_approved"

    cur.execute(
        """SELECT COUNT(*) AS total
           FROM leave_applications la
           JOIN users u ON la.student_id = u.id
           WHERE u.department = %s""",
        (faculty_dept,)
    )
    total = cur.fetchone()["total"]

    cur.execute(
        """SELECT COUNT(*) AS cnt
           FROM leave_applications la
           JOIN users u ON la.student_id = u.id
           WHERE u.department = %s AND la.status=%s""",
        (faculty_dept, review_status)
    )
    pending = cur.fetchone()["cnt"]

    cur.execute(
        """SELECT COUNT(*) AS cnt
           FROM leave_applications la
           JOIN users u ON la.student_id = u.id
           WHERE u.department = %s AND la.status='approved'""",
        (faculty_dept,)
    )
    approved = cur.fetchone()["cnt"]

    cur.execute(
        """SELECT COUNT(*) AS cnt
           FROM leave_applications la
           JOIN users u ON la.student_id = u.id
           WHERE u.department = %s AND la.status='rejected'""",
        (faculty_dept,)
    )
    rejected = cur.fetchone()["cnt"]

    cur.execute(
        """SELECT la.*, u.full_name, u.roll_no, u.department
           FROM leave_applications la
           JOIN users u ON la.student_id = u.id
           WHERE u.department = %s
           ORDER BY la.applied_at DESC LIMIT 5""",
        (faculty_dept,)
    )
    recent = cur.fetchall()
    cur.close()

    return render_template(
        "faculty/dashboard.html",
        total=total, pending=pending, approved=approved, rejected=rejected, recent=recent,
        reviewer_role=role
    )


@app.route("/faculty/requests")
@role_required("faculty", "hod")
def faculty_requests():
    """Faculty/HOD: view leave requests from their own department."""
    status_filter = request.args.get("status", "")
    search        = request.args.get("search", "").strip()
    faculty_dept  = session.get("dept")
    role          = session.get("role")

    query  = """SELECT la.*, u.full_name, u.roll_no, u.department
                FROM leave_applications la
                JOIN users u ON la.student_id = u.id
                WHERE u.department = %s """
    params = [faculty_dept]

    if status_filter in APPROVAL_STATUSES:
        query  += " AND la.status = %s"
        params.append(status_filter)
    elif role == "faculty":
        query += " AND la.status IN ('hod_approved', 'approved', 'rejected')"

    if search:
        query  += " AND u.full_name LIKE %s"
        params.append(f"%{search}%")

    query += " ORDER BY la.applied_at DESC"

    cur = get_cursor()
    cur.execute(query, params)
    leaves = cur.fetchall()
    cur.close()

    return render_template(
        "faculty/leave_requests.html",
        leaves=leaves, status_filter=status_filter, search=search, reviewer_role=role
    )


@app.route("/faculty/review/<int:leave_id>", methods=["GET", "POST"])
@role_required("faculty", "hod")
def faculty_review(leave_id):
    """Faculty/HOD: review and approve/reject an in-department leave application."""
    cur = get_cursor()
    faculty_dept = session.get("dept")
    role = session.get("role")
    cur.execute(
        """SELECT la.*, u.full_name, u.roll_no, u.department, u.email
           FROM leave_applications la
           JOIN users u ON la.student_id = u.id
           WHERE la.id = %s AND u.department = %s""",
        (leave_id, faculty_dept)
    )
    leave = cur.fetchone()

    if not leave:
        cur.close()
        flash("Leave application not found for your department.", "danger")
        return redirect(url_for("faculty_requests"))

    if request.method == "POST":
        action  = request.form.get("action")
        remarks = request.form.get("remarks", "").strip()

        required_status = "pending" if role == "hod" else "hod_approved"
        reviewer_name = "HOD" if role == "hod" else "Faculty"

        if leave["status"] != required_status:
            cur.close()
            flash(f"Only applications pending {reviewer_name} review can be actioned.", "warning")
            return redirect(url_for("faculty_review", leave_id=leave_id))

        if action not in ("approve", "reject"):
            cur.close()
            flash("Invalid action.", "danger")
            return redirect(url_for("faculty_review", leave_id=leave_id))

        if role == "faculty" and action == "reject":
            cur.close()
            flash("Faculty can only approve requests already vetted by HOD.", "danger")
            return redirect(url_for("faculty_review", leave_id=leave_id))

        if role == "hod":
            new_status = "hod_approved" if action == "approve" else "rejected"
            cur.execute(
                """UPDATE leave_applications la
                   JOIN users u ON la.student_id = u.id
                   SET la.status=%s, la.hod_remarks=%s
                   WHERE la.id=%s AND u.department=%s""",
                (new_status, remarks, leave_id, faculty_dept)
            )
        else:
            new_status = "approved" if action == "approve" else "rejected"
            cur.execute(
                """UPDATE leave_applications la
                   JOIN users u ON la.student_id = u.id
                   SET la.status=%s, la.faculty_remarks=%s
                   WHERE la.id=%s AND u.department=%s""",
                (new_status, remarks, leave_id, faculty_dept)
            )
        mysql.connection.commit()
        cur.close()

        flash(f"Leave application status updated to {STATUS_LABELS[new_status]}.", "success")
        return redirect(url_for("faculty_requests"))

    cur.close()
    return render_template("faculty/review_leave.html", leave=leave, reviewer_role=role)


@app.route("/faculty/profile")
@role_required("faculty", "hod")
def faculty_profile():
    """Faculty: view their profile."""
    cur = get_cursor()
    cur.execute("SELECT * FROM users WHERE id = %s", (session["user_id"],))
    user = cur.fetchone()
    cur.close()
    return render_template("faculty/profile.html", user=user)


# ──────────────────────────────────────────────
# ADMIN ROUTES
# ──────────────────────────────────────────────

@app.route("/admin/dashboard")
@role_required("admin")
def admin_dashboard():
    """Admin dashboard with system-wide stats."""
    cur = get_cursor()

    cur.execute("SELECT COUNT(*) AS cnt FROM users WHERE role='student' AND status='active'")
    students = cur.fetchone()["cnt"]

    cur.execute("SELECT COUNT(*) AS cnt FROM users WHERE role='faculty' AND status='active'")
    faculty = cur.fetchone()["cnt"]

    cur.execute("SELECT COUNT(*) AS cnt FROM leave_applications")
    total_leaves = cur.fetchone()["cnt"]

    cur.execute("SELECT COUNT(*) AS cnt FROM leave_applications WHERE status IN ('pending', 'hod_approved')")
    pending = cur.fetchone()["cnt"]

    cur.execute("SELECT COUNT(*) AS cnt FROM leave_applications WHERE status='approved'")
    approved = cur.fetchone()["cnt"]

    cur.execute("SELECT COUNT(*) AS cnt FROM leave_applications WHERE status='rejected'")
    rejected = cur.fetchone()["cnt"]

    cur.execute(
        """SELECT la.*, u.full_name, u.roll_no FROM leave_applications la
           JOIN users u ON la.student_id = u.id
           ORDER BY la.applied_at DESC LIMIT 6"""
    )
    recent_leaves = cur.fetchall()
    cur.close()

    return render_template(
        "admin/dashboard.html",
        students=students, faculty=faculty,
        total_leaves=total_leaves, pending=pending,
        approved=approved, rejected=rejected,
        recent_leaves=recent_leaves
    )


@app.route("/admin/users")
@role_required("admin")
def admin_users():
    """Admin: view all users."""
    role_filter = request.args.get("role", "")
    search      = request.args.get("search", "").strip()

    query  = "SELECT * FROM users WHERE 1=1"
    params = []

    if role_filter in ("student", "faculty", "hod", "admin"):
        query  += " AND role = %s"
        params.append(role_filter)

    if search:
        query  += " AND (full_name LIKE %s OR email LIKE %s)"
        params.extend([f"%{search}%", f"%{search}%"])

    query += " ORDER BY created_at DESC"

    cur = get_cursor()
    cur.execute(query, params)
    users = cur.fetchall()
    cur.close()

    return render_template("admin/manage_users.html", users=users, role_filter=role_filter, search=search)


@app.route("/admin/users/add", methods=["GET", "POST"])
@role_required("admin")
def admin_add_user():
    """Admin: add a new user."""
    if request.method == "POST":
        full_name  = request.form.get("full_name", "").strip()
        email      = request.form.get("email", "").strip()
        password   = request.form.get("password", "").strip()
        role       = request.form.get("role", "").strip()
        department = request.form.get("department", "").strip()
        roll_no    = request.form.get("roll_no", "").strip() or None

        if not all([full_name, email, password, role, department]):
            flash("All fields are required.", "danger")
            return render_template("admin/add_user.html")

        if role not in ("student", "faculty", "hod", "admin"):
            flash("Invalid role selected.", "danger")
            return render_template("admin/add_user.html")

        # Check duplicate email
        cur = get_cursor()
        cur.execute("SELECT id FROM users WHERE email = %s", (email,))
        if cur.fetchone():
            flash("Email already exists.", "warning")
            cur.close()
            return render_template("admin/add_user.html")

        hashed_pw = generate_password_hash(password)
        cur.execute(
            """INSERT INTO users (full_name, email, password, role, department, roll_no, status)
               VALUES (%s, %s, %s, %s, %s, %s, 'active')""",
            (full_name, email, hashed_pw, role, department, roll_no)
        )
        mysql.connection.commit()
        cur.close()

        flash("User added successfully!", "success")
        return redirect(url_for("admin_users"))

    return render_template("admin/add_user.html")


@app.route("/admin/users/edit/<int:user_id>", methods=["GET", "POST"])
@role_required("admin")
def admin_edit_user(user_id):
    """Admin: edit an existing user."""
    cur = get_cursor()
    cur.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    user = cur.fetchone()

    if not user:
        cur.close()
        flash("User not found.", "danger")
        return redirect(url_for("admin_users"))

    if request.method == "POST":
        full_name  = request.form.get("full_name", "").strip()
        department = request.form.get("department", "").strip()
        roll_no    = request.form.get("roll_no", "").strip() or None
        status     = request.form.get("status", "active")
        new_pw     = request.form.get("password", "").strip()

        if not all([full_name, department]):
            flash("Name and department are required.", "danger")
            return render_template("admin/edit_user.html", user=user)

        if new_pw:
            # Update password too
            hashed_pw = generate_password_hash(new_pw)
            cur.execute(
                """UPDATE users SET full_name=%s, department=%s, roll_no=%s, status=%s, password=%s
                   WHERE id=%s""",
                (full_name, department, roll_no, status, hashed_pw, user_id)
            )
        else:
            cur.execute(
                "UPDATE users SET full_name=%s, department=%s, roll_no=%s, status=%s WHERE id=%s",
                (full_name, department, roll_no, status, user_id)
            )

        mysql.connection.commit()
        cur.close()
        flash("User updated successfully!", "success")
        return redirect(url_for("admin_users"))

    cur.close()
    return render_template("admin/edit_user.html", user=user)


@app.route("/admin/users/delete/<int:user_id>", methods=["POST"])
@role_required("admin")
def admin_delete_user(user_id):
    """Admin: delete a user (cannot delete self)."""
    if user_id == session["user_id"]:
        flash("You cannot delete your own account.", "danger")
        return redirect(url_for("admin_users"))

    cur = get_cursor()
    cur.execute("DELETE FROM users WHERE id = %s", (user_id,))
    mysql.connection.commit()
    cur.close()

    flash("User deleted successfully.", "info")
    return redirect(url_for("admin_users"))


@app.route("/admin/users/toggle/<int:user_id>", methods=["POST"])
@role_required("admin")
def admin_toggle_user(user_id):
    """Admin: activate or deactivate a user."""
    cur = get_cursor()
    cur.execute("SELECT status FROM users WHERE id = %s", (user_id,))
    user = cur.fetchone()

    if not user:
        flash("User not found.", "danger")
    else:
        new_status = "inactive" if user["status"] == "active" else "active"
        cur.execute("UPDATE users SET status = %s WHERE id = %s", (new_status, user_id))
        mysql.connection.commit()
        flash(f"User status changed to {new_status}.", "info")

    cur.close()
    return redirect(url_for("admin_users"))


@app.route("/admin/leaves")
@role_required("admin")
def admin_leaves():
    """Admin: view all leave applications."""
    status_filter = request.args.get("status", "")
    search        = request.args.get("search", "").strip()

    query  = """SELECT la.*, u.full_name, u.roll_no, u.department
                FROM leave_applications la
                JOIN users u ON la.student_id = u.id
                WHERE 1=1"""
    params = []

    if status_filter in APPROVAL_STATUSES:
        query  += " AND la.status = %s"
        params.append(status_filter)

    if search:
        query  += " AND u.full_name LIKE %s"
        params.append(f"%{search}%")

    query += " ORDER BY la.applied_at DESC"

    cur = get_cursor()
    cur.execute(query, params)
    leaves = cur.fetchall()
    cur.close()

    return render_template(
        "admin/leave_records.html",
        leaves=leaves, status_filter=status_filter, search=search
    )


@app.route("/admin/reports")
@role_required("admin")
def admin_reports():
    """Admin: summary reports."""
    cur = get_cursor()

    # Dept-wise leave count
    cur.execute(
        """SELECT u.department, COUNT(*) AS cnt
           FROM leave_applications la
           JOIN users u ON la.student_id = u.id
           GROUP BY u.department"""
    )
    dept_stats = cur.fetchall()

    # Monthly leave applications (current year)
    cur.execute(
        """SELECT MONTH(applied_at) AS month, COUNT(*) AS cnt
           FROM leave_applications
           WHERE YEAR(applied_at) = YEAR(CURDATE())
           GROUP BY MONTH(applied_at)"""
    )
    monthly = cur.fetchall()

    # Leave type breakdown
    cur.execute(
        """SELECT leave_type, COUNT(*) AS cnt
           FROM leave_applications
           GROUP BY leave_type"""
    )
    type_stats = cur.fetchall()

    cur.close()
    return render_template(
        "admin/reports.html",
        dept_stats=dept_stats, monthly=monthly, type_stats=type_stats
    )


@app.route("/admin/profile")
@role_required("admin")
def admin_profile():
    """Admin: view their profile."""
    cur = get_cursor()
    cur.execute("SELECT * FROM users WHERE id = %s", (session["user_id"],))
    user = cur.fetchone()
    cur.close()
    return render_template("admin/profile.html", user=user)


# ──────────────────────────────────────────────
# Run Application
# ──────────────────────────────────────────────
if __name__ == "__main__":
    app.run(debug=True)
