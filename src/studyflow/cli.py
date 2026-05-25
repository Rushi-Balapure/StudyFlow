from __future__ import annotations

import argparse
from uuid import uuid4

from studyflow.config import get_settings
from studyflow.graph.graph import build_graph
from studyflow.graph.state import GraphState
from studyflow.store.repository import count_scores, create_session, finalize_session, init_db


def build_initial_state(
    goal: str,
    duration_min: int,
    content_sources: list[str],
    db_path: str,
    live_updates: bool = True,
) -> GraphState:
    return {
        "session_id": str(uuid4()),
        "goal": goal,
        "duration_min": duration_min,
        "content_sources": content_sources,
        "current_step": 0,
        "plan": [],
        "current_topic": None,
        "lesson": None,
        "quiz": [],
        "evaluation": None,
        "focus_events": [],
        "messages": [],
        "done": False,
        "db_path": db_path,
        "live_updates": live_updates,
    }


def _parse_sources(raw: str) -> list[str]:
    parts = [item.strip() for item in raw.split(",")]
    return [item for item in parts if item]


def _print_plan(plan: list[str]) -> None:
    print("\n--- Plan ---")
    for idx, item in enumerate(plan, start=1):
        print(f"{idx}. {item}")


def _print_last_quiz(quiz: list[dict[str, str]]) -> None:
    print("\n--- Last Quiz ---")
    for idx, item in enumerate(quiz, start=1):
        print(f"{idx}. {item['question']}")
        print(f"   Expected: {item['expected_answer']}")


def _print_evaluation(evaluation: dict[str, object] | None) -> None:
    print("\n--- Evaluation ---")
    if evaluation is None:
        print("No evaluation available.")
        return
    print(f"Score: {evaluation['score']}")
    print(f"Feedback: {evaluation['feedback']}")


def _print_messages(messages: list[str]) -> None:
    print("\n--- Messages ---")
    for msg in messages:
        print(f"- {msg}")


def run_start_session(
    goal: str,
    duration_min: int,
    sources_raw: str,
    live_updates: bool,
) -> int:
    settings = get_settings()
    content_sources = _parse_sources(sources_raw)
    if not content_sources:
        content_sources = ["generated"]

    init_db(settings.sqlite_path)
    graph = build_graph()
    initial_state = build_initial_state(
        goal=goal,
        duration_min=duration_min,
        content_sources=content_sources,
        db_path=settings.sqlite_path,
        live_updates=live_updates,
    )

    create_session(
        db_path=settings.sqlite_path,
        session_id=initial_state["session_id"],
        goal=goal,
        duration_min=duration_min,
        content_sources=content_sources,
    )

    final_state = graph.invoke(initial_state)
    finalize_session(settings.sqlite_path, final_state["session_id"])

    print(f"\nSession ID: {final_state['session_id']}")
    print(f"Goal: {final_state['goal']}")
    print(f"Duration: {final_state['duration_min']} min")
    print(f"Sources: {', '.join(final_state['content_sources'])}")
    _print_plan(final_state["plan"])

    print("\n--- Last Lesson ---")
    print(final_state["lesson"] or "No lesson generated.")

    _print_last_quiz(final_state["quiz"])
    _print_evaluation(final_state["evaluation"])
    _print_messages(final_state["messages"])

    stored_scores = count_scores(settings.sqlite_path, final_state["session_id"])
    print("\n--- Final ---")
    print(f"Completed: {final_state['done']}")
    print(f"Scores stored in SQLite: {stored_scores}")
    print(f"SQLite DB: {settings.sqlite_path}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(prog="studyflow")
    subparsers = parser.add_subparsers(dest="command", required=True)

    start_parser = subparsers.add_parser("start-session")
    start_parser.add_argument("--goal", required=True, type=str)
    start_parser.add_argument("--duration", required=False, type=int, default=30)
    start_parser.add_argument(
        "--sources",
        required=False,
        type=str,
        default="generated",
        help="Comma-separated sources, e.g. notes.md,https://example.com,generated",
    )
    start_parser.add_argument(
        "--quiet-agents",
        action="store_true",
        help="Disable small live agent status prints during execution",
    )

    args = parser.parse_args()

    if args.command == "start-session":
        return run_start_session(
            goal=args.goal,
            duration_min=args.duration,
            sources_raw=args.sources,
            live_updates=not args.quiet_agents,
        )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
