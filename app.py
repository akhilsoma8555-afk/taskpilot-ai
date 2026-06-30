from flask import Flask, render_template, request, redirect, url_for
from gemini_helper import generate_plan
import sqlite3
from datetime import datetime

app = Flask(__name__)

DATABASE = "tasks.db"

def init_db():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS tasks(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT,
    deadline TEXT,
    priority TEXT,
    status TEXT,
    created_at TEXT
)
    """)

    conn.commit()
    conn.close()

init_db()


@app.route("/")
def index():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row

    tasks = conn.execute(
        "SELECT * FROM tasks ORDER BY deadline"
    ).fetchall()
    next_task = None

    for task in tasks:
        if task["status"] == "Pending":
            next_task = task
            break
    pending = conn.execute(
        "SELECT COUNT(*) FROM tasks WHERE status='Pending'"
    ).fetchone()[0]

    completed = conn.execute(
        "SELECT COUNT(*) FROM tasks WHERE status='Completed'"
    ).fetchone()[0]

    total = pending + completed

    progress = 0
    if total > 0:
        progress = int((completed / total) * 100)

    conn.close()

    return render_template(
        "index.html",
        tasks=tasks,
        pending=pending,
        completed=completed,
        progress=progress,
        next_task=next_task
    )


@app.route("/add", methods=["POST"])
def add():

    title = request.form["title"]
    description = request.form["description"]
    deadline = request.form["deadline"]
    priority = request.form["priority"]

    conn = sqlite3.connect(DATABASE)

    created_at = datetime.now().strftime("%d-%m-%Y %H:%M")

    conn.execute(
        """
        INSERT INTO tasks(title,description,deadline,priority,status,created_at)
        VALUES(?,?,?,?,?,?)
        """,
        (
            title,
            description,
            deadline,
            priority,
            "Pending",
            created_at
        ),
    )


    conn.commit()
    conn.close()

    return redirect("/")


@app.route("/complete/<int:id>")
def complete(id):

    conn = sqlite3.connect(DATABASE)

    conn.execute(
        "UPDATE tasks SET status='Completed' WHERE id=?",
        (id,),
    )

    conn.commit()
    conn.close()

    return redirect("/")


@app.route("/delete/<int:id>")
def delete(id):

    conn = sqlite3.connect(DATABASE)

    conn.execute(
        "DELETE FROM tasks WHERE id=?",
        (id,),
    )

    conn.commit()
    conn.close()

    return redirect("/")
@app.route("/ai-plan")
def ai_plan():

    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row

    tasks = conn.execute(
        "SELECT * FROM tasks WHERE status='Pending'"
    ).fetchall()

    # Dashboard statistics
    pending = conn.execute(
        "SELECT COUNT(*) FROM tasks WHERE status='Pending'"
    ).fetchone()[0]

    completed = conn.execute(
        "SELECT COUNT(*) FROM tasks WHERE status='Completed'"
    ).fetchone()[0]

    total = pending + completed

    progress = 0
    if total > 0:
        progress = int((completed / total) * 100)

    conn.close()

    if len(tasks) == 0:
        return render_template(
            "planner.html",
            response="🎉 No pending tasks.",
            progress=progress
        )

    task_list = ""

    for task in tasks:
        task_list += f"""
Title: {task['title']}
Description: {task['description']}
Deadline: {task['deadline']}
Priority: {task['priority']}

"""

    plan = generate_plan(task_list)

    return render_template(
        "planner.html",
        response=plan,
        progress=progress
    )

import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)