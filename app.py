from flask import Flask, render_template, request
from db import get_connection

app = Flask(__name__)


@app.route("/")
def home():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM students")
    total_students = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM grades")
    total_subjects = cursor.fetchone()[0]

    cursor.execute("SELECT AVG(marks) FROM grades")
    avg_result = cursor.fetchone()[0]

    class_average = round(avg_result, 2) if avg_result else 0

    cursor.execute("""
        SELECT s.name
        FROM students s
        JOIN grades g
        ON s.roll_number = g.roll_number
        GROUP BY s.roll_number
        ORDER BY AVG(g.marks) DESC
        LIMIT 1
    """)

    topper = cursor.fetchone()
    topper_name = topper[0] if topper else "N/A"

    # Chart Data
    cursor.execute("""
        SELECT s.name,
               ROUND(AVG(g.marks),2)
        FROM students s
        JOIN grades g
        ON s.roll_number = g.roll_number
        GROUP BY s.roll_number
        ORDER BY AVG(g.marks) DESC
    """)

    chart_data = cursor.fetchall()

    names = [row[0] for row in chart_data]
    averages = [row[1] for row in chart_data]

    conn.close()

    return render_template(
        "home.html",
        total_students=total_students,
        total_subjects=total_subjects,
        class_average=class_average,
        topper_name=topper_name,
        names=names,
        averages=averages
    )

@app.route("/add_student", methods=["GET", "POST"])
def add_student():

    if request.method == "POST":

        name = request.form["name"]
        roll = request.form["roll"]

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM students WHERE roll_number=?",
            (roll,)
        )

        if cursor.fetchone():
            conn.close()
            return "Roll Number already exists!"

        cursor.execute(
            "INSERT INTO students (roll_number, name) VALUES (?, ?)",
            (roll, name)
        )

        conn.commit()
        conn.close()

        return render_template(
            "success.html",
            message=f"Student {name} added successfully!"
        )

    return render_template("add_student.html")


@app.route("/view_students")
@app.route("/view_students")
def view_students():

    search = request.args.get("search", "")

    conn = get_connection()
    cursor = conn.cursor()

    if search:

        cursor.execute("""
            SELECT
                s.roll_number,
                s.name,
                g.id,
                g.subject,
                g.marks
            FROM students s
            LEFT JOIN grades g
            ON s.roll_number = g.roll_number
            WHERE s.roll_number LIKE ?
               OR s.name LIKE ?
            ORDER BY s.roll_number
        """, (f"%{search}%", f"%{search}%"))

    else:

        cursor.execute("""
            SELECT
                s.roll_number,
                s.name,
                g.id,
                g.subject,
                g.marks
            FROM students s
            LEFT JOIN grades g
            ON s.roll_number = g.roll_number
            ORDER BY s.roll_number
        """)

    students = cursor.fetchall()

    conn.close()

    return render_template(
        "view_students.html",
        students=students,
        search=search
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
            "SELECT * FROM students WHERE roll_number=?",
            (roll,)
        )

        if not cursor.fetchone():
            conn.close()
            return "Student not found!"

        cursor.execute(
            """
            INSERT INTO grades
            (roll_number, subject, marks)
            VALUES (?, ?, ?)
            """,
            (roll, subject, marks)
        )

        conn.commit()
        conn.close()

        return render_template(
            "success.html",
            message=f"Grade added successfully for Roll Number {roll}!"
        )

    return render_template("add_grades.html")


@app.route("/class_average")
def class_average():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT s.roll_number,
               s.name,
               AVG(g.marks) AS average_marks
        FROM students s
        LEFT JOIN grades g
        ON s.roll_number = g.roll_number
        GROUP BY s.roll_number, s.name
    """)

    averages = cursor.fetchall()

    conn.close()

    return render_template(
        "class_average.html",
        averages=averages
    )

@app.route("/topper")
def topper():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            s.roll_number,
            s.name,
            AVG(g.marks) AS avg_marks
        FROM students s
        JOIN grades g
        ON s.roll_number = g.roll_number
        GROUP BY s.roll_number, s.name
        HAVING avg_marks = (
            SELECT MAX(student_avg)
            FROM (
                SELECT AVG(marks) AS student_avg
                FROM grades
                GROUP BY roll_number
            )
        )
    """)

    toppers = cursor.fetchall()

    conn.close()

    if not toppers:
        return "No grades available."

    return render_template(
        "topper.html",
        toppers=toppers,
        average=round(toppers[0][2], 2)
    )


@app.route("/delete_grade/<int:grade_id>", methods=["GET", "POST"])
def delete_grade(grade_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT roll_number, subject, marks
        FROM grades
        WHERE id = ?
        """,
        (grade_id,)
    )

    grade = cursor.fetchone()

    if not grade:
        conn.close()
        return "Grade not found."

    roll = grade[0]

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM grades
        WHERE roll_number = ?
        """,
        (roll,)
    )

    count = cursor.fetchone()[0]

    if request.method == "POST":

        if count == 1:

            cursor.execute(
                "DELETE FROM grades WHERE id = ?",
                (grade_id,)
            )

            cursor.execute(
                "DELETE FROM students WHERE roll_number = ?",
                (roll,)
            )

            message = "Student deleted successfully!"

        else:

            cursor.execute(
                "DELETE FROM grades WHERE id = ?",
                (grade_id,)
            )

            message = "Subject deleted successfully!"

        conn.commit()
        conn.close()

        return render_template(
            "success.html",
            message=message
        )

    conn.close()

    return render_template(
        "confirm_delete_grade.html",
        grade=grade,
        count=count
    )


@app.route("/student_report/<roll>")
def student_report(roll):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM students WHERE roll_number = ?",
        (roll,)
    )

    student = cursor.fetchone()

    cursor.execute(
        """
        SELECT subject, marks
        FROM grades
        WHERE roll_number = ?
        """,
        (roll,)
    )

    grades = cursor.fetchall()

    cursor.execute(
        """
        SELECT AVG(marks)
        FROM grades
        WHERE roll_number = ?
        """,
        (roll,)
    )

    average = cursor.fetchone()[0]

    conn.close()

    return render_template(
        "student_report.html",
        student=student,
        grades=grades,
        average=round(average, 2) if average else 0
    )


@app.route("/edit_grade/<int:grade_id>", methods=["GET", "POST"])
def edit_grade(grade_id):

    conn = get_connection()
    cursor = conn.cursor()

    if request.method == "POST":

        subject = request.form["subject"]
        marks = float(request.form["marks"])

        cursor.execute(
            """
            UPDATE grades
            SET subject = ?,
                marks = ?
            WHERE id = ?
            """,
            (subject, marks, grade_id)
        )

        conn.commit()
        conn.close()

        return render_template(
            "success.html",
            message="Grade updated successfully!"
        )

    cursor.execute(
        """
        SELECT id,
               roll_number,
               subject,
               marks
        FROM grades
        WHERE id = ?
        """,
        (grade_id,)
    )

    grade = cursor.fetchone()

    conn.close()

    return render_template(
        "edit_grade.html",
        grade=grade
    )


@app.route("/no_grade_record")
def no_grade_record():

    return render_template(
        "no_grade_record.html"
    )


if __name__ == "__main__":
    app.run(debug=True)