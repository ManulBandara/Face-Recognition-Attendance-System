import sqlite3
import face_recognition
import pickle
import os

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
image_path = os.path.join("student_images", photo_name)
image = face_recognition.load_image_file(image_path)
face_encoding = face_recognition.face_encodings(image)[0]

# 3. Convert encoding to binary and save
encoded_face = pickle.dumps(face_encoding)
cur.execute("INSERT INTO face_data (student_id, encoding) VALUES (?,?)",
            (student_id, encoded_face))
conn.commit()

cur.close()
conn.close()
print(f"✅ Student {name} registered successfully!")
