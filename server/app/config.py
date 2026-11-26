"""Configuration for the admissions assistant."""

from __future__ import annotations

import os
from pathlib import Path

DATA_DIR = Path(os.getenv("DATA_DIR", "data"))
INDEX_PATH = DATA_DIR / "index.npz"
CHUNKS_PATH = DATA_DIR / "chunks.json"

CORPUS_URLS: list[str] = [
    "https://www.amrita.edu/admissions/",
    "https://www.amrita.edu/admissions/notifications/",
    "https://www.amrita.edu/admissions/postgraduate/",
    "https://www.amrita.edu/program/btech-computer-science-and-engineering/",
    "https://www.amrita.edu/program/btech-in-artificial-intelligence-and-data-science/",
    "https://www.amrita.edu/campus/chennai/",
    "https://www.amrita.edu/campus/bengaluru/",
    "https://www.amrita.edu/campus/coimbatore/",
]

CHUNK_CHARS = 900
CHUNK_OVERLAP = 150
TOP_K = 8
MIN_SCORE = float(os.getenv("MIN_SCORE", "0.45"))
EMBEDDING_BACKEND = os.getenv("EMBEDDINGS", "fastembed")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "BAAI/bge-small-en-v1.5")

NOT_FOUND_ANSWER = (
    "I couldn't find that in the official Amrita admissions pages I have indexed. "
    "Admission rules and dates change every cycle, so please check "
    "https://www.amrita.edu/admissions/ or contact the admissions office directly "
    "rather than relying on an answer I can't cite."
)
