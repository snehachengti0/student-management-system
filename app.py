from datetime import date, datetime
from functools import wraps

from flask import (Flask, flash, redirect, render_template, request,
                   session, url_for)
from werkzeug.security import check_password_hash, generate_password_hash

from config import Config
from db import query

app = Flask(__name__)
app.config.from_object(Config)


# ---------- One-time admin seeding ----------
def seed_admin():
    row = query("SELECT id FROM admin WHERE username=%s",
                (Config.ADMIN_USERNAME,), fetchone=True)
    if not row:
        query(
            "INSERT INTO admin (username, password_hash) VALUES (%s, %s)",
            (Config.ADMIN_USERNAME,
             generate_password_hash(Config.ADMIN_PASSWORD)),
            commit=True,
        )
        print(f"[seed] Admin '{Config.ADMIN_USERNAME}' created.")


# ---------- Decorators ----------
def login_required(role=None):
    def wrapper(fn):
        @wraps(fn)
        def inner(*args, **kwargs):
            if "user_id" not in session:
                flash("Please log in first.", "error")
                return redirect(url_for("login"))
            if role and session.get("role") != role:
                flash("Access denied.", "error")
                return redirect(url_for("dashboard"))
            return fn(*args, **kwargs)
        return inner
    return wrapper


# ---------- Auth ----------
@app.route("/")
def index():
    if "user_id" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        role = request.form.get("role", "student")
        identifier = request.form.get("identifier", "").strip()
        password = request.form.get("password", "")

        if role == "admin":
            row = query("SELECT * FROM admin WHERE username=%s",
                        (identifier,), fetchone=True)
        else:
            row = query("SELECT * FROM students WHERE email=%s OR roll_no=%s",
                        (identifier, identifier), fetchone=True)

        if row and check_password_hash(row["password_hash"], password):
            session.clear()
            session["user_id"] = row["id"]
            session["role"] = role
            session["name"] = row.get("name") or row.get("username")
            flash(f"Welcome back, {session['name']}!", "success")
            return redirect(url_for("dashboard"))
        flash("Invalid credentials.", "error")

    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Student self-registration."""
    if request.method == "POST":
        form = request.form
        roll_no = form["roll_no"].strip()
        email = form["email"].strip().lower()
        password = form["password"]

        exists = query(
            "SELECT id FROM students WHERE roll_no=%s OR email=%s",
            (roll_no, email), fetchone=True,
        )
        if exists:
            flash("Roll number or email already registered.", "error")
            return redirect(url_for("register"))

        query(
            """INSERT INTO students
               (roll_no, name, email, password_hash, phone, course, year_of_study, address)
               VALUES (%s,%s,%s,%s,%s,%s,%s,%s)""",
            (roll_no, form["name"].strip(), email,
             generate_password_hash(password),
             form.get("phone"), form.get("course"),
             int(form.get("year_of_study") or 1),
             form.get("address")),
            commit=True,
        )
        flash("Registration successful. Please log in.", "success")
        return redirect(url_for("login"))
    return render_template("register.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out.", "success")
    return redirect(url_for("login"))


# ---------- Dashboard ----------
@app.route("/dashboard")
@login_required()
def dashboard():
    if session["role"] == "admin":
        total_students = query("SELECT COUNT(*) c FROM students",
                               fetchone=True)["c"]
        today = date.today().isoformat()
        present_today = query(
            "SELECT COUNT(*) c FROM attendance WHERE attendance_date=%s AND status='Present'",
            (today,), fetchone=True)["c"]
        absent_today = query(
            "SELECT COUNT(*) c FROM attendance WHERE attendance_date=%s AND status='Absent'",
            (today,), fetchone=True)["c"]
        recent = query("SELECT * FROM students ORDER BY id DESC LIMIT 5",
                       fetchall=True)
        return render_template("admin_dashboard.html",
                               total_students=total_students,
                               present_today=present_today,
                               absent_today=absent_today,
                               recent=recent, today=today)

    # student dashboard
    sid = session["user_id"]
    student = query("SELECT * FROM students WHERE id=%s", (sid,), fetchone=True)
    total = query("SELECT COUNT(*) c FROM attendance WHERE student_id=%s",
                  (sid,), fetchone=True)["c"]
    present = query(
        "SELECT COUNT(*) c FROM attendance WHERE student_id=%s AND status='Present'",
        (sid,), fetchone=True)["c"]
    percent = round((present / total * 100), 2) if total else 0.0
    return render_template("student_dashboard.html",
                           student=student, total=total,
                           present=present, percent=percent)


# ---------- Student CRUD (admin) ----------
@app.route("/students")
@login_required(role="admin")
def students_list():
    q = request.args.get("q", "").strip()
    if q:
        like = f"%{q}%"
        rows = query(
            """SELECT * FROM students
               WHERE name LIKE %s OR roll_no LIKE %s OR email LIKE %s OR course LIKE %s
               ORDER BY id DESC""",
            (like, like, like, like), fetchall=True,
        )
    else:
        rows = query("SELECT * FROM students ORDER BY id DESC", fetchall=True)
    return render_template("students_list.html", students=rows, q=q)


@app.route("/students/add", methods=["GET", "POST"])
@login_required(role="admin")
def add_student():
    if request.method == "POST":
        form = request.form
        exists = query(
            "SELECT id FROM students WHERE roll_no=%s OR email=%s",
            (form["roll_no"], form["email"].lower()), fetchone=True,
        )
        if exists:
            flash("Roll number or email already exists.", "error")
            return redirect(url_for("add_student"))
        query(
            """INSERT INTO students
               (roll_no, name, email, password_hash, phone, course, year_of_study, address)
               VALUES (%s,%s,%s,%s,%s,%s,%s,%s)""",
            (form["roll_no"].strip(), form["name"].strip(),
             form["email"].strip().lower(),
             generate_password_hash(form["password"]),
             form.get("phone"), form.get("course"),
             int(form.get("year_of_study") or 1),
             form.get("address")),
            commit=True,
        )
        flash("Student added.", "success")
        return redirect(url_for("students_list"))
    return render_template("add_student.html")


@app.route("/students/<int:sid>/edit", methods=["GET", "POST"])
@login_required(role="admin")
def edit_student(sid):
    student = query("SELECT * FROM students WHERE id=%s", (sid,), fetchone=True)
    if not student:
        flash("Student not found.", "error")
        return redirect(url_for("students_list"))

    if request.method == "POST":
        form = request.form
        query(
            """UPDATE students SET name=%s, email=%s, phone=%s,
                   course=%s, year_of_study=%s, address=%s
               WHERE id=%s""",
            (form["name"].strip(), form["email"].strip().lower(),
             form.get("phone"), form.get("course"),
             int(form.get("year_of_study") or 1),
             form.get("address"), sid),
            commit=True,
        )
        # Optional password change
        if form.get("password"):
            query("UPDATE students SET password_hash=%s WHERE id=%s",
                  (generate_password_hash(form["password"]), sid),
                  commit=True)
        flash("Student updated.", "success")
        return redirect(url_for("students_list"))
    return render_template("edit_student.html", student=student)


@app.route("/students/<int:sid>/delete", methods=["POST"])
@login_required(role="admin")
def delete_student(sid):
    query("DELETE FROM students WHERE id=%s", (sid,), commit=True)
    flash("Student deleted.", "success")
    return redirect(url_for("students_list"))


# ---------- Attendance ----------
@app.route("/attendance", methods=["GET", "POST"])
@login_required(role="admin")
def attendance():
    today = request.args.get("date") or date.today().isoformat()
    students = query("SELECT id, roll_no, name FROM students ORDER BY roll_no",
                     fetchall=True)

    if request.method == "POST":
        att_date = request.form.get("date") or today
        for s in students:
            status = request.form.get(f"status_{s['id']}", "Absent")
            query(
                """INSERT INTO attendance (student_id, attendance_date, status)
                   VALUES (%s,%s,%s)
                   ON DUPLICATE KEY UPDATE status=VALUES(status)""",
                (s["id"], att_date, status), commit=True,
            )
        flash(f"Attendance saved for {att_date}.", "success")
        return redirect(url_for("attendance", date=att_date))

    # Existing records for the chosen date -> {student_id: status}
    rows = query(
        "SELECT student_id, status FROM attendance WHERE attendance_date=%s",
        (today,), fetchall=True,
    )
    existing = {r["student_id"]: r["status"] for r in rows}
    return render_template("attendance.html", students=students,
                           existing=existing, today=today)


@app.route("/attendance/view")
@login_required()
def attendance_view():
    if session["role"] == "admin":
        sid = request.args.get("student_id", type=int)
        students = query("SELECT id, roll_no, name FROM students ORDER BY roll_no",
                         fetchall=True)
        records = []
        if sid:
            records = query(
                """SELECT attendance_date, status FROM attendance
                   WHERE student_id=%s ORDER BY attendance_date DESC""",
                (sid,), fetchall=True,
            )
        return render_template("attendance_view.html",
                               students=students, records=records,
                               selected=sid)
    # student view
    sid = session["user_id"]
    records = query(
        """SELECT attendance_date, status FROM attendance
           WHERE student_id=%s ORDER BY attendance_date DESC""",
        (sid,), fetchall=True,
    )
    return render_template("attendance_view.html",
                           students=None, records=records, selected=sid)


# ---------- Jinja filters ----------
@app.template_filter("fmtdate")
def fmtdate(value):
    if isinstance(value, (datetime, date)):
        return value.strftime("%d %b %Y")
    return value


if __name__ == "__main__":
    with app.app_context():
        seed_admin()
    app.run(debug=True, host="0.0.0.0", port=5000)
