"""
utils/db.py — SQLite database helpers
======================================
Single point of contact between Streamlit pages and the milo.db SQLite file.

Schema
------
    users(user_id, username, password_hash, salt, created_at)
    exercises(exercise_id, user_id, name, muscle_group)
    weekly_plan(plan_id, user_id, day_of_week, workout_name)
    plan_exercises(id, user_id, day_of_week, exercise_id, sets, reps, weight_kg)
    sessions(session_id, user_id, date, created_at)
    sets_log(log_id, session_id, exercise_id, set_number,
             planned_reps, planned_weight_kg, actual_reps, actual_weight_kg, completed)
"""

import datetime
import hashlib
import os
import secrets
import sqlite3

import pandas as pd

# ---------------------------------------------------------------------------
# Database path
# ---------------------------------------------------------------------------
_MODULE_DIR   = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(_MODULE_DIR)
_DB_PATH      = os.path.join(_PROJECT_ROOT, "milo.db")


def _get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(_DB_PATH, check_same_thread=False)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


# ---------------------------------------------------------------------------
# Schema initialisation
# ---------------------------------------------------------------------------

def init_db() -> None:
    """Create all tables if they don't exist. Safe to call on every startup."""
    conn = _get_conn()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            user_id       INTEGER PRIMARY KEY AUTOINCREMENT,
            username      TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            salt          TEXT NOT NULL,
            created_at    DATETIME DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS exercises (
            exercise_id  INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id      INTEGER NOT NULL,
            name         TEXT NOT NULL,
            muscle_group TEXT DEFAULT '',
            UNIQUE(user_id, name)
        );

        CREATE TABLE IF NOT EXISTS weekly_plan (
            plan_id      INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id      INTEGER NOT NULL,
            day_of_week  TEXT NOT NULL,
            workout_name TEXT NOT NULL,
            UNIQUE(user_id, day_of_week)
        );

        CREATE TABLE IF NOT EXISTS plan_exercises (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     INTEGER NOT NULL,
            day_of_week TEXT NOT NULL,
            exercise_id INTEGER NOT NULL,
            sets        INTEGER NOT NULL,
            reps        INTEGER NOT NULL,
            weight_kg   REAL NOT NULL
        );

        CREATE TABLE IF NOT EXISTS sessions (
            session_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id    INTEGER NOT NULL,
            date       TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS sets_log (
            log_id            INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id        INTEGER NOT NULL,
            exercise_id       INTEGER NOT NULL,
            set_number        INTEGER NOT NULL,
            planned_reps      INTEGER,
            planned_weight_kg REAL,
            actual_reps       INTEGER,
            actual_weight_kg  REAL,
            completed         INTEGER DEFAULT 1
        );
    """)
    conn.commit()
    conn.close()


# ---------------------------------------------------------------------------
# Password helpers
# ---------------------------------------------------------------------------

def _hash_password(password: str, salt: str) -> str:
    return hashlib.pbkdf2_hmac(
        "sha256", password.encode(), salt.encode(), 100_000
    ).hex()


# ---------------------------------------------------------------------------
# User auth
# ---------------------------------------------------------------------------

def verify_user(username: str, password: str) -> dict | None:
    """Returns {"user_id", "username"} on success, None on failure."""
    conn = _get_conn()
    row = conn.execute(
        "SELECT user_id, username, password_hash, salt FROM users WHERE username = ?",
        (username,),
    ).fetchone()
    conn.close()
    if row is None:
        return None
    user_id, uname, stored_hash, salt = row
    if _hash_password(password, salt) == stored_hash:
        return {"user_id": user_id, "username": uname}
    return None


def create_user(username: str, password: str) -> bool:
    """Register a new user. Returns False if the username is already taken."""
    salt          = secrets.token_hex(16)
    password_hash = _hash_password(password, salt)
    try:
        conn = _get_conn()
        conn.execute(
            "INSERT INTO users (username, password_hash, salt) VALUES (?, ?, ?)",
            (username, password_hash, salt),
        )
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False


# ---------------------------------------------------------------------------
# Exercise helpers
# ---------------------------------------------------------------------------

def _get_or_create_exercise(conn: sqlite3.Connection, user_id: int, name: str) -> int:
    """Return exercise_id for (user_id, name), inserting a row if needed."""
    row = conn.execute(
        "SELECT exercise_id FROM exercises WHERE user_id=? AND name=?",
        (user_id, name),
    ).fetchone()
    if row:
        return row[0]
    cur = conn.execute(
        "INSERT INTO exercises (user_id, name) VALUES (?, ?)",
        (user_id, name),
    )
    return cur.lastrowid


def get_exercise_id(user_id: int, name: str) -> int | None:
    """Return the exercise_id for a given exercise name, or None if not found."""
    conn = _get_conn()
    row = conn.execute(
        "SELECT exercise_id FROM exercises WHERE user_id=? AND name=?",
        (user_id, name),
    ).fetchone()
    conn.close()
    return row[0] if row else None


def get_all_exercises(user_id: int) -> list[str]:
    """Return all exercise names for this user, sorted alphabetically."""
    conn = _get_conn()
    rows = conn.execute(
        "SELECT name FROM exercises WHERE user_id=? ORDER BY name",
        (user_id,),
    ).fetchall()
    conn.close()
    return [r[0] for r in rows]


# ---------------------------------------------------------------------------
# Weekly plan
# ---------------------------------------------------------------------------

def get_weekly_plan(user_id: int) -> dict:
    """Return {day_name: workout_name} for every day that has a plan row."""
    conn = _get_conn()
    rows = conn.execute(
        "SELECT day_of_week, workout_name FROM weekly_plan WHERE user_id=?",
        (user_id,),
    ).fetchall()
    conn.close()
    return {r[0]: r[1] for r in rows}


def save_weekly_plan(user_id: int, plan_dict: dict) -> bool:
    """Replace the user's weekly schedule with plan_dict {day: workout_name}."""
    try:
        conn = _get_conn()
        conn.execute("DELETE FROM weekly_plan WHERE user_id=?", (user_id,))
        conn.executemany(
            "INSERT INTO weekly_plan (user_id, day_of_week, workout_name) VALUES (?,?,?)",
            [(user_id, day, name) for day, name in plan_dict.items()],
        )
        conn.commit()
        conn.close()
        return True
    except sqlite3.Error:
        return False


def save_plan_exercise(
    user_id: int, day: str, exercise_name: str,
    sets: int, reps: int, weight_kg: float,
) -> bool:
    """Add an exercise to a specific day in the user's plan."""
    try:
        conn = _get_conn()
        exercise_id = _get_or_create_exercise(conn, user_id, exercise_name)
        conn.execute(
            """INSERT INTO plan_exercises
               (user_id, day_of_week, exercise_id, sets, reps, weight_kg)
               VALUES (?,?,?,?,?,?)""",
            (user_id, day, exercise_id, sets, reps, weight_kg),
        )
        conn.commit()
        conn.close()
        return True
    except sqlite3.Error:
        return False


# ---------------------------------------------------------------------------
# Today's workout
# ---------------------------------------------------------------------------

def get_today_workout(user_id: int) -> dict:
    """
    Return {"workout_name": str, "exercises": [{"name", "sets", "reps", "weight_kg"}]}
    for today's day of week. Returns a Rest day dict if no plan is set.
    """
    today = datetime.datetime.today().strftime("%A")
    conn  = _get_conn()

    plan_row = conn.execute(
        "SELECT workout_name FROM weekly_plan WHERE user_id=? AND day_of_week=?",
        (user_id, today),
    ).fetchone()

    if plan_row is None:
        conn.close()
        return {"workout_name": "Rest", "exercises": []}

    workout_name = plan_row[0]

    rows = conn.execute(
        """SELECT e.name, pe.sets, pe.reps, pe.weight_kg
           FROM plan_exercises pe
           JOIN exercises e ON pe.exercise_id = e.exercise_id
           WHERE pe.user_id=? AND pe.day_of_week=?
           ORDER BY pe.id""",
        (user_id, today),
    ).fetchall()
    conn.close()

    return {
        "workout_name": workout_name,
        "exercises": [
            {"name": r[0], "sets": r[1], "reps": r[2], "weight_kg": r[3]}
            for r in rows
        ],
    }


# ---------------------------------------------------------------------------
# Session logging
# ---------------------------------------------------------------------------

def save_session(user_id: int, sets_data: list) -> bool:
    """
    Persist a completed session to the database.

    sets_data is a list of dicts (one per set across all exercises):
        "name"              str   exercise name
        "planned_weight_kg" float
        "planned_reps"      int
        "actual_weight_kg"  float
        "actual_reps"       int
        "completed"         bool
    """
    today = datetime.datetime.today().strftime("%Y-%m-%d")
    try:
        conn = _get_conn()

        cur        = conn.execute(
            "INSERT INTO sessions (user_id, date) VALUES (?,?)", (user_id, today)
        )
        session_id = cur.lastrowid

        # Group sets by exercise name to assign set numbers
        by_exercise: dict[str, list] = {}
        for item in sets_data:
            by_exercise.setdefault(item["name"], []).append(item)

        for ex_name, sets in by_exercise.items():
            exercise_id = _get_or_create_exercise(conn, user_id, ex_name)
            for set_num, s in enumerate(sets, start=1):
                conn.execute(
                    """INSERT INTO sets_log
                       (session_id, exercise_id, set_number,
                        planned_reps, planned_weight_kg,
                        actual_reps,  actual_weight_kg, completed)
                       VALUES (?,?,?,?,?,?,?,?)""",
                    (
                        session_id, exercise_id, set_num,
                        s["planned_reps"],      s["planned_weight_kg"],
                        s["actual_reps"],       s["actual_weight_kg"],
                        1 if s["completed"] else 0,
                    ),
                )

        conn.commit()
        conn.close()
        return True
    except sqlite3.Error:
        return False


# ---------------------------------------------------------------------------
# Exercise history
# ---------------------------------------------------------------------------

def get_exercise_history(user_id: int, exercise_id: int) -> pd.DataFrame:
    """
    Return per-session aggregated history for one exercise.

    Columns: date, planned_weight_kg, actual_weight_kg,
             planned_reps, actual_reps, sets_completed.
    """
    conn = _get_conn()
    rows = conn.execute(
        """SELECT
               s.date,
               AVG(sl.planned_weight_kg)   AS planned_weight_kg,
               AVG(sl.actual_weight_kg)    AS actual_weight_kg,
               ROUND(AVG(sl.planned_reps)) AS planned_reps,
               ROUND(AVG(sl.actual_reps))  AS actual_reps,
               SUM(sl.completed)           AS sets_completed
           FROM sets_log sl
           JOIN sessions s ON sl.session_id = s.session_id
           WHERE s.user_id=? AND sl.exercise_id=?
           GROUP BY s.session_id, s.date
           ORDER BY s.date ASC""",
        (user_id, exercise_id),
    ).fetchall()
    conn.close()

    if not rows:
        return pd.DataFrame(
            columns=["date", "planned_weight_kg", "actual_weight_kg",
                     "planned_reps", "actual_reps", "sets_completed"]
        )

    return pd.DataFrame(
        rows,
        columns=["date", "planned_weight_kg", "actual_weight_kg",
                 "planned_reps", "actual_reps", "sets_completed"],
    )
