from flask import Flask, render_template, request, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.secret_key = "my_secret_key"


# Database Configuration----------------

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///tasks.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)


# File Upload Folder---------------

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER



# Database Model (Table)----------------

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    assignee_name = db.Column(db.String(200))
    assigned_by = db.Column(db.String(200))
    due_date = db.Column(db.String(50))
    pdf_file = db.Column(db.String(200))


# Create DB table
with app.app_context():
    db.create_all()



# Home Page---------------

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        session["assignee_name"] = request.form.get("assignee_name")
        session["assigned_by"] = request.form.get("assigned_by")
        session["due_date"] = request.form.get("due_date")

        pdf = request.files.get("task_pdf")
        filename = None

        if pdf:
            # Validate file type
            if not pdf.filename.lower().endswith(".pdf"):
                return "Error: Only PDF files are allowed!", 400

            # Validate file size (5–10 MB)
            pdf.seek(0, os.SEEK_END)
            file_size = pdf.tell()
            pdf.seek(0)

            min_size = 5 * 1024 * 1024  # 5 MB
            max_size = 10 * 1024 * 1024 # 10 MB

            if file_size < min_size or file_size > max_size:
                return "Error: File size must be between 5 MB and 10 MB!", 400

            filename = pdf.filename
            pdf.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
            session["pdf_file"] = filename

        new_task = Task(
            assignee_name=session["assignee_name"],
            assigned_by=session["assigned_by"],
            due_date=session["due_date"],
            pdf_file=filename,
        )
        db.session.add(new_task)
        db.session.commit()

        return redirect(url_for("success"))

    return render_template("index.html")


# Success Page---------------

@app.route("/success")
def success():
    return "Task saved successfully in SQLite + Session!"



# API To See All Tasks---------------

@app.route("/all")
def all_tasks():
    tasks = Task.query.all()
    return {
        "tasks": [
            {
                "id": t.id,
                "assignee_name": t.assignee_name,
                "assigned_by": t.assigned_by,
                "due_date": t.due_date,
                "pdf_file": t.pdf_file,
            }
            for t in tasks
        ]
    }


if __name__ == "__main__":
    app.run(debug=True)