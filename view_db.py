import sqlite3

conn = sqlite3.connect("student_tracker.db")
cursor = conn.cursor()

print("STUDENTS TABLE")
cursor.execute("SELECT * FROM students")

for row in cursor.fetchall():
    print(row)

print("\nGRADES TABLE")
cursor.execute("SELECT * FROM grades")

for row in cursor.fetchall():
    print(row)

conn.close()