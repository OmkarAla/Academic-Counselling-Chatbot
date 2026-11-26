"""Embedding backends.

`fastembed` gives real semantic embeddings (ONNX, no torch). The hashing
backend exists so tests and offline runs work without downloading a model;
it is lexical, not semantic, and the README says so.
"""

from __future__ import annotations

import hashlib
import re
from typing import Protocol

import numpy as np

DIMENSION = 384
TOKEN = re.compile(r"[a-z0-9]+")


class Embedder(Protocol):
    name: str

    def embed(self, texts: list[str]) -> np.ndarray: ...


def _normalise(matrix: np.ndarray) -> np.ndarray:
    norms = np.linalg.norm(matrix, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    return matrix / norms


class HashingEmbedder:
    """Deterministic lexical fallback: hashed bag of words, L2-normalised."""

    name = "hashing"

    def embed(self, texts: list[str]) -> np.ndarray:
        rows = np.zeros((len(texts), DIMENSION), dtype=np.float32)
        for row, text in enumerate(texts):
            counts: dict[int, int] = {}
            for token in TOKEN.findall(text.lower()):
                index = int.from_bytes(
                    hashlib.blake2b(token.encode(), digest_size=4).digest(), "big"
                ) % DIMENSION
                counts[index] = counts.get(index, 0) + 1
            for index, count in counts.items():
                rows[row, index] = 1.0 + np.log(count)
        return _normalise(rows)


class FastEmbedder:
    name = "fastembed"

    def __init__(self, model: str) -> None:
        from fastembed import TextEmbedding

        self._model = TextEmbedding(model)

    def embed(self, texts: list[str]) -> np.ndarray:
        vectors = list(self._model.embed(texts))
        return _normalise(np.asarray(vectors, dtype=np.float32))


def get_embedder(backend: str | None = None) -> Embedder:
    from . import config

    chosen = backend or config.EMBEDDING_BACKEND
    if chosen == "hashing":
        return HashingEmbedder()
    if chosen == "fastembed":
        try:
            return FastEmbedder(config.EMBEDDING_MODEL)
        except Exception:  # model download or onnx runtime unavailable
            return HashingEmbedder()
    raise ValueError(f"unknown embedding backend: {chosen}")
