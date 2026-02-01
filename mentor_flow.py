import tkinter as tk
from tkinter import messagebox
import sqlite3

DB_PATH = r"D:\Mentor Mentee Sem 3 Project\mentor_mentee.db"

CURRENT_MENTOR_ID = None


# ---------------- DATABASE ----------------
def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# ---------------- VERIFICATION STATUS ----------------
def get_verification_status(student_id):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute(
        "SELECT COUNT(*) FROM Attendance WHERE student_id=? AND status='PENDING'",
        (student_id,)
    )
    att_pending = cur.fetchone()[0]

    cur.execute(
        "SELECT COUNT(*) FROM Marks WHERE student_id=? AND status='PENDING'",
        (student_id,)
    )
    marks_pending = cur.fetchone()[0]

    conn.close()

    if att_pending > 0 or marks_pending > 0:
        return "Pending Verification"
    return "All Submissions Verified"


# ---------------- ENTRY POINT ----------------
def mentor_login_success(mentor_id, root):
    global CURRENT_MENTOR_ID
    CURRENT_MENTOR_ID = mentor_id
    mentor_dashboard(root)


# ---------------- DASHBOARD ----------------
def mentor_dashboard(root):
    win = tk.Toplevel(root)
    win.title("Mentor Dashboard")
    win.geometry("750x420")

    tk.Label(
        win,
        text="My Students",
        font=("Arial", 14, "bold")
    ).pack(pady=10)

    listbox = tk.Listbox(win, width=110)
    listbox.pack(pady=10)

    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        SELECT student_id, name, roll_no
        FROM Student
        WHERE mentor_id=?
    """, (CURRENT_MENTOR_ID,))
    students = cur.fetchall()
    conn.close()

    student_ids = []

    for s in students:
        status = get_verification_status(s["student_id"])
        text = f"{s['roll_no']} | {s['name']} | {status}"
        listbox.insert(tk.END, text)
        student_ids.append(s["student_id"])

    def view_student():
        sel = listbox.curselection()
        if not sel:
            messagebox.showerror("Error", "Select a student")
            return

        student_id = student_ids[sel[0]]
        win.destroy()
        student_detail_view(student_id, root)

    tk.Button(
        win,
        text="View Student Details",
        width=25,
        command=view_student
    ).pack(pady=10)


# ---------------- STUDENT DETAIL VIEW ----------------
def student_detail_view(student_id, root):
    win = tk.Toplevel(root)
    win.title("Student Details")
    win.geometry("780x620")

    conn = get_conn()
    cur = conn.cursor()

    # ---------- PERSONAL DETAILS ----------
    cur.execute("""
        SELECT name, roll_no, dob, father_name, mother_name,
               father_phone, mother_phone, home_address
        FROM Student
        WHERE student_id=?
    """, (student_id,))
    s = cur.fetchone()

    tk.Label(win, text="Personal Details",
             font=("Arial", 13, "bold")).pack(pady=5)

    details = (
        f"Name: {s['name']}\n"
        f"Roll No: {s['roll_no']}\n"
        f"DOB: {s['dob']}\n"
        f"Father: {s['father_name']} ({s['father_phone']})\n"
        f"Mother: {s['mother_name']} ({s['mother_phone']})\n"
        f"Address: {s['home_address']}"
    )

    tk.Label(win, text=details, justify="left").pack(pady=5)

    # ---------- ATTENDANCE ----------
    tk.Label(win, text="Attendance",
             font=("Arial", 12, "bold")).pack(pady=5)

    cur.execute("""
        SELECT att_id, month, attendance_percent, status
        FROM Attendance
        WHERE student_id=?
    """, (student_id,))
    attendance = cur.fetchall()

    att_list = tk.Listbox(win, width=95)
    att_list.pack()

    att_ids = []
    for a in attendance:
        att_list.insert(
            tk.END,
            f"{a['month']} | {a['attendance_percent']}% | {a['status']}"
        )
        att_ids.append(a["att_id"])

    def approve_attendance():
        sel = att_list.curselection()
        if not sel:
            messagebox.showerror("Error", "Select attendance record")
            return

        att_id = att_ids[sel[0]]

        conn2 = get_conn()
        cur2 = conn2.cursor()
        cur2.execute("""
            UPDATE Attendance
            SET status='APPROVED'
            WHERE att_id=? AND status='PENDING'
        """, (att_id,))
        conn2.commit()
        conn2.close()

        win.destroy()
        mentor_dashboard(root)

    tk.Button(
        win,
        text="Approve Attendance",
        command=approve_attendance
    ).pack(pady=5)

    # ---------- MARKS ----------
    tk.Label(win, text="Marks",
             font=("Arial", 12, "bold")).pack(pady=5)

    cur.execute("""
        SELECT mark_id, semester, mid_sem, end_sem, status
        FROM Marks
        WHERE student_id=?
    """, (student_id,))
    marks = cur.fetchall()

    mark_list = tk.Listbox(win, width=95)
    mark_list.pack()

    mark_ids = []
    for m in marks:
        mark_list.insert(
            tk.END,
            f"Sem {m['semester']} | Mid {m['mid_sem']} | End {m['end_sem']} | {m['status']}"
        )
        mark_ids.append(m["mark_id"])

    def approve_marks():
        sel = mark_list.curselection()
        if not sel:
            messagebox.showerror("Error", "Select marks record")
            return

        mark_id = mark_ids[sel[0]]

        conn2 = get_conn()
        cur2 = conn2.cursor()
        cur2.execute("""
            UPDATE Marks
            SET status='APPROVED'
            WHERE mark_id=? AND status='PENDING'
        """, (mark_id,))
        conn2.commit()
        conn2.close()

        win.destroy()
        mentor_dashboard(root)

    tk.Button(
        win,
        text="Approve Marks",
        command=approve_marks
    ).pack(pady=5)

    conn.close()
