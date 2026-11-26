"""Answer generation.

Default is extractive: return the paragraph from the retrieved chunks that
actually overlaps the question, with citations. That works with no API key and
cannot invent a fee or a date. If COHERE_API_KEY is set, a model rewrites the
same evidence into a shorter answer, still constrained to those paragraphs.
"""

from __future__ import annotations

import os
import re

from .index import Hit

TOKEN = re.compile(r"[a-z0-9]+")
STOPWORDS = {
    "the", "a", "an", "and", "or", "of", "to", "in", "on", "for", "is", "are",
    "was", "were", "be", "been", "what", "when", "where", "which", "who", "how",
    "do", "does", "did", "can", "could", "should", "would", "i", "my", "me",
    "we", "our", "you", "your", "it", "its", "this", "that", "with", "about",
    "from", "at", "by", "as", "if", "not", "no", "any", "there", "their",
}


def _terms(text: str) -> set[str]:
    return {
        token
        for token in TOKEN.findall(text.lower())
        if len(token) > 2 and token not in STOPWORDS
    }


def select_evidence(query: str, hits: list[Hit], limit: int = 2) -> list[str]:
    """Paragraphs (not sentences) that overlap the question, best first.

    Programs pages are full of course lists; scoring whole paragraphs keeps the
    answer to a single coherent statement instead of a pile of fragments.
    """
    terms = _terms(query)
    scored: list[tuple[float, str]] = []

    for hit in hits:
        for paragraph in hit.chunk.text.split("\n\n"):
            candidate = paragraph.strip()
            if len(candidate) < 30:
                continue
            overlap = len(terms & _terms(candidate))
            if overlap == 0:
                continue
            scored.append((overlap * (0.5 + hit.score), candidate))

    scored.sort(key=lambda item: item[0], reverse=True)

    chosen: list[str] = []
    for _, paragraph in scored:
        if paragraph in chosen:
            continue
        chosen.append(paragraph)
        if len(chosen) == limit:
            break
    return chosen


def _cohere(query: str, evidence: list[str]) -> str | None:
    key = os.environ.get("COHERE_API_KEY")
    if not key:
        return None

    import cohere

    client = cohere.Client(key)
    response = client.chat(
        model="command-r",
        message=(
            "Answer the student's question using only the supplied documents. "
            "If the documents do not contain the answer, say so plainly. "
            "Do not add dates, fees or eligibility rules that are not in them."
        ),
        documents=[{"text": paragraph} for paragraph in evidence],
        temperature=0.1,
    )
    return response.text.strip()


def answer(query: str, evidence: list[str]) -> str:
    if not evidence:
        return ""
    try:
        generated = _cohere(query, evidence)
    except Exception:
        generated = None
    return generated or " ".join(evidence[:2])
