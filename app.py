from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "messages.db"

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "change-this-secret-before-deploying")

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                message TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()

# Ensure the message table exists both locally and when deployed with Gunicorn.
init_db()

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        message = request.form.get("message", "").strip()

        if not name or not email or not message:
            flash("Please complete all fields.", "error")
            return redirect(url_for("home") + "#contact")

        if len(name) > 80 or len(email) > 160 or len(message) > 3000 or "@" not in email:
            flash("Please check your details and try again.", "error")
            return redirect(url_for("home") + "#contact")

        with sqlite3.connect(DB_PATH) as conn:
            conn.execute(
                "INSERT INTO messages (name, email, message) VALUES (?, ?, ?)",
                (name, email, message)
            )
            conn.commit()

        flash("Thanks! Your message has been received.", "success")
        return redirect(url_for("home") + "#contact")

    projects = [
        {"number": "01", "title": "Colour & Character", "type": "VISUAL STUDY", "image": "project1.jpeg", "description": "Expressive portrait imagery, colour contrast and visual mood."},
        {"number": "02", "title": "Golden Hour Stories", "type": "CINEMATIC PHOTOGRAPHY", "image": "project2.jpeg", "description": "A cinematic frame built around light, atmosphere and composition."},
        {"number": "03", "title": "The Edit Suite", "type": "DIGITAL CREATION", "image": "project3.jpeg", "description": "A creator’s workspace celebrating the craft of visual storytelling."},
    ]
    return render_template("index.html", projects=projects)

@app.route("/health")
def health():
    return {"status": "ok"}

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
