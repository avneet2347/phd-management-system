import tkinter as tk
from tkinter import ttk
from tkinter import messagebox, filedialog
from PIL import Image, ImageTk
from datetime import datetime
import webbrowser
import sqlite3
import csv
import os
import shutil

class AdminUI:
    def __init__(self, root, db_file, file_manager, show_login_callback):
        self.root = root
        self.db_file = db_file
        self.file_manager = file_manager
        self.show_login = show_login_callback
        self.is_admin = True
        self.cert_dir = file_manager.cert_dir
        self.pic_dir = file_manager.pic_dir
        self.present_dir = file_manager.present_dir
        self.synopsis_dir = file_manager.synopsis_dir
        self.setup_styles()

    def setup_styles(self):
        style = ttk.Style()
        style.configure("TFrame", background="#F5F7FA")
        style.configure("Card.TFrame", background="#FFFFFF", relief="flat")
        style.configure("Shadow.TFrame", background="#FFFFFF", relief="flat")
        style.configure("TButton", font=("Inter", 11), padding=10, background="#EDEFF2", foreground="#000000")
        style.configure("Danger.TButton", font=("Inter", 11), padding=10, background="#FF3B30", foreground="#FFFFFF")
        style.configure("TextButton.TButton", font=("Inter", 10), padding=5, background="#F5F7FA", foreground="#000000")
        style.configure("Heading.TLabel", font=("Inter", 20, "bold"), background="#F5F7FA", foreground="#000000")
        style.configure("TLabel", font=("Inter", 11), background="#F5F7FA", foreground="#000000")
        style.configure("Project.TLabel", font=("Inter", 12, "bold"), background="#FFFFFF", foreground="#000000")
        style.configure("Author.TLabel", font=("Inter", 10), background="#FFFFFF", foreground="#000000")
        style.map("TButton", background=[("active", "#D1D5DB")])
        style.map("Danger.TButton", background=[("active", "#FF1A0F")])
        style.map("TextButton.TButton", background=[("active", "#EDEFF2")])

    def button_bind(self, button):
        button.bind("<Enter>", lambda e: button.configure(cursor="hand2"))
        button.bind("<Leave>", lambda e: button.configure(cursor=""))

    def create_scrollable_frame(self, parent):
        canvas = tk.Canvas(parent, bg="#F5F7FA", highlightthickness=0)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        card_frame = ttk.Frame(canvas, style="Card.TFrame")
        card_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=card_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        return card_frame, canvas

    def get_student_presentations(self, student_id):
        try:
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM presentations WHERE student_id = ?", (student_id,))
                return cursor.fetchall()
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Error fetching presentations: {e}", parent=self.root)
            return []

    def get_student_synopsis(self, student_id):
        try:
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM synopsis WHERE student_id = ?", (student_id,))
                return cursor.fetchone()
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Error fetching synopsis: {e}", parent=self.root)
            return None

    def get_student_certificates(self, student_id):
        try:
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id, certificate_title, certificate_path FROM certificates WHERE student_id = ?", (student_id,))
                return cursor.fetchall()
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Error fetching certificates: {e}", parent=self.root)
            return []

    def show_admin_dashboard(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        card_frame, canvas = self.create_scrollable_frame(self.root)
        card_frame.configure(padding=30)

        ttk.Label(
            card_frame,
            text="Admin Dashboard",
            style="Heading.TLabel"
        ).pack(pady=20)

        buttons = [
            ("Add Student", self.show_add_student),
            ("View All Students", self.show_view_students),
            ("Update Student", self.show_update_student),
            ("Delete Student", self.show_delete_student),
            ("Search Student", self.show_search_student),
            ("Manage Presentations", self.show_manage_presentations),
            ("Export to CSV", self.export_to_csv)
        ]

        for text, command in buttons:
            btn = ttk.Button(
                card_frame,
                text=text,
                style="TButton",
                command=command
            )
            btn.pack(pady=10, padx=20, fill="x", ipady=5)
            self.button_bind(btn)

        back_btn = ttk.Button(
            card_frame,
            text="Back to Login",
            style="TButton",
            command=self.show_login
        )
        back_btn.pack(pady=10, padx=20, fill="x", ipady=5)
        self.button_bind(back_btn)

        canvas.bind_all("<MouseWheel>", lambda event: canvas.yview_scroll(int(-1 * (event.delta / 120)), "units"))
        canvas.bind_all("<Button-4>", lambda event: canvas.yview_scroll(-1, "units"))
        canvas.bind_all("<Button-5>", lambda event: canvas.yview_scroll(1, "units"))

        card_frame.update_idletasks()
        canvas.configure(scrollregion=canvas.bbox("all"))

        self.root.update()

    def export_to_csv(self):
        try:
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM students")
                students = cursor.fetchall()

                if not students:
                    messagebox.showinfo("Info", "No students to export.", parent=self.root)
                    return

                file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
                if not file_path:
                    return

                with open(file_path, 'w', newline='') as csvfile:
                    writer = csv.writer(csvfile)
                    headers = ["ID", "Roll Number", "Batch From", "Batch To", "Original Batch To", "Name", "Email", "Department", "Supervisor",
                               "Registration Date", "DOB", "Picture Path", "Title", "Publications"]
                    writer.writerow(headers)
                    for student in students:
                        writer.writerow(student)

                messagebox.showinfo("Success", f"Student data exported to {file_path}!", parent=self.root)
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Error exporting to CSV: {e}", parent=self.root)
        except Exception as e:
            messagebox.showerror("Error", f"Error writing CSV: {e}", parent=self.root)

    def show_add_student(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        card_frame, canvas = self.create_scrollable_frame(self.root)
        card_frame.configure(padding=30)

        ttk.Label(card_frame, text="Add New Student", style="Heading.TLabel").pack(pady=20)

        fields = ["Name", "Roll Number", "Email", "Date of Birth (DD-MM-YYYY)", "Department", "Supervisor", 
                  "Registration Date (DD-MM-YYYY)", "Title", "Publications"]
        entries = {}
        for field in fields:
            if field == "Roll Number":
                ttk.Label(card_frame, text=field).pack(anchor="w", padx=20, pady=(10, 0))
                entry = ttk.Entry(card_frame)
                entry.pack(pady=10, padx=20, fill="x", ipady=5)
                entries[field] = entry

                batch_frame = ttk.Frame(card_frame, style="Card.TFrame")
                batch_frame.pack(pady=10, padx=20, fill="x")
                
                ttk.Label(batch_frame, text="Batch From").pack(side="left", padx=(0, 10))
                batch_from_entry = ttk.Entry(batch_frame, width=10)
                batch_from_entry.pack(side="left", padx=(0, 20))
                entries["Batch From"] = batch_from_entry
                
                ttk.Label(batch_frame, text="Batch To").pack(side="left", padx=(0, 10))
                batch_to_entry = ttk.Entry(batch_frame, width=10)
                batch_to_entry.pack(side="left")
                entries["Batch To"] = batch_to_entry

            else:
                ttk.Label(card_frame, text=field).pack(anchor="w", padx=20, pady=(10, 0))
                entry = ttk.Entry(card_frame)
                entry.pack(pady=10, padx=20, fill="x", ipady=5)
                entries[field] = entry

        picture_path = tk.StringVar()
        presentation_path = tk.StringVar()
        presentation_date = tk.StringVar()
        progress_notes = tk.StringVar()
        synopsis_data = {}
        certificates_data = []

        def select_picture():
            path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.png")])
            if path:
                picture_path.set(path)
            self.root.lift()  # Ensure main window stays accessible
            card_frame.winfo_toplevel().lift()  # Bring add student window back to front

        def select_presentation():
            path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf"), ("PPT files", "*.ppt *.pptx")])
            if path:
                presentation_path.set(path)
            self.root.lift()  # Ensure main window stays accessible
            card_frame.winfo_toplevel().lift()  # Bring add student window back to front

        def add_synopsis():
            synopsis_window = tk.Toplevel(self.root)
            synopsis_window.title("Add Synopsis")
            synopsis_window.geometry("600x500")
            synopsis_window.configure(bg="#F5F7FA")
            synopsis_window.transient(self.root)  # Set as transient to the main window
            synopsis_window.grab_set()  # Ensure it stays in focus

            top_bar = ttk.Frame(synopsis_window, style="Shadow.TFrame")
            top_bar.pack(fill="x", padx=20, pady=(10, 0))
            left_frame = ttk.Frame(top_bar, style="Shadow.TFrame")
            left_frame.pack(side="left", padx=10)
            project_label = ttk.Label(left_frame, text="PhD Management System", style="Project.TLabel")
            project_label.pack(anchor="w", pady=2)
            author_label = ttk.Label(left_frame, text="Project by: Avneet Kaur, B.Tech (CSE), 6th Sem", style="Author.TLabel")
            author_label.pack(anchor="w", pady=2)
            home_btn = ttk.Button(top_bar, text="Home", style="TextButton.TButton", 
                                 command=self.show_admin_dashboard)
            home_btn.pack(side="right", pady=2, padx=10)
            self.button_bind(home_btn)
            logout_btn = ttk.Button(top_bar, text="Log Out", style="TextButton.TButton", 
                                   command=self.show_login)
            logout_btn.pack(side="right", pady=2, padx=10)
            self.button_bind(logout_btn)

            card_frame_synopsis = ttk.Frame(synopsis_window, style="Card.TFrame")
            card_frame_synopsis.pack(expand=True, fill="both", padx=20, pady=20)

            ttk.Label(card_frame_synopsis, text="Synopsis Details", style="Heading.TLabel").pack(pady=20)

            ttk.Label(card_frame_synopsis, text="Synopsis Title").pack(anchor="w", padx=20, pady=(10, 0))
            synopsis_title_entry = ttk.Entry(card_frame_synopsis)
            synopsis_title_entry.pack(pady=10, padx=20, fill="x", ipady=5)

            ttk.Label(card_frame_synopsis, text="Submission Date (DD-MM-YYYY)").pack(anchor="w", padx=20, pady=(10, 0))
            submission_date_entry = ttk.Entry(card_frame_synopsis)
            submission_date_entry.pack(pady=10, padx=20, fill="x", ipady=5)

            ttk.Label(card_frame_synopsis, text="Abstract (4–5 lines)").pack(anchor="w", padx=20, pady=(10, 0))
            abstract_text = tk.Text(card_frame_synopsis, height=5, font=("Inter", 11))
            abstract_text.pack(pady=10, padx=20, fill="x")

            synopsis_file_path = tk.StringVar()
            def select_synopsis_file():
                path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
                if path:
                    synopsis_file_path.set(path)
                synopsis_window.lift()  # Bring synopsis window back to front
                synopsis_window.grab_set()  # Restore focus to synopsis window

            synopsis_file_btn = ttk.Button(card_frame_synopsis, text="Select Synopsis PDF (Optional)", style="TButton", command=select_synopsis_file)
            synopsis_file_btn.pack(pady=10, padx=20, fill="x", ipady=5)
            self.button_bind(synopsis_file_btn)

            def save_synopsis():
                synopsis_data['title'] = synopsis_title_entry.get().strip()
                synopsis_data['submission_date'] = submission_date_entry.get().strip()
                synopsis_data['abstract'] = abstract_text.get("1.0", tk.END).strip()
                synopsis_data['file_path'] = synopsis_file_path.get()
                
                if not all([synopsis_data['title'], synopsis_data['submission_date'], synopsis_data['abstract']]):
                    messagebox.showerror("Error", "Synopsis Title, Submission Date, and Abstract are required.", parent=synopsis_window)
                    return
                try:
                    datetime.strptime(synopsis_data['submission_date'], "%d-%m-%Y")
                except ValueError:
                    messagebox.showerror("Error", "Invalid date format. Use DD-MM-YYYY.", parent=synopsis_window)
                    return

                messagebox.showinfo("Success", "Synopsis details saved. Submit student to finalize.", parent=synopsis_window)
                synopsis_window.destroy()

            save_btn = ttk.Button(card_frame_synopsis, text="Save Synopsis", style="Danger.TButton", command=save_synopsis)
            save_btn.pack(pady=20, padx=20, fill="x", ipady=5)
            self.button_bind(save_btn)

            cancel_btn = ttk.Button(card_frame_synopsis, text="Cancel", style="TButton", command=synopsis_window.destroy)
            cancel_btn.pack(pady=10, padx=20, fill="x", ipady=5)
            self.button_bind(cancel_btn)

        def add_certificates():
            certificates_window = tk.Toplevel(self.root)
            certificates_window.title("Add Certificates")
            certificates_window.geometry("600x600")
            certificates_window.configure(bg="#F5F7FA")
            certificates_window.transient(self.root)  # Set as transient to the main window
            certificates_window.grab_set()  # Ensure it stays in focus

            top_bar = ttk.Frame(certificates_window, style="Shadow.TFrame")
            top_bar.pack(fill="x", padx=20, pady=(10, 0))
            left_frame = ttk.Frame(top_bar, style="Shadow.TFrame")
            left_frame.pack(side="left", padx=10)
            project_label = ttk.Label(left_frame, text="PhD Management System", style="Project.TLabel")
            project_label.pack(anchor="w", pady=2)
            author_label = ttk.Label(left_frame, text="Project by: Avneet Kaur, B.Tech (CSE), 6th Sem", style="Author.TLabel")
            author_label.pack(anchor="w", pady=2)
            home_btn = ttk.Button(top_bar, text="Home", style="TextButton.TButton", 
                                 command=self.show_admin_dashboard)
            home_btn.pack(side="right", pady=2, padx=10)
            self.button_bind(home_btn)
            logout_btn = ttk.Button(top_bar, text="Log Out", style="TextButton.TButton", 
                                   command=self.show_login)
            logout_btn.pack(side="right", pady=2, padx=10)
            self.button_bind(logout_btn)

            card_frame_certs = ttk.Frame(certificates_window, style="Card.TFrame")
            card_frame_certs.pack(expand=True, fill="both", padx=20, pady=20)

            ttk.Label(card_frame_certs, text="Add Certificates", style="Heading.TLabel").pack(pady=20)

            certs_listbox = tk.Listbox(card_frame_certs, height=10, font=("Inter", 11))
            certs_listbox.pack(pady=10, padx=20, fill="both")

            ttk.Label(card_frame_certs, text="Certificate Title").pack(anchor="w", padx=20, pady=(10, 0))
            cert_title_entry = ttk.Entry(card_frame_certs)
            cert_title_entry.pack(pady=10, padx=20, fill="x", ipady=5)

            cert_file_path = tk.StringVar()
            def select_certificate_file():
                path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
                if path:
                    cert_file_path.set(path)
                certificates_window.lift()  # Bring certificates window back to front
                certificates_window.grab_set()  # Restore focus to certificates window

            cert_file_btn = ttk.Button(card_frame_certs, text="Select Certificate PDF", style="TButton", command=select_certificate_file)
            cert_file_btn.pack(pady=10, padx=20, fill="x", ipady=5)
            self.button_bind(cert_file_btn)

            def add_certificate():
                title = cert_title_entry.get().strip()
                path = cert_file_path.get()
                if not title or not path:
                    messagebox.showerror("Error", "Certificate title and file are required.", parent=certificates_window)
                    return
                certificates_data.append({"title": title, "path": path})
                certs_listbox.insert(tk.END, f"{title}: {os.path.basename(path)}")
                cert_title_entry.delete(0, tk.END)
                cert_file_path.set("")
                messagebox.showinfo("Success", "Certificate added to list.", parent=certificates_window)

            add_cert_btn = ttk.Button(card_frame_certs, text="Add Certificate", style="TButton", command=add_certificate)
            add_cert_btn.pack(pady=10, padx=20, fill="x", ipady=5)
            self.button_bind(add_cert_btn)

            def save_certificates():
                messagebox.showinfo("Success", "Certificates saved. Submit student to finalize.", parent=certificates_window)
                certificates_window.destroy()

            save_btn = ttk.Button(card_frame_certs, text="Save Certificates", style="Danger.TButton", command=save_certificates)
            save_btn.pack(pady=20, padx=20, fill="x", ipady=5)
            self.button_bind(save_btn)

            cancel_btn = ttk.Button(card_frame_certs, text="Cancel", style="TButton", command=certificates_window.destroy)
            cancel_btn.pack(pady=10, padx=20, fill="x", ipady=5)
            self.button_bind(cancel_btn)

        pic_btn = ttk.Button(card_frame, text="Select Picture (JPG/PNG)", style="TButton", command=select_picture)
        pic_btn.pack(pady=10, padx=20, fill="x", ipady=5)
        self.button_bind(pic_btn)

        cert_btn = ttk.Button(card_frame, text="Add Certificates", style="TButton", command=add_certificates)
        cert_btn.pack(pady=10, padx=20, fill="x", ipady=5)
        self.button_bind(cert_btn)

        ttk.Label(card_frame, text="6-Month Presentation Date (DD-MM-YYYY)").pack(anchor="w", padx=20, pady=(10, 0))
        pres_date_entry = ttk.Entry(card_frame, textvariable=presentation_date)
        pres_date_entry.pack(pady=10, padx=20, fill="x", ipady=5)
        ttk.Label(card_frame, text="Progress Notes").pack(anchor="w", padx=20, pady=(10, 0))
        progress_entry = ttk.Entry(card_frame, textvariable=progress_notes)
        progress_entry.pack(pady=10, padx=20, fill="x", ipady=5)
        pres_btn = ttk.Button(card_frame, text="Select Presentation File (PDF/PPT)", style="TButton", command=select_presentation)
        pres_btn.pack(pady=10, padx=20, fill="x", ipady=5)
        self.button_bind(pres_btn)

        synopsis_btn = ttk.Button(card_frame, text="Add Synopsis", style="TButton", command=add_synopsis)
        synopsis_btn.pack(pady=10, padx=20, fill="x", ipady=5)
        self.button_bind(synopsis_btn)

        def submit():
            name = entries["Name"].get().strip()
            roll_number = entries["Roll Number"].get().strip()
            batch_from = entries["Batch From"].get().strip()
            batch_to = entries["Batch To"].get().strip()
            email = entries["Email"].get().strip()
            dob_str = entries["Date of Birth (DD-MM-YYYY)"].get().strip()
            department = entries["Department"].get().strip()
            supervisor = entries["Supervisor"].get().strip()
            registration_date_str = entries["Registration Date (DD-MM-YYYY)"].get().strip()
            title = entries["Title"].get().strip()
            publications = entries["Publications"].get().strip()
            pres_date_str = presentation_date.get().strip()
            progress = progress_notes.get().strip()
            pres_file = presentation_path.get()

            try:
                dob = datetime.strptime(dob_str, "%d-%m-%Y").strftime("%Y-%m-%d") if dob_str else None
                registration_date = datetime.strptime(registration_date_str, "%d-%m-%Y").strftime("%Y-%m-%d") if registration_date_str else None
                pres_date = datetime.strptime(pres_date_str, "%d-%m-%Y").strftime("%Y-%m-%d") if pres_date_str else None
            except ValueError:
                messagebox.showerror("Error", "Invalid date format. Use DD-MM-YYYY.", parent=self.root)
                return

            try:
                if batch_from:
                    int(batch_from)
                if batch_to:
                    int(batch_to)
            except ValueError:
                messagebox.showerror("Error", "Batch From and To must be valid years.", parent=self.root)
                return

            if not all([name, roll_number, email, department, supervisor, registration_date, title, publications]):
                messagebox.showerror("Error", "All fields except DOB, Batch, and presentation fields are required.", parent=self.root)
                return

            if (pres_date_str or progress or pres_file) and not all([pres_date_str, progress]):
                messagebox.showerror("Error", "Presentation date and progress notes are required if adding a presentation.", parent=self.root)
                return

            pic_path = picture_path.get()
            final_pic_path = None
            final_pres_path = None
            final_synopsis_path = None

            try:
                with sqlite3.connect(self.db_file) as conn:
                    cursor = conn.cursor()
                    cursor.execute('''
                        INSERT INTO students (roll_number, batch_from, batch_to, original_batch_to, name, email, department, supervisor, registration_date, 
                                            dob, picture_path, title, publications)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (roll_number, batch_from or None, batch_to or None, batch_to or None, name, email, department, supervisor, registration_date, 
                          dob, None, title, publications))
                    student_id = cursor.lastrowid

                    if pic_path:
                        final_pic_path = os.path.join(self.pic_dir, f"{student_id}_{roll_number}{os.path.splitext(pic_path)[1]}")
                        shutil.copy(pic_path, final_pic_path)
                    if pres_file and pres_date and progress:
                        final_pres_path = os.path.join(self.present_dir, f"{student_id}_{pres_date.replace('-', '')}{os.path.splitext(pres_file)[1]}")
                        shutil.copy(pres_file, final_pres_path)
                        cursor.execute('''
                            INSERT INTO presentations (student_id, presentation_date, progress_notes, presentation_file)
                            VALUES (?, ?, ?, ?)
                        ''', (student_id, pres_date, progress, final_pres_path))
                    if synopsis_data.get('title') and synopsis_data.get('submission_date') and synopsis_data.get('abstract'):
                        submission_date = datetime.strptime(synopsis_data['submission_date'], "%d-%m-%Y").strftime("%Y-%m-%d")
                        if synopsis_data.get('file_path'):
                            final_synopsis_path = os.path.join(self.synopsis_dir, f"{student_id}_{submission_date.replace('-', '')}.pdf")
                            shutil.copy(synopsis_data['file_path'], final_synopsis_path)
                        cursor.execute('''
                            INSERT INTO synopsis (student_id, synopsis_title, submission_date, abstract, synopsis_file)
                            VALUES (?, ?, ?, ?, ?)
                        ''', (student_id, synopsis_data['title'], submission_date, synopsis_data['abstract'], final_synopsis_path))
                    for cert in certificates_data:
                        final_cert_path = os.path.join(self.cert_dir, f"{student_id}_{cert['title'].replace(' ', '_')}.pdf")
                        shutil.copy(cert['path'], final_cert_path)
                        cursor.execute('''
                            INSERT INTO certificates (student_id, certificate_title, certificate_path)
                            VALUES (?, ?, ?)
                        ''', (student_id, cert['title'], final_cert_path))
                    conn.commit()

                    if final_pic_path:
                        cursor.execute('''
                            UPDATE students 
                            SET picture_path = ?
                            WHERE id = ?
                        ''', (final_pic_path, student_id))
                        conn.commit()

                    messagebox.showinfo("Success", f"Student {name} added successfully with ID {student_id}!", parent=self.root)
                    self.show_admin_dashboard()
            except sqlite3.Error as e:
                messagebox.showerror("Error", f"Error adding student: {e}", parent=self.root)

        submit_btn = ttk.Button(card_frame, text="Submit", style="Danger.TButton", command=submit)
        submit_btn.pack(pady=20, padx=20, fill="x", ipady=5)
        self.button_bind(submit_btn)
        cancel_btn = ttk.Button(card_frame, text="Cancel", style="TButton", command=self.show_admin_dashboard)
        cancel_btn.pack(pady=10, padx=20, fill="x", ipady=5)
        self.button_bind(cancel_btn)

        canvas.bind_all("<MouseWheel>", lambda event: canvas.yview_scroll(int(-1 * (event.delta / 120)), "units"))
        canvas.bind_all("<Button-4>", lambda event: canvas.yview_scroll(-1, "units"))
        canvas.bind_all("<Button-5>", lambda event: canvas.yview_scroll(1, "units"))
        
        card_frame.update_idletasks()
        canvas.configure(scrollregion=canvas.bbox("all"))

    def show_manage_presentations(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        card_frame, canvas = self.create_scrollable_frame(self.root)
        card_frame.configure(padding=30)

        ttk.Label(card_frame, text="Manage Presentations", style="Heading.TLabel").pack(pady=20)
        ttk.Label(card_frame, text="Student ID").pack(anchor="w", padx=20, pady=(10, 0))
        id_entry = ttk.Entry(card_frame)
        id_entry.pack(pady=10, padx=20, fill="x", ipady=5)

        def load_presentations():
            try:
                student_id = int(id_entry.get())
                with sqlite3.connect(self.db_file) as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT name FROM students WHERE id = ?", (student_id,))
                    student = cursor.fetchone()
                    if not student:
                        messagebox.showerror("Error", "Student not found.", parent=self.root)
                        return

                    for widget in card_frame.winfo_children():
                        widget.destroy()

                    card_frame.configure(padding=30)
                    ttk.Label(card_frame, text=f"Presentations for {student[0]}", style="Heading.TLabel").pack(pady=20)

                    tree = ttk.Treeview(card_frame, columns=("ID", "Date", "Progress", "File"), show="headings")
                    tree.heading("ID", text="ID")
                    tree.heading("Date", text="Date")
                    tree.heading("Progress", text="Progress Notes")
                    tree.heading("File", text="File")
                    tree.column("ID", width=50)
                    tree.column("Date", width=100)
                    tree.column("Progress", width=300)
                    tree.column("File", width=200)
                    tree.pack(fill="both", expand=True, padx=20, pady=10)

                    presentations = self.get_student_presentations(student_id)
                    for pres in presentations:
                        file_status = os.path.basename(pres[4]) if pres[4] and os.path.exists(pres[4]) else "N/A"
                        tree.insert("", "end", values=(pres[0], pres[2], pres[3], file_status))

                    def view_file(event):
                        selected = tree.selection()
                        if not selected:
                            return
                        item = tree.item(selected[0])
                        pres_id = item["values"][0]
                        with sqlite3.connect(self.db_file) as conn:
                            cursor = conn.cursor()
                            cursor.execute("SELECT presentation_file FROM presentations WHERE id = ?", (pres_id,))
                            file_path = cursor.fetchone()[0]
                            if file_path and os.path.exists(file_path):
                                webbrowser.open(f"file://{os.path.abspath(file_path)}")
                            else:
                                messagebox.showinfo("Info", "Presentation file not available.", parent=self.root)

                    tree.bind("<<TreeviewSelect>>", view_file)

                    ttk.Label(card_frame, text="Add New Presentation").pack(anchor="w", padx=20, pady=(20, 0))
                    ttk.Label(card_frame, text="Presentation Date (DD-MM-YYYY)").pack(anchor="w", padx=20, pady=(10, 0))
                    pres_date_entry = ttk.Entry(card_frame)
                    pres_date_entry.pack(pady=10, padx=20, fill="x", ipady=5)
                    ttk.Label(card_frame, text="Progress Notes").pack(anchor="w", padx=20, pady=(10, 0))
                    progress_entry = ttk.Entry(card_frame)
                    progress_entry.pack(pady=10, padx=20, fill="x", ipady=5)
                    presentation_path = tk.StringVar()
                    def select_presentation():
                        path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf"), ("PPT files", "*.ppt *.pptx")])
                        if path:
                            presentation_path.set(path)
                        card_frame.winfo_toplevel().lift()  # Bring manage presentations window back to front
                        card_frame.winfo_toplevel().grab_set()  # Restore focus

                    pres_btn = ttk.Button(card_frame, text="Select Presentation File (PDF/PPT)", style="TButton", command=select_presentation)
                    pres_btn.pack(pady=10, padx=20, fill="x", ipady=5)
                    self.button_bind(pres_btn)

                    def add_presentation():
                        pres_date_str = pres_date_entry.get().strip()
                        progress = progress_entry.get().strip()
                        pres_file = presentation_path.get()
                        try:
                            pres_date = datetime.strptime(pres_date_str, "%d-%m-%Y").strftime("%Y-%m-%d") if pres_date_str else None
                        except ValueError:
                            messagebox.showerror("Error", "Invalid date format. Use DD-MM-YYYY.", parent=self.root)
                            return
                        if not all([pres_date, progress]):
                            messagebox.showerror("Error", "Presentation date and progress notes are required.", parent=self.root)
                            return
                        final_pres_path = None
                        if pres_file:
                            final_pres_path = os.path.join(self.present_dir, f"{student_id}_{pres_date.replace('-', '')}{os.path.splitext(pres_file)[1]}")
                            shutil.copy(pres_file, final_pres_path)
                        try:
                            with sqlite3.connect(self.db_file) as conn:
                                cursor = conn.cursor()
                                cursor.execute('''
                                    INSERT INTO presentations (student_id, presentation_date, progress_notes, presentation_file)
                                    VALUES (?, ?, ?, ?)
                                ''', (student_id, pres_date, progress, final_pres_path))
                                conn.commit()
                                messagebox.showinfo("Success", "Presentation added successfully!", parent=self.root)
                                load_presentations()
                        except sqlite3.Error as e:
                            messagebox.showerror("Error", f"Error adding presentation: {e}", parent=self.root)

                    add_btn = ttk.Button(card_frame, text="Add Presentation", style="Danger.TButton", command=add_presentation)
                    add_btn.pack(pady=20, padx=20, fill="x", ipady=5)
                    self.button_bind(add_btn)

                    back_btn = ttk.Button(card_frame, text="Back", style="TButton", command=self.show_admin_dashboard)
                    back_btn.pack(pady=10, padx=20, fill="x", ipady=5)
                    self.button_bind(back_btn)

            except ValueError:
                messagebox.showerror("Error", "Invalid ID. Please enter a number.", parent=self.root)

        load_btn = ttk.Button(card_frame, text="Load Presentations", style="TButton", command=load_presentations)
        load_btn.pack(pady=20, padx=20, fill="x", ipady=5)
        self.button_bind(load_btn)
        back_btn = ttk.Button(card_frame, text="Back", style="TButton", command=self.show_admin_dashboard)
        back_btn.pack(pady=10, padx=20, fill="x", ipady=5)
        self.button_bind(back_btn)

        canvas.bind_all("<MouseWheel>", lambda event: canvas.yview_scroll(int(-1 * (event.delta / 120)), "units"))
        canvas.bind_all("<Button-4>", lambda event: canvas.yview_scroll(-1, "units"))
        canvas.bind_all("<Button-5>", lambda event: canvas.yview_scroll(1, "units"))
        
        card_frame.update_idletasks()
        canvas.configure(scrollregion=canvas.bbox("all"))

    def show_view_students(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        card_frame, canvas = self.create_scrollable_frame(self.root)
        card_frame.configure(padding=30)

        ttk.Label(card_frame, text="All Students", style="Heading.TLabel").pack(pady=20)

        students_frame = ttk.Frame(card_frame, style="Card.TFrame")
        students_frame.pack(fill="both", expand=True, padx=20, pady=10)

        selected_student_id = tk.StringVar()

        try:
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM students")
                students = cursor.fetchall()

                if not students:
                    ttk.Label(students_frame, text="No students found.", font=("Inter", 11)).pack(pady=10)
                else:
                    for idx, student in enumerate(students):
                        student_frame = ttk.Frame(students_frame, style="Card.TFrame", borderwidth=1, relief="solid")
                        student_frame.pack(fill="x", padx=10, pady=5, ipady=5)

                        dob = student[10] if student[10] else "N/A"
                        title = student[12] if student[12] else "N/A"
                        publications = student[13] if student[13] else "N/A"
                        batch_from = student[2] if student[2] else None
                        batch_to = student[3] if student[3] else None
                        original_batch_to = student[4] if student[4] else None

                        batch_display = "N/A"
                        if batch_from and batch_to:
                            batch_display = f"{batch_from}-{batch_to}"
                            if original_batch_to:
                                try:
                                    batch_to_int = int(batch_to)
                                    original_batch_to_int = int(original_batch_to)
                                    extension_years = batch_to_int - original_batch_to_int
                                    if extension_years > 0:
                                        batch_display += f" (Extended by {extension_years} year{'s' if extension_years != 1 else ''})"
                                except ValueError:
                                    pass

                        fields = [
                            f"ID: {student[0]}",
                            f"Roll No: {student[1]}",
                            f"Batch: {batch_display}",
                            f"Name: {student[5]}",
                            f"Email: {student[6]}",
                            f"DOB: {dob}",
                            f"Department: {student[7]}",
                            f"Supervisor: {student[8]}",
                            f"Registration Date: {student[9]}",
                            f"Title: {title}",
                            f"Publications: {publications}"
                        ]

                        for field in fields:
                            ttk.Label(
                                student_frame,
                                text=field,
                                font=("Inter", 11),
                                wraplength=600
                            ).pack(anchor="w", padx=10, pady=2)

                        ttk.Radiobutton(
                            student_frame,
                            text="Select",
                            variable=selected_student_id,
                            value=str(student[0])
                        ).pack(anchor="w", padx=10, pady=5)

        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Error viewing students: {e}", parent=self.root)

        image_frame = ttk.Frame(card_frame, style="Card.TFrame")
        image_frame.pack(pady=10, fill="x", padx=20)

        def show_details():
            for widget in image_frame.winfo_children():
                widget.destroy()

            student_id = selected_student_id.get()
            if not student_id:
                return

            student_id = int(student_id)
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT picture_path FROM students WHERE id = ?", (student_id,))
                pic_path = cursor.fetchone()[0]

            if pic_path and os.path.exists(pic_path):
                try:
                    image = Image.open(pic_path)
                    image = image.resize((150, 150), Image.LANCZOS)
                    image = ImageTk.PhotoImage(image)
                    img_label = ttk.Label(image_frame, image=image, background="#FFFFFF")
                    img_label.image = image
                    img_label.pack(pady=10)
                except Exception as e:
                    ttk.Label(image_frame, text=f"Unable to load picture: {e}", font=("Inter", 11)).pack(pady=10)
            else:
                ttk.Label(image_frame, text="Picture not available", font=("Inter", 11)).pack(pady=10)

            certificates = self.get_student_certificates(student_id)
            if certificates:
                ttk.Label(image_frame, text="Certificates:", font=("Inter", 11, "bold")).pack(pady=5)
                for cert in certificates:
                    cert_label = f"Title: {cert[1]}"
                    ttk.Label(image_frame, text=cert_label, font=("Inter", 11)).pack(pady=2)
                    if cert[2] and os.path.exists(cert[2]):
                        cert_btn = ttk.Button(image_frame, text=f"View Certificate ({os.path.basename(cert[2])})", style="TButton",
                                             command=lambda p=cert[2]: webbrowser.open(f"file://{os.path.abspath(p)}"))
                        cert_btn.pack(pady=5, padx=20, ipady=5)
                        self.button_bind(cert_btn)
                    else:
                        ttk.Label(image_frame, text="Certificate file not available", font=("Inter", 11)).pack(pady=2)
            else:
                ttk.Label(image_frame, text="No certificates recorded", font=("Inter", 11)).pack(pady=5)

            synopsis = self.get_student_synopsis(student_id)
            if synopsis:
                ttk.Label(image_frame, text="Synopsis:", font=("Inter", 11, "bold")).pack(pady=5)
                synopsis_label = f"Title: {synopsis[2]}\nSubmission Date: {synopsis[3]}\nAbstract: {synopsis[4]}"
                ttk.Label(image_frame, text=synopsis_label, font=("Inter", 11), wraplength=600).pack(pady=2)
                if synopsis[5] and os.path.exists(synopsis[5]):
                    synopsis_btn = ttk.Button(image_frame, text=f"View Synopsis PDF ({os.path.basename(synopsis[5])})", style="TButton",
                                            command=lambda p=synopsis[5]: webbrowser.open(f"file://{os.path.abspath(p)}"))
                    synopsis_btn.pack(pady=5, padx=20, ipady=5)
                    self.button_bind(synopsis_btn)
                else:
                    ttk.Label(image_frame, text="Synopsis PDF not available", font=("Inter", 11)).pack(pady=2)
            else:
                ttk.Label(image_frame, text="No synopsis recorded", font=("Inter", 11)).pack(pady=5)

            presentations = self.get_student_presentations(student_id)
            if presentations:
                ttk.Label(image_frame, text="6-Month Presentations:", font=("Inter", 11, "bold")).pack(pady=5)
                for pres in presentations:
                    pres_label = f"Date: {pres[2]}, Progress: {pres[3]}"
                    ttk.Label(image_frame, text=pres_label, font=("Inter", 11)).pack(pady= 10)
                    if pres[4] and os.path.exists(pres[4]):
                        pres_btn = ttk.Button(image_frame, text=f"View Presentation ({os.path.basename(pres[4])})", style="TButton",
                                             command=lambda p=pres[4]: webbrowser.open(f"file://{os.path.abspath(p)}"))
                        pres_btn.pack(pady=5, padx=20, ipady=5)
                        self.button_bind(pres_btn)
                    else:
                        ttk.Label(image_frame, text="Presentation file not available", font=("Inter", 11)).pack(pady=2)
            else:
                ttk.Label(image_frame, text="No presentations recorded", font=("Inter", 11)).pack(pady=5)

        show_details_btn = ttk.Button(card_frame, text="Show Details", style="TButton", command=show_details)
        show_details_btn.pack(pady=10, padx=20, fill="x", ipady=5)
        self.button_bind(show_details_btn)

        back_btn = ttk.Button(card_frame, text="Back", style="TButton", command=self.show_admin_dashboard)
        back_btn.pack(pady=20, padx=20, fill="x", ipady=5)
        self.button_bind(back_btn)

        canvas.bind_all("<MouseWheel>", lambda event: canvas.yview_scroll(int(-1 * (event.delta / 120)), "units"))
        canvas.bind_all("<Button-4>", lambda event: canvas.yview_scroll(-1, "units"))
        canvas.bind_all("<Button-5>", lambda event: canvas.yview_scroll(1, "units"))
        
        card_frame.update_idletasks()
        canvas.configure(scrollregion=canvas.bbox("all"))

    def show_update_student(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        card_frame, canvas = self.create_scrollable_frame(self.root)
        card_frame.configure(padding=20)

        ttk.Label(card_frame, text="Update Student", style="Heading.TLabel").pack(pady=10)
        ttk.Label(card_frame, text="Student ID").pack(anchor="w", padx=20, pady=(5, 0))
        id_entry = ttk.Entry(card_frame)
        id_entry.pack(pady=5, padx=20, fill="x", ipady=3)

        def load_student():
            try:
                student_id = int(id_entry.get())
                with sqlite3.connect(self.db_file) as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT * FROM students WHERE id = ?", (student_id,))
                    student = cursor.fetchone()
                    if not student:
                        messagebox.showerror("Error", "Student not found.", parent=self.root)
                        return

                    for widget in card_frame.winfo_children():
                        widget.destroy()

                    card_frame.configure(padding=20)
                    ttk.Label(card_frame, text="Update Student", style="Heading.TLabel").pack(pady=10)

                    fields = ["Name", "Roll Number", "Email", "Date of Birth (DD-MM-YYYY)", "Department", "Supervisor", 
                              "Registration Date (DD-MM-YYYY)", "Title", "Publications"]
                    entries = {}
                    try:
                        dob_display = datetime.strptime(student[10], "%Y-%m-%d").strftime("%d-%m-%Y") if student[10] else ""
                    except (ValueError, TypeError):
                        dob_display = student[10] if student[10] else ""
                    try:
                        reg_date_display = datetime.strptime(student[9], "%Y-%m-%d").strftime("%d-%m-%Y") if student[9] else ""
                    except (ValueError, TypeError):
                        reg_date_display = student[9] if student[9] else ""
                    defaults = [student[5], student[1], student[6], dob_display, 
                                student[7], student[8], reg_date_display, 
                                student[12] if student[12] else "", 
                                student[13] if student[13] else ""]
                    for field, default in zip(fields, defaults):
                        if field == "Roll Number":
                            ttk.Label(card_frame, text=field).pack(anchor="w", padx=20, pady=(5, 0))
                            entry = ttk.Entry(card_frame)
                            entry.insert(0, default)
                            entry.pack(pady=5, padx=20, fill="x", ipady=3)
                            entries[field] = entry

                            batch_frame = ttk.Frame(card_frame, style="Card.TFrame")
                            batch_frame.pack(pady=5, padx=20, fill="x")
                            
                            ttk.Label(batch_frame, text="Batch From").pack(side="left", padx=(0, 10))
                            batch_from_entry = ttk.Entry(batch_frame, width=10)
                            batch_from_entry.insert(0, student[2] if student[2] else "")
                            batch_from_entry.pack(side="left", padx=(0, 20))
                            entries["Batch From"] = batch_from_entry
                            
                            ttk.Label(batch_frame, text="Batch To").pack(side="left", padx=(0, 10))
                            batch_to_entry = ttk.Entry(batch_frame, width=10)
                            batch_to_entry.insert(0, student[3] if student[3] else "")
                            batch_to_entry.pack(side="left")
                            entries["Batch To"] = batch_to_entry

                            ttk.Label(batch_frame, text="Extend By (Years)").pack(side="left", padx=(20, 10))
                            extension_entry = ttk.Entry(batch_frame, width=5)
                            extension_entry.pack(side="left")
                            extension_entry.insert(0, "0")

                            def apply_extension():
                                try:
                                    years_to_extend = int(extension_entry.get())
                                    if years_to_extend < 0:
                                        messagebox.showerror("Error", "Extension years cannot be negative.", parent=self.root)
                                        return
                                    current_to = batch_to_entry.get().strip()
                                    if not current_to:
                                        messagebox.showerror("Error", "Please enter a Batch To year first.", parent=self.root)
                                        return
                                    to_year = int(current_to)
                                    new_to_year = to_year + years_to_extend
                                    batch_to_entry.delete(0, tk.END)
                                    batch_to_entry.insert(0, str(new_to_year))
                                except ValueError:
                                    messagebox.showerror("Error", "Please enter a valid number of years to extend.", parent=self.root)

                            extension_btn = ttk.Button(batch_frame, text="Apply Extension", style="TButton", command=apply_extension)
                            extension_btn.pack(side="left", padx=(10, 0))
                            self.button_bind(extension_btn)
                        else:
                            ttk.Label(card_frame, text=field).pack(anchor="w", padx=20, pady=(5, 0))
                            entry = ttk.Entry(card_frame)
                            entry.insert(0, default)
                            entry.pack(pady=5, padx=20, fill="x", ipady=3)
                            entries[field] = entry

                    picture_path = tk.StringVar(value=student[11] if student[11] else "")
                    certificates_data = []

                    def select_picture():
                        path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.png")])
                        if path:
                            picture_path.set(path)
                        card_frame.winfo_toplevel().lift()  # Bring update student window back to front
                        card_frame.winfo_toplevel().grab_set()  # Restore focus

                    def update_certificates():
                        certificates_window = tk.Toplevel(self.root)
                        certificates_window.title("Update Certificates")
                        certificates_window.geometry("600x600")
                        certificates_window.configure(bg="#F5F7FA")
                        certificates_window.transient(self.root)  # Set as transient to the main window
                        certificates_window.grab_set()  # Ensure it stays in focus

                        top_bar = ttk.Frame(certificates_window, style="Shadow.TFrame")
                        top_bar.pack(fill="x", padx=20, pady=(10, 0))
                        left_frame = ttk.Frame(top_bar, style="Shadow.TFrame")
                        left_frame.pack(side="left", padx=10)
                        project_label = ttk.Label(left_frame, text="PhD Management System", style="Project.TLabel")
                        project_label.pack(anchor="w", pady=2)
                        author_label = ttk.Label(left_frame, text="Project by: Avneet Kaur, B.Tech (CSE), 6th Sem", style="Author.TLabel")
                        author_label.pack(anchor="w", pady=2)
                        home_btn = ttk.Button(top_bar, text="Home", style="TextButton.TButton", 
                                             command=self.show_admin_dashboard)
                        home_btn.pack(side="right", pady=2, padx=10)
                        self.button_bind(home_btn)
                        logout_btn = ttk.Button(top_bar, text="Log Out", style="TextButton.TButton", 
                                               command=self.show_login)
                        logout_btn.pack(side="right", pady=2, padx=10)
                        self.button_bind(logout_btn)

                        card_frame_certs = ttk.Frame(certificates_window, style="Card.TFrame")
                        card_frame_certs.pack(expand=True, fill="both", padx=20, pady=20)

                        ttk.Label(card_frame_certs, text="Update Certificates", style="Heading.TLabel").pack(pady=20)

                        certs_listbox = tk.Listbox(card_frame_certs, height=10, font=("Inter", 11))
                        certs_listbox.pack(pady=10, padx=20, fill="both")

                        existing_certs = self.get_student_certificates(student_id)
                        for cert in existing_certs:
                            certs_listbox.insert(tk.END, f"{cert[1]}: {os.path.basename(cert[2]) if cert[2] else 'N/A'}")

                        ttk.Label(card_frame_certs, text="Certificate Title").pack(anchor="w", padx=20, pady=(10, 0))
                        cert_title_entry = ttk.Entry(card_frame_certs)
                        cert_title_entry.pack(pady=10, padx=20, fill="x", ipady=5)

                        cert_file_path = tk.StringVar()
                        def select_certificate_file():
                            path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
                            if path:
                                cert_file_path.set(path)
                            certificates_window.lift()  # Bring certificates window back to front
                            certificates_window.grab_set()  # Restore focus to certificates window

                        cert_file_btn = ttk.Button(card_frame_certs, text="Select Certificate PDF", style="TButton", command=select_certificate_file)
                        cert_file_btn.pack(pady=10, padx=20, fill="x", ipady=5)
                        self.button_bind(cert_file_btn)

                        def add_certificate():
                            title = cert_title_entry.get().strip()
                            path = cert_file_path.get()
                            if not title or not path:
                                messagebox.showerror("Error", "Certificate title and file are required.", parent=certificates_window)
                                return
                            certificates_data.append({"title": title, "path": path})
                            certs_listbox.insert(tk.END, f"{title}: {os.path.basename(path)}")
                            cert_title_entry.delete(0, tk.END)
                            cert_file_path.set("")
                            messagebox.showinfo("Success", "Certificate added to list.", parent=certificates_window)

                        add_cert_btn = ttk.Button(card_frame_certs, text="Add Certificate", style="TButton", command=add_certificate)
                        add_cert_btn.pack(pady=10, padx=20, fill="x", ipady=5)
                        self.button_bind(add_cert_btn)

                        def save_certificates():
                            messagebox.showinfo("Success", "Certificates saved. Submit student to finalize.", parent=certificates_window)
                            certificates_window.destroy()

                        save_btn = ttk.Button(card_frame_certs, text="Save Certificates", style="Danger.TButton", command=save_certificates)
                        save_btn.pack(pady=20, padx=20, fill="x", ipady=5)
                        self.button_bind(save_btn)

                        cancel_btn = ttk.Button(card_frame_certs, text="Cancel", style="TButton", command=certificates_window.destroy)
                        cancel_btn.pack(pady=10, padx=20, fill="x", ipady=5)
                        self.button_bind(cancel_btn)

                    pic_btn = ttk.Button(card_frame, text="Select Picture (JPG/PNG)", style="TButton", command=select_picture)
                    pic_btn.pack(pady=5, padx=20, fill="x", ipady=3)
                    self.button_bind(pic_btn)

                    cert_btn = ttk.Button(card_frame, text="Update Certificates", style="TButton", command=update_certificates)
                    cert_btn.pack(pady=5, padx=20, fill="x", ipady=3)
                    self.button_bind(cert_btn)

                    synopsis = self.get_student_synopsis(student_id)
                    synopsis_data = {}
                    if synopsis:
                        ttk.Label(card_frame, text="Synopsis:", font=("Inter", 11, "bold")).pack(anchor="w", padx=20, pady=(5, 0))
                        synopsis_label = f"Title: {synopsis[2]} | Submission Date: {synopsis[3]}"
                        ttk.Label(card_frame, text=synopsis_label, font=("Inter", 10), wraplength=600).pack(anchor="w", padx=40, pady=2)
                        if synopsis[5] and os.path.exists(synopsis[5]):
                            synopsis_btn = ttk.Button(card_frame, text="View Synopsis PDF", style="TButton",
                                                    command=lambda p=synopsis[5]: webbrowser.open(f"file://{os.path.abspath(p)}"))
                            synopsis_btn.pack(pady=2, padx=40, fill="x", ipady=2)
                            self.button_bind(synopsis_btn)

                    def update_synopsis():
                        synopsis_window = tk.Toplevel(self.root)
                        synopsis_window.title("Update Synopsis")
                        synopsis_window.geometry("600x500")
                        synopsis_window.configure(bg="#F5F7FA")
                        synopsis_window.transient(self.root)  # Set as transient to the main window
                        synopsis_window.grab_set()  # Ensure it stays in focus

                        top_bar = ttk.Frame(synopsis_window, style="Shadow.TFrame")
                        top_bar.pack(fill="x", padx=20, pady=(10, 0))
                        left_frame = ttk.Frame(top_bar, style="Shadow.TFrame")
                        left_frame.pack(side="left", padx=10)
                        project_label = ttk.Label(left_frame, text="PhD Management System", style="Project.TLabel")
                        project_label.pack(anchor="w", pady=2)
                        author_label = ttk.Label(left_frame, text="Project by: Avneet Kaur, B.Tech (CSE), 6th Sem", style="Author.TLabel")
                        author_label.pack(anchor="w", pady=2)
                        home_btn = ttk.Button(top_bar, text="Home", style="TextButton.TButton", 
                                             command=self.show_admin_dashboard)
                        home_btn.pack(side="right", pady=2, padx=10)
                        self.button_bind(home_btn)
                        logout_btn = ttk.Button(top_bar, text="Log Out", style="TextButton.TButton", 
                                               command=self.show_login)
                        logout_btn.pack(side="right", pady=2, padx=10)
                        self.button_bind(logout_btn)

                        card_frame_synopsis = ttk.Frame(synopsis_window, style="Card.TFrame")
                        card_frame_synopsis.pack(expand=True, fill="both", padx=20, pady=20)

                        ttk.Label(card_frame_synopsis, text="Synopsis Details", style="Heading.TLabel").pack(pady=20)

                        ttk.Label(card_frame_synopsis, text="Synopsis Title").pack(anchor="w", padx=20, pady=(10, 0))
                        synopsis_title_entry = ttk.Entry(card_frame_synopsis)
                        synopsis_title_entry.insert(0, synopsis[2] if synopsis else "")
                        synopsis_title_entry.pack(pady=10, padx=20, fill="x", ipady=5)

                        ttk.Label(card_frame_synopsis, text="Submission Date (DD-MM-YYYY)").pack(anchor="w", padx=20, pady=(10, 0))
                        submission_date_entry = ttk.Entry(card_frame_synopsis)
                        submission_date_entry.insert(0, datetime.strptime(synopsis[3], "%Y-%m-%d").strftime("%d-%m-%Y") if synopsis else "")
                        submission_date_entry.pack(pady=10, padx=20, fill="x", ipady=5)

                        ttk.Label(card_frame_synopsis, text="Abstract (4–5 lines)").pack(anchor="w", padx=20, pady=(10, 0))
                        abstract_text = tk.Text(card_frame_synopsis, height=5, font=("Inter", 11))
                        abstract_text.insert("1.0", synopsis[4] if synopsis else "")
                        abstract_text.pack(pady=10, padx=20, fill="x")

                        synopsis_file_path = tk.StringVar(value=synopsis[5] if synopsis else "")
                        def select_synopsis_file():
                            path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
                            if path:
                                synopsis_file_path.set(path)
                            synopsis_window.lift()  # Bring synopsis window back to front
                            synopsis_window.grab_set()  # Restore focus to synopsis window

                        synopsis_file_btn = ttk.Button(card_frame_synopsis, text="Select Synopsis PDF (Optional)", style="TButton", command=select_synopsis_file)
                        synopsis_file_btn.pack(pady=10, padx=20, fill="x", ipady=5)
                        self.button_bind(synopsis_file_btn)

                        def save_synopsis():
                            synopsis_data['title'] = synopsis_title_entry.get().strip()
                            synopsis_data['submission_date'] = submission_date_entry.get().strip()
                            synopsis_data['abstract'] = abstract_text.get("1.0", tk.END).strip()
                            synopsis_data['file_path'] = synopsis_file_path.get()
                            
                            if not all([synopsis_data['title'], synopsis_data['submission_date'], synopsis_data['abstract']]):
                                messagebox.showerror("Error", "Synopsis Title, Submission Date, and Abstract are required.", parent=synopsis_window)
                                return
                            try:
                                datetime.strptime(synopsis_data['submission_date'], "%d-%m-%Y")
                            except ValueError:
                                messagebox.showerror("Error", "Invalid date format. Use DD-MM-YYYY.", parent=synopsis_window)
                                return

                            messagebox.showinfo("Success", "Synopsis details saved. Submit student to finalize.", parent=synopsis_window)
                            synopsis_window.destroy()

                        save_btn = ttk.Button(card_frame_synopsis, text="Save Synopsis", style="Danger.TButton", command=save_synopsis)
                        save_btn.pack(pady=20, padx=20, fill="x", ipady=5)
                        self.button_bind(save_btn)

                        cancel_btn = ttk.Button(card_frame_synopsis, text="Cancel", style="TButton", command=synopsis_window.destroy)
                        cancel_btn.pack(pady=10, padx=20, fill="x", ipady=5)
                        self.button_bind(cancel_btn)

                    synopsis_btn = ttk.Button(card_frame, text="Update Synopsis", style="TButton", command=update_synopsis)
                    synopsis_btn.pack(pady=5, padx=20, fill="x", ipady=3)
                    self.button_bind(synopsis_btn)

                    ttk.Label(card_frame, text="Current Presentations:", font=("Inter", 11, "bold")).pack(anchor="w", padx=20, pady=(5, 0))
                    presentations = self.get_student_presentations(student_id)
                    if presentations:
                        for pres in presentations:
                            pres_label = f"Date: {pres[2]} | Progress: {pres[3]}"
                            ttk.Label(card_frame, text=pres_label, font=("Inter", 10)).pack(anchor="w", padx=40, pady=1)
                            if pres[4] and os.path.exists(pres[4]):
                                pres_btn = ttk.Button(card_frame, text="View Presentation", style="TButton",
                                                     command=lambda p=pres[4]: webbrowser.open(f"file://{os.path.abspath(p)}"))
                                pres_btn.pack(pady=2, padx=40, fill="x", ipady=2)
                                self.button_bind(pres_btn)
                    else:
                        ttk.Label(card_frame, text="No presentations recorded", font=("Inter", 10)).pack(anchor="w", padx=40, pady=1)

                    ttk.Label(card_frame, text="Current Certificates:", font=("Inter", 11, "bold")).pack(anchor="w", padx=20, pady=(5, 0))
                    certificates = self.get_student_certificates(student_id)
                    if certificates:
                        for cert in certificates:
                            cert_label = f"Title: {cert[1]}"
                            ttk.Label(card_frame, text=cert_label, font=("Inter", 10)).pack(anchor="w", padx=40, pady=1)
                            if cert[2] and os.path.exists(cert[2]):
                                cert_btn = ttk.Button(card_frame, text="View Certificate", style="TButton",
                                                     command=lambda p=cert[2]: webbrowser.open(f"file://{os.path.abspath(p)}"))
                                cert_btn.pack(pady=2, padx=40, fill="x", ipady=2)
                                self.button_bind(cert_btn)
                    else:
                        ttk.Label(card_frame, text="No certificates recorded", font=("Inter", 10)).pack(anchor="w", padx=40, pady=1)

                    def submit():
                        name = entries["Name"].get().strip()
                        roll_number = entries["Roll Number"].get().strip()
                        batch_from = entries["Batch From"].get().strip()
                        batch_to = entries["Batch To"].get().strip()
                        email = entries["Email"].get().strip()
                        dob_str = entries["Date of Birth (DD-MM-YYYY)"].get().strip()
                        department = entries["Department"].get().strip()
                        supervisor = entries["Supervisor"].get().strip()
                        registration_date_str = entries["Registration Date (DD-MM-YYYY)"].get().strip()
                        title = entries["Title"].get().strip()
                        publications = entries["Publications"].get().strip()

                        try:
                            dob = datetime.strptime(dob_str, "%d-%m-%Y").strftime("%Y-%m-%d") if dob_str else None
                            registration_date = datetime.strptime(registration_date_str, "%d-%m-%Y").strftime("%Y-%m-%d") if registration_date_str else None
                        except ValueError:
                            messagebox.showerror("Error", "Invalid date format. Use DD-MM-YYYY.", parent=self.root)
                            return

                        try:
                            if batch_from:
                                int(batch_from)
                            if batch_to:
                                int(batch_to)
                        except ValueError:
                            messagebox.showerror("Error", "Batch From and To must be valid years.", parent=self.root)
                            return

                        if not all([name, roll_number, email, department, supervisor, registration_date, title, publications]):
                            messagebox.showerror("Error", "All fields except DOB and Batch are required.", parent=self.root)
                            return

                        pic_path = picture_path.get()
                        final_pic_path = student[11]
                        final_synopsis_path = synopsis[5] if synopsis else None

                        try:
                            with sqlite3.connect(self.db_file) as conn:
                                cursor = conn.cursor()
                                if pic_path and pic_path != student[11]:
                                    final_pic_path = os.path.join(self.pic_dir, f"{student_id}_{roll_number}{os.path.splitext(pic_path)[1]}")
                                    shutil.copy(pic_path, final_pic_path)
                                cursor.execute('''
                                    UPDATE students 
                                    SET roll_number = ?, batch_from = ?, batch_to = ?, name = ?, email = ?, department = ?, 
                                        supervisor = ?, registration_date = ?, dob = ?, picture_path = ?, 
                                        title = ?, publications = ?
                                    WHERE id = ?
                                ''', (roll_number, batch_from or None, batch_to or None, name, email, department, supervisor, 
                                      registration_date, dob, final_pic_path, title, publications, student_id))
                                
                                if certificates_data:
                                    cursor.execute("DELETE FROM certificates WHERE student_id = ?", (student_id,))
                                    for cert in certificates_data:
                                        final_cert_path = os.path.join(self.cert_dir, f"{student_id}_{cert['title'].replace(' ', '_')}.pdf")
                                        shutil.copy(cert['path'], final_cert_path)
                                        cursor.execute('''
                                            INSERT INTO certificates (student_id, certificate_title, certificate_path)
                                            VALUES (?, ?, ?)
                                        ''', (student_id, cert['title'], final_cert_path))
                                
                                if synopsis_data.get('title') and synopsis_data.get('submission_date') and synopsis_data.get('abstract'):
                                    submission_date = datetime.strptime(synopsis_data['submission_date'], "%d-%m-%Y").strftime("%Y-%m-%d")
                                    if synopsis_data.get('file_path') and synopsis_data.get('file_path') != (synopsis[5] if synopsis else None):
                                        final_synopsis_path = os.path.join(self.synopsis_dir, f"{student_id}_{submission_date.replace('-', '')}.pdf")
                                        shutil.copy(synopsis_data['file_path'], final_synopsis_path)
                                    cursor.execute('''
                                        INSERT OR REPLACE INTO synopsis (id, student_id, synopsis_title, submission_date, abstract, synopsis_file)
                                        VALUES ((SELECT id FROM synopsis WHERE student_id = ?), ?, ?, ?, ?, ?)
                                    ''', (student_id, student_id, synopsis_data['title'], submission_date, synopsis_data['abstract'], final_synopsis_path))
                                
                                conn.commit()
                                messagebox.showinfo("Success", f"Student {name} updated successfully!", parent=self.root)
                                self.show_admin_dashboard()
                        except sqlite3.Error as e:
                            messagebox.showerror("Error", f"Error updating student: {e}", parent=self.root)

                    submit_btn = ttk.Button(card_frame, text="Submit", style="Danger.TButton", command=submit)
                    submit_btn.pack(pady=20, padx=20, fill="x", ipady=5)
                    self.button_bind(submit_btn)
                    cancel_btn = ttk.Button(card_frame, text="Cancel", style="TButton", command=self.show_admin_dashboard)
                    cancel_btn.pack(pady=10, padx=20, fill="x", ipady=5)
                    self.button_bind(cancel_btn)

            except ValueError:
                messagebox.showerror("Error", "Invalid ID. Please enter a number.", parent=self.root)

        load_btn = ttk.Button(card_frame, text="Load Student", style="TButton", command=load_student)
        load_btn.pack(pady=20, padx=20, fill="x", ipady=5)
        self.button_bind(load_btn)
        back_btn = ttk.Button(card_frame, text="Back", style="TButton", command=self.show_admin_dashboard)
        back_btn.pack(pady=10, padx=20, fill="x", ipady=5)
        self.button_bind(back_btn)

        canvas.bind_all("<MouseWheel>", lambda event: canvas.yview_scroll(int(-1 * (event.delta / 120)), "units"))
        canvas.bind_all("<Button-4>", lambda event: canvas.yview_scroll(-1, "units"))
        canvas.bind_all("<Button-5>", lambda event: canvas.yview_scroll(1, "units"))
        
        card_frame.update_idletasks()
        canvas.configure(scrollregion=canvas.bbox("all"))

    def show_delete_student(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        card_frame, canvas = self.create_scrollable_frame(self.root)
        card_frame.configure(padding=30)

        ttk.Label(card_frame, text="Delete Student", style="Heading.TLabel").pack(pady=20)
        ttk.Label(card_frame, text="Student ID").pack(anchor="w", padx=20, pady=(10, 0))
        id_entry = ttk.Entry(card_frame)
        id_entry.pack(pady=10, padx=20, fill="x", ipady=5)

        def delete_student():
            try:
                student_id = int(id_entry.get())
                with sqlite3.connect(self.db_file) as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT name, picture_path FROM students WHERE id = ?", (student_id,))
                    student = cursor.fetchone()
                    if not student:
                        messagebox.showerror("Error", "Student not found.", parent=self.root)
                        return

                    if messagebox.askyesno("Confirm", f"Are you sure you want to delete {student[0]}?", parent=self.root):
                        cursor.execute("DELETE FROM students WHERE id = ?", (student_id,))
                        cursor.execute("DELETE FROM presentations WHERE student_id = ?", (student_id,))
                        cursor.execute("DELETE FROM synopsis WHERE student_id = ?", (student_id,))
                        cursor.execute("DELETE FROM certificates WHERE student_id = ?", (student_id,))
                        conn.commit()
                        if student[1] and os.path.exists(student[1]):
                            os.remove(student[1])
                        messagebox.showinfo("Success", f"Student {student[0]} deleted successfully!", parent=self.root)
                        self.show_admin_dashboard()
            except ValueError:
                messagebox.showerror("Error", "Invalid ID. Please enter a number.", parent=self.root)
            except sqlite3.Error as e:
                messagebox.showerror("Error", f"Error deleting student: {e}", parent=self.root)

        delete_btn = ttk.Button(card_frame, text="Delete", style="Danger.TButton", command=delete_student)
        delete_btn.pack(pady=20, padx=20, fill="x", ipady=5)
        self.button_bind(delete_btn)
        back_btn = ttk.Button(card_frame, text="Back", style="TButton", command=self.show_admin_dashboard)
        back_btn.pack(pady=10, padx=20, fill="x", ipady=5)
        self.button_bind(back_btn)

        canvas.bind_all("<MouseWheel>", lambda event: canvas.yview_scroll(int(-1 * (event.delta / 120)), "units"))
        canvas.bind_all("<Button-4>", lambda event: canvas.yview_scroll(-1, "units"))
        canvas.bind_all("<Button-5>", lambda event: canvas.yview_scroll(1, "units"))
        
        card_frame.update_idletasks()
        canvas.configure(scrollregion=canvas.bbox("all"))

    def show_search_student(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        card_frame, canvas = self.create_scrollable_frame(self.root)
        card_frame.configure(padding=30)

        ttk.Label(card_frame, text="Search Student", style="Heading.TLabel").pack(pady=20)
        ttk.Label(card_frame, text="Search by Name or Roll Number").pack(anchor="w", padx=20, pady=(10, 0))
        search_entry = ttk.Entry(card_frame)
        search_entry.pack(pady=10, padx=20, fill="x", ipady=5)

        result_frame = ttk.Frame(card_frame, style="Card.TFrame")
        result_frame.pack(pady=10, fill="both", expand=True, padx=20)

        selected_student_id = tk.StringVar()
  # To track the selected student  # To track the selected student

        def search():
            for widget in result_frame.winfo_children():
                widget.destroy()

            search_term = search_entry.get().strip()
            if not search_term:
                messagebox.showerror("Error", "Please enter a search term.", parent=self.root)
                return

            try:
                with sqlite3.connect(self.db_file) as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT * FROM students WHERE name LIKE ? OR roll_number LIKE ?", 
                                  (f"%{search_term}%", f"%{search_term}%"))
                    students = cursor.fetchall()

                    if not students:
                        ttk.Label(result_frame, text="No students found.", font=("Inter", 11)).pack(pady=10)
                        return

                    # Frame to hold student details in a vertical layout
                    students_frame = ttk.Frame(result_frame, style="Card.TFrame")
                    students_frame.pack(fill="both", expand=True, padx=20, pady=10)

                    for idx, student in enumerate(students):
                        # Create a frame for each student with a border
                        student_frame = ttk.Frame(students_frame, style="Card.TFrame", borderwidth=1, relief="solid")
                        student_frame.pack(fill="x", padx=10, pady=5, ipady=5)

                        # Calculate batch display with extension
                        dob = student[9] if student[9] else "N/A"
                        title = student[12] if student[12] else "N/A"
                        publications = student[13] if student[13] else "N/A"
                        batch_from = student[2] if student[2] else None
                        batch_to = student[3] if student[3] else None
                        original_batch_to = student[4] if student[4] else None

                        batch_display = "N/A"
                        if batch_from and batch_to:
                            batch_display = f"{batch_from}-{batch_to}"
                            if original_batch_to:
                                try:
                                    batch_to_int = int(batch_to)
                                    original_batch_to_int = int(original_batch_to)
                                    extension_years = batch_to_int - original_batch_to_int
                                    if extension_years > 0:
                                        batch_display += f" (Extended by {extension_years} year{'s' if extension_years != 1 else ''})"
                                except ValueError:
                                    # If conversion fails, just show the batch range without extension
                                    pass

                        # Fields to display in a vertical layout
                        fields = [
                            f"ID: {student[0]}",
                            f"Roll No: {student[1]}",
                            f"Batch: {batch_display}",
                            f"Name: {student[5]}",
                            f"Email: {student[6]}",
                            f"DOB: {dob}",
                            f"Department: {student[7]}",
                            f"Supervisor: {student[8]}",
                            f"Registration Date: {student[9]}",
                            f"Title: {title}",
                            f"Publications: {publications}"
                        ]

                        # Display each field as a label in a row
                        for field in fields:
                            ttk.Label(
                                student_frame,
                                text=field,
                                font=("Inter", 11),
                                wraplength=600  # Allow wrapping for long text
                            ).pack(anchor="w", padx=10, pady=2)

                        # Add a radio button to select this student
                        ttk.Radiobutton(
                            student_frame,
                            text="Select",
                            variable=selected_student_id,
                            value=str(student[0])
                        ).pack(anchor="w", padx=10, pady=5)

                    image_frame = ttk.Frame(result_frame, style="Card.TFrame")
                    image_frame.pack(pady=10, fill="x", padx=20)

                    def show_details():
                        for widget in image_frame.winfo_children():
                            widget.destroy()

                        student_id = selected_student_id.get()
                        if not student_id:
                            return

                        student_id = int(student_id)
                        with sqlite3.connect(self.db_file) as conn:
                            cursor = conn.cursor()
                            cursor.execute("SELECT certificate_path, picture_path FROM students WHERE id = ?", (student_id,))
                            cert_path, pic_path = cursor.fetchone()

                        if pic_path and os.path.exists(pic_path):
                            try:
                                image = Image.open(pic_path)
                                image = image.resize((150, 150), Image.LANCZOS)
                                image = ImageTk.PhotoImage(image)
                                img_label = ttk.Label(image_frame, image=image, background="#FFFFFF")
                                img_label.image = image
                                img_label.pack(pady=10)
                            except Exception as e:
                                ttk.Label(image_frame, text=f"Unable to load picture: {e}", font=("Inter", 11)).pack(pady=10)
                        else:
                            ttk.Label(image_frame, text="Picture not available", font=("Inter", 11)).pack(pady=10)

                        if cert_path and os.path.exists(cert_path):
                            cert_btn = ttk.Button(image_frame, text="View Certificate", style="TButton",
                                                 command=lambda: webbrowser.open(f"file://{os.path.abspath(cert_path)}"))
                            cert_btn.pack(pady=10, padx=20, ipady=5)
                            self.button_bind(cert_btn)
                        else:
                            ttk.Label(image_frame, text="Certificate not available", font=("Inter", 11)).pack(pady=10)

                        synopsis = self.get_student_synopsis(student_id)
                        if synopsis:
                            ttk.Label(image_frame, text="Synopsis:", font=("Inter", 11, "bold")).pack(pady=5)
                            synopsis_label = f"Title: {synopsis[2]}\nSubmission Date: {synopsis[3]}\nAbstract: {synopsis[4]}"
                            ttk.Label(image_frame, text=synopsis_label, font=("Inter", 11), wraplength=600).pack(pady=2)
                            if synopsis[5] and os.path.exists(synopsis[5]):
                                synopsis_btn = ttk.Button(image_frame, text=f"View Synopsis PDF ({os.path.basename(synopsis[5])})", 
                                                        style="TButton",
                                                        command=lambda p=synopsis[5]: webbrowser.open(f"file://{os.path.abspath(p)}"))
                                synopsis_btn.pack(pady=5, padx=20, ipady=5)
                                self.button_bind(synopsis_btn)
                            else:
                                ttk.Label(image_frame, text="Synopsis PDF not available", font=("Inter", 11)).pack(pady=2)
                        else:
                            ttk.Label(image_frame, text="No synopsis recorded", font=("Inter", 11)).pack(pady=5)

                        presentations = self.get_student_presentations(student_id)
                        if presentations:
                            ttk.Label(image_frame, text="6-Month Presentations:", font=("Inter", 11, "bold")).pack(pady=5)
                            for pres in presentations:
                                pres_label = f"Date: {pres[2]}, Progress: {pres[3]}"
                                ttk.Label(image_frame, text=pres_label, font=("Inter", 11)).pack(pady=2)
                                if pres[4] and os.path.exists(pres[4]):
                                    pres_btn = ttk.Button(image_frame, text=f"View Presentation ({os.path.basename(pres[4])})", 
                                                         style="TButton",
                                                         command=lambda p=pres[4]: webbrowser.open(f"file://{os.path.abspath(p)}"))
                                    pres_btn.pack(pady=5, padx=20, ipady=5)
                                    self.button_bind(pres_btn)
                                else:
                                    ttk.Label(image_frame, text="Presentation file not available", font=("Inter", 11)).pack(pady=2)
                        else:
                            ttk.Label(image_frame, text="No presentations recorded", font=("Inter", 11)).pack(pady=5)

                    # Button to trigger showing details of the selected student
                    show_details_btn = ttk.Button(result_frame, text="Show Details", style="TButton", command=show_details)
                    show_details_btn.pack(pady=10, padx=20, fill="x", ipady=5)
                    self.button_bind(show_details_btn)

            except sqlite3.Error as e:
                messagebox.showerror("Error", f"Error searching students: {e}", parent=self.root)

        search_btn = ttk.Button(card_frame, text="Search", style="TButton", command=search)
        search_btn.pack(pady=10, padx=20, fill="x", ipady=5)
        self.button_bind(search_btn)

        back_btn = ttk.Button(card_frame, text="Back", style="TButton", command=self.show_admin_dashboard)
        back_btn.pack(pady=10, padx=20, fill="x", ipady=5)
        self.button_bind(back_btn)

        canvas.bind_all("<MouseWheel>", lambda event: canvas.yview_scroll(int(-1 * (event.delta / 120)), "units"))
        canvas.bind_all("<Button-4>", lambda event: canvas.yview_scroll(-1, "units"))
        canvas.bind_all("<Button-5>", lambda event: canvas.yview_scroll(1, "units"))
        
        card_frame.update_idletasks()
        canvas.configure(scrollregion=canvas.bbox("all"))