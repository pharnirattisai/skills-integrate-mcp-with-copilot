"""Database utilities for persistent activity storage.

This module provides:
- Lightweight SQLite connection helpers
- File-based migration runner
- Seed data for development
- Data access functions used by the API
"""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Dict, List, Any


BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
MIGRATIONS_DIR = BASE_DIR / "migrations"
DB_PATH = DATA_DIR / "activities.db"


DEFAULT_ACTIVITIES = [
    {
        "name": "Chess Club",
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 12,
        "participants": ["michael@mergington.edu", "daniel@mergington.edu"],
    },
    {
        "name": "Programming Class",
        "description": "Learn programming fundamentals and build software projects",
        "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
        "max_participants": 20,
        "participants": ["emma@mergington.edu", "sophia@mergington.edu"],
    },
    {
        "name": "Gym Class",
        "description": "Physical education and sports activities",
        "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
        "max_participants": 30,
        "participants": ["john@mergington.edu", "olivia@mergington.edu"],
    },
    {
        "name": "Soccer Team",
        "description": "Join the school soccer team and compete in matches",
        "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
        "max_participants": 22,
        "participants": ["liam@mergington.edu", "noah@mergington.edu"],
    },
    {
        "name": "Basketball Team",
        "description": "Practice and play basketball with the school team",
        "schedule": "Wednesdays and Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 15,
        "participants": ["ava@mergington.edu", "mia@mergington.edu"],
    },
    {
        "name": "Art Club",
        "description": "Explore your creativity through painting and drawing",
        "schedule": "Thursdays, 3:30 PM - 5:00 PM",
        "max_participants": 15,
        "participants": ["amelia@mergington.edu", "harper@mergington.edu"],
    },
    {
        "name": "Drama Club",
        "description": "Act, direct, and produce plays and performances",
        "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
        "max_participants": 20,
        "participants": ["ella@mergington.edu", "scarlett@mergington.edu"],
    },
    {
        "name": "Math Club",
        "description": "Solve challenging problems and participate in math competitions",
        "schedule": "Tuesdays, 3:30 PM - 4:30 PM",
        "max_participants": 10,
        "participants": ["james@mergington.edu", "benjamin@mergington.edu"],
    },
    {
        "name": "Debate Team",
        "description": "Develop public speaking and argumentation skills",
        "schedule": "Fridays, 4:00 PM - 5:30 PM",
        "max_participants": 12,
        "participants": ["charlotte@mergington.edu", "henry@mergington.edu"],
    },
]


def _get_connection() -> sqlite3.Connection:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """Apply migrations and ensure development seed data exists."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    MIGRATIONS_DIR.mkdir(parents=True, exist_ok=True)

    with _get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS schema_migrations (
                filename TEXT PRIMARY KEY,
                applied_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        migration_files = sorted(MIGRATIONS_DIR.glob("*.sql"))
        for migration_file in migration_files:
            already_applied = conn.execute(
                "SELECT 1 FROM schema_migrations WHERE filename = ?",
                (migration_file.name,),
            ).fetchone()

            if already_applied:
                continue

            sql = migration_file.read_text(encoding="utf-8")
            conn.executescript(sql)
            conn.execute(
                "INSERT INTO schema_migrations (filename) VALUES (?)",
                (migration_file.name,),
            )

        _seed_activities_if_empty(conn)
        conn.commit()


def _seed_activities_if_empty(conn: sqlite3.Connection) -> None:
    row = conn.execute("SELECT COUNT(*) AS count FROM activities").fetchone()
    if row and row["count"] > 0:
        return

    for activity in DEFAULT_ACTIVITIES:
        cursor = conn.execute(
            """
            INSERT INTO activities (name, description, schedule, max_participants)
            VALUES (?, ?, ?, ?)
            """,
            (
                activity["name"],
                activity["description"],
                activity["schedule"],
                activity["max_participants"],
            ),
        )
        activity_id = cursor.lastrowid

        for email in activity["participants"]:
            conn.execute(
                """
                INSERT INTO activity_participants (activity_id, email)
                VALUES (?, ?)
                """,
                (activity_id, email),
            )


def get_activities() -> Dict[str, Dict[str, Any]]:
    with _get_connection() as conn:
        activity_rows = conn.execute(
            """
            SELECT id, name, description, schedule, max_participants
            FROM activities
            ORDER BY name
            """
        ).fetchall()

        participant_rows = conn.execute(
            """
            SELECT a.name AS activity_name, p.email
            FROM activity_participants p
            JOIN activities a ON a.id = p.activity_id
            ORDER BY p.id
            """
        ).fetchall()

    participants_by_activity: Dict[str, List[str]] = {}
    for row in participant_rows:
        participants_by_activity.setdefault(row["activity_name"], []).append(row["email"])

    response: Dict[str, Dict[str, Any]] = {}
    for row in activity_rows:
        name = row["name"]
        response[name] = {
            "description": row["description"],
            "schedule": row["schedule"],
            "max_participants": row["max_participants"],
            "participants": participants_by_activity.get(name, []),
        }

    return response


def signup_for_activity(activity_name: str, email: str) -> str:
    with _get_connection() as conn:
        activity = conn.execute(
            "SELECT id, max_participants FROM activities WHERE name = ?",
            (activity_name,),
        ).fetchone()

        if not activity:
            raise KeyError("Activity not found")

        already_signed_up = conn.execute(
            "SELECT 1 FROM activity_participants WHERE activity_id = ? AND email = ?",
            (activity["id"], email),
        ).fetchone()
        if already_signed_up:
            raise ValueError("Student is already signed up")

        count_row = conn.execute(
            "SELECT COUNT(*) AS count FROM activity_participants WHERE activity_id = ?",
            (activity["id"],),
        ).fetchone()
        if count_row and count_row["count"] >= activity["max_participants"]:
            raise OverflowError("Activity is full")

        conn.execute(
            "INSERT INTO activity_participants (activity_id, email) VALUES (?, ?)",
            (activity["id"], email),
        )
        conn.commit()

    return f"Signed up {email} for {activity_name}"


def unregister_from_activity(activity_name: str, email: str) -> str:
    with _get_connection() as conn:
        activity = conn.execute(
            "SELECT id FROM activities WHERE name = ?",
            (activity_name,),
        ).fetchone()
        if not activity:
            raise KeyError("Activity not found")

        existing = conn.execute(
            "SELECT id FROM activity_participants WHERE activity_id = ? AND email = ?",
            (activity["id"], email),
        ).fetchone()
        if not existing:
            raise ValueError("Student is not signed up for this activity")

        conn.execute(
            "DELETE FROM activity_participants WHERE id = ?",
            (existing["id"],),
        )
        conn.commit()

    return f"Unregistered {email} from {activity_name}"