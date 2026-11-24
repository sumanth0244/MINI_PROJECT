from flask import Flask, request, jsonify, render_template
from config import Config
from models import conn, one, all, run
from agents import AGENTS
from games import make

app = Flask(__name__)
app.config.from_object(Config)
NAMES = {
    "sequence": "Sequence Memory",
    "missing_object": "Missing Object",
    "association": "Picture Association",
    "recognition": "Picture Recognition",
}


def ensure_schema():
    try:
        cols = {row["Field"] for row in all("SHOW COLUMNS FROM patients")}
        if "email" not in cols:
            run("ALTER TABLE patients ADD COLUMN email VARCHAR(120) NULL")
    except Exception:
        pass


def init_patient_levels(pid):
    c = conn()
    try:
        q = c.cursor()
        for k in NAMES:
            q.execute(
                "INSERT INTO patient_game_levels(patient_id,game_id) SELECT %s,id FROM games WHERE game_key=%s",
                (pid, k),
            )
        c.commit()
    finally:
        q.close()
        c.close()


ensure_schema()


@app.get("/")
def home():
    return render_template("index.html")


@app.get("/patient")
def patient_window():
    return render_template("patient.html")


@app.get("/caregiver")
def caregiver_window():
    return render_template("caregiver.html")


@app.get("/play/<key>")
def play(key):
    if key not in NAMES:
        return "Not found", 404
    return render_template("game.html", game_key=key)


@app.get("/api/patients")
def patients():
    return jsonify(
        all(
            """
            SELECT p.*,
                   COUNT(s.id) AS sessions,
                   ROUND(AVG(s.accuracy),1) AS average_accuracy
            FROM patients p
            LEFT JOIN game_sessions s ON s.patient_id=p.id
            GROUP BY p.id
            ORDER BY p.full_name
            """
        )
    )


@app.post("/api/patients")
def add_patient():
    d = request.get_json() or {}
    code = (d.get("patient_code") or "").strip()
    email = (d.get("email") or "").strip()
    name = (d.get("full_name") or "").strip() or code
    if not code or not email:
        return jsonify(error="Patient ID and email are required"), 400
    if "@" not in email or "." not in email:
        return jsonify(error="Enter a valid email address"), 400
    try:
        pid = run(
            "INSERT INTO patients(patient_code,full_name,email,age,caregiver_name) VALUES(%s,%s,%s,%s,%s)",
            (code, name, email, d.get("age") or None, d.get("caregiver_name") or None),
        )
        init_patient_levels(pid)
        return jsonify(id=pid, patient_code=code, email=email, full_name=name), 201
    except Exception:
        return jsonify(error="Could not register patient. Check duplicate Patient ID and database setup."), 400


@app.post("/api/patient/login")
def patient_login():
    code = ((request.get_json() or {}).get("patient_code") or "").strip()
    if not code:
        return jsonify(error="Enter your Patient ID"), 400
    patient = one("SELECT * FROM patients WHERE patient_code=%s", (code,))
    if not patient:
        return jsonify(error="Patient ID not found. Ask your caregiver to register you first."), 404
    return jsonify(patient)


@app.get("/api/games")
def game_list():
    pid = request.args.get("patient_id", type=int)
    if not pid or not one("SELECT id FROM patients WHERE id=%s", (pid,)):
        return jsonify(error="Select a valid patient"), 400
    return jsonify(
        all(
            "SELECT g.game_key,g.game_name,p.current_level FROM games g JOIN patient_game_levels p ON p.game_id=g.id WHERE p.patient_id=%s ORDER BY g.id",
            (pid,),
        )
    )


@app.post("/api/game/start")
def start():
    d = request.get_json() or {}
    pid = d.get("patient_id")
    key = d.get("game_key")
    if key not in NAMES or not one("SELECT id FROM patients WHERE id=%s", (pid,)):
        return jsonify(error="Valid patient and game required"), 400
    row = one(
        "SELECT p.current_level FROM patient_game_levels p JOIN games g ON p.game_id=g.id WHERE p.patient_id=%s AND g.game_key=%s",
        (pid, key),
    )
    level = row["current_level"]
    result = make(key, AGENTS[key].parameters(level))
    result["level"] = level
    return jsonify(result)


@app.post("/api/game/submit")
def submit():
    d = request.get_json() or {}
    pid = d.get("patient_id")
    key = d.get("game_key")
    if key not in NAMES or not one("SELECT id FROM patients WHERE id=%s", (pid,)):
        return jsonify(error="Valid patient and game required"), 400
    g = one("SELECT id FROM games WHERE game_key=%s", (key,))
    level = one(
        "SELECT current_level FROM patient_game_levels WHERE patient_id=%s AND game_id=%s",
        (pid, g["id"]),
    )
    if not level:
        return jsonify(error="Patient level missing"), 404
    total = max(1, int(d.get("total_questions", 1)))
    correct = max(0, min(total, int(d.get("correct_answers", 0))))
    acc = round(correct / total * 100, 2)
    sid = run(
        "INSERT INTO game_sessions(patient_id,game_id,difficulty,total_questions,correct_answers,accuracy,reaction_time,attempts,hints_used,completed) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
        (
            pid,
            g["id"],
            level["current_level"],
            total,
            correct,
            acc,
            float(d.get("reaction_time", 0)),
            int(d.get("attempts", 0)),
            int(d.get("hints_used", 0)),
            bool(d.get("completed", True)),
        ),
    )
    recent = all(
        "SELECT accuracy,completed,hints_used FROM game_sessions WHERE patient_id=%s AND game_id=%s ORDER BY created_at DESC,id DESC LIMIT 3",
        (pid, g["id"]),
    )
    nxt, decision, reason = AGENTS[key].recommend(level["current_level"], recent)
    run(
        "UPDATE patient_game_levels SET current_level=%s WHERE patient_id=%s AND game_id=%s",
        (nxt, pid, g["id"]),
    )
    run(
        "INSERT INTO agent_decisions(patient_id,game_id,session_id,previous_level,recommended_level,decision,reason) VALUES(%s,%s,%s,%s,%s,%s,%s)",
        (pid, g["id"], sid, level["current_level"], nxt, decision, reason),
    )
    return jsonify(accuracy=acc, previous_level=level["current_level"], next_level=nxt, decision=decision, reason=reason)


@app.get("/api/progress/<int:pid>")
def progress(pid):
    patient = one("SELECT * FROM patients WHERE id=%s", (pid,))
    if not patient:
        return jsonify(error="Patient not found"), 404
    games = all(
        """
        SELECT g.game_key,g.game_name,p.current_level,COUNT(s.id) sessions,ROUND(AVG(s.accuracy),1) average_accuracy
        FROM games g
        JOIN patient_game_levels p ON p.game_id=g.id AND p.patient_id=%s
        LEFT JOIN game_sessions s ON s.game_id=g.id AND s.patient_id=%s
        GROUP BY g.id,g.game_key,g.game_name,p.current_level
        ORDER BY g.id
        """,
        (pid, pid),
    )
    sessions = all(
        """
        SELECT g.game_name,s.difficulty,s.correct_answers,s.total_questions,s.accuracy,s.reaction_time,s.created_at
        FROM game_sessions s JOIN games g ON s.game_id=g.id
        WHERE s.patient_id=%s
        ORDER BY s.created_at DESC,s.id DESC
        LIMIT 20
        """,
        (pid,),
    )
    decisions = all(
        """
        SELECT g.game_name,d.previous_level,d.recommended_level,d.decision,d.reason,d.created_at
        FROM agent_decisions d JOIN games g ON d.game_id=g.id
        WHERE d.patient_id=%s
        ORDER BY d.created_at DESC LIMIT 10
        """,
        (pid,),
    )
    return jsonify(patient=patient, games=games, sessions=sessions, decisions=decisions)


if __name__ == "__main__":
    app.run(debug=True)
