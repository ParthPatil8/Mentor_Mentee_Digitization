#!/usr/bin/env python3
"""mentor_mentee_gui_fixed.py
Fixed Tkinter GUI for Mentor-Mentee SQLite DB with Add/Update/Delete student support.
This version fixes indentation issues that caused Pylance errors like 'return can be used only within a function'.
"""
import sqlite3
import os
import statistics
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

DB_PATH = os.path.join(os.path.dirname(__file__), 'mentor_mentee.db')
MARK_THRESHOLD = 60.0
ATTENDANCE_THRESHOLD = 75.0

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def create_tables():
    conn = get_conn()
    c = conn.cursor()
    c.executescript("""
    CREATE TABLE IF NOT EXISTS Mentor (
        mentor_id INTEGER PRIMARY KEY ,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        phone TEXT,
        department TEXT
    );
    CREATE TABLE IF NOT EXISTS Student (
        student_id INTEGER PRIMARY KEY ,
        name TEXT NOT NULL,
        roll_no TEXT UNIQUE,
        address TEXT,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        phone TEXT,
        parent_phone TEXT,
        mentor_id INTEGER,
        FOREIGN KEY (mentor_id) REFERENCES Mentor(mentor_id)
    );
    CREATE TABLE IF NOT EXISTS Marks (
        mark_id INTEGER PRIMARY KEY ,
        student_id INTEGER NOT NULL,
        semester INTEGER NOT NULL,
        mid_sem REAL,
        end_sem REAL,
        FOREIGN KEY (student_id) REFERENCES Student(student_id)
    );
    CREATE TABLE IF NOT EXISTS Attendance (
        att_id INTEGER PRIMARY KEY ,
        student_id INTEGER NOT NULL,
        month TEXT NOT NULL,
        attendance_percent REAL,
        FOREIGN KEY (student_id) REFERENCES Student(student_id)
    );
    CREATE TABLE IF NOT EXISTS ExtraCurricular (
        ec_id INTEGER PRIMARY KEY ,
        student_id INTEGER NOT NULL,
        activity_name TEXT,
        level TEXT,
        achievement TEXT,
        FOREIGN KEY (student_id) REFERENCES Student(student_id)
    );
    CREATE TABLE IF NOT EXISTS CoCurricular (
        cc_id INTEGER PRIMARY KEY ,
        student_id INTEGER NOT NULL,
        activity_name TEXT,
        level TEXT,
        achievement TEXT,
        FOREIGN KEY (student_id) REFERENCES Student(student_id)
    );
    """)
    conn.commit()
    conn.close()

def compute_avg_marks(student_id):
    conn = get_conn()
    rows = conn.execute("SELECT mid_sem, end_sem FROM Marks WHERE student_id = ?", (student_id,)).fetchall()
    conn.close()
    if not rows:
        return None
    per_sem_averages = []
    for r in rows:
        mid = r['mid_sem'] or 0
        end = r['end_sem'] or 0
        per_sem_averages.append((mid + end) / 2.0)
    return statistics.mean(per_sem_averages) if per_sem_averages else None

def get_overall_attendance(student_id):
    conn = get_conn()
    rows = conn.execute("SELECT attendance_percent FROM Attendance WHERE student_id = ?", (student_id,)).fetchall()
    conn.close()
    if not rows:
        return None
    values = [r['attendance_percent'] for r in rows if r['attendance_percent'] is not None]
    return statistics.mean(values) if values else None

def seed_sample_data():
    conn = get_conn()
    c = conn.cursor()
    existing = c.execute("SELECT COUNT(*) as cnt FROM Student").fetchone()['cnt']
    if existing:
        if not messagebox.askyesno("Seed data", "DB already has students. Overwrite sample data?"):
            return
    c.executescript("""
    DELETE FROM Mentor;
    DELETE FROM Student;
    DELETE FROM Marks;
    DELETE FROM Attendance;
    DELETE FROM ExtraCurricular;
    DELETE FROM CoCurricular;
    """)
    c.execute("INSERT INTO Mentor (name,email,password,phone,department) VALUES (?,?,?,?,?)",
              ('Dr. Sharma','sharma@fcrit.edu','mentor123','9876543210','CSE'))
    c.execute("INSERT INTO Mentor (name,email,password,phone,department) VALUES (?,?,?,?,?)",
              ('Dr. Rao','rao@fcrit.edu','mentor123','9876501234','CSE'))
    c.execute("INSERT INTO Student (name, roll_no, address, email, password, phone, parent_phone, mentor_id) VALUES (?,?,?,?,?,?,?,?)",
              ('Parth Patil','CSE201','Vashi','parth@fcrit.edu','parth123','9999999999','8888888888',1))
    c.execute("INSERT INTO Student (name, roll_no, address, email, password, phone, parent_phone, mentor_id) VALUES (?,?,?,?,?,?,?,?)",
              ('Ayesha Khan','CSE202','Nerul','ayesha@fcrit.edu','ayesha123','9999900000','7777777777',1))
    c.execute("INSERT INTO Student (name, roll_no, address, email, password, phone, parent_phone, mentor_id) VALUES (?,?,?,?,?,?,?,?)",
              ('Rohit Desai','CSE203','Vashi','rohit@fcrit.edu','rohit123','9999988888','6666666666',2))
    c.execute("INSERT INTO Marks (student_id, semester, mid_sem, end_sem) VALUES (?,?,?,?)",(1,1,78,82))
    c.execute("INSERT INTO Marks (student_id, semester, mid_sem, end_sem) VALUES (?,?,?,?)",(1,2,70,74))
    c.execute("INSERT INTO Marks (student_id, semester, mid_sem, end_sem) VALUES (?,?,?,?)",(2,1,40,45))
    c.execute("INSERT INTO Marks (student_id, semester, mid_sem, end_sem) VALUES (?,?,?,?)",(3,1,55,60))
    c.execute("INSERT INTO Attendance (student_id, month, attendance_percent) VALUES (?,?,?)",(1,'2025-09',92.0))
    c.execute("INSERT INTO Attendance (student_id, month, attendance_percent) VALUES (?,?,?)",(1,'2025-10',88.0))
    c.execute("INSERT INTO Attendance (student_id, month, attendance_percent) VALUES (?,?,?)",(2,'2025-09',60.0))
    c.execute("INSERT INTO Attendance (student_id, month, attendance_percent) VALUES (?,?,?)",(2,'2025-10',58.0))
    c.execute("INSERT INTO Attendance (student_id, month, attendance_percent) VALUES (?,?,?)",(3,'2025-09',76.0))
    c.execute("INSERT INTO ExtraCurricular (student_id, activity_name, level, achievement) VALUES (?,?,?,?)",(1,'Robotics Club','College','Member'))
    c.execute("INSERT INTO CoCurricular (student_id, activity_name, level, achievement) VALUES (?,?,?,?)",(1,'Coding Contest','State','2nd Place'))
    c.execute("INSERT INTO ExtraCurricular (student_id, activity_name, level, achievement) VALUES (?,?,?,?)",(2,'Debate Club','College',''))
    conn.commit()
    conn.close()
    messagebox.showinfo("Seed", "Sample data seeded.")

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Mentor-Mentee - GUI (fixed)")
        self.geometry("980x540")
        self.create_widgets()

    def create_widgets(self):
        top = ttk.Frame(self)
        top.pack(fill='x', padx=10, pady=10)

        ttk.Button(top, text="Seed Sample Data", command=seed_sample_data).pack(side='left', padx=4)
        ttk.Button(top, text="List Students", command=self.show_students).pack(side='left', padx=4)
        ttk.Button(top, text="Add Student", command=self.form_add_student).pack(side='left', padx=4)
        ttk.Button(top, text="Update Student", command=self.form_update_student).pack(side='left', padx=4)
        ttk.Button(top, text="Delete Student", command=self.delete_student_prompt).pack(side='left', padx=4)
        ttk.Button(top, text="Add Marks", command=self.form_add_marks).pack(side='left', padx=4)
        ttk.Button(top, text="Add Attendance", command=self.form_add_attendance).pack(side='left', padx=4)
        ttk.Button(top, text="Student Details", command=self.ask_and_show_student_details).pack(side='left', padx=4)
        ttk.Button(top, text="Weak/Strong (Marks)", command=self.show_weak_strong).pack(side='left', padx=4)
        ttk.Button(top, text="Attendance Defaulters", command=self.show_attendance_defaulters).pack(side='left', padx=4)

        self.tree = ttk.Treeview(self, columns=('A','B','C','D','E'), show='headings')
        self.tree.pack(fill='both', expand=True, padx=10, pady=10)
        self.clear_tree()

    def clear_tree(self, cols=None, headings=None):
        for i in self.tree.get_children():
            self.tree.delete(i)
        if cols is None:
            cols = ('A','B','C','D','E')
            headings = ('ID', 'Name', 'Roll No', 'Email', 'Mentor ID')
        self.tree.config(columns=cols)
        for i,col in enumerate(cols):
            self.tree.heading(col, text=headings[i] if headings and i < len(headings) else col)
            self.tree.column(col, width=160, anchor='w')

    def show_students(self):
        conn = get_conn()
        rows = conn.execute("SELECT student_id, name, roll_no, email, mentor_id FROM Student").fetchall()
        conn.close()
        self.clear_tree(cols=('ID','Name','Roll','Email','MentorID'),
                        headings=('ID','Name','Roll No','Email','MentorID'))
        for r in rows:
            self.tree.insert('', 'end', values=(r['student_id'], r['name'], r['roll_no'] or '', r['email'], r['mentor_id'] or ''))

    def form_add_student(self):
        w = tk.Toplevel(self); w.title("Add Student"); w.geometry("420x380")
        labels = ['Name','Roll No','Address','Email','Password','Phone','Parent Phone','Mentor ID (opt)']
        entries = {}
        for i,lab in enumerate(labels):
            ttk.Label(w, text=lab).grid(row=i, column=0, sticky='w', padx=8, pady=6)
            e = ttk.Entry(w); e.grid(row=i, column=1, padx=8, pady=6)
            entries[lab] = e
        def submit():
            vals = {k:entries[k].get().strip() for k in labels}
            try:
                mentor_id = int(vals['Mentor ID (opt)']) if vals['Mentor ID (opt)'] else None
            except ValueError:
                messagebox.showerror("Error","Mentor ID must be a number")
                return
            conn = get_conn()
            try:
                conn.execute("""INSERT INTO Student (name, roll_no, address, email, password, phone, parent_phone, mentor_id)
                                VALUES (?,?,?,?,?,?,?,?)""",(
                             vals['Name'] or None, vals['Roll No'] or None, vals['Address'] or None,
                              vals['Email'], vals['Password'], vals['Phone'] or None, vals['Parent Phone'] or None, mentor_id))
                conn.commit()
                messagebox.showinfo("OK","Student added.")
                w.destroy()
                self.show_students()
            except sqlite3.IntegrityError as e:
                messagebox.showerror("DB Error", str(e))
            finally:
                conn.close()
        ttk.Button(w, text="Submit", command=submit).grid(row=len(labels), column=0, columnspan=2, pady=12)

    def form_update_student(self):
        sid = simpledialog.askinteger("Update Student", "Enter Student ID to update")
        if not sid:
            return
        conn = get_conn()
        cur = conn.execute("SELECT * FROM Student WHERE student_id = ?", (sid,)).fetchone()
        conn.close()
        if not cur:
            messagebox.showerror("Not found", "Student ID not found")
            return
        w = tk.Toplevel(self); w.title("Update Student"); w.geometry("420x420")
        labels = ['Name','Roll No','Address','Email','Password','Phone','Parent Phone','Mentor ID (opt)']
        entries = {}
        values = {
            'Name': cur['name'] or '',
            'Roll No': cur['roll_no'] or '',
            'Address': cur['address'] or '',
            'Email': cur['email'] or '',
            'Password': cur['password'] or '',
            'Phone': cur['phone'] or '',
            'Parent Phone': cur['parent_phone'] or '',
            'Mentor ID (opt)': str(cur['mentor_id']) if cur['mentor_id'] else ''
        }
        for i,lab in enumerate(labels):
            ttk.Label(w, text=lab).grid(row=i, column=0, sticky='w', padx=8, pady=6)
            e = ttk.Entry(w); e.grid(row=i, column=1, padx=8, pady=6)
            e.insert(0, values[lab])
            entries[lab] = e
        def submit_update():
            vals = {k:entries[k].get().strip() for k in labels}
            try:
                mentor_id = int(vals['Mentor ID (opt)']) if vals['Mentor ID (opt)'] else None
            except ValueError:
                messagebox.showerror("Error","Mentor ID must be a number")
                return
            conn = get_conn()
            try:
                conn.execute("""UPDATE Student SET name=?, roll_no=?, address=?, email=?, password=?, phone=?, parent_phone=?, mentor_id=?
                                WHERE student_id=?""", (vals['Name'] or None, vals['Roll No'] or None, vals['Address'] or None,
                                                         vals['Email'], vals['Password'], vals['Phone'] or None, vals['Parent Phone'] or None, mentor_id, sid))
                conn.commit()
                messagebox.showinfo("OK","Student updated.")
                w.destroy()
                self.show_students()
            except sqlite3.IntegrityError as e:
                messagebox.showerror("DB Error", str(e))
            finally:
                conn.close()
        ttk.Button(w, text="Update", command=submit_update).grid(row=len(labels), column=0, columnspan=2, pady=12)

    def delete_student_prompt(self):
        sid = simpledialog.askinteger("Delete Student", "Enter Student ID to delete")
        if not sid:
            return
        conn = get_conn()
        cur = conn.execute("SELECT name FROM Student WHERE student_id = ?", (sid,)).fetchone()
        conn.close()
        if not cur:
            messagebox.showerror("Not found", "Student ID not found")
            return
        confirm = messagebox.askyesno("Confirm Delete", f"Delete student {cur['name']} and all related records?")
        if not confirm:
            return
        try:
            conn = get_conn()
            conn.execute("DELETE FROM Student WHERE student_id = ?", (sid,))
            conn.execute("DELETE FROM Marks WHERE student_id = ?", (sid,))
            conn.execute("DELETE FROM Attendance WHERE student_id = ?", (sid,))
            conn.execute("DELETE FROM ExtraCurricular WHERE student_id = ?", (sid,))
            conn.execute("DELETE FROM CoCurricular WHERE student_id = ?", (sid,))
            conn.commit()
            conn.close()
            messagebox.showinfo("Deleted", "Student and related records deleted.")
            self.show_students()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def form_add_marks(self):
        w = tk.Toplevel(self); w.title("Add Marks"); w.geometry("340x220")
        ttk.Label(w, text="Student ID").grid(row=0, column=0, padx=8, pady=8)
        sid = ttk.Entry(w); sid.grid(row=0, column=1)
        ttk.Label(w, text="Semester (int)").grid(row=1, column=0, padx=8, pady=8)
        sem = ttk.Entry(w); sem.grid(row=1, column=1)
        ttk.Label(w, text="Mid sem (0-100)").grid(row=2, column=0, padx=8, pady=8)
        mid = ttk.Entry(w); mid.grid(row=2, column=1)
        ttk.Label(w, text="End sem (0-100)").grid(row=3, column=0, padx=8, pady=8)
        end = ttk.Entry(w); end.grid(row=3, column=1)
        def submit():
            try:
                sidi = int(sid.get().strip())
                semester = int(sem.get().strip())
                midv = float(mid.get().strip() or 0)
                endv = float(end.get().strip() or 0)
            except ValueError:
                messagebox.showerror("Error","Please enter numeric values")
                return
            conn = get_conn()
            conn.execute("INSERT INTO Marks (student_id, semester, mid_sem, end_sem) VALUES (?,?,?,?)",
                         (sidi, semester, midv, endv))
            conn.commit(); conn.close()
            messagebox.showinfo("OK","Marks added.")
            w.destroy()
        ttk.Button(w, text="Submit", command=submit).grid(row=4, column=0, columnspan=2, pady=12)

    def form_add_attendance(self):
        w = tk.Toplevel(self); w.title("Add Attendance"); w.geometry("320x200")
        ttk.Label(w, text="Student ID").grid(row=0, column=0, padx=8, pady=8)
        sid = ttk.Entry(w); sid.grid(row=0, column=1)
        ttk.Label(w, text="Month (YYYY-MM)").grid(row=1, column=0, padx=8, pady=8)
        month = ttk.Entry(w); month.grid(row=1, column=1)
        ttk.Label(w, text="Attendance %").grid(row=2, column=0, padx=8, pady=8)
        perc = ttk.Entry(w); perc.grid(row=2, column=1)
        def submit():
            try:
                sidi = int(sid.get().strip()); p = float(perc.get().strip())
            except ValueError:
                messagebox.showerror("Error","Please enter valid numeric values")
                return
            conn = get_conn()
            conn.execute("INSERT INTO Attendance (student_id, month, attendance_percent) VALUES (?,?,?)",
                         (sidi, month.get().strip(), p))
            conn.commit(); conn.close()
            messagebox.showinfo("OK","Attendance added.")
            w.destroy()
        ttk.Button(w, text="Submit", command=submit).grid(row=3, column=0, columnspan=2, pady=12)

    def ask_and_show_student_details(self):
        sid = simpledialog.askinteger("Student ID", "Enter Student ID")
        if sid:
            self.show_student_details(sid)

    def show_student_details(self, student_id):
        conn = get_conn()
        s = conn.execute("SELECT * FROM Student WHERE student_id = ?", (student_id,)).fetchone()
        if not s:
            messagebox.showerror("Not found", "Student not found")
            conn.close()
            return
        rows_marks = conn.execute("SELECT semester, mid_sem, end_sem FROM Marks WHERE student_id = ? ORDER BY semester", (student_id,)).fetchall()
        rows_att = conn.execute("SELECT month, attendance_percent FROM Attendance WHERE student_id = ? ORDER BY month", (student_id,)).fetchall()
        ec = conn.execute("SELECT activity_name, level, achievement FROM ExtraCurricular WHERE student_id = ?", (student_id,)).fetchall()
        cc = conn.execute("SELECT activity_name, level, achievement FROM CoCurricular WHERE student_id = ?", (student_id,)).fetchall()
        conn.close()
        self.clear_tree(cols=('Field','Value'), headings=('Field','Value'))
        self.tree.insert('', 'end', values=('Name', s['name']))
        self.tree.insert('', 'end', values=('Roll No', s['roll_no'] or ''))
        self.tree.insert('', 'end', values=('Email', s['email']))
        self.tree.insert('', 'end', values=('Phone', s['phone'] or ''))
        self.tree.insert('', 'end', values=('Parent Phone', s['parent_phone'] or ''))
        self.tree.insert('', 'end', values=('Address', s['address'] or ''))
        avg = compute_avg_marks(student_id)
        self.tree.insert('', 'end', values=('Average Marks', f"{avg:.2f}" if avg is not None else 'No marks'))
        overall_att = get_overall_attendance(student_id)
        self.tree.insert('', 'end', values=('Overall Attendance', f"{overall_att:.2f}%" if overall_att is not None else 'No attendance'))
        if rows_marks:
            self.tree.insert('', 'end', values=('--- Marks ---',''))
            for m in rows_marks:
                self.tree.insert('', 'end', values=(f"Sem {m['semester']}", f"Mid:{m['mid_sem']}  End:{m['end_sem']}"))
        if rows_att:
            self.tree.insert('', 'end', values=('--- Attendance ---',''))
            for a in rows_att:
                self.tree.insert('', 'end', values=(a['month'], f"{a['attendance_percent']}%"))
        if ec:
            self.tree.insert('', 'end', values=('--- Extra Curricular ---',''))
            for e in ec:
                self.tree.insert('', 'end', values=(e['activity_name'], f"{e['level']} | {e['achievement'] or ''}"))
        if cc:
            self.tree.insert('', 'end', values=('--- Co Curricular ---',''))
            for e in cc:
                self.tree.insert('', 'end', values=(e['activity_name'], f"{e['level']} | {e['achievement'] or ''}"))

    def show_weak_strong(self):
        conn = get_conn()
        studs = conn.execute("SELECT student_id, name FROM Student").fetchall()
        conn.close()
        weak=[]; strong=[]
        for s in studs:
            avg = compute_avg_marks(s['student_id'])
            if avg is None or avg < MARK_THRESHOLD:
                weak.append((s['student_id'], s['name'], f"{avg:.2f}" if avg is not None else 'No marks'))
            else:
                strong.append((s['student_id'], s['name'], f"{avg:.2f}"))
        self.clear_tree(cols=('ID','Name','Avg'), headings=('ID','Name','Avg'))
        self.tree.insert('', 'end', values=('---Weak---','', ''))
        for w in weak:
            self.tree.insert('', 'end', values=w)
        self.tree.insert('', 'end', values=('---Strong---','', ''))
        for st in strong:
            self.tree.insert('', 'end', values=st)

    def show_attendance_defaulters(self):
        conn = get_conn()
        studs = conn.execute("SELECT student_id, name FROM Student").fetchall()
        conn.close()
        defaulters=[]
        for s in studs:
            att = get_overall_attendance(s['student_id'])
            if att is None or att < ATTENDANCE_THRESHOLD:
                defaulters.append((s['student_id'], s['name'], f"{att:.2f}%" if att is not None else 'No attendance'))
        self.clear_tree(cols=('ID','Name','Attendance'), headings=('ID','Name','Attendance'))
        for d in defaulters:
            self.tree.insert('', 'end', values=d)

if __name__ == '__main__':
    create_tables()
    # ensure DB file exists
    if not os.path.exists(DB_PATH):
        # create empty DB file
        open(DB_PATH, 'a').close()
    root = App()
    root.mainloop()
