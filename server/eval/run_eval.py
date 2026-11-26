"""Retrieval evaluation: recall@3 against the indexed admissions corpus.

    python -m eval.run_eval
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app import config  # noqa: E402
from app.embedding import get_embedder  # noqa: E402
from app.index import Index  # noqa: E402


def main() -> int:
    index = Index.load(config.INDEX_PATH, config.CHUNKS_PATH)
    if not index.chunks:
        print("index is empty; run `python -m app.ingest` first")
        return 1

    embedder = get_embedder(index.embedder)
    questions = json.loads((ROOT / "eval" / "questions.json").read_text())

    passed = 0
    print(f"{'question':<66} {'result':<6} top source")
    print("-" * 110)
    for item in questions:
        hits = index.search(item["question"], embedder, k=3)
        urls = [hit.chunk.url for hit in hits]
        ok = item["expected_url"] in urls
        passed += int(ok)
        top = urls[0].removeprefix("https://www.amrita.edu") if urls else "-"
        print(f"{item['question'][:64]:<66} {'PASS' if ok else 'FAIL':<6} {top}")

    print(f"\nrecall@3: {passed}/{len(questions)}")
    return 0 if passed == len(questions) else 1


if __name__ == "__main__":
    raise SystemExit(main())
