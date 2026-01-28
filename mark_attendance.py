import cv2
import sqlite3
import datetime
import os
import numpy as np

# -----------------------------
# CONNECT TO DATABASE
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
        student_name = os.path.splitext(
            filename)[0]  # filename without extension
        img_path = os.path.join(student_folder, filename)
        img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
        students[student_name] = img

print(f"Loaded {len(students)} students from {student_folder}")

# -----------------------------
# HAAR CASCADE FACE DETECTOR
# -----------------------------
face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# -----------------------------
# START WEBCAM
# -----------------------------
cap = cv2.VideoCapture(0)
today = str(datetime.date.today())
print("Press 'q' to quit the attendance system")

while True:
    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame")
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(
        gray, scaleFactor=1.3, minNeighbors=5)

    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        face_img = gray[y:y+h, x:x+w]  # crop detected face

        for student_name, student_img in students.items():
            # Resize student photo to detected face size
            student_resized = cv2.resize(student_img, (w, h))

            # Compare using template matching
            res = cv2.matchTemplate(
                face_img, student_resized, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, _ = cv2.minMaxLoc(res)

            if max_val > 0.6:  # threshold, adjust if needed
                # Get student ID from database
                cur.execute(
                    "SELECT student_id FROM students WHERE name=?", (student_name,))
                result = cur.fetchone()
                if result:
                    student_id = result[0]
                    # Check if already marked
                    cur.execute(
                        "SELECT * FROM attendance WHERE student_id=? AND date=?", (student_id, today))
                    if not cur.fetchone():
                        cur.execute(
                            "INSERT INTO attendance (student_id, date, status) VALUES (?, ?, ?)",
                            (student_id, today, "Present")
                        )
                        conn.commit()
                        print(f"✅ Attendance marked for {student_name}")
                break  # stop checking other students for this face

        cv2.putText(frame, "Face Detected", (x, y-10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

    cv2.imshow("Attendance System", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# -----------------------------
# CLEAN UP
# -----------------------------
cap.release()
cv2.destroyAllWindows()
cur.close()
conn.close()
print("Attendance system closed")
