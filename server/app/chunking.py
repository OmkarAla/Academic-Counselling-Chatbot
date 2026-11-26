"""Paragraph-aware chunking with character overlap.

Chunks carry their source URL, page title and fetch timestamp so every answer
can cite where it came from and when it was true.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass

from . import config
from .fetch import Page


@dataclass(frozen=True)
class Chunk:
    id: str
    url: str
    title: str
    fetched_at: str
    text: str


def _split_long(paragraph: str, size: int, overlap: int) -> list[str]:
    pieces: list[str] = []
    start = 0
    while start < len(paragraph):
        end = min(start + size, len(paragraph))
        pieces.append(paragraph[start:end])
        if end == len(paragraph):
            break
        start = max(end - overlap, start + 1)
    return pieces


def chunk_page(
    page: Page,
    size: int = config.CHUNK_CHARS,
    overlap: int = config.CHUNK_OVERLAP,
) -> list[Chunk]:
    paragraphs = [p.strip() for p in page.text.split("\n\n") if p.strip()]
    if not paragraphs:
        return []

    blocks: list[str] = []
    for paragraph in paragraphs:
        if len(paragraph) > size:
            blocks.extend(_split_long(paragraph, size, overlap))
        else:
            blocks.append(paragraph)

    chunks: list[str] = []
    current = ""
    for block in blocks:
        candidate = f"{current}\n\n{block}".strip() if current else block
        if len(candidate) <= size:
            current = candidate
            continue
        if current:
            chunks.append(current)
            tail = current[-overlap:] if overlap else ""
            budget = size - len(block) - 2
            if budget <= 0:
                tail = ""
            else:
                tail = tail[-budget:]
            current = f"{tail}\n\n{block}".strip() if tail else block
        else:
            current = block
    if current:
        chunks.append(current)

    result: list[Chunk] = []
    for index, text in enumerate(chunks):
        digest = hashlib.sha1(f"{page.url}:{index}".encode()).hexdigest()[:12]
        result.append(
            Chunk(
                id=digest,
                url=page.url,
                title=page.title,
                fetched_at=page.fetched_at,
                text=text,
            )
        )
    return result
