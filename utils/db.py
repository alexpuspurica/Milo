"""
utils/db.py — SQLite database helpers
======================================
This module is the single point of contact between the Streamlit pages and the
SQLite database that stores all user data (session logs and workout plans).

Each function follows a consistent pattern:
    1. Open a connection to `milo.db` (created automatically on first run).
    2. Execute the relevant SQL query / write.
    3. Close the connection and return a Python-native result.

The stubs below return **hardcoded fake data** so that the UI can be built and
tested before the real SQLite logic is implemented.  Replace the `return`
statements with real SQL when the database schema is finalised.

Database schema (planned)
--------------------------
    users(user_id, username, password_hash, salt, created_at)
    exercises(exercise_id, name, muscle_group, wger_id)
    weekly_plan(user_id, day_of_week, workout_name)
    plan_exercises(user_id, day_of_week, exercise_id, sets, reps, weight_kg)
    sessions(session_id, user_id, date, recovery_score)
    sets_log(log_id, session_id, exercise_id, set_number, reps, weight_kg, completed)
"""

import hashlib
import os
import secrets
import sqlite3

import pandas as pd

# ---------------------------------------------------------------------------
# Database path — sits at the project root alongside app.py
# ---------------------------------------------------------------------------
_MODULE_DIR   = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(_MODULE_DIR)
_DB_PATH      = os.path.join(_PROJECT_ROOT, "milo.db")


def _get_conn() -> sqlite3.Connection:
    return sqlite3.connect(_DB_PATH, check_same_thread=False)


# ---------------------------------------------------------------------------
# Schema initialisation — call once at app startup
# ---------------------------------------------------------------------------

def init_db() -> None:
    """Create all tables if they don't exist yet."""
    conn = _get_conn()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            user_id       INTEGER PRIMARY KEY AUTOINCREMENT,
            username      TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            salt          TEXT NOT NULL,
            created_at    DATETIME DEFAULT CURRENT_TIMESTAMP
        );
    """)
    conn.commit()
    conn.close()


# ---------------------------------------------------------------------------
# Password helpers (never stored in plain text)
# ---------------------------------------------------------------------------

def _hash_password(password: str, salt: str) -> str:
    return hashlib.pbkdf2_hmac(
        "sha256", password.encode(), salt.encode(), 100_000
    ).hex()


# ---------------------------------------------------------------------------
# User auth
# ---------------------------------------------------------------------------

def verify_user(username: str, password: str) -> dict | None:
    """
    Check credentials. Returns {"user_id": int, "username": str} on success,
    None if the username doesn't exist or the password is wrong.
    """
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
    """
    Register a new user. Returns True on success, False if the username is
    already taken. Called by the sign-up page.
    """
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
        return False  # username already taken


# ---------------------------------------------------------------------------
# Read helpers
# ---------------------------------------------------------------------------

def get_today_workout(user_id: int) -> dict:
    """
    Return the planned workout for today based on the user's weekly schedule.

    Parameters
    ----------
    user_id : int
        Identifies which user's plan to look up.

    Returns
    -------
    dict
        Keys:
            "workout_name" (str)  — e.g. "Push"
            "exercises"   (list)  — list of dicts, each with keys:
                "name"     (str)
                "sets"     (int)
                "reps"     (int)
                "weight_kg" (float)

    Notes
    -----
    Real implementation: join weekly_plan + plan_exercises on today's weekday.
    """
    # --- STUB: return fake data so the UI renders without a real database ---
    return {
        "workout_name": "Push",
        "exercises": [
            {"name": "Bench Press",    "sets": 4, "reps": 8,  "weight_kg": 80.0},
            {"name": "Overhead Press", "sets": 3, "reps": 10, "weight_kg": 50.0},
            {"name": "Tricep Pushdown","sets": 3, "reps": 12, "weight_kg": 30.0},
        ],
    }


def get_exercise_history(user_id: int, exercise_id: int) -> pd.DataFrame:
    """
    Return the full log of completed sets for a given exercise.

    Parameters
    ----------
    user_id : int
        The user whose history to retrieve.
    exercise_id : int
        Which exercise to filter by.

    Returns
    -------
    pd.DataFrame
        Columns: date (str), planned_weight_kg (float), actual_weight_kg (float),
                 planned_reps (int), actual_reps (int), sets_completed (int).

    Notes
    -----
    Real implementation: SELECT from sets_log JOIN sessions WHERE user_id and
    exercise_id, ordered by date ASC.
    """
    # --- STUB: six fake historical sessions ---
    return pd.DataFrame(
        {
            "date":               ["2025-03-01", "2025-03-08", "2025-03-15",
                                   "2025-03-22", "2025-03-29", "2025-04-05"],
            "planned_weight_kg":  [75.0, 75.0, 77.5, 77.5, 80.0, 80.0],
            "actual_weight_kg":   [75.0, 75.0, 77.5, 80.0, 80.0, 82.5],
            "planned_reps":       [8,    8,    8,    8,    8,    8   ],
            "actual_reps":        [8,    7,    8,    8,    8,    8   ],
            "sets_completed":     [4,    3,    4,    4,    4,    4   ],
        }
    )


def get_weekly_plan(user_id: int) -> dict:
    """
    Return the user's weekly training schedule (day → workout name mapping).

    Parameters
    ----------
    user_id : int
        The user whose plan to retrieve.

    Returns
    -------
    dict
        Keys are full day names ("Monday" … "Sunday"), values are workout
        names or "Rest".

    Notes
    -----
    Real implementation: SELECT day_of_week, workout_name FROM weekly_plan
    WHERE user_id = ?.
    """
    # --- STUB: a classic Push / Pull / Legs split ---
    return {
        "Monday":    "Push",
        "Tuesday":   "Pull",
        "Wednesday": "Legs",
        "Thursday":  "Rest",
        "Friday":    "Push",
        "Saturday":  "Pull",
        "Sunday":    "Rest",
    }


def get_all_exercises(user_id: int) -> list:
    """
    Return the names of all exercises in the user's exercise library.

    Parameters
    ----------
    user_id : int
        The user whose library to retrieve.

    Returns
    -------
    list[str]
        Exercise names, sorted alphabetically.

    Notes
    -----
    Real implementation: SELECT DISTINCT name FROM exercises WHERE user_id = ?
    ORDER BY name.
    """
    # --- STUB: a small default exercise list ---
    return [
        "Bench Press",
        "Deadlift",
        "Overhead Press",
        "Romanian Deadlift",
        "Squat",
        "Tricep Pushdown",
    ]


# ---------------------------------------------------------------------------
# Write helpers
# ---------------------------------------------------------------------------

def save_session(user_id: int, exercise_id: int, sets_data: list) -> bool:
    """
    Persist one completed session to the database.

    Parameters
    ----------
    user_id : int
        The user who completed the session.
    exercise_id : int
        Which exercise this data belongs to.
    sets_data : list[dict]
        One dict per set, each containing:
            "set_number"  (int)
            "reps"        (int)
            "weight_kg"   (float)
            "completed"   (bool)

    Returns
    -------
    bool
        True if the write succeeded, False on error.

    Notes
    -----
    Real implementation: INSERT INTO sessions and then INSERT INTO sets_log
    inside a transaction so both succeed or both roll back together.
    """
    # --- STUB: pretend the write succeeded ---
    # TODO: open milo.db, INSERT session row, then INSERT one sets_log row per
    #       set in sets_data, wrapped in a try/except that returns False on
    #       any sqlite3.Error.
    return True


def save_weekly_plan(user_id: int, plan_dict: dict) -> bool:
    """
    Persist the user's weekly schedule to the database.

    Parameters
    ----------
    user_id : int
        The user whose plan to update.
    plan_dict : dict
        Same format as returned by get_weekly_plan() — day name → workout name.

    Returns
    -------
    bool
        True if the write succeeded, False on error.

    Notes
    -----
    Real implementation: DELETE existing rows for this user, then INSERT fresh
    rows from plan_dict (upsert-style to avoid duplicates).
    """
    # --- STUB: pretend the write succeeded ---
    return True
