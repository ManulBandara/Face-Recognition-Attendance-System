import cv2
import sqlite3
import datetime
import os

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
        path = os.path.join(student_folder, filename)
        students[student_name] = cv2.imread(path, cv2.IMREAD_GRAYSCALE)

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
        print("Failed to grab frame from webcam")
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(
        gray, scaleFactor=1.3, minNeighbors=5)

    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        # -----------------------------
        # MARK ATTENDANCE FOR ALL STUDENTS
        # -----------------------------
        for student_name in students.keys():
            # Get student ID from database
            cur.execute(
                "SELECT student_id FROM students WHERE name=?", (student_name,))
            result = cur.fetchone()
            if result:
                student_id = result[0]
                # Check if attendance already marked for today
                cur.execute(
                    "SELECT * FROM attendance WHERE student_id=? AND date=?", (student_id, today))
                if not cur.fetchone():
                    cur.execute(
                        "INSERT INTO attendance (student_id, date, status) VALUES (?, ?, ?)",
                        (student_id, today, "Present")
                    )
                    conn.commit()
                    print(f"✅ Attendance marked for {student_name}")

        cv2.putText(frame, "Face Detected", (x, y - 10),
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
