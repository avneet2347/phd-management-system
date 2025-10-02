import sqlite3
import os
from tkinter import messagebox

class DatabaseManager:
    def __init__(self):
        self.db_file = "phd_management.db"
        self.upload_dir = "Uploads"
        self.cert_dir = os.path.join(self.upload_dir, "certificates")
        self.pic_dir = os.path.join(self.upload_dir, "pictures")
        self.present_dir = os.path.join(self.upload_dir, "presentations")
        self.synopsis_dir = os.path.join(self.upload_dir, "synopsis")
        os.makedirs(self.cert_dir, exist_ok=True)
        os.makedirs(self.pic_dir, exist_ok=True)
        os.makedirs(self.present_dir, exist_ok=True)
        os.makedirs(self.synopsis_dir, exist_ok=True)
        self.create_or_migrate_table()

    def create_or_migrate_table(self):
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS students (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    roll_number TEXT NOT NULL,
                    batch_from TEXT,
                    batch_to TEXT,
                    original_batch_to TEXT,
                    name TEXT NOT NULL,
                    email TEXT NOT NULL,
                    department TEXT NOT NULL,
                    supervisor TEXT NOT NULL,
                    registration_date TEXT NOT NULL,
                    dob TEXT,
                    picture_path TEXT,
                    title TEXT NOT NULL,
                    publications TEXT NOT NULL
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS presentations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    student_id INTEGER NOT NULL,
                    presentation_date TEXT NOT NULL,
                    progress_notes TEXT NOT NULL,
                    presentation_file TEXT,
                    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS synopsis (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    student_id INTEGER NOT NULL,
                    synopsis_title TEXT NOT NULL,
                    submission_date TEXT NOT NULL,
                    abstract TEXT NOT NULL,
                    synopsis_file TEXT,
                    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS certificates (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    student_id INTEGER NOT NULL,
                    certificate_title TEXT NOT NULL,
                    certificate_path TEXT NOT NULL,
                    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
                )
            ''')
            cursor.execute("PRAGMA table_info(students)")
            columns = [col[1] for col in cursor.fetchall()]
            if 'title' not in columns:
                cursor.execute("ALTER TABLE students ADD COLUMN title TEXT NOT NULL DEFAULT ''")
            if 'publications' not in columns:
                cursor.execute("ALTER TABLE students ADD COLUMN publications TEXT NOT NULL DEFAULT ''")
            if 'registration_date' not in columns and 'enrollment_date' in columns:
                cursor.execute("ALTER TABLE students RENAME COLUMN enrollment_date TO registration_date")
            if 'batch_from' not in columns:
                cursor.execute("ALTER TABLE students ADD COLUMN batch_from TEXT")
            if 'batch_to' not in columns:
                cursor.execute("ALTER TABLE students ADD COLUMN batch_to TEXT")
            if 'original_batch_to' not in columns:
                cursor.execute("ALTER TABLE students ADD COLUMN original_batch_to TEXT")
                cursor.execute("UPDATE students SET original_batch_to = batch_to WHERE original_batch_to IS NULL")
            if 'certificate_path' in columns:
                cursor.execute("SELECT id, certificate_path FROM students WHERE certificate_path IS NOT NULL")
                existing_certs = cursor.fetchall()
                for student_id, cert_path in existing_certs:
                    cursor.execute('''
                        INSERT INTO certificates (student_id, certificate_title, certificate_path)
                        VALUES (?, ?, ?)
                    ''', (student_id, "Default Certificate", cert_path))
                cursor.execute("ALTER TABLE students DROP COLUMN certificate_path")
            conn.commit()

    def login(self, username, password):
        from datetime import datetime
        if username == "admin" and password == "admin":
            self.is_admin = True
            self.current_user = "admin"
            return True
        try:
            try:
                dob = datetime.strptime(password, "%d-%m-%Y").strftime("%Y-%m-%d")
            except ValueError:
                return False
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM students WHERE email = ? AND (dob = ? OR dob IS NULL)", (username, dob))
                student = cursor.fetchone()
                if student:
                    self.is_admin = False
                    self.current_user = student[0]
                    return True
                return False
        except sqlite3.Error:
            return False

    def view_own_details(self):
        try:
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM students WHERE id = ?", (self.current_user,))
                student = cursor.fetchone()
                return student
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Error fetching student details: {e}", parent=self.root)
            return None

    def get_student_synopsis(self, student_id):
        try:
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM synopsis WHERE student_id = ?", (student_id,))
                return cursor.fetchone()
        except sqlite3.Error as e:
            print(f"Error fetching synopsis: {e}")
            return None

    def get_student_presentations(self, student_id):
        try:
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM presentations WHERE student_id = ?", (student_id,))
                return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Error fetching presentations: {e}")
            return []

    def get_student_certificates(self, student_id):
        try:
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id, certificate_title, certificate_path FROM certificates WHERE student_id = ?", (student_id,))
                return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Error fetching certificates: {e}")
            return []