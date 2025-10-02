CREATE TABLE students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    roll_number TEXT NOT NULL UNIQUE,
    batch_from INTEGER,
    batch_to INTEGER,
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    department TEXT NOT NULL,
    supervisor TEXT NOT NULL,
    registration_date TEXT NOT NULL,
    dob TEXT,
    certificate_path TEXT,
    picture_path TEXT,
    title TEXT NOT NULL,
    publications TEXT NOT NULL
);

CREATE TABLE synopsis (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    synopsis_title TEXT NOT NULL,
    submission_date TEXT NOT NULL,
    abstract TEXT NOT NULL,
    synopsis_file TEXT,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
);

CREATE TABLE presentations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    presentation_date TEXT NOT NULL,
    progress_notes TEXT NOT NULL,
    presentation_file TEXT,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
);
