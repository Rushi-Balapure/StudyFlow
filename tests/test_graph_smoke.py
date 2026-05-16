from studyflow.cli import build_initial_state
from studyflow.graph.graph import build_graph


def test_graph_runs_end_to_end() -> None:
    graph = build_graph()
    state = build_initial_state(goal="linear algebra", duration_min=25)
    result = graph.invoke(state)

    assert result["done"] is True
    assert len(result["plan"]) == 3
    assert result["current_step"] == 3
    assert result["last_score"] is not None
    assert len(result["messages"]) > 0
