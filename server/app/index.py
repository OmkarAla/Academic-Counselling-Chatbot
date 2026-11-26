"""Vector index over chunks, persisted as a small npz + json pair."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
import re

import numpy as np

from .chunking import Chunk
from .embedding import Embedder

TOKEN = re.compile(r"[a-z0-9]+")


@dataclass(frozen=True)
class Hit:
    chunk: Chunk
    score: float


class Index:
    def __init__(self, chunks: list[Chunk], vectors: np.ndarray, embedder: str) -> None:
        if len(chunks) != len(vectors):
            raise ValueError("chunks and vectors must align")
        self.chunks = chunks
        self.vectors = vectors.astype(np.float32)
        self.embedder = embedder

    @classmethod
    def build(cls, chunks: list[Chunk], embedder: Embedder) -> "Index":
        vectors = embedder.embed([chunk.text for chunk in chunks])
        return cls(chunks, vectors, embedder.name)

    def search(
        self,
        query: str,
        embedder: Embedder,
        k: int = 5,
        max_per_source: int = 1,
    ) -> list[Hit]:
        if not self.chunks:
            return []
        query_vector = embedder.embed([query])[0]
        scores = self.vectors @ query_vector

        # A page that happens to contain many chunks should not crowd out the
        # page that actually answers the question: one hit per source by
        # default, plus a small boost when the query matches the page title or
        # URL (short queries carry little semantic signal on their own).
        tokens = set(TOKEN.findall(query.lower()))
        for position, chunk in enumerate(self.chunks):
            metadata = f"{chunk.title} {chunk.url}".lower()
            if tokens & set(TOKEN.findall(metadata)):
                scores[position] += 0.03

        order = np.argsort(-scores)
        picked: list[Hit] = []
        per_source: dict[str, int] = {}
        for position in order:
            chunk = self.chunks[int(position)]
            if per_source.get(chunk.url, 0) >= max_per_source:
                continue
            picked.append(Hit(chunk, float(scores[int(position)])))
            per_source[chunk.url] = per_source.get(chunk.url, 0) + 1
            if len(picked) == max(1, k):
                break
        return picked

    def save(self, index_path: Path, chunks_path: Path) -> None:
        index_path.parent.mkdir(parents=True, exist_ok=True)
        np.savez_compressed(
            index_path, vectors=self.vectors, embedder=np.array([self.embedder])
        )
        payload = [
            {
                "id": chunk.id,
                "url": chunk.url,
                "title": chunk.title,
                "fetched_at": chunk.fetched_at,
                "text": chunk.text,
            }
            for chunk in self.chunks
        ]
        chunks_path.write_text(json.dumps(payload), encoding="utf-8")

    @classmethod
    def load(cls, index_path: Path, chunks_path: Path) -> "Index":
        if not index_path.exists() or not chunks_path.exists():
            return cls([], np.zeros((0, 384), dtype=np.float32), "none")

        data = np.load(index_path, allow_pickle=False)
        vectors = data["vectors"]
        embedder = str(data["embedder"][0])
        payload = json.loads(chunks_path.read_text(encoding="utf-8"))
        chunks = [
            Chunk(
                id=item["id"],
                url=item["url"],
                title=item["title"],
                fetched_at=item["fetched_at"],
                text=item["text"],
            )
            for item in payload
        ]
        return cls(chunks, vectors, embedder)
