import sqlite3

conn = sqlite3.connect("attendance.db")
cur = conn.cursor()

total_days = 30  # Adjust as per total lectures

cur.execute("SELECT student_id, name FROM students")
students = cur.fetchall()

for student_id, name in students:
    cur.execute(
        "SELECT COUNT(*) FROM attendance WHERE student_id=?", (student_id,))
    present_days = cur.fetchone()[0]
    attendance_percent = (present_days / total_days) * 100
    print(f"{name}: {attendance_percent:.2f}% attendance")
    if attendance_percent < 80:
        print(f"⚠️ Warning: {name} attendance is below 80%!")

cur.close()
conn.close()
