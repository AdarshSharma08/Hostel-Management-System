import customtkinter as ctk
import sqlite3
import hashlib
from tkinter import messagebox
from datetime import datetime

# ================= CONFIGURATION =================

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

DB_NAME = "hostel.db"

# ================= DATABASE =================

def connect_db():
    return sqlite3.connect(DB_NAME)


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def initialize_database():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            room TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS complaints (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            category TEXT NOT NULL,
            description TEXT NOT NULL,
            status TEXT DEFAULT 'Pending',
            created_at TEXT NOT NULL,
            FOREIGN KEY(student_id) REFERENCES students(id)
        )
    """)

    cursor.execute(
        "SELECT id FROM students WHERE username = ?",
        ("student1",)
    )

    if cursor.fetchone() is None:
        cursor.execute("""
            INSERT INTO students (name, username, password, room)
            VALUES (?, ?, ?, ?)
        """, (
            "Student One",
            "student1",
            hash_password("student123"),
            "101"
        ))

    conn.commit()
    conn.close()


# ================= APPLICATION =================

class HostelManagementApp(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title("Hostel Management System")
        self.geometry("1000x650")
        self.minsize(850, 550)

        self.current_student = None

        initialize_database()
        self.show_home()

    def clear_screen(self):
        for widget in self.winfo_children():
            widget.destroy()

    def create_card(self, title, subtitle=""):
        self.clear_screen()

        self.configure(fg_color="#F1F5F9")

        card = ctk.CTkFrame(
            self,
            corner_radius=20,
            fg_color="white"
        )
        card.pack(
            fill="both",
            expand=True,
            padx=35,
            pady=35
        )

        ctk.CTkLabel(
            card,
            text=title,
            font=("Arial", 28, "bold"),
            text_color="#17365D"
        ).pack(pady=(35, 8))

        if subtitle:
            ctk.CTkLabel(
                card,
                text=subtitle,
                font=("Arial", 14),
                text_color="#64748B"
            ).pack(pady=(0, 20))

        return card

    def create_entry(self, parent, placeholder, show=None):
        entry = ctk.CTkEntry(
            parent,
            width=320,
            height=42,
            placeholder_text=placeholder,
            show=show
        )
        entry.pack(pady=8)
        return entry

    def create_button(
        self, parent, text, command,
        color="#2563EB", width=250
    ):
        button = ctk.CTkButton(
            parent,
            text=text,
            command=command,
            width=width,
            height=42,
            corner_radius=10,
            fg_color=color,
            hover_color="#1D4ED8",
            font=("Arial", 14, "bold")
        )
        button.pack(pady=8)
        return button

    # ================= HOME PAGE =================

    def show_home(self):
        card = self.create_card(
            "HOSTEL MANAGEMENT SYSTEM",
            "Smart Hostel Complaint & Maintenance Portal"
        )

        ctk.CTkLabel(
            card,
            text="Welcome!",
            font=("Arial", 23, "bold"),
            text_color="#334155"
        ).pack(pady=(30, 10))

        ctk.CTkLabel(
            card,
            text=(
                "Manage hostel complaints, track progress,\n"
                "and improve your hostel experience."
            ),
            font=("Arial", 15),
            text_color="#64748B",
            justify="center"
        ).pack(pady=10)

        self.create_button(
            card, "ADMIN LOGIN", self.show_admin_login
        )

        self.create_button(
            card, "STUDENT LOGIN", self.show_student_login,
            color="#0F766E"
        )

        self.create_button(
            card, "STUDENT REGISTRATION",
            self.show_registration,
            color="#475569"
        )

        ctk.CTkLabel(
            card,
            text="B.Tech Mini Project",
            font=("Arial", 12),
            text_color="#94A3B8"
        ).pack(side="bottom", pady=20)

    # ================= ADMIN LOGIN =================

    def show_admin_login(self):
        card = self.create_card(
            "ADMIN LOGIN",
            "Sign in to manage hostel complaints"
        )

        username = self.create_entry(card, "Admin username")
        password = self.create_entry(
            card, "Admin password", show="*"
        )

        def login():
            if (
                username.get().strip() == "admin"
                and password.get() == "admin123"
            ):
                self.show_admin_dashboard()
            else:
                messagebox.showerror(
                    "Login Failed",
                    "Invalid admin username or password."
                )

        self.create_button(card, "LOGIN", login)
        self.create_button(
            card, "BACK", self.show_home, color="#64748B"
        )

    # ================= STUDENT REGISTRATION =================

    def show_registration(self):
        card = self.create_card(
            "STUDENT REGISTRATION",
            "Create your student account"
        )

        name = self.create_entry(card, "Full name")
        username = self.create_entry(card, "Choose username")
        password = self.create_entry(
            card, "Choose password", show="*"
        )
        room = self.create_entry(card, "Room number")

        def register():
            student_name = name.get().strip()
            student_username = username.get().strip()
            student_password = password.get()
            student_room = room.get().strip()

            if not all([
                student_name,
                student_username,
                student_password,
                student_room
            ]):
                messagebox.showwarning(
                    "Missing Details",
                    "Please fill in all fields."
                )
                return

            if len(student_password) < 6:
                messagebox.showwarning(
                    "Weak Password",
                    "Password must contain at least 6 characters."
                )
                return

            conn = connect_db()
            cursor = conn.cursor()

            try:
                cursor.execute("""
                    INSERT INTO students
                    (name, username, password, room)
                    VALUES (?, ?, ?, ?)
                """, (
                    student_name,
                    student_username,
                    hash_password(student_password),
                    student_room
                ))

                conn.commit()

                messagebox.showinfo(
                    "Success",
                    "Registration successful! Please log in."
                )

                self.show_student_login()

            except sqlite3.IntegrityError:
                messagebox.showerror(
                    "Registration Failed",
                    "This username already exists."
                )

            finally:
                conn.close()

        self.create_button(card, "REGISTER", register)

        self.create_button(
            card, "BACK", self.show_home, color="#64748B"
        )

    # ================= STUDENT LOGIN =================

    def show_student_login(self):
        card = self.create_card(
            "STUDENT LOGIN",
            "Sign in to submit and track complaints"
        )

        username = self.create_entry(card, "Student username")
        password = self.create_entry(
            card, "Student password", show="*"
        )

        def login():
            conn = connect_db()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT id, name, username, room
                FROM students
                WHERE username = ? AND password = ?
            """, (
                username.get().strip(),
                hash_password(password.get())
            ))

            student = cursor.fetchone()
            conn.close()

            if student:
                self.current_student = student
                self.show_student_dashboard()
            else:
                messagebox.showerror(
                    "Login Failed",
                    "Invalid student username or password."
                )

        self.create_button(card, "LOGIN", login)

        self.create_button(
            card, "BACK", self.show_home, color="#64748B"
        )

    # ================= STUDENT DASHBOARD =================

    def show_student_dashboard(self):
        student = self.current_student

        card = self.create_card(
            f"Welcome, {student[1]}",
            f"Student Dashboard | Room: {student[3]}"
        )

        self.create_button(
            card, "SUBMIT COMPLAINT",
            self.show_submit_complaint,
            color="#0F766E"
        )

        self.create_button(
            card, "MY COMPLAINTS",
            self.show_my_complaints
        )

        self.create_button(
            card, "LOGOUT",
            self.logout,
            color="#64748B"
        )

    # ================= SUBMIT COMPLAINT =================

    def show_submit_complaint(self):
        card = self.create_card(
            "SUBMIT COMPLAINT",
            "Describe the hostel issue you are facing"
        )

        category = ctk.CTkOptionMenu(
            card,
            values=[
                "Electricity",
                "Water",
                "Cleaning",
                "Internet",
                "Maintenance",
                "Other"
            ],
            width=320,
            height=40
        )
        category.pack(pady=10)

        description = ctk.CTkTextbox(
            card,
            width=420,
            height=140
        )
        description.pack(pady=10)

        def submit():
            text = description.get("1.0", "end").strip()

            if not text:
                messagebox.showwarning(
                    "Missing Details",
                    "Please enter a complaint description."
                )
                return

            conn = connect_db()
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO complaints
                (student_id, category, description, status, created_at)
                VALUES (?, ?, ?, ?, ?)
            """, (
                self.current_student[0],
                category.get(),
                text,
                "Pending",
                datetime.now().strftime("%Y-%m-%d %H:%M")
            ))

            conn.commit()
            conn.close()

            messagebox.showinfo(
                "Success",
                "Your complaint has been submitted."
            )

            self.show_student_dashboard()

        self.create_button(card, "SUBMIT", submit)

        self.create_button(
            card, "BACK",
            self.show_student_dashboard,
            color="#64748B"
        )

    # ================= MY COMPLAINTS =================

    def show_my_complaints(self):
        card = self.create_card(
            "MY COMPLAINTS",
            "Track the status of your complaints"
        )

        container = ctk.CTkScrollableFrame(
            card,
            width=650,
            height=300
        )
        container.pack(padx=15, pady=10, fill="both", expand=True)

        conn = connect_db()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, category, description, status, created_at
            FROM complaints
            WHERE student_id = ?
            ORDER BY id DESC
        """, (self.current_student[0],))

        records = cursor.fetchall()
        conn.close()

        if not records:
            ctk.CTkLabel(
                container,
                text="You have not submitted any complaints."
            ).pack(pady=20)

        for record in records:
            text = (
                f"Complaint #{record[0]}\n"
                f"Category: {record[1]}\n"
                f"Description: {record[2]}\n"
                f"Status: {record[3]}\n"
                f"Date: {record[4]}"
            )

            ctk.CTkLabel(
                container,
                text=text,
                justify="left",
                anchor="w",
                fg_color="#E2E8F0",
                text_color="#0F172A",
                corner_radius=10,
                padx=15,
                pady=12,
                wraplength=600
            ).pack(fill="x", padx=5, pady=7)

        self.create_button(
            card, "BACK",
            self.show_student_dashboard,
            color="#64748B"
        )

    # ================= ADMIN DASHBOARD =================

    def show_admin_dashboard(self):
        card = self.create_card(
            "ADMIN DASHBOARD",
            "Manage all hostel complaints"
        )

        conn = connect_db()
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM complaints")
        total = cursor.fetchone()[0]

        cursor.execute("""
            SELECT COUNT(*) FROM complaints
            WHERE status = 'Pending'
        """)
        pending = cursor.fetchone()[0]

        cursor.execute("""
            SELECT COUNT(*) FROM complaints
            WHERE status = 'Resolved'
        """)
        resolved = cursor.fetchone()[0]

        conn.close()

        ctk.CTkLabel(
            card,
            text=(
                f"Total Complaints: {total}\n"
                f"Pending Complaints: {pending}\n"
                f"Resolved Complaints: {resolved}"
            ),
            font=("Arial", 18),
            text_color="#334155",
            justify="left"
        ).pack(pady=25)

        self.create_button(
            card, "VIEW ALL COMPLAINTS",
            self.show_all_complaints
        )

        self.create_button(
            card, "LOGOUT",
            self.logout,
            color="#64748B"
        )

    # ================= VIEW ALL COMPLAINTS =================

    def show_all_complaints(self):
        card = self.create_card(
            "COMPLAINT MANAGEMENT",
            "Review complaints and update their status"
        )

        container = ctk.CTkScrollableFrame(
            card,
            width=700,
            height=330
        )
        container.pack(padx=10, pady=10, fill="both", expand=True)

        conn = connect_db()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT c.id, s.name, s.room, c.category,
                   c.description, c.status, c.created_at
            FROM complaints c
            JOIN students s ON c.student_id = s.id
            ORDER BY c.id DESC
        """)

        records = cursor.fetchall()
        conn.close()

        if not records:
            ctk.CTkLabel(
                container,
                text="No complaints have been submitted."
            ).pack(pady=20)

        for record in records:
            complaint_id = record[0]

            text = (
                f"Complaint #{complaint_id} | {record[1]}\n"
                f"Room: {record[2]} | Category: {record[3]}\n"
                f"Description: {record[4]}\n"
                f"Status: {record[5]} | Date: {record[6]}"
            )

            frame = ctk.CTkFrame(
                container,
                corner_radius=10
            )
            frame.pack(fill="x", padx=5, pady=7)

            ctk.CTkLabel(
                frame,
                text=text,
                justify="left",
                anchor="w",
                wraplength=620
            ).pack(fill="x", padx=12, pady=8)

            status_menu = ctk.CTkOptionMenu(
                frame,
                values=["Pending", "In Progress", "Resolved"],
                width=150
            )
            status_menu.set(record[5])
            status_menu.pack(side="left", padx=10, pady=8)

            def update_status(cid=complaint_id, menu=status_menu):
                conn2 = connect_db()
                cursor2 = conn2.cursor()

                cursor2.execute("""
                    UPDATE complaints
                    SET status = ?
                    WHERE id = ?
                """, (menu.get(), cid))

                conn2.commit()
                conn2.close()

                messagebox.showinfo(
                    "Updated",
                    f"Complaint #{cid} status updated."
                )

            ctk.CTkButton(
                frame,
                text="Update Status",
                command=update_status,
                width=140
            ).pack(side="left", padx=10, pady=8)

        self.create_button(
            card, "BACK TO DASHBOARD",
            self.show_admin_dashboard,
            color="#64748B"
        )

    # ================= LOGOUT =================

    def logout(self):
        self.current_student = None
        self.show_home()


# ================= START APPLICATION =================

if __name__ == "__main__":
    app = HostelManagementApp()
    app.mainloop()