from __future__ import annotations

import argparse
from uuid import uuid4

from studyflow.graph.graph import build_graph
from studyflow.graph.state import GraphState


def build_initial_state(goal: str, duration_min: int) -> GraphState:
    return {
        "session_id": str(uuid4()),
        "goal": goal,
        "duration_min": duration_min,
        "current_step": 0,
        "plan": [],
        "current_topic": None,
        "lesson": None,
        "quiz": [],
        "last_score": None,
        "focus_events": [],
        "messages": [],
        "done": False,
    }


def run_start_session(goal: str, duration_min: int) -> int:
    graph = build_graph()
    initial_state = build_initial_state(goal=goal, duration_min=duration_min)
    final_state = graph.invoke(initial_state)

    print(f"\nSession ID: {final_state['session_id']}")
    print(f"Goal: {final_state['goal']}")
    print(f"Duration: {final_state['duration_min']} min")
    print("\n--- Plan ---")
    for idx, item in enumerate(final_state["plan"], start=1):
        print(f"{idx}. {item}")

    print("\n--- Messages ---")
    for msg in final_state["messages"]:
        print(f"- {msg}")

    print("\n--- Final ---")
    print(f"Completed: {final_state['done']}")
    print(f"Last score: {final_state['last_score']}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(prog="studyflow")
    subparsers = parser.add_subparsers(dest="command", required=True)

    start_parser = subparsers.add_parser("start-session")
    start_parser.add_argument("--goal", required=True, type=str)
    start_parser.add_argument("--duration", required=False, type=int, default=30)

    args = parser.parse_args()

    if args.command == "start-session":
        return run_start_session(goal=args.goal, duration_min=args.duration)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
