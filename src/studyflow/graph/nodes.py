from __future__ import annotations

from typing import Any

from studyflow.config import get_settings
from studyflow.graph.state import EvaluationResult, GraphState, QuizItem
from studyflow.llm.provider import OpenAICompatibleProvider, extract_json_object
from studyflow.store.repository import add_event, add_score


def _append_message(state: GraphState, text: str) -> list[str]:
    return [*state["messages"], text]


def _status(state: GraphState, text: str) -> None:
    if state["live_updates"]:
        print(text)


def _provider() -> OpenAICompatibleProvider:
    settings = get_settings()
    return OpenAICompatibleProvider(
        model_name=settings.model_name,
        base_url=settings.base_url,
        api_key=settings.api_key,
    )


def _fallback_plan(goal: str) -> list[str]:
    return [
        f"Foundations of {goal}",
        f"Core concepts of {goal}",
        f"Practice and review of {goal}",
    ]


def _coerce_plan(data: dict[str, Any], goal: str) -> list[str]:
    plan_raw = data.get("plan")
    if not isinstance(plan_raw, list):
        return _fallback_plan(goal)

    cleaned = [str(item).strip() for item in plan_raw if str(item).strip()]
    return cleaned[:5] if cleaned else _fallback_plan(goal)


def _coerce_quiz(data: dict[str, Any], topic: str) -> list[QuizItem]:
    items_raw = data.get("quiz")
    if not isinstance(items_raw, list):
        return [{"question": f"What is the key idea in {topic}?", "expected_answer": "Short explanation."}]

    quiz: list[QuizItem] = []
    for item in items_raw[:3]:
        if not isinstance(item, dict):
            continue
        question = str(item.get("question", "")).strip()
        expected = str(item.get("expected_answer", "")).strip()
        if question and expected:
            quiz.append({"question": question, "expected_answer": expected})

    if quiz:
        return quiz
    return [{"question": f"What is the key idea in {topic}?", "expected_answer": "Short explanation."}]


def _parse_evaluation(parsed: dict[str, Any]) -> EvaluationResult:
    score_raw = parsed.get("score", 0.5)
    try:
        score = float(score_raw)
    except (TypeError, ValueError):
        score = 0.5
    score = max(0.0, min(score, 1.0))
    feedback = str(parsed.get("feedback", "Keep practicing this concept.")).strip()
    return {"score": round(score, 2), "feedback": feedback}


def planner_node(state: GraphState) -> dict[str, Any]:
    _status(state, "[planner] selecting next study topic")
    plan = state["plan"]
    if not plan:
        _status(state, "[planner] generating study plan")
        prompt = (
            "Create a short prerequisite-aware study plan as JSON.\n"
            "Return ONLY JSON: {\"plan\": [\"topic1\", \"topic2\", ...]}.\n"
            f"Goal: {state['goal']}\n"
            f"Duration minutes: {state['duration_min']}\n"
            f"Content sources: {', '.join(state['content_sources'])}"
        )
        raw = _provider().chat(
            "You are a strict study planner. Return valid JSON only.",
            prompt,
        )
        plan = _coerce_plan(extract_json_object(raw), state["goal"])

    if state["current_step"] >= len(plan):
        _status(state, "[planner] session plan complete")
        add_event(
            state["db_path"],
            state["session_id"],
            state["current_step"],
            "planner",
            {"status": "completed"},
        )
        return {
            "plan": plan,
            "current_topic": None,
            "done": True,
            "messages": _append_message(state, "Planner: session objective completed."),
        }

    topic = plan[state["current_step"]]
    _status(state, f"[planner] next topic: {topic}")
    add_event(
        state["db_path"],
        state["session_id"],
        state["current_step"],
        "planner",
        {"topic": topic},
    )
    return {
        "plan": plan,
        "current_topic": topic,
        "done": False,
        "messages": _append_message(state, f"Planner: next topic -> {topic}"),
    }


def focus_node(state: GraphState) -> dict[str, Any]:
    _status(state, "[focus] monitoring for distractions")
    event = "Focus: monitoring active (warn + soft-block policy loaded)."
    add_event(
        state["db_path"],
        state["session_id"],
        state["current_step"],
        "focus",
        {"event": event},
    )
    return {
        "focus_events": [*state["focus_events"], event],
        "messages": _append_message(state, event),
    }


def tutor_node(state: GraphState) -> dict[str, Any]:
    topic = state["current_topic"] or "General topic"
    _status(state, f"[tutor] preparing lesson for: {topic}")
    prompt = (
        "Teach this topic for a beginner in concise format.\n"
        "Include:\n"
        "1) core idea\n"
        "2) one concrete example\n"
        "3) two quick self-check questions\n"
        f"Topic: {topic}\n"
        f"Goal context: {state['goal']}"
    )
    lesson = _provider().chat(
        "You are a practical tutor. Be clear and concise.",
        prompt,
    )
    add_event(
        state["db_path"],
        state["session_id"],
        state["current_step"],
        "tutor",
        {"topic": topic},
    )
    return {
        "lesson": lesson,
        "messages": _append_message(state, f"Tutor: delivered lesson for {topic}."),
    }


def evaluator_node(
    state: GraphState,
    user_answer: str | None = None,
) -> dict[str, Any]:
    topic = state["current_topic"] or "General topic"
    _status(state, f"[evaluator] creating quiz and scoring for: {topic}")
    lesson = state["lesson"] or ""

    # Determine if we need to show the question (new interactive mode)
    needs_question = user_answer is None or user_answer.strip() == ""

    prompt = (
        f"Given the lesson, create a micro-quiz and readiness estimate.\n"
        f"Return ONLY JSON with this exact schema:\n"
        "{\"question\": \"...\", \"expected_answer\": \"...\", \"user_answer\": \"...\"},\n"
        "\"score\": 0.0,\n"
        "\"feedback\": \"...\"}\n"
        f"Score must be between 0 and 1.\n"
        f"Topic: {topic}\n"
        f"Lesson:\n{lesson}"
    )

    raw = _provider().chat(
        "You are an evaluator. Return strict valid JSON only.",
        prompt,
    )
    parsed = extract_json_object(raw)
    quiz = _coerce_quiz(parsed, topic)
    evaluation = _parse_evaluation(parsed)

    # Track attempt count and answer for adaptive routing
    if user_answer is not None:
        state["attempt_count"] += 1
        state["learner_answer"] = user_answer.strip()

    add_event(
        state["db_path"],
        state["session_id"],
        state["current_step"],
        "evaluator",
        {"topic": topic, "score": evaluation["score"]},
    )
    add_score(
        state["db_path"],
        state["session_id"],
        state["current_step"],
        topic,
        evaluation["score"],
        evaluation["feedback"],
    )

    # Adaptive routing based on user response
    if needs_question and state["attempt_count"] < 2:
        _status(state, f"[evaluator] showing question for: {topic}")
        return {
            "quiz": quiz,
            "evaluation": evaluation,
            "messages": _append_message(state, f"Evaluator: score={evaluation['score']:.2f}.",),
        }
    elif user_answer is not None and state["attempt_count"] >= 3:
        # Strong performance - advance
        _status(state, f"[evaluator] strong performance for {topic}, advancing")
        return {
            "quiz": [],
            "evaluation": evaluation,
            "messages": _append_message(state, f"Evaluator: advanced to next topic.",),
        }
    else:
        # Weak performance - remediate
        _status(state, f"[evaluator] weak performance for {topic}, remediating")
        return {
            "quiz": quiz,
            "evaluation": evaluation,
            "messages": _append_message(state, f"Evaluator: score={evaluation['score']:.2f}. Remediate this topic.",),
        }


def memory_node(state: GraphState) -> dict[str, Any]:
    _status(state, "[memory] saving session progress")
    next_step = state["current_step"] + 1
    add_event(
        state["db_path"],
        state["session_id"],
        state["current_step"],
        "memory",
        {"next_step": next_step},
    )
    return {
        "current_step": next_step,
        "messages": _append_message(state, f"Memory: persisted step {next_step}.",),
    }


def planner_route(state: GraphState) -> str:
    if state["done"] and state["learner_answer"] is not None:
        # Session complete - check for remediation needed
        if state["attempt_count"] >= 3:
            _status(state, "[planner] session complete with strong performance")
            return "end"
        else:
            _status(state, "[planner] session complete, continuing to next topic")
            return "continue"
    return "continue"


def planner_route(state: GraphState) -> str:
    return "end" if state["done"] else "continue"
