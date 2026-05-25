from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def init_db(db_path: str) -> None:
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                goal TEXT NOT NULL,
                duration_min INTEGER NOT NULL,
                content_sources_json TEXT NOT NULL,
                status TEXT NOT NULL,
                created_at TEXT NOT NULL,
                completed_at TEXT
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS session_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                step INTEGER NOT NULL,
                agent TEXT NOT NULL,
                payload_json TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS session_scores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                step INTEGER NOT NULL,
                topic TEXT NOT NULL,
                score REAL NOT NULL,
                feedback TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.commit()


def create_session(
    db_path: str,
    session_id: str,
    goal: str,
    duration_min: int,
    content_sources: list[str],
) -> None:
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            """
            INSERT INTO sessions (
                session_id, goal, duration_min, content_sources_json, status, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                session_id,
                goal,
                duration_min,
                json.dumps(content_sources),
                "in_progress",
                _utc_now(),
            ),
        )
        conn.commit()


def finalize_session(db_path: str, session_id: str) -> None:
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            """
            UPDATE sessions
            SET status = ?, completed_at = ?
            WHERE session_id = ?
            """,
            ("completed", _utc_now(), session_id),
        )
        conn.commit()


def add_event(
    db_path: str,
    session_id: str,
    step: int,
    agent: str,
    payload: dict[str, object],
) -> None:
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            """
            INSERT INTO session_events (session_id, step, agent, payload_json, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (session_id, step, agent, json.dumps(payload), _utc_now()),
        )
        conn.commit()


def add_score(
    db_path: str,
    session_id: str,
    step: int,
    topic: str,
    score: float,
    feedback: str,
) -> None:
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            """
            INSERT INTO session_scores (session_id, step, topic, score, feedback, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (session_id, step, topic, score, feedback, _utc_now()),
        )
        conn.commit()


def count_scores(db_path: str, session_id: str) -> int:
    with sqlite3.connect(db_path) as conn:
        row = conn.execute(
            "SELECT COUNT(*) FROM session_scores WHERE session_id = ?",
            (session_id,),
        ).fetchone()
    return int(row[0]) if row else 0
