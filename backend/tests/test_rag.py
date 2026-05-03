from pathlib import Path

from app.rag.manager import RAGManager


def test_rag_routes_learning_and_job_queries(monkeypatch):
    monkeypatch.setattr(RAGManager, "_load_model", staticmethod(lambda: None))
    manager = RAGManager(Path("app/data/rag"))
    manager.build()

    assert manager.route("how should I learn testing?") == ["learning"]
    assert manager.route("what is required for backend job roles?") == ["job"]
    assert manager.route("how do I learn job expectations?") == ["learning", "job"]
    _, reason = manager.route_with_reason("how do I learn job expectations?")
    assert "merged" in reason.lower()

    results = manager.retrieve("backend testing roadmap", ["learning", "job"], top_k=3)
    assert results
    assert results[0].source in {"learning", "job"}
    assert results[0].source_label
    assert results[0].chunk_id
