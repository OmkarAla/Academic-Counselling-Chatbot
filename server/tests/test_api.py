from fastapi.testclient import TestClient

from app.chunking import Chunk
from app.embedding import HashingEmbedder
from app.index import Index
from app.main import create_app


def client() -> TestClient:
    chunks = [
        Chunk(
            id="a",
            url="https://www.amrita.edu/admissions/",
            title="Admissions",
            fetched_at="2026-11-26T00:00:00+00:00",
            text=(
                "Applications for B.Tech 2027 opened on November 7, 2026. "
                "Students may apply through both AEEE and JEE Main pathways."
            ),
        ),
        Chunk(
            id="b",
            url="https://www.amrita.edu/admissions/notifications/",
            title="Notifications",
            fetched_at="2026-11-26T00:00:00+00:00",
            text="AEEE 2027 will be conducted between April 15 and May 7, 2027.",
        ),
    ]
    index = Index.build(chunks, HashingEmbedder())
    app = create_app(index=index, embedder=HashingEmbedder(), min_score=0.2)
    return TestClient(app)


def test_health_reports_chunk_count():
    response = client().get("/health")

    assert response.status_code == 200
    assert response.json()["chunks"] == 2


def test_documents_lists_sources():
    urls = {doc["url"] for doc in client().get("/documents").json()["documents"]}

    assert "https://www.amrita.edu/admissions/" in urls


def test_chat_returns_grounded_answer_with_citation():
    response = client().post("/chat", json={"query": "when is AEEE 2027 conducted"})

    body = response.json()
    assert response.status_code == 200
    assert body["grounded"] is True
    assert "April" in body["answer"] or "AEEE" in body["answer"]
    assert body["citations"][0]["url"].startswith("https://www.amrita.edu/")


def test_chat_refuses_when_nothing_matches():
    response = client().post("/chat", json={"query": "xyzzy plugh quux"})

    body = response.json()
    assert body["grounded"] is False
    assert body["citations"] == []
    assert "couldn't find" in body["answer"].lower()


def test_rejects_empty_query():
    assert client().post("/chat", json={"query": ""}).status_code == 422
