import sqlite3
import os
import shutil

# Connect to DB
conn = sqlite3.connect("attendance.db")
cur = conn.cursor()

# 1. Add student info
name = input("Enter student name: ")
email = input("Enter student email: ")
reg_no = input("Enter registration number: ")

cur.execute("INSERT INTO students (name,email,reg_no) VALUES (?,?,?)",
            (name, email, reg_no))
student_id = cur.lastrowid
conn.commit()

# 2. Upload student photo
photo_name = input(
    "Enter student photo filename (in student_images folder, e.g., student1.jpg): ")
source_path = os.path.join("student_images", photo_name)

# Optional: copy photo to a separate folder with student ID as name
dest_path = os.path.join("student_images", f"{student_id}.jpg")
shutil.copyfile(source_path, dest_path)

print(f"✅ Student {name} registered with ID {student_id}!")
cur.close()
conn.close()
