import tkinter as tk
from tkinter import messagebox
import sqlite3

DB_PATH = r"D:\Mentor Mentee Sem 3 Project\mentor_mentee.db"


# ---------------- DATABASE ----------------
def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# ---------------- PROFILE CHECK ----------------
def is_profile_complete(student_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        SELECT dob, father_name, mother_name,
               father_phone, mother_phone, home_address
        FROM Student
        WHERE student_id = ?
    """, (student_id,))
    row = cur.fetchone()
    conn.close()
    return row and all(row)


# ---------------- ENTRY POINT ----------------
def student_login_success(student_id, root):
    if not is_profile_complete(student_id):
        personal_details_form(student_id, root)
    else:
        attendance_form(student_id, root)


# ---------------- PERSONAL DETAILS ----------------
def personal_details_form(student_id, root):
    win = tk.Toplevel(root)
    win.title("Personal Details")
    win.geometry("420x520")

    tk.Label(win, text="Personal Details",
             font=("Arial", 13, "bold")).pack(pady=10)

    def field(label):
        tk.Label(win, text=label).pack()
        e = tk.Entry(win, width=35)
        e.pack(pady=4)
        return e

    dob = field("DOB (YYYY-MM-DD)")
    father_name = field("Father Name")
    mother_name = field("Mother Name")
    father_phone = field("Father Phone (10 digits)")
    mother_phone = field("Mother Phone (10 digits)")
    home_address = field("Home Address")

    def save():
        if not (father_phone.get().isdigit() and len(father_phone.get()) == 10):
            messagebox.showerror("Error", "Invalid father's phone")
            return
        if not (mother_phone.get().isdigit() and len(mother_phone.get()) == 10):
            messagebox.showerror("Error", "Invalid mother's phone")
            return

        conn = get_conn()
        cur = conn.cursor()
        cur.execute("""
            UPDATE Student
            SET dob=?, father_name=?, mother_name=?,
                father_phone=?, mother_phone=?, home_address=?
            WHERE student_id=?
        """, (
            dob.get(), father_name.get(), mother_name.get(),
            father_phone.get(), mother_phone.get(),
            home_address.get(), student_id
        ))
        conn.commit()
        conn.close()

        win.destroy()
        attendance_form(student_id, root)

    tk.Button(win, text="Save & Continue", command=save).pack(pady=20)


# ---------------- ATTENDANCE (PENDING) ----------------
def attendance_form(student_id, root):
    win = tk.Toplevel(root)
    win.title("Attendance")
    win.geometry("350x300")

    tk.Label(win, text="Attendance Entry",
             font=("Arial", 12, "bold")).pack(pady=10)

    month = tk.Entry(win, width=25)
    percent = tk.Entry(win, width=25)

    tk.Label(win, text="Month (YYYY-MM)").pack()
    month.pack(pady=5)

    tk.Label(win, text="Attendance %").pack()
    percent.pack(pady=5)

    def submit():
        try:
            p = float(percent.get())
            if not (0 <= p <= 100):
                raise ValueError
        except:
            messagebox.showerror("Error", "Attendance must be 0–100")
            return

        conn = get_conn()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO Attendance
            (student_id, month, attendance_percent, status)
            VALUES (?, ?, ?, 'PENDING')
        """, (student_id, month.get(), p))
        conn.commit()
        conn.close()

        win.destroy()
        marks_form(student_id, root)

    tk.Button(win, text="Next", command=submit).pack(pady=20)


# ---------------- MARKS (PENDING) ----------------
def marks_form(student_id, root):
    win = tk.Toplevel(root)
    win.title("Marks Entry")
    win.geometry("350x350")

    tk.Label(win, text="Marks Entry",
             font=("Arial", 12, "bold")).pack(pady=10)

    semester = tk.Entry(win, width=25)
    mid = tk.Entry(win, width=25)
    end = tk.Entry(win, width=25)

    tk.Label(win, text="Semester (e.g. 3)").pack()
    semester.pack(pady=5)

    tk.Label(win, text="Mid Sem (0–30)").pack()
    mid.pack(pady=5)

    tk.Label(win, text="End Sem (0–50)").pack()
    end.pack(pady=5)

    def submit():
        try:
            sem = int(semester.get())
            midv = float(mid.get())
            endv = float(end.get())

            if sem <= 0:
                raise ValueError
            if not (0 <= midv <= 30 and 0 <= endv <= 50):
                raise ValueError

        except:
            messagebox.showerror("Error", "Invalid semester or marks")
            return

        conn = get_conn()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO Marks
            (student_id, semester, mid_sem, end_sem, status)
            VALUES (?, ?, ?, ?, 'PENDING')
        """, (student_id, sem, midv, endv))
        conn.commit()
        conn.close()

        win.destroy()
        status_screen(root)

    tk.Button(win, text="Submit Marks", command=submit).pack(pady=20)


# ---------------- STATUS ----------------
def status_screen(root):
    win = tk.Toplevel(root)
    win.title("Status")
    win.geometry("320x220")

    tk.Label(
        win,
        text="Submission Successful\n\nSTATUS: PENDING\nWaiting for mentor approval",
        font=("Arial", 11),
        fg="orange",
        justify="center"
    ).pack(expand=True)
