import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import webbrowser
from PIL import Image, ImageTk
import sqlite3
import os

class StudentUI:
    def __init__(self, root, db_file, file_manager, show_login, student_id):
        self.root = root
        self.db_file = db_file
        self.file_manager = file_manager
        self.show_login = show_login
        self.student_id = student_id
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

    def button_bind(self, button):
        button.bind("<Enter>", lambda e: button.configure(cursor="hand2"))
        button.bind("<Leave>", lambda e: button.configure(cursor=""))

    def get_student_synopsis(self, student_id):
        try:
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM synopsis WHERE student_id = ?", (student_id,))
                return cursor.fetchone()
        except sqlite3.Error:
            return None

    def get_student_presentations(self, student_id):
        try:
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM presentations WHERE student_id = ?", (student_id,))
                return cursor.fetchall()
        except sqlite3.Error:
            return []

    def show_student_dashboard(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        card_frame, canvas = self.create_scrollable_frame(self.root)
        card_frame.configure(padding=30)

        # Heading
        ttk.Label(
            card_frame,
            text="Student Dashboard",
            style="Heading.TLabel"
        ).pack(pady=20)

        # Fetch and display student details
        try:
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM students WHERE id = ?", (self.student_id,))
                student = cursor.fetchone()
                if not student:
                    messagebox.showerror("Error", "Student not found.", parent=self.root)
                    self.show_login()
                    return

                # Create a frame for student details with a border
                student_frame = ttk.Frame(card_frame, style="Card.TFrame", borderwidth=1, relief="solid")
                student_frame.pack(fill="x", padx=20, pady=10, ipady=5)

                # Calculate batch display with extension
                batch_from = student[2] if student[2] else None
                batch_to = student[3] if student[3] else None
                original_batch_to = student[4] if student[4] else None
                batch_display = f"{batch_from}-{batch_to}" if batch_from and batch_to else "N/A"
                if batch_from and batch_to and original_batch_to:
                    try:
                        batch_to_int = int(batch_to)
                        original_batch_to_int = int(original_batch_to)
                        extension_years = batch_to_int - original_batch_to_int
                        if extension_years > 0:
                            batch_display += f" (Extended by {extension_years} year{'s' if extension_years != 1 else ''})"
                    except ValueError:
                        pass

                # Display student details in a vertical layout, ensuring labels stretch
                fields = [
                    f"ID: {student[0]}",
                    f"Roll No: {student[1]}",
                    f"Batch: {batch_display}",
                    f"Name: {student[5]}",
                    f"Email: {student[6]}",
                    f"DOB: {student[10] if student[10] else 'N/A'}",
                    f"Department: {student[7]}",
                    f"Supervisor: {student[8]}",
                    f"Registration Date: {student[9] if student[9] else 'N/A'}",
                    f"Title: {student[13] if student[13] else 'N/A'}",
                    f"Publications: {student[14] if student[14] else 'N/A'}"
                ]

                for field in fields:
                    label = ttk.Label(
                        student_frame,
                        text=field,
                        font=("Inter", 11),
                        wraplength=600,
                        style="TLabel"
                    )
                    label.pack(fill="x", padx=10, pady=2)  # Remove anchor="w" to allow centering

        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Error loading student details: {e}", parent=self.root)
            self.show_login()
            return

        # Navigation buttons
        buttons = [
            ("View Profile", self.show_profile),
            ("View Synopsis", self.show_synopsis),
            ("View Presentations", self.show_presentations),
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

        # Log Out button with Danger style to match AdminUI's action buttons
        logout_btn = ttk.Button(
            card_frame,
            text="Log Out",
            style="Danger.TButton",  # Changed to Danger.TButton for color
            command=self.show_login
        )
        logout_btn.pack(pady=10, padx=20, fill="x", ipady=5)
        self.button_bind(logout_btn)

        # Scroll bindings
        canvas.bind_all("<MouseWheel>", lambda event: canvas.yview_scroll(int(-1 * (event.delta / 120)), "units"))
        canvas.bind_all("<Button-4>", lambda event: canvas.yview_scroll(-1, "units"))
        canvas.bind_all("<Button-5>", lambda event: canvas.yview_scroll(1, "units"))

        card_frame.update_idletasks()
        canvas.configure(scrollregion=canvas.bbox("all"))

    def show_profile(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        card_frame, canvas = self.create_scrollable_frame(self.root)
        card_frame.configure(padding=30)

        ttk.Label(
            card_frame,
            text="Student Profile",
            style="Heading.TLabel"
        ).pack(pady=20)

        try:
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM students WHERE id = ?", (self.student_id,))
                student = cursor.fetchone()
                if not student:
                    messagebox.showerror("Error", "Student not found.", parent=self.root)
                    self.show_student_dashboard()
                    return

                # Create a frame for student details with a border
                student_frame = ttk.Frame(card_frame, style="Card.TFrame", borderwidth=1, relief="solid")
                student_frame.pack(fill="x", padx=20, pady=10, ipady=5)

                # Calculate batch display with extension
                batch_from = student[2] if student[2] else None
                batch_to = student[3] if student[3] else None
                original_batch_to = student[4] if student[4] else None
                batch_display = f"{batch_from}-{batch_to}" if batch_from and batch_to else "N/A"
                if batch_from and batch_to and original_batch_to:
                    try:
                        batch_to_int = int(batch_to)
                        original_batch_to_int = int(original_batch_to)
                        extension_years = batch_to_int - original_batch_to_int
                        if extension_years > 0:
                            batch_display += f" (Extended by {extension_years} year{'s' if extension_years != 1 else ''})"
                    except ValueError:
                        pass

                # Display student details in a vertical layout
                fields = [
                    f"ID: {student[0]}",
                    f"Roll No: {student[1]}",
                    f"Batch: {batch_display}",
                    f"Name: {student[5]}",
                    f"Email: {student[6]}",
                    f"DOB: {student[10] if student[10] else 'N/A'}",
                    f"Department: {student[7]}",
                    f"Supervisor: {student[8]}",
                    f"Registration Date: {student[9] if student[9] else 'N/A'}",
                    f"Title: {student[13] if student[13] else 'N/A'}",
                    f"Publications: {student[14] if student[14] else 'N/A'}"
                ]

                for field in fields:
                    label = ttk.Label(
                        student_frame,
                        text=field,
                        font=("Inter", 11),
                        wraplength=600,
                        style="TLabel"
                    )
                    label.pack(fill="x", padx=10, pady=2)  # Remove anchor="w" to allow centering

                details_frame = ttk.Frame(card_frame, style="Card.TFrame")
                details_frame.pack(pady=10, fill="x", padx=20)

                # Picture
                if student[12] and os.path.exists(student[12]):
                    try:
                        image = Image.open(student[12])
                        image = image.resize((150, 150), Image.LANCZOS)
                        image = ImageTk.PhotoImage(image)
                        img_label = ttk.Label(details_frame, image=image, background="#FFFFFF")
                        img_label.image = image
                        img_label.pack(pady=10)
                    except Exception as e:
                        ttk.Label(details_frame, text=f"Unable to load picture: {e}", font=("Inter", 11), style="TLabel").pack(pady=10)
                else:
                    ttk.Label(details_frame, text="Picture not available", font=("Inter", 11), style="TLabel").pack(pady=10)

                # Certificate
                if student[11] and os.path.exists(student[11]):
                    cert_btn = ttk.Button(
                        details_frame,
                        text="View Certificate",
                        style="TButton",
                        command=lambda: webbrowser.open(f"file://{os.path.abspath(student[11])}")
                    )
                    cert_btn.pack(pady=10, padx=20, fill="x", ipady=5)
                    self.button_bind(cert_btn)
                else:
                    ttk.Label(details_frame, text="Certificate not available", font=("Inter", 11), style="TLabel").pack(pady=10)

                # Synopsis
                synopsis = self.get_student_synopsis(self.student_id)
                if synopsis:
                    ttk.Label(details_frame, text="Synopsis:", font=("Inter", 11, "bold"), style="TLabel").pack(pady=5)
                    synopsis_label = f"Title: {synopsis[2]}\nSubmission Date: {synopsis[3]}\nAbstract: {synopsis[4]}"
                    ttk.Label(details_frame, text=synopsis_label, font=("Inter", 11), wraplength=600, style="TLabel").pack(pady=2)
                    if synopsis[5] and os.path.exists(synopsis[5]):
                        synopsis_btn = ttk.Button(
                            details_frame,
                            text=f"View Synopsis PDF ({os.path.basename(synopsis[5])})",
                            style="Danger.TButton",  # Changed to Danger.TButton for color
                            command=lambda: webbrowser.open(f"file://{os.path.abspath(synopsis[5])}")
                        )
                        synopsis_btn.pack(pady=5, padx=20, fill="x", ipady=5)
                        self.button_bind(synopsis_btn)
                    else:
                        ttk.Label(details_frame, text="Synopsis PDF not available", font=("Inter", 11), style="TLabel").pack(pady=2)
                else:
                    ttk.Label(details_frame, text="No synopsis recorded", font=("Inter", 11), style="TLabel").pack(pady=5)

                # Presentations
                presentations = self.get_student_presentations(self.student_id)
                if presentations:
                    ttk.Label(details_frame, text="6-Month Presentations:", font=("Inter", 11, "bold"), style="TLabel").pack(pady=5)
                    for pres in presentations:
                        pres_label = f"Date: {pres[2]}, Progress: {pres[3]}"
                        ttk.Label(details_frame, text=pres_label, font=("Inter", 11), style="TLabel").pack(pady=2)
                        if pres[4] and os.path.exists(pres[4]):
                            pres_btn = ttk.Button(
                                details_frame,
                                text=f"View Presentation ({os.path.basename(pres[4])})",
                                style="Danger.TButton",  # Changed to Danger.TButton for color
                                command=lambda p=pres[4]: webbrowser.open(f"file://{os.path.abspath(p)}")
                            )
                            pres_btn.pack(pady=5, padx=20, fill="x", ipady=5)
                            self.button_bind(pres_btn)
                        else:
                            ttk.Label(details_frame, text="Presentation file not available", font=("Inter", 11), style="TLabel").pack(pady=2)
                else:
                    ttk.Label(details_frame, text="No presentations recorded", font=("Inter", 11), style="TLabel").pack(pady=5)

        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Error loading profile: {e}", parent=self.root)

        back_btn = ttk.Button(
            card_frame,
            text="Back",
            style="TButton",
            command=self.show_student_dashboard
        )
        back_btn.pack(pady=10, padx=20, fill="x", ipady=5)
        self.button_bind(back_btn)

        canvas.bind_all("<MouseWheel>", lambda event: canvas.yview_scroll(int(-1 * (event.delta / 120)), "units"))
        canvas.bind_all("<Button-4>", lambda event: canvas.yview_scroll(-1, "units"))
        canvas.bind_all("<Button-5>", lambda event: canvas.yview_scroll(1, "units"))

        card_frame.update_idletasks()
        canvas.configure(scrollregion=canvas.bbox("all"))

    def show_synopsis(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        card_frame, canvas = self.create_scrollable_frame(self.root)
        card_frame.configure(padding=30)

        ttk.Label(
            card_frame,
            text="Synopsis",
            style="Heading.TLabel"
        ).pack(pady=20)

        synopsis_frame = ttk.Frame(card_frame, style="Card.TFrame")
        synopsis_frame.pack(pady=40, fill="x", padx=20)

        synopsis = self.get_student_synopsis(self.student_id)
        if synopsis:
            ttk.Label(synopsis_frame, text="Synopsis:", font=("Inter", 11, "bold"), style="TLabel").pack(pady=5)
            synopsis_label = f"Title: {synopsis[2]}\nSubmission Date: {synopsis[3]}\nAbstract: {synopsis[4]}"
            ttk.Label(
                synopsis_frame,
                text=synopsis_label,
                font=("Inter", 11),
                wraplength=600,
                style="TLabel"
            ).pack(fill="x", padx=10, pady=5)

            if synopsis[5] and os.path.exists(synopsis[5]):
                synopsis_btn = ttk.Button(
                    synopsis_frame,
                    text=f"View Synopsis PDF ({os.path.basename(synopsis[5])})",
                    style="Danger.TButton",  # Changed to Danger.TButton for color
                    command=lambda: webbrowser.open(f"file://{os.path.abspath(synopsis[5])}")
                )
                synopsis_btn.pack(pady=5, padx=20, fill="x", ipady=5)
                self.button_bind(synopsis_btn)
            else:
                ttk.Label(synopsis_frame, text="Synopsis PDF not available", font=("Inter", 11), style="TLabel").pack(fill="x", padx=10, pady=5)
        else:
            ttk.Label(synopsis_frame, text="No synopsis recorded", font=("Inter", 11), style="TLabel").pack(fill="x", padx=10, pady=5)

        back_btn = ttk.Button(
            card_frame,
            text="Back",
            style="TButton",
            command=self.show_student_dashboard
        )
        back_btn.pack(pady=10, padx=20, fill="x", ipady=5)
        self.button_bind(back_btn)

        canvas.bind_all("<MouseWheel>", lambda event: canvas.yview_scroll(int(-1 * (event.delta / 120)), "units"))
        canvas.bind_all("<Button-4>", lambda event: canvas.yview_scroll(-1, "units"))
        canvas.bind_all("<Button-5>", lambda event: canvas.yview_scroll(1, "units"))

        card_frame.update_idletasks()
        canvas.configure(scrollregion=canvas.bbox("all"))

    def show_presentations(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        card_frame, canvas = self.create_scrollable_frame(self.root)
        card_frame.configure(padding=30)

        ttk.Label(
            card_frame,
            text="6-Month Presentations",
            style="Heading.TLabel"
        ).pack(pady=20)

        presentations_frame = ttk.Frame(card_frame, style="Card.TFrame")
        presentations_frame.pack(pady=10, fill="x", padx=20)

        presentations = self.get_student_presentations(self.student_id)
        if presentations:
            ttk.Label(presentations_frame, text="Presentations:", font=("Inter", 11, "bold"), style="TLabel").pack(pady=5)
            for pres in presentations:
                pres_label = f"Date: {pres[2]}, Progress: {pres[3]}"
                ttk.Label(presentations_frame, text=pres_label, font=("Inter", 11), style="TLabel").pack(fill="x", padx=10, pady=2)
                if pres[4] and os.path.exists(pres[4]):
                    pres_btn = ttk.Button(
                        presentations_frame,
                        text=f"View Presentation ({os.path.basename(pres[4])})",
                        style="Danger.TButton",  # Changed to Danger.TButton for color
                        command=lambda p=pres[4]: webbrowser.open(f"file://{os.path.abspath(p)}")
                    )
                    pres_btn.pack(pady=5, padx=20, fill="x", ipady=5)
                    self.button_bind(pres_btn)
                else:
                    ttk.Label(presentations_frame, text="Presentation file not available", font=("Inter", 11), style="TLabel").pack(fill="x", padx=10, pady=2)
        else:
            ttk.Label(presentations_frame, text="No presentations recorded", font=("Inter", 11), style="TLabel").pack(fill="x", padx=10, pady=5)

        back_btn = ttk.Button(
            card_frame,
            text="Back",
            style="TButton",
            command=self.show_student_dashboard
        )
        back_btn.pack(pady=10, padx=20, fill="x", ipady=5)
        self.button_bind(back_btn)

        canvas.bind_all("<MouseWheel>", lambda event: canvas.yview_scroll(int(-1 * (event.delta / 120)), "units"))
        canvas.bind_all("<Button-4>", lambda event: canvas.yview_scroll(-1, "units"))
        canvas.bind_all("<Button-5>", lambda event: canvas.yview_scroll(1, "units"))

        card_frame.update_idletasks()
        canvas.configure(scrollregion=canvas.bbox("all"))