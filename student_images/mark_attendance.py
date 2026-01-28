import cv2
import sqlite3
import datetime
import os

# Connect to DB
conn = sqlite3.connect("attendance.db")
cur = conn.cursor()

# Load student IDs and images
student_folder = "student_images"
students = {}
for filename in os.listdir(student_folder):
    if filename.endswith(".jpg"):
        student_id = int(os.path.splitext(filename)[0])
        students[student_id] = cv2.imread(os.path.join(
            student_folder, filename), cv2.IMREAD_GRAYSCALE)

# Haar cascade for face detection
face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

cap = cv2.VideoCapture(0)
today = str(datetime.date.today())

print("Press 'q' to quit the attendance system")

while True:
    ret, frame = cap.read()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(
        gray, scaleFactor=1.3, minNeighbors=5)

    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
        # For beginners, we just mark all detected faces as "Present"
        for student_id in students.keys():
            cur.execute(
                "SELECT * FROM attendance WHERE student_id=? AND date=?", (student_id, today))
            if not cur.fetchone():
                cur.execute("INSERT INTO attendance (student_id, date, status) VALUES (?,?,?)",
                            (student_id, today, "Present"))
                conn.commit()
                print(f"✅ Attendance marked for student ID {student_id}")
        cv2.putText(frame, "Detected", (x, y-10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

    cv2.imshow("Attendance System", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
cur.close()
conn.close()
