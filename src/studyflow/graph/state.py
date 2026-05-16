from __future__ import annotations

from typing import TypedDict

class QuizItem(TypedDict):
    question: str
    expected_answer: str

class GraphState(TypedDict):
    session_id: str
    goal: str
    duration_min: int
    current_step: int
    plan: list[str]
    current_topic: str | None
    lesson: str | None
    quiz: list[QuizItem]
    last_score: float | None
    focus_events: list[str]
    messages: list[str]
    done: bool
