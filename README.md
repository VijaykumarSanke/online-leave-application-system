# 📚 Online Leave Application System for College
**CBP Project | Python Flask + MySQL + Bootstrap 5**

---

## 🚀 Setup Instructions

### Step 1: Install Python Packages
```bash
pip install -r requirements.txt
```

### Step 2: Start XAMPP
- Open **XAMPP Control Panel**
- Start **Apache** and **MySQL**

### Step 3: Create the Database
1. Open your browser → go to `http://localhost/phpmyadmin`
2. Click **New** → type database name: `college_leave_system` → Click **Create**
3. Click the database → go to the **SQL** tab
4. Open `database.sql` from this project folder
5. Copy all content and paste into the SQL tab → Click **Go**

### Step 4: Seed the Database (Insert Hashed Passwords)
```bash
python seed_db.py
```
This inserts all sample users with properly hashed passwords.

### Step 5: Run the Flask App
```bash
python app.py
```
Open browser → `http://127.0.0.1:5000`

---

## 🔐 Test Login Credentials

| Role    | Email                   | Password     |
|---------|-------------------------|--------------|
| Admin   | admin@college.com       | Admin@123    |
| Faculty | faculty1@college.com    | Faculty@123  |
| Faculty | faculty2@college.com    | Faculty@123  |
| Student | student1@college.com    | Student@123  |
| Student | student2@college.com    | Student@123  |

---

## 📁 Project Structure

```
online_leave_system/
├── app.py               ← Main Flask app with all routes
├── config.py            ← Database & secret key config
├── seed_db.py           ← Inserts sample data with hashed passwords
├── requirements.txt     ← Python dependencies
├── database.sql         ← MySQL schema
├── README.md            ← This file
│
├── static/
│   ├── css/style.css    ← All custom styles
│   └── js/script.js     ← Client-side interactions
│
└── templates/
    ├── base.html        ← Master layout with dynamic sidebar
    ├── login.html
    ├── register.html
    ├── student/
    │   ├── dashboard.html
    │   ├── apply_leave.html
    │   ├── my_leaves.html
    │   └── profile.html
    ├── faculty/
    │   ├── dashboard.html
    │   ├── leave_requests.html
    │   ├── review_leave.html
    │   └── profile.html
    └── admin/
        ├── dashboard.html
        ├── manage_users.html
        ├── add_user.html
        ├── edit_user.html
        ├── leave_records.html
        ├── reports.html
        └── profile.html
```

---

## 📖 Viva / Project Explanation

### What is this project?
This is an **Online Leave Application System** for colleges. It replaces the traditional paper-based leave process with a digital web application where students can apply for leave online and faculty/admin can manage it.

### Tech Stack Used
| Layer     | Technology           |
|-----------|----------------------|
| Frontend  | HTML, CSS, Bootstrap 5, JavaScript |
| Backend   | Python Flask         |
| Database  | MySQL (via XAMPP)    |
| Auth      | Session-based + Werkzeug password hashing |

### Modules

#### 1. Authentication Module
- Login page validates email + password from database
- Password is hashed using `Werkzeug` — never stored as plain text
- After login, the user's **role** is read from the database
- Flask `session` stores user info securely
- **Role-based redirection**: student → student dashboard, faculty → faculty dashboard, admin → admin dashboard

#### 2. Student Module
- Apply for leave with: title, type, dates, reason
- View all applications with current status (Pending / Approved / Rejected)
- Edit or delete **only pending** applications
- See faculty remarks when approved/rejected

#### 3. Faculty Module
- View all student leave requests
- Filter by status or search by student name
- Open a request and **approve or reject** it with remarks
- View history of processed requests

#### 4. Admin Module
- View system-wide statistics
- **Full CRUD** for user management (add, edit, delete, activate/deactivate)
- View all leave records with filters
- View summary reports (department-wise, type-wise, monthly)

### Database Tables
| Table              | Purpose                              |
|--------------------|--------------------------------------|
| `users`            | Stores all users (student/faculty/admin) with hashed passwords |
| `leave_applications` | Stores all leave requests with status |
| `departments`      | List of college departments          |

### Security Features
- Passwords hashed with `Werkzeug` (bcrypt-based)
- SQL injection prevented using **parameterized queries**
- **Session-based authentication**
- **Role-based route protection** — students cannot access faculty or admin pages
- Unauthorized access redirected to login

### Key Flask Concepts Used
- **`@app.route()`** — maps URLs to Python functions
- **`render_template()`** — renders HTML with Jinja2
- **`redirect()` + `url_for()`** — navigation between routes
- **`session`** — stores logged-in user info across requests
- **`flash()`** — shows success/error messages
- **`@wraps` decorators** — for custom route protection

### Future Enhancements
- Email notifications when leave is approved/rejected
- PDF export of leave history
- Leave balance tracking (e.g., 12 sick leaves per year)
- Student can upload medical certificates
- OTP-based password reset
- Admin-configurable leave types and limits
- Multi-level approval (HOD → Principal)

---

## 💡 How Role-Based UI Works (Important for Viva)

1. User logs in → server checks email + password in MySQL
2. If valid → role is fetched from `users.role` column
3. Role is saved in **Flask session** (`session['role']`)
4. `base.html` template reads `session.role` and renders the **correct sidebar menu**
5. Each route has a `@role_required(...)` decorator — if a student tries to access `/faculty/...`, they are **blocked and redirected**
6. This is **fully database-driven** — change the role in DB and the user gets a different UI automatically

---

*Built with ❤️ for CBP Project*
