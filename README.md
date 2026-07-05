"# Student Management System

A web-based Student Management System built with **Flask + MySQL + HTML/CSS**.
Includes admin & student authentication, student CRUD, daily attendance, search, and dashboards.

---

## 1. Project Structure

```
student_management/
├── app.py                 # Main Flask application (all routes)
├── config.py              # Reads env vars
├── db.py                  # MySQL connection pool & query helper
├── requirements.txt       # Python dependencies
├── schema.sql             # MySQL schema (run once)
├── .env.example           # Copy to .env and fill in your creds
├── static/
│   └── css/
│       └── style.css      # Modern dashboard styling
└── templates/
    ├── base.html          # Shared layout (sidebar + topbar)
    ├── login.html
    ├── register.html
    ├── admin_dashboard.html
    ├── student_dashboard.html
    ├── students_list.html
    ├── add_student.html
    ├── edit_student.html
    ├── attendance.html
    └── attendance_view.html
```

---

## 2. Prerequisites

- **Python 3.9+**
- **MySQL 5.7+** (or MariaDB) installed and running
- pip / venv

---

## 3. Setup Instructions

### Step 1 — Create the MySQL database
Open your MySQL client (Workbench, CLI, phpMyAdmin) and run the file `schema.sql`:

```bash
mysql -u root -p < schema.sql
```

This creates:
- Database `student_management`
- Tables: `admin`, `students`, `attendance`

### Step 2 — Create a virtual environment & install dependencies

```bash
cd student_management
python -m venv venv
# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate

pip install -r requirements.txt
```

### Step 3 — Configure environment variables

Copy `.env.example` to `.env` and fill in **your MySQL password**:

```
SECRET_KEY=some-random-string
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=your_mysql_password
MYSQL_DB=student_management
ADMIN_USERNAME=admin
ADMIN_PASSWORD=admin123
```

### Step 4 — Run the app

```bash
python app.py
```

Open http://localhost:5000

The **admin user is auto-created** on first run using the credentials from `.env`.

---

## 4. Default Credentials

| Role    | Username / Email          | Password  |
|---------|---------------------------|-----------|
| Admin   | `admin`                   | `admin123` |
| Student | Register via `/register` (or admin adds one) | (chosen by you) |

Change the admin password from `.env` before deploying.

---

## 5. Features

| Feature | Where |
|---|---|
| **Student Registration** | `/register` — students sign up themselves |
| **Login Authentication** | `/login` — role toggle (Admin / Student), password hashing via Werkzeug |
| **Add Student** | Admin → “Add Student” |
| **Update Student** | Admin → Students list → “Edit” |
| **Delete Student** | Admin → Students list → “Delete” (with confirm) |
| **Search Student** | Admin → Students list → search bar (name / roll no / email / course) |
| **Attendance** | Admin marks Present/Absent per date; Student views own history |
| **Dashboard** | Admin: total students, present/absent today, recent adds. Student: attendance %, profile snapshot |
| **Database Integration** | MySQL via `mysql-connector-python` connection pool |

---

## 6. How the Code is Organised (for interviews)

- **`app.py`** — all Flask routes grouped by concern (Auth → Dashboard → Student CRUD → Attendance). Uses a small `login_required(role=…)` decorator for access control.
- **`db.py`** — a single `query()` helper that uses a **MySQL connection pool**, so you never leak connections. Every route calls this helper.
- **`config.py`** — pulls all secrets from `.env` (using `python-dotenv`).
- **`schema.sql`** — the exact SQL you can walk an interviewer through: 3 tables, foreign key on attendance, unique `(student_id, attendance_date)` so re-marking updates instead of duplicating.
- **`templates/base.html`** — one shared layout with a sidebar; every page extends it → keeps HTML DRY.
- **`static/css/style.css`** — hand-written CSS (no framework) so you can explain every rule.

---

## 7. Interview Talking Points

1. **CRUD** — students table has full Create/Read/Update/Delete via 5 routes; deletes cascade to attendance thanks to `ON DELETE CASCADE`.
2. **Authentication** — two roles (admin, student) share one login route; passwords stored via `werkzeug.security.generate_password_hash` (PBKDF2). Sessions handled by Flask’s signed cookies.
3. **Attendance design choice** — one row per `(student_id, date)`. Uses `INSERT ... ON DUPLICATE KEY UPDATE` so re-submitting the form for the same day just updates the status.
4. **Search** — server-side `LIKE %q%` across 4 columns; simple, indexable, no ORM overhead.
5. **Security basics** — parameterised queries (SQL injection safe), password hashing, role-based route guarding, CSRF-friendly forms (add Flask-WTF if you want stricter CSRF).
6. **Scalability** — used a connection pool instead of opening a new MySQL connection per request.

---

## 8. Troubleshooting

- **`mysql.connector.errors.ProgrammingError: 1045 Access denied`** → wrong `MYSQL_PASSWORD` in `.env`.
- **`Unknown database 'student_management'`** → you skipped `schema.sql`. Run it first.
- **Port 5000 busy** → change `port=5000` in `app.py` last line.
- **CSS not loading** → make sure `static/css/style.css` path is correct and the app is served from the `student_management/` folder.

---

## 9. What to Say in an Interview (30-sec pitch)

> “I built a Flask + MySQL Student Management System with role-based login for admins and students. Admins can perform full CRUD on student records, mark daily Present/Absent attendance, and search students; students can register, view their profile, and see their attendance percentage. Data is stored in a normalised 3-table MySQL schema with foreign keys and a unique constraint on (student, date) so attendance can’t be double-recorded. Passwords are hashed with Werkzeug, and all DB access goes through a parameterised query helper on top of a connection pool.”
"