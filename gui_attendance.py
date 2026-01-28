import tkinter as tk
from tkinter import ttk, messagebox
import cv2
import sqlite3
import datetime
import os
import numpy as np

# -----------------------------
# DATABASE
# -----------------------------
conn = sqlite3.connect("attendance.db")
cur = conn.cursor()

# -----------------------------
# LOAD STUDENT PHOTOS
# -----------------------------
student_folder = "student_images"
students = {}

for filename in os.listdir(student_folder):
    if filename.lower().endswith((".jpg", ".png")):
        student_name = os.path.splitext(filename)[0]
        img_path = os.path.join(student_folder, filename)
        img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
        students[student_name] = img

print(f"Loaded {len(students)} students")

# -----------------------------
# FACE CASCADE
# -----------------------------
face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
today = str(datetime.date.today())

# -----------------------------
# GUI
# -----------------------------
root = tk.Tk()
root.title("Face Recognition Attendance")
root.geometry("700x500")

# Title
tk.Label(root, text="Face Recognition Attendance System",
         font=("Arial", 18)).pack(pady=10)

# Button to mark attendance


def mark_attendance():
    cap = cv2.VideoCapture(0)
    messagebox.showinfo("Info", "Press 'q' in webcam window to quit")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(
            gray, scaleFactor=1.3, minNeighbors=5)

        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            face_img = gray[y:y+h, x:x+w]

            for student_name, student_img in students.items():
                student_resized = cv2.resize(student_img, (w, h))
                res = cv2.matchTemplate(
                    face_img, student_resized, cv2.TM_CCOEFF_NORMED)
                _, max_val, _, _ = cv2.minMaxLoc(res)
                if max_val > 0.6:
                    cur.execute(
                        "SELECT student_id FROM students WHERE name=?", (student_name,))
                    result = cur.fetchone()
                    if result:
                        student_id = result[0]
                        cur.execute(
                            "SELECT * FROM attendance WHERE student_id=? AND date=?", (student_id, today))
                        if not cur.fetchone():
                            cur.execute("INSERT INTO attendance (student_id,date,status) VALUES (?,?,?)",
                                        (student_id, today, "Present"))
                            conn.commit()
                            print(f"✅ Attendance marked for {student_name}")
                    break

        cv2.imshow("Mark Attendance", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    refresh_table()


tk.Button(root, text="Mark Attendance", font=(
    "Arial", 14), command=mark_attendance).pack(pady=10)

# Table to show attendance
tree = ttk.Treeview(root, columns=("Name", "Status"), show="headings")
tree.heading("Name", text="Student Name")
tree.heading("Status", text="Status")
tree.pack(fill="both", expand=True, pady=10)


def refresh_table():
    for row in tree.get_children():
        tree.delete(row)
    cur.execute("SELECT s.name, a.status FROM students s LEFT JOIN attendance a ON s.student_id = a.student_id AND a.date=? ORDER BY s.name", (today,))
    rows = cur.fetchall()
    for name, status in rows:
        status = status if status else "Absent"
        tree.insert("", "end", values=(name, status))


refresh_table()

root.mainloop()
cur.close()
conn.close()
