"""
seed_db.py
Run this script ONCE after importing database.sql to insert
properly hashed passwords for all sample users.

Usage:
    python seed_db.py
"""

import MySQLdb as mysql
from werkzeug.security import generate_password_hash

# ---- DB connection config (change if needed) ----
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "passwd": "",          # XAMPP default is empty password
    "db": "college_leave_system"
}

# Sample users with plain-text passwords
SAMPLE_USERS = [
    {
        "full_name": "Admin User",
        "email": "admin@college.com",
        "password": "Admin@123",
        "role": "admin",
        "department": "Administration",
        "roll_no": None,
        "status": "active"
    },
    {
        "full_name": "Dr. Meera Iyer",
        "email": "hod1@college.com",
        "password": "Hod@123",
        "role": "hod",
        "department": "Computer Science",
        "roll_no": None,
        "status": "active"
    },
    {
        "full_name": "Dr. Ramesh Kumar",
        "email": "faculty1@college.com",
        "password": "Faculty@123",
        "role": "faculty",
        "department": "Computer Science",
        "roll_no": None,
        "status": "active"
    },
    {
        "full_name": "Prof. Sunita Sharma",
        "email": "faculty2@college.com",
        "password": "Faculty@123",
        "role": "faculty",
        "department": "Information Technology",
        "roll_no": None,
        "status": "active"
    },
    {
        "full_name": "Amit Patel",
        "email": "student1@college.com",
        "password": "Student@123",
        "role": "student",
        "department": "Computer Science",
        "roll_no": "CS2021001",
        "status": "active"
    },
    {
        "full_name": "Priya Singh",
        "email": "student2@college.com",
        "password": "Student@123",
        "role": "student",
        "department": "Information Technology",
        "roll_no": "IT2021005",
        "status": "active"
    }
]

LEAVE_DATA = [
    (5, 'Sick Leave Request', 'sick_leave', '2024-03-10', '2024-03-12',
     'I have high fever and doctor advised me to rest for 3 days.', 'approved', 'Forwarded to faculty.', 'Get well soon. Leave approved.'),
    (5, 'Family Function', 'personal_leave', '2024-03-20', '2024-03-21',
     'Sister marriage ceremony at hometown.', 'approved', 'Approved by HOD.', 'Approved. Best wishes to your family.'),
    (5, 'Medical Emergency', 'emergency', '2024-04-01', '2024-04-02',
     'Accident in family. Need to go to hospital.', 'pending', None, None),
    (6, 'Health Issue', 'sick_leave', '2024-03-15', '2024-03-15',
     'Severe migraine. Cannot attend classes.', 'rejected',
     'Medical certificate not attached. Please reapply with documents.', None),
    (6, 'Sports Event', 'others', '2024-04-05', '2024-04-07',
     'Selected for inter-college cricket tournament.', 'hod_approved', 'Participation verified. Forwarded to faculty.', None),
]


def seed():
    conn = mysql.connect(**DB_CONFIG)
    cursor = conn.cursor()

    # Clear existing data (order matters for FK constraints)
    cursor.execute("DELETE FROM leave_applications")
    cursor.execute("DELETE FROM users")
    cursor.execute("ALTER TABLE users AUTO_INCREMENT = 1")
    cursor.execute("ALTER TABLE leave_applications AUTO_INCREMENT = 1")

    # Insert users with hashed passwords
    for user in SAMPLE_USERS:
        hashed_pw = generate_password_hash(user["password"])
        cursor.execute(
            """INSERT INTO users (full_name, email, password, role, department, roll_no, status)
               VALUES (%s, %s, %s, %s, %s, %s, %s)""",
            (user["full_name"], user["email"], hashed_pw,
             user["role"], user["department"], user["roll_no"], user["status"])
        )
        print(f"  [OK] Inserted {user['role']}: {user['email']}")

    # Insert leave applications
    for leave in LEAVE_DATA:
        cursor.execute(
            """INSERT INTO leave_applications
               (student_id, title, leave_type, from_date, to_date, reason, status, hod_remarks, faculty_remarks)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
            leave
        )

    conn.commit()
    cursor.close()
    conn.close()

    print("\nDONE: Database seeded successfully!\n")
    print("=" * 45)
    print("  LOGIN CREDENTIALS FOR TESTING")
    print("=" * 45)
    print(f"  ADMIN    : admin@college.com    / Admin@123")
    print(f"  HOD      : hod1@college.com      / Hod@123")
    print(f"  FACULTY  : faculty1@college.com / Faculty@123")
    print(f"  FACULTY  : faculty2@college.com / Faculty@123")
    print(f"  STUDENT  : student1@college.com / Student@123")
    print(f"  STUDENT  : student2@college.com / Student@123")
    print("=" * 45)


if __name__ == "__main__":
    seed()
