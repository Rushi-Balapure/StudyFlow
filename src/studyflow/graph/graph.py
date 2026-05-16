from __future__ import annotations

from langgraph.graph import END, START, StateGraph

from studyflow.graph.nodes import (
    evaluator_node,
    focus_node,
    memory_node,
    planner_node,
    planner_route,
    tutor_node,
)
from studyflow.graph.state import GraphState


def build_graph():
    workflow = StateGraph(GraphState)

    workflow.add_node("planner", planner_node)
    workflow.add_node("focus", focus_node)
    workflow.add_node("tutor", tutor_node)
    workflow.add_node("evaluator", evaluator_node)
    workflow.add_node("memory", memory_node)

    workflow.add_edge(START, "planner")
    workflow.add_conditional_edges(
        "planner",
        planner_route,
        {"continue": "focus", "end": END},
    )
    workflow.add_edge("focus", "tutor")
    workflow.add_edge("tutor", "evaluator")
    workflow.add_edge("evaluator", "memory")
    workflow.add_edge("memory", "planner")

    return workflow.compile()

