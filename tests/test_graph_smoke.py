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
