# phd-management-system
# PhD Management System

![PhD Management System Banner](https://via.placeholder.com/800x200/00A3B5/FFFFFF?text=PhD+Management+System)  
*A Desktop Application for Managing PhD Student Records, Presentations, and Progress Tracking*

## Overview

The **PhD Management System** is a user-friendly desktop application built with Python and Tkinter, designed to streamline the administration and tracking of PhD students' academic progress. It allows administrators to manage student details, handle file uploads (e.g., certificates, pictures, presentations, and synopsis PDFs), and track key milestones like synopsis submissions and 6-monthly presentations. Students can securely log in to view their own profiles and documents.

This system addresses common challenges in academic departments, such as manual record-keeping, file organization, and progress monitoring. It uses SQLite for lightweight, local data storage and supports features like batch extensions for extended PhD durations.

**Key Goals:**
- Centralized management of student data.
- Secure access for admins and students.
- Easy file handling and viewing.
- Export capabilities for reporting.

## Features

### Admin Features
- **Student Management**: Add, view, update, delete, and search students by roll number, name, email, or other fields.
- **File Uploads**: Upload and manage student pictures, certificates, presentation files (e.g., PPT/PDF), and synopsis PDFs.
- **Progress Tracking**: Record and view 6-monthly presentations with progress notes and dates.
- **Synopsis Management**: Track synopsis submissions, including titles, abstracts, and files.
- **Batch Extensions**: Automatically calculate and display extensions based on original and current batch years.
- **Data Export**: Export student data to CSV for easy reporting or backups.
- **Search & View Details**: Advanced search with preview of images, certificates, and linked documents.

### Student Features
- **Secure Login**: Log in using email and date of birth (DOB).
- **Profile Viewing**: Access personal details, including roll number, batch, thesis title, publications, and supervisor.
- **Document Access**: View synopsis details and download/view presentation files.
- **Dashboard Navigation**: Simple interface to switch between profile, synopsis, and presentations.

### General Features
- **Responsive UI**: Scrollable frames with custom styling for a modern look (using ttk themes).
- **File Organization**: Automatic directory creation for uploads (e.g., `Uploads/certificates/`, `Uploads/presentations/`).
- **Error Handling**: Robust SQLite operations with migration support for schema updates.
- **Cross-Platform**: Runs on Windows, macOS, and Linux (Python 3.x required).

## Tech Stack

- **Backend**: Python 3.12+
- **Database**: SQLite (file-based: `phd_management.db`)
- **Frontend**: Tkinter (with ttk for styling) + PIL (Pillow) for image handling
- **File Management**: Built-in `os`, `shutil`, and `webbrowser` for opening files
- **Other Libraries**: `datetime` for date handling, `csv` for exports
- **No External Dependencies**: Fully self-contained (no pip installs needed beyond standard libraries; Pillow is optional for images).

## Installation

1. **Clone the Repository**:
   ```
   git clone https://github.com/yourusername/phd-management-system.git
   cd phd-management-system
   ```

2. **Install Python Dependencies** (if needed for images):
   - The core app runs on standard Python libraries.
   - For image viewing: `pip install Pillow` (PIL).

3. **Run the Application**:
   ```
   python main.py
   ```
   - The database (`phd_management.db`) and uploads folder (`Uploads/`) will be created automatically on first run.

4. **Initial Setup**:
   - Admin login: Username `admin`, Password `admin`.
   - Add students via the admin dashboard to test student logins.

## Usage

### Logging In
- **Admin**: Use `admin` / `admin` to access full management tools.
- **Student**: Use email as username and DOB (format: DD-MM-YYYY) as password.

### Admin Workflow
1. Log in as admin.
2. Use the dashboard to add a new student (fill form, upload files).
3. Search or view students to update details or add presentations/synopsis.
4. Export data to CSV for records.

### Student Workflow
1. Log in with email and DOB.
2. View dashboard for profile summary.
3. Navigate to "View Synopsis" or "View Presentations" to access documents (opens in default viewer/browser).

### File Handling
- All uploads are stored in `Uploads/` subfolders.
- Deleting a student cascades to remove related files and DB entries.

## Screenshots

### Login Screen
![Login Screen](screenshots/login.png)  
*(Placeholder: Add actual screenshot here)*

### Admin Dashboard
![Admin Dashboard](screenshots/admin_dashboard.png)  
*(Placeholder: Add actual screenshot here)*

### Student Profile
![Student Profile](screenshots/student_profile.png)  
*(Placeholder: Add actual screenshot here)*

### Add Student Form
![Add Student](screenshots/add_student.png)  
*(Placeholder: Add actual screenshot here)*

*(Tip: Take screenshots using tools like Snipping Tool or OBS Studio and add them to a `screenshots/` folder.)*

## Database Schema

The app uses SQLite with the following tables (auto-migrated on startup):

- **students**: Core student info (id, roll_number, batch_from/to, name, email, etc.).
- **synopsis**: Synopsis details (title, submission_date, abstract, file path).
- **presentations**: Presentation records (date, progress_notes, file path).
- **certificates**: Certificate uploads (title, path).

See `phd_management.sql` for full schema.

## Potential Improvements
- Add email notifications for deadlines.
- Integrate cloud storage (e.g., Google Drive) for files.
- Web version using Flask/Django.
- Advanced reporting with charts (e.g., progress timelines).

## Contributing

Contributions are welcome! Please follow these steps:
1. Fork the repository.
2. Create a feature branch (`git checkout -b feature/amazing-feature`).
3. Commit changes (`git commit -m 'Add amazing feature'`).
4. Push to the branch (`git push origin feature/amazing-feature`).
5. Open a Pull Request.

Report issues or suggest features via GitHub Issues.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Developed by **Avneet Kaur**, B.Tech (CSE), 6th Semester.
- Built with love for academic management! 🚀

---

*Last Updated: April 28, 2025*  
