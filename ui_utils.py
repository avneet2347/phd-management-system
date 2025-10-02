import tkinter as tk
from tkinter import ttk

class UIUtils:
    def setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TFrame", background="#F5F7FA")
        style.configure("TLabel", background="#F5F7FA", foreground="#2D3748", font=("Inter", 12))
        style.configure("TEntry", fieldbackground="#FFFFFF", foreground="#2D3748", font=("Inter", 11), 
                       insertcolor="#00A3B5", borderwidth=1, relief="flat")
        style.configure("TButton", background="#00A3B5", foreground="#FFFFFF", font=("Inter", 11, "bold"), 
                       borderwidth=0, padding=10, relief="flat")
        style.map("TButton",
                  background=[("active", "#008A99")],
                  foreground=[("active", "#FFFFFF")])
        style.configure("Heading.TLabel", font=("Inter", 20, "bold"), foreground="#FF6B6B")
        style.configure("Card.TFrame", background="#FFFFFF", relief="flat")
        style.configure("Danger.TButton", background="#FF6B6B", foreground="#FFFFFF", font=("Inter", 11, "bold"), 
                       borderwidth=0, padding=10, relief="flat")
        style.map("Danger.TButton",
                  background=[("active", "#FF8787")],
                  foreground=[("active", "#FFFFFF")])
        style.configure("Treeview", background="#FFFFFF", foreground="#2D3748", fieldbackground="#FFFFFF", 
                       font=("Inter", 10), rowheight=30)
        style.configure("Treeview.Heading", background="#00A3B5", foreground="#FFFFFF", font=("Inter", 10, "bold"))
        style.map("Treeview",
                  background=[("selected", "#E6F0FA")],
                  foreground=[("selected", "#2D3748")])
        style.configure("TextButton.TButton", background="#F5F7FA", foreground="#2D3748", font=("Inter", 11), 
                       borderwidth=0, padding=5, relief="flat")
        style.map("TextButton.TButton",
                  foreground=[("active", "#00A3B5")])
        style.configure("Shadow.TFrame", background="#F5F7FA")
        style.configure("Project.TLabel", background="#F5F7FA", foreground="#000000", font=("Inter", 12, "bold"))
        style.configure("Author.TLabel", background="#F5F7FA", foreground="#000000", font=("Inter", 10))
        self.button_bind = lambda btn: (
            btn.bind("<Enter>", lambda e: btn.configure(style="Danger.TButton" if btn["style"] == "Danger.TButton" else "TextButton.TButton" if btn["style"] == "TextButton.TButton" else "TButton")),
            btn.bind("<Leave>", lambda e: btn.configure(style=btn["style"]))
        )

    def create_scrollable_frame(self, parent, include_buttons=True):
        top_bar = ttk.Frame(parent, style="Shadow.TFrame")
        top_bar.pack(fill="x", padx=20, pady=(10, 0))

        if include_buttons:
            left_frame = ttk.Frame(top_bar, style="Shadow.TFrame")
            left_frame.pack(side="left", padx=10)
            project_label = ttk.Label(left_frame, text="PhD Management System", style="Project.TLabel")
            project_label.pack(anchor="w", pady=2)
            author_label = ttk.Label(left_frame, text="Avneet Kaur, B.Tech (CSE), 6th Sem", style="Author.TLabel")
            author_label.pack(anchor="w", pady=2)

            home_btn = ttk.Button(top_bar, text="Home", style="TextButton.TButton", 
                                 command=self.show_admin_dashboard if self.is_admin else self.show_student_dashboard)
            home_btn.pack(side="right", pady=2, padx=10)
            self.button_bind(home_btn)

            logout_btn = ttk.Button(top_bar, text="Log Out", style="TextButton.TButton", 
                                   command=self.show_login)
            logout_btn.pack(side="right", pady=2, padx=10)
            self.button_bind(logout_btn)

        container = ttk.Frame(parent, style="Shadow.TFrame")
        container.pack(expand=True, fill="both", padx=20, pady=20)
        canvas = tk.Canvas(container, bg="#F5F7FA", highlightthickness=0)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas, style="Card.TFrame")
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        window = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        
        def configure_canvas(event):
            canvas_width = event.width
            frame_width = scrollable_frame.winfo_reqwidth()
            canvas.itemconfig(window, width=max(canvas_width, frame_width))
        
        canvas.bind("<Configure>", configure_canvas)
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True, padx=(10, 0))
        scrollbar.pack(side="right", fill="y")
        
        scrollable_frame.update_idletasks()
        canvas.configure(scrollregion=canvas.bbox("all"))
        
        return scrollable_frame, canvas
