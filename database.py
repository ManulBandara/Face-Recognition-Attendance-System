import sqlite3

conn = sqlite3.connect("attendance.db")
cur = conn.cursor()

# Students table
cur.execute("""
CREATE TABLE IF NOT EXISTS students (
    student_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    email TEXT,
    reg_no TEXT
)
""")

# Face encodings table
cur.execute("""
CREATE TABLE IF NOT EXISTS face_data (
    student_id INTEGER,
    encoding BLOB
)
""")

# Attendance table
cur.execute("""
CREATE TABLE IF NOT EXISTS attendance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER,
    date TEXT,
    status TEXT
)
""")

conn.commit()
conn.close()
print("Database and tables created successfully!")
