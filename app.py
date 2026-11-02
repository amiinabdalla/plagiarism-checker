# BACKEND-KA (Flask) + DATABASE (SQLite): laba mode (Compare two documents + Internet check)
import os
import sqlite3
from datetime import datetime
from flask import Flask, render_template, request, redirect
from extract import extract_text
from similarity import cosine_score, jaccard_score, overlap_score, shared_ngrams, highlight, classify
from webcheck import check_text, verdict, strip_refs

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024  # CHANGED [Bug 6]: xadka fayl la soo gelinayo = 10 MB
DB = "history.db"
ADMIN_KEY = os.environ.get("ADMIN_KEY", "")  # CHANGED [Admin]: furaha lagu tirtiro database-ka (Render: Environment Variable)
N = 4  # cabbirka kooxda erayada (4-gram)


def db():
    return sqlite3.connect(DB)


def init_db():
    with db() as con:
        con.execute("""CREATE TABLE IF NOT EXISTS documents(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT, body TEXT, created TEXT)""")


init_db()  # CHANGED [Bug 5/Deploy]: waxay shaqaysaa marka app-ka la furo (gunicorn ma isticmaalo `__main__`)


def page(result=None, error=None, mode="compare", status=200):
    """Soo bandhig bogga (hal meel) iyo xogta guud."""
    with db() as con:
        count = con.execute("SELECT COUNT(*) FROM documents").fetchone()[0]
    return render_template("index.html", result=result, error=error, mode=mode, count=count,
                           clear_enabled=bool(ADMIN_KEY) or app.debug, need_key=bool(ADMIN_KEY)), status


def get_input(side):
    """Qoraal la qoray AMA fayl. Soo celiyaa (magac, qoraal, khalad)."""
    file = request.files.get("file_" + side)
    if file and file.filename:
        text = strip_refs(extract_text(file))
        if not text.strip():  # CHANGED [Bug 7]: fariin cad ah (PDF scan)
            return file.filename, "", "No text could be read from this file. It may be a scanned PDF."
        return file.filename, text, None
    return "Typed text", strip_refs(request.form.get("text_" + side, "")), None


def run_compare():
    """CHANGED [Mode 2 docs]: labo dukumenti, TF-IDF + cosine + xeerarka 70/40."""
    _, a, err_a = get_input("a")
    _, b, err_b = get_input("b")
    if err_a or err_b:
        return None, err_a or err_b
    if len(a.split()) < 5 or len(b.split()) < 5:
        return None, "Both documents must contain at least 5 words."
    score = round(cosine_score(a, b) * 100, 1)
    shared = shared_ngrams(a, b, N)
    return {"mode": "compare", "pct": score, "level": classify(score),
            "jaccard": round(jaccard_score(a, b) * 100, 1),
            "overlap": round(overlap_score(a, b, N) * 100, 1),
            "html_a": highlight(a, shared, N), "html_b": highlight(b, shared, N)}, None


def run_web():
    """Hubinta internet-ka iyo database-ka (hal qoraal)."""
    title, text, err = get_input("w")
    if err:
        return None, err
    if len(text.split()) < 8:
        return None, "The text is too short (at least 8 words required)."
    with db() as con:  # CHANGED [Bug 1]: ha la barbar dhigin nuqulkiisa
        docs = con.execute("SELECT title, created, body FROM documents WHERE body != ?", (text,)).fetchall()
    result = check_text(text, docs)
    if result is None:
        return None, "The text is too short (at least 8 words required)."
    result.update(mode="web", verdict=verdict(result["pct"]), html=highlight(text, result["shared"], result["n"]), saved=False)
    if request.form.get("save"):  # CHANGED [Privacy]: kaydinta waa ikhtiyaar (checkbox)
        with db() as con:
            if not con.execute("SELECT 1 FROM documents WHERE body = ?", (text,)).fetchone():  # CHANGED [Bug 1]
                con.execute("INSERT INTO documents(title,body,created) VALUES(?,?,?)",
                            (title, text, datetime.now().strftime("%Y-%m-%d %H:%M")))
        result["saved"] = True
    return result, None


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        mode = request.form.get("mode", "compare")
        result, error = run_compare() if mode == "compare" else run_web()
        return page(result, error, mode)
    return page()


@app.errorhandler(413)
def too_large(e):
    """CHANGED [Bug 6]: fayl ka weyn 10 MB."""
    return page(error="The file is too large (maximum 10 MB).", status=413)


@app.route("/clear", methods=["POST"])
def clear():
    """CHANGED [Admin]: tirtirista database-ka waa la ilaaliyay."""
    if ADMIN_KEY:
        if request.form.get("key", "") != ADMIN_KEY:
            return page(error="Wrong admin key.", status=403)
    elif not app.debug:
        return page(error="Clearing the database is disabled on this server.", status=403)
    with db() as con:
        con.execute("DELETE FROM documents")
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)
