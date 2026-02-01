import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

# IMPORTANT: adjust path if needed
DB_PATH = r"D:\Mentor Mentee Sem 3 Project\mentor_mentee.db"

# import student flow
from student_flow import student_login_success
#import mentor flow
from mentor_flow import mentor_login_success



# ---------- DATABASE ----------
def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# ---------- LOGIN LOGIC ----------
def login():
    email = email_entry.get().strip()
    password = password_entry.get().strip()
    role = role_var.get()

    if not email or not password:
        messagebox.showerror("Error", "All fields are required")
        return

    try:
        conn = get_conn()
        cur = conn.cursor()

        if role == "Student":
            cur.execute(
                "SELECT * FROM Student WHERE email=? AND password=?",
                (email, password)
            )
        elif role == "Mentor":
            cur.execute(
                "SELECT * FROM Mentor WHERE email=? AND password=?",
                (email, password)
            )
        else:  # Admin
            cur.execute(
                "SELECT * FROM Admin WHERE email=? AND password=?",
                (email, password)
            )

        user = cur.fetchone()
        conn.close()

        if not user:
            messagebox.showerror("Login Failed", "Invalid credentials")
            return

        messagebox.showinfo("Success", f"{role} login successful")

        # ---- ROLE BASED FLOW ----
        if role == "Student":
            student_id = user["student_id"]
            root.withdraw()
            student_login_success(student_id, root)


        elif role == "Mentor":
            mentor_id = user["mentor_id"]
            root.withdraw()
            mentor_login_success(mentor_id, root)

        else:  # Admin
            messagebox.showinfo(
                "Admin",
                "Admin dashboard will be implemented next"
            )

    except Exception as e:
        messagebox.showerror("Error", str(e))


# ---------- GUI ----------
root = tk.Tk()
root.title("Mentor–Mentee Login")
root.geometry("350x320")
root.resizable(False, False)

tk.Label(
    root,
    text="Mentor–Mentee System",
    font=("Arial", 14, "bold")
).pack(pady=10)

tk.Label(root, text="Email").pack()
email_entry = tk.Entry(root, width=30)
email_entry.pack(pady=5)

tk.Label(root, text="Password").pack()
password_entry = tk.Entry(root, width=30, show="*")
password_entry.pack(pady=5)

tk.Label(root, text="Login As").pack()
role_var = tk.StringVar(value="Student")

role_dropdown = ttk.Combobox(
    root,
    textvariable=role_var,
    values=["Student", "Mentor", "Admin"],
    state="readonly",
    width=27
)
role_dropdown.pack(pady=5)

tk.Button(
    root,
    text="Login",
    width=15,
    command=login
).pack(pady=20)

root.mainloop()
