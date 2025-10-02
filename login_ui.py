import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

class LoginUI:
    def show_login(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        card_frame, canvas = self.create_scrollable_frame(self.root, include_buttons=False)
        card_frame.configure(padding=30)

        ttk.Label(card_frame, text="PhD Management System", style="Heading.TLabel").pack(pady=20)
        ttk.Label(card_frame, text="Username").pack(anchor="w", padx=20, pady=(10, 0))
        username_entry = ttk.Entry(card_frame)
        username_entry.pack(pady=10, padx=20, fill="x", ipady=5)
        ttk.Label(card_frame, text="Password").pack(anchor="w", padx=20, pady=(10, 0))
        password_entry = ttk.Entry(card_frame, show="*")
        password_entry.pack(pady=10, padx=20, fill="x", ipady=5)

        def try_login():
            if self.login(username_entry.get(), password_entry.get()):
                if self.is_admin:
                    self.show_admin_dashboard()
                else:
                    self.show_student_dashboard()
            else:
                messagebox.showerror("Error", "Invalid credentials.", parent=self.root)

        login_btn = ttk.Button(card_frame, text="Login", style="Danger.TButton", command=try_login)
        login_btn.pack(pady=20, padx=20, fill="x", ipady=5)
        self.button_bind(login_btn)

        canvas.bind_all("<MouseWheel>", lambda event: canvas.yview_scroll(int(-1 * (event.delta / 120)), "units"))
        canvas.bind_all("<Button-4>", lambda event: canvas.yview_scroll(-1, "units"))
        canvas.bind_all("<Button-5>", lambda event: canvas.yview_scroll(1, "units"))
        
        card_frame.update_idletasks()
        canvas.configure(scrollregion=canvas.bbox("all"))
