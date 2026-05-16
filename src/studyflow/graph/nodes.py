from __future__ import annotations

from typing import Any

from studyflow.graph.state import GraphState, QuizItem


def _append_message(state: GraphState, text: str) -> list[str]:
    return [*state["messages"], text]


def _starter_plan(goal: str) -> list[str]:
    return [
        f"Foundations of {goal}",
        f"Core concepts of {goal}",
        f"Practice and review of {goal}",
    ]


def planner_node(state: GraphState) -> dict[str, Any]:
    plan = state["plan"] or _starter_plan(state["goal"])
    if state["current_step"] >= len(plan):
        return {
            "plan": plan,
            "current_topic": None,
            "done": True,
            "messages": _append_message(state, "Planner: session objective completed."),
        }
    return {
        "plan": plan,
        "current_topic": plan[state["current_step"]],
        "done": False,
        "messages": _append_message(
            state,
            f"Planner: next topic -> {plan[state['current_step']]}",
        ),
    }


def focus_node(state: GraphState) -> dict[str, Any]:
    event = "Focus: monitoring active (warn + soft-block enabled)."
    return {
        "focus_events": [*state["focus_events"], event],
        "messages": _append_message(state, event),
    }


def tutor_node(state: GraphState) -> dict[str, Any]:
    topic = state["current_topic"] or "No topic"
    lesson = (
        f"Topic: {topic}\n"
        "1) Understand the core idea.\n"
        "2) Connect it to one practical example.\n"
        "3) Explain it back in your own words."
    )
    return {
        "lesson": lesson,
        "messages": _append_message(state, f"Tutor: delivered lesson for {topic}."),
    }


def evaluator_node(state: GraphState) -> dict[str, Any]:
    topic = state["current_topic"] or "general topic"
    quiz: list[QuizItem] = [
        {
            "question": f"What is the main idea behind '{topic}'?",
            "expected_answer": "A concise explanation in your own words.",
        }
    ]
    score = round(min(1.0, 0.6 + (0.1 * state["current_step"])), 2)
    return {
        "quiz": quiz,
        "last_score": score,
        "messages": _append_message(state, f"Evaluator: score={score:.2f}."),
    }


def memory_node(state: GraphState) -> dict[str, Any]:
    next_step = state["current_step"] + 1
    return {
        "current_step": next_step,
        "messages": _append_message(state, f"Memory: persisted step {next_step}."),
    }


def planner_route(state: GraphState) -> str:
    return "end" if state["done"] else "continue"
