"""FastAPI service for the Amrita admissions assistant."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from . import config
from .embedding import get_embedder
from .generate import answer as compose_answer, select_evidence
from .index import Index


class ChatRequest(BaseModel):
    query: str = Field(min_length=2, max_length=500)


def create_app(
    index: Index | None = None,
    embedder=None,
    min_score: float | None = None,
) -> FastAPI:
    app = FastAPI(title="Amrita Admissions Assistant", version="2.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["*"],
    )

    loaded = index or Index.load(config.INDEX_PATH, config.CHUNKS_PATH)
    model = embedder or get_embedder(
        None if loaded.embedder in (None, "none") else loaded.embedder
    )
    threshold = min_score if min_score is not None else config.MIN_SCORE
    if model.name == "hashing":
        # Lexical scores live on a different scale than embedding cosine.
        threshold = threshold * 0.5

    @app.get("/health")
    def health() -> dict:
        return {
            "status": "ok",
            "chunks": len(loaded.chunks),
            "embedder": model.name,
        }

    @app.get("/documents")
    def documents() -> dict:
        seen: dict[str, dict] = {}
        for chunk in loaded.chunks:
            seen.setdefault(
                chunk.url,
                {"url": chunk.url, "title": chunk.title, "fetched_at": chunk.fetched_at},
            )
        return {"documents": list(seen.values())}

    @app.post("/chat")
    def chat(request: ChatRequest) -> dict:
        hits = loaded.search(request.query, model, k=config.TOP_K, max_per_source=3)
        kept = [hit for hit in hits if hit.score >= threshold]

        if not kept:
            return {
                "answer": config.NOT_FOUND_ANSWER,
                "grounded": False,
                "citations": [],
            }

        evidence = select_evidence(request.query, kept)
        if not evidence:
            return {
                "answer": config.NOT_FOUND_ANSWER,
                "grounded": False,
                "citations": [],
            }

        citations: list[dict] = []
        for hit in kept:
            if not any(paragraph in hit.chunk.text for paragraph in evidence):
                continue
            if any(c["url"] == hit.chunk.url for c in citations):
                continue
            citations.append(
                {
                    "url": hit.chunk.url,
                    "title": hit.chunk.title,
                    "fetched_at": hit.chunk.fetched_at,
                    "score": round(hit.score, 3),
                }
            )
            if len(citations) == 3:
                break

        return {
            "answer": compose_answer(request.query, evidence),
            "grounded": True,
            "citations": citations,
        }

    return app


app = create_app()
