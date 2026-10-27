# BACKEND-KA (Flask) + DATABASE (SQLite): hal sanduuq, raadin internet ah
import sqlite3
from datetime import datetime
from flask import Flask, render_template, request, redirect
from extract import extract_text
from similarity import highlight
from webcheck import check_text, verdict, strip_refs

app = Flask(__name__)
DB = "history.db"


def db():
    return sqlite3.connect(DB)


def init_db():
    with db() as con:
        con.execute("""CREATE TABLE IF NOT EXISTS documents(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT, body TEXT, created TEXT)""")


@app.route("/", methods=["GET", "POST"])
def index():
    result, error = None, None
    if request.method == "POST":
        file = request.files.get("file")
        if file and file.filename:
            title, text = file.filename, extract_text(file)
        else:
            title, text = "Typed text", request.form.get("text", "")
        text = strip_refs(text)  # ka saar [1], [A] iwm.
        if len(text.split()) < 8:
            error = "The text is too short (at least 8 words required)."
        else:
            with db() as con:
                docs = con.execute("SELECT title, created, body FROM documents").fetchall()
            result = check_text(text, docs)
            result["verdict"] = verdict(result["pct"])
            result["html"] = highlight(text, result["shared"], result["n"])
            with db() as con:  # kaydi qoraalka si mustaqbalka loogu barbar dhigo
                con.execute("INSERT INTO documents(title,body,created) VALUES(?,?,?)",
                            (title, text, datetime.now().strftime("%Y-%m-%d %H:%M")))
    with db() as con:
        count = con.execute("SELECT COUNT(*) FROM documents").fetchone()[0]
    return render_template("index.html", result=result, error=error, count=count)


@app.route("/clear", methods=["POST"])
def clear():
    with db() as con:
        con.execute("DELETE FROM documents")
    return redirect("/")


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
