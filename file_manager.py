import os
import shutil
import sqlite3

class FileManager:
    def __init__(self, upload_dir="Uploads"):
        self.upload_dir = upload_dir
        self.cert_dir = os.path.join(upload_dir, "certificates")
        self.pic_dir = os.path.join(upload_dir, "pictures")
        self.present_dir = os.path.join(upload_dir, "presentations")
        self.synopsis_dir = os.path.join(upload_dir, "synopsis")
        os.makedirs(self.cert_dir, exist_ok=True)
        os.makedirs(self.pic_dir, exist_ok=True)
        os.makedirs(self.present_dir, exist_ok=True)
        os.makedirs(self.synopsis_dir, exist_ok=True)
        self.db_file = "phd_management.db"

    def delete_student_files(self, student_id):
        try:
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                # Get student picture path
                cursor.execute("SELECT picture_path FROM students WHERE id = ?", (student_id,))
                picture_path = cursor.fetchone()
                
                # Get all certificate paths
                cursor.execute("SELECT certificate_path FROM certificates WHERE student_id = ?", (student_id,))
                certificate_paths = [row[0] for row in cursor.fetchall()]
                
                # Get presentation paths
                cursor.execute("SELECT presentation_file FROM presentations WHERE student_id = ?", (student_id,))
                presentation_paths = [row[0] for row in cursor.fetchall()]
                
                # Get synopsis path
                cursor.execute("SELECT synopsis_file FROM synopsis WHERE student_id = ?", (student_id,))
                synopsis_path = cursor.fetchone()
                
                # Delete picture file if exists                if picture_path and picture_path[0] and os.path.exists(picture_path[0]):
                os.remove(picture_path[0])
                
                # Delete certificate files if exists
                for cert_path in certificate_paths:
                    if cert_path and os.path.exists(cert_path):
                        os.remove(cert_path[0])
                
                # Delete presentation files if exists
                for presentation_path in presentation_paths:
                    if presentation_path and os.path.exists(presentation_path):
                        os.remove(presentation_path)
                
                # Delete synopsis file if exists
                if synopsis_path and synopsis_path[0] and os.path.exists(synopsis_path[0]):
                    os.remove(synopsis_path[0])
                    
        except sqlite3.Error as e:
            print(f"Error accessing database: {e}")
        except OSError as e:
            print(f"Error deleting files: {e}")