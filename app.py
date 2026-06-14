from flask import Flask, render_template, request
from db import get_connection

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/add_student", methods=["GET", "POST"])
def add_student():

    if request.method == "POST":

        name = request.form["name"]
        roll = request.form["roll"]

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM students WHERE roll_number=%s",
            (roll,)
        )

        if cursor.fetchone():
            conn.close()
            return "Roll Number already exists!"

        cursor.execute(
            "INSERT INTO students (roll_number, name) VALUES (%s, %s)",
            (roll, name)
        )

        conn.commit()
        conn.close()

        return f"Student {name} added successfully!"

    return render_template("add_student.html")


@app.route("/view_students")
def view_students():

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        "SELECT * FROM students"
    )

    students = cursor.fetchall()

    conn.close()

    return render_template(
        "view_students.html",
        students=students
    )


@app.route("/add_grades", methods=["GET", "POST"])
def add_grades():

    if request.method == "POST":

        roll = request.form["roll"]
        subject = request.form["subject"]
        marks = float(request.form["marks"])

        if marks < 0 or marks > 100:
            return "Marks must be between 0 and 100."

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM students WHERE roll_number=%s",
            (roll,)
        )

        if not cursor.fetchone():
            conn.close()
            return "Student not found!"

        cursor.execute(
            """
            INSERT INTO grades
            (roll_number, subject, marks)
            VALUES (%s, %s, %s)
            """,
            (roll, subject, marks)
        )

        conn.commit()
        conn.close()

        return "Grade added successfully!"

    return render_template("add_grades.html")


@app.route("/class_average")
def class_average():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT AVG(marks) FROM grades"
    )

    result = cursor.fetchone()

    conn.close()

    average = round(result[0], 2) if result[0] else 0

    return render_template(
        "class_average.html",
        average=average
    )


@app.route("/topper")
def topper():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT s.roll_number,
               s.name,
               AVG(g.marks) AS avg_marks
        FROM students s
        JOIN grades g
        ON s.roll_number = g.roll_number
        GROUP BY s.roll_number, s.name
        ORDER BY avg_marks DESC
        LIMIT 1
    """)

    topper = cursor.fetchone()

    conn.close()

    if not topper:
        return "No grades available."

    return render_template(
        "topper.html",
        name=topper[1],
        roll=topper[0],
        average=round(topper[2], 2)
    )


if __name__ == "__main__":
    app.run(debug=True)