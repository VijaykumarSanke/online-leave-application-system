# Online Leave Application System

A web-based application developed to automate the leave application process in colleges.  
It allows **students** to apply for leave online, **faculty** to approve/reject requests, and **admins** to manage users and reports.

## Features
- Student leave application and tracking
- Faculty leave approval/rejection
- Admin dashboard and user management
- Role-based login system
- Leave records and reports
- Different UI for Student / Faculty / Admin

## Tech Stack
- **Frontend:** HTML, CSS, JavaScript, Bootstrap
- **Backend:** Python Flask
- **Database:** MySQL
- **Tools:** VS Code, XAMPP

## Modules
### Student Module
- Apply for leave
- Edit/Delete pending leave
- View leave history
- Track approval status

### Faculty Module
- View leave requests
- Approve/Reject applications
- Add remarks
- View approved history

### Admin Module
- Manage users
- View leave records
- Generate reports
- Monitor system activity

## How to Run
1. Clone the repository
2. Create virtual environment
3. Install dependencies
4. Import `database.sql` in MySQL
5. Run `seed_db.py`
6. Start the Flask app using `python app.py`

## Default Login Credentials

### Admin
- **Email:** admin@college.com
- **Password:** Admin@123

### Faculty
- **Email:** faculty1@college.com
- **Password:** Faculty@123

### Student
- **Email:** student1@college.com
- **Password:** Student@123

## Future Enhancements
- Email notifications
- PDF leave reports
- Mobile responsive improvements
- HOD / Principal approval workflow

## Author
**Vijaykumar Sanke**
