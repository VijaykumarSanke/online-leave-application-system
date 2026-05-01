-- ============================================================
-- Online Leave Application System for College
-- Database Schema + Sample Data
-- ============================================================

-- Create and use the database
CREATE DATABASE IF NOT EXISTS college_leave_system;
USE college_leave_system;

-- ============================================================
-- TABLE: departments
-- ============================================================
CREATE TABLE IF NOT EXISTS departments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    department_name VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- TABLE: users
-- ============================================================
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(150) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    password VARCHAR(256) NOT NULL,       -- hashed password
    role ENUM('student', 'faculty', 'hod', 'admin') NOT NULL,
    department VARCHAR(100),
    roll_no VARCHAR(50),                  -- only for students
    status ENUM('active', 'inactive') DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- TABLE: leave_applications
-- ============================================================
CREATE TABLE IF NOT EXISTS leave_applications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    title VARCHAR(200) NOT NULL,
    leave_type ENUM('sick_leave', 'personal_leave', 'emergency', 'others') NOT NULL,
    from_date DATE NOT NULL,
    to_date DATE NOT NULL,
    reason TEXT NOT NULL,
    status ENUM('pending', 'hod_approved', 'approved', 'rejected') DEFAULT 'pending',
    hod_remarks TEXT,
    faculty_remarks TEXT,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES users(id) ON DELETE CASCADE
);

-- ============================================================
-- SAMPLE DATA: Departments
-- ============================================================
INSERT INTO departments (department_name) VALUES
('Computer Science'),
('Information Technology'),
('Electronics'),
('Mechanical Engineering'),
('Civil Engineering');

-- ============================================================
-- SAMPLE DATA: Users
-- Passwords are hashed using Werkzeug's generate_password_hash
-- Plain passwords:
--   admin@college.com     → Admin@123
--   faculty1@college.com  → Faculty@123
--   faculty2@college.com  → Faculty@123
--   student1@college.com  → Student@123
--   student2@college.com  → Student@123
-- ============================================================
INSERT INTO users (full_name, email, password, role, department, roll_no, status) VALUES
(
    'Admin User',
    'admin@college.com',
    'scrypt:32768:8:1$8GRpxkr5Qa7HwrFz$6d77f2d9e39b0ef6a0c55c35f41e3d0c5e8e6f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2',
    'admin',
    'Administration',
    NULL,
    'active'
),
(
    'Dr. Meera Iyer',
    'hod1@college.com',
    'scrypt:32768:8:1$8GRpxkr5Qa7HwrFz$6d77f2d9e39b0ef6a0c55c35f41e3d0c5e8e6f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2',
    'hod',
    'Computer Science',
    NULL,
    'active'
),
(
    'Dr. Ramesh Kumar',
    'faculty1@college.com',
    'scrypt:32768:8:1$8GRpxkr5Qa7HwrFz$6d77f2d9e39b0ef6a0c55c35f41e3d0c5e8e6f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2',
    'faculty',
    'Computer Science',
    NULL,
    'active'
),
(
    'Prof. Sunita Sharma',
    'faculty2@college.com',
    'scrypt:32768:8:1$8GRpxkr5Qa7HwrFz$6d77f2d9e39b0ef6a0c55c35f41e3d0c5e8e6f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2',
    'faculty',
    'Information Technology',
    NULL,
    'active'
),
(
    'Amit Patel',
    'student1@college.com',
    'scrypt:32768:8:1$8GRpxkr5Qa7HwrFz$6d77f2d9e39b0ef6a0c55c35f41e3d0c5e8e6f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2',
    'student',
    'Computer Science',
    'CS2021001',
    'active'
),
(
    'Priya Singh',
    'student2@college.com',
    'scrypt:32768:8:1$8GRpxkr5Qa7HwrFz$6d77f2d9e39b0ef6a0c55c35f41e3d0c5e8e6f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2',
    'student',
    'Information Technology',
    'IT2021005',
    'active'
);

-- ============================================================
-- SAMPLE DATA: Leave Applications
-- ============================================================
INSERT INTO leave_applications (student_id, title, leave_type, from_date, to_date, reason, status, hod_remarks, faculty_remarks) VALUES
(5, 'Sick Leave Request', 'sick_leave', '2024-03-10', '2024-03-12', 'I have high fever and doctor advised me to rest for 3 days.', 'approved', 'Forwarded to faculty.', 'Get well soon. Leave approved.'),
(5, 'Family Function', 'personal_leave', '2024-03-20', '2024-03-21', 'Sister marriage ceremony at hometown.', 'approved', 'Approved by HOD.', 'Approved. Best wishes to your family.'),
(5, 'Medical Emergency', 'emergency', '2024-04-01', '2024-04-02', 'Accident in family. Need to go to hospital.', 'pending', NULL, NULL),
(6, 'Health Issue', 'sick_leave', '2024-03-15', '2024-03-15', 'Severe migraine. Cannot attend classes.', 'rejected', 'Medical certificate not attached. Please reapply with documents.', NULL),
(6, 'Sports Event', 'others', '2024-04-05', '2024-04-07', 'Selected for inter-college cricket tournament.', 'hod_approved', 'Participation verified. Forwarded to faculty.', NULL);

-- NOTE: The password hashes above are placeholders.
-- The actual hashes will be generated by the Python script (seed_db.py).
-- Run: python seed_db.py   to insert properly hashed passwords.
