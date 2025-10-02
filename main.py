import tkinter as tk
from db_manager import DatabaseManager
from ui_utils import UIUtils
from login_ui import LoginUI
from admin_ui import AdminUI
from student_ui import StudentUI
from file_manager import FileManager

class PhDManagement(DatabaseManager, UIUtils, LoginUI, AdminUI, FileManager):
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("PhD Management System")
        self.root.geometry("900x700")
        self.root.configure(bg="#F5F7FA")
        self.root.deiconify()  # Ensure window is visible
        self.root.lift()  # Bring window to foreground
        self.db_file = "phd_management.db"
        self.upload_dir = "Uploads"
        self.current_user = None
        self.is_admin = False
        super().__init__()
        self.setup_styles()
        self.show_login()

    def show_student_dashboard(self):
        # Create a StudentUI instance with the current user's ID
        student_ui = StudentUI(self.root, self.db_file, FileManager(self.upload_dir), self.show_login, self.current_user)
        student_ui.show_student_dashboard()

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = PhDManagement()
    app.run()