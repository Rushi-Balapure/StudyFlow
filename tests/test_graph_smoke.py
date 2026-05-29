from pathlib import Path

from studyflow.cli import build_initial_state
from studyflow.graph.graph import build_graph
from studyflow.store.repository import init_db


def test_graph_runs_end_to_end(tmp_path: Path) -> None:
    db_path = str(tmp_path / "studyflow_test.db")
    init_db(db_path)

    graph = build_graph()
    state = build_initial_state(
        goal="linear algebra",
        duration_min=25,
        content_sources=["generated"],
        db_path=db_path,
    )
    result = graph.invoke(state)

    assert result["done"] is True
    assert len(result["plan"]) >= 1
    assert result["current_step"] >= 1
    assert result["evaluation"] is not None
    assert len(result["messages"]) > 0


def test_answer_quiz_with_adaptive_routing(tmp_path: Path) -> None:
    """
    Test interactive quiz answering with adaptive routing.
    Tests that weak performance triggers remediation and strong performance advances.
    """
    import sqlite3
    from datetime import datetime, timezone

    db_path = str(tmp_path / "studyflow_test.db")
    init_db(db_path)

    # Create a session with an initial step (step 0 is the lesson)
    cursor = sqlite3.connect(db_path)
    cursor.execute(
        "INSERT INTO sessions (session_id, goal, duration_min, content_sources_json, status, created_at) VALUES (?, ?, ?, ?, ?, ?)",
        (
            str(uuid4()),
            "linear algebra",
            25,
            json.dumps(["generated"]),
            "in_progress",
            datetime.now(timezone.utc).isoformat(),
        ),
    )
    cursor.execute(
        "INSERT INTO session_events (session_id, step, agent, payload_json) VALUES (?, ?, ?, ?)",
        (
            str(uuid4()),
            0,
            "tutor",
            json.dumps({"topic": "linear algebra"}),
        ),
    )
    cursor.execute(
        "INSERT INTO session_scores (session_id, step, topic, score, feedback) VALUES (?, ?, ?, ?, ?)",
        (
            str(uuid4()),
            0,
            "linear algebra",
            0.5,
            "Keep practicing this concept.",
        ),
    )
    cursor.execute("UPDATE sessions SET current_step = 1 WHERE session_id = ?", (str(uuid4()),))

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Get max attempts for this topic in session
    cursor.execute(
        "SELECT MAX(attempt_count) FROM session_scores WHERE session_id = ? AND topic = 'linear algebra'",
        (str(uuid4()),),
    )
    row = cursor.fetchone()
    max_attempts = int(row[0]) if row else 3

    # Test weak performance - should trigger remediation
    conn.execute(
        "UPDATE session_scores SET step = ?, learner_answer = 'wrong' WHERE session_id = ? AND topic = 'linear algebra'",
        (1, str(uuid4())),
    )
    conn.commit()

    # Run answer-quiz with weak performance - should return 1 (needs remediation)
    result = run_answer_quiz(
        session_id=str(uuid4()),
        question="What is linear algebra?",
        expected_answer="Linear algebra studies vectors, matrices, and transformations.",
    )

    assert result == 1, "Weak performance should trigger remediation"

    # Test strong performance - should advance (return 0)
    conn.execute(
        "UPDATE session_scores SET step = ?, learner_answer = 'correct' WHERE session_id = ? AND topic = 'linear algebra'",
        (2, str(uuid4())),
    )
    conn.commit()

    # Run answer-quiz with strong performance - should return 0 (advances)
    result = run_answer_quiz(
        session_id=str(uuid4()),
        question="What is linear algebra?",
        expected_answer="Linear algebra studies vectors, matrices, and transformations.",
    )

    assert result == 0, "Strong performance should advance to next topic"

    conn.close()

