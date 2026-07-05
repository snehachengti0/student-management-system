# 🎓 Student Management System

A full-stack **Student Management System** built using **Python Flask** and **MySQL**. The application provides separate Admin and Student modules for managing students, attendance, and authentication through a simple, responsive web interface.

---

## 🚀 Features

### 👨‍💼 Admin
- Secure Admin Login
- Dashboard with statistics
- Add new students
- View all students
- Edit student details
- Search students
- Mark daily attendance
- View attendance records

### 👨‍🎓 Student
- Student Registration
- Secure Login
- View personal dashboard
- Check attendance records

---

## 🛠️ Tech Stack

- **Backend:** Python, Flask
- **Frontend:** HTML5, CSS3, Jinja2
- **Database:** MySQL
- **Authentication:** Password Hashing
- **Version Control:** Git & GitHub

---

## 📂 Project Structure

```
student-management-system/
│── static/
│   └── css/
│
│── templates/
│   ├── login.html
│   ├── register.html
│   ├── admin_dashboard.html
│   ├── student_dashboard.html
│   ├── students_list.html
│   ├── add_student.html
│   ├── edit_student.html
│   ├── attendance.html
│   ├── attendance_view.html
│   └── base.html
│
│── app.py
│── db.py
│── config.py
│── schema.sql
│── requirements.txt
│── README.md
```

---

## ⚙️ Installation

### 1. Clone the repository

```bash
git clone https://github.com/snehachengti0/student-management-system.git
cd student-management-system
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it:

**Windows**

```bash
.venv\Scripts\activate
```

**Linux / Mac**

```bash
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure MySQL

Create a database:

```sql
CREATE DATABASE student_management;
```

Import the schema:

```sql
SOURCE schema.sql;
```

### 5. Update Database Configuration

Edit `config.py` and update your MySQL credentials.

Example:

```python
MYSQL_HOST = "localhost"
MYSQL_USER = "root"
MYSQL_PASSWORD = "your_password"
MYSQL_DB = "student_management"
```

### 6. Run the application

```bash
python app.py
```

Open your browser:

```
http://127.0.0.1:5000
```

---

## 📸 Screenshots

Add screenshots here:

- Login Page
- Admin Dashboard
- Student Dashboard
- Student List
- Attendance Page

---

## 🔐 Default Admin Login

Username:

```
admin
```

Password:

```
admin123
```

*(Change these credentials before deploying.)*

---

## 📈 Future Enhancements

- Export Attendance to Excel/PDF
- Email Notifications
- Student Profile Photos
- Password Reset
- Charts & Analytics
- Responsive Mobile UI

---

## 👩‍💻 Author

**Sneha Chengti**

GitHub:
https://github.com/snehachengti0

---

## ⭐ If you found this project useful

Please consider giving it a ⭐ on GitHub.




