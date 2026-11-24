import os
import sqlite3
from flask import Flask, jsonify, render_template, request
from translator import translate

app = Flask(__name__)
DB_PATH = os.path.join(os.path.dirname(__file__), "database", "history.db")


def db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with db() as conn:
        conn.execute(
            """CREATE TABLE IF NOT EXISTS history (
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   source TEXT, target TEXT,
                   original TEXT, translation TEXT,
                   created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)"""
        )


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/translate", methods=["POST"])
def api_translate():
    data = request.get_json(silent=True) or {}
    text = data.get("text", "")
    try:
        result = translate(text, data.get("source", "auto"), data.get("target"))
    except ValueError as e:
        return jsonify(error=str(e)), 400
    except Exception:
        return jsonify(error="Translation failed. Check the server log."), 500

    with db() as conn:
        conn.execute(
            "INSERT INTO history (source, target, original, translation) VALUES (?,?,?,?)",
            (result["source"], result["target"], text.strip(), result["translation"]),
        )
    return jsonify(result)


@app.route("/api/history")
def api_history():
    with db() as conn:
        rows = conn.execute(
            "SELECT * FROM history ORDER BY id DESC LIMIT 20"
        ).fetchall()
    return jsonify([dict(r) for r in rows])


@app.route("/api/history", methods=["DELETE"])
def clear_history():
    with db() as conn:
        conn.execute("DELETE FROM history")
    return jsonify(ok=True)


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
