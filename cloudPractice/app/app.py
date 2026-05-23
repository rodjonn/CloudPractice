import os
import time

import mysql.connector
from flask import Flask, redirect, render_template, request

app = Flask(__name__)

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "db"),
    "port": int(os.getenv("DB_PORT", "3306")),
    "user": os.getenv("DB_USER", "todo_user"),
    "password": os.getenv("DB_PASSWORD", "todo_pass"),
    "database": os.getenv("DB_NAME", "todo_db"),
}


def get_db():
    for _ in range(10):
        try:
            return mysql.connector.connect(**DB_CONFIG)
        except mysql.connector.Error:
            time.sleep(3)
    raise RuntimeError("Cannot connect to MySQL")


@app.route("/")
def index():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT id, title, done FROM todos ORDER BY id DESC")
    todos = cursor.fetchall()
    cursor.close()
    db.close()
    return render_template("index.html", todos=todos)


@app.route("/add", methods=["POST"])
def add():
    title = request.form.get("title", "").strip()
    if title:
        db = get_db()
        cursor = db.cursor()
        cursor.execute("INSERT INTO todos (title, done) VALUES (%s, 0)", (title,))
        db.commit()
        cursor.close()
        db.close()
    return redirect("/")


@app.route("/toggle/<int:todo_id>")
def toggle(todo_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("UPDATE todos SET done = NOT done WHERE id = %s", (todo_id,))
    db.commit()
    cursor.close()
    db.close()
    return redirect("/")


@app.route("/delete/<int:todo_id>")
def delete(todo_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM todos WHERE id = %s", (todo_id,))
    db.commit()
    cursor.close()
    db.close()
    return redirect("/")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
