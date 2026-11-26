"""Fetch the admissions corpus and build the index.

    python -m app.ingest
    python -m app.ingest --urls https://www.amrita.edu/admissions/
"""

from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import replace

from . import config
from .chunking import chunk_page
from .embedding import get_embedder
from .fetch import Page, fetch_page
from .index import Index


BOILERPLATE_MARKERS = (
    "amrita vishwa vidyapeetham is a multi-campus",
    "privacy policy",
    "terms of use",
    "cookie",
)


def is_boilerplate(paragraph: str) -> bool:
    lowered = paragraph.lower()
    return any(marker in lowered for marker in BOILERPLATE_MARKERS)


def drop_shared_boilerplate(pages: list[Page]) -> list[Page]:
    """Remove shared navigation, footer text and menu-shaped paragraphs."""
    counts: Counter[str] = Counter()
    for page in pages:
        for paragraph in {p.strip() for p in page.text.split("\n\n") if p.strip()}:
            counts[paragraph] += 1

    shared = {paragraph for paragraph, seen in counts.items() if seen >= 2}
    cleaned: list[Page] = []
    for page in pages:
        kept = [
            paragraph.strip()
            for paragraph in page.text.split("\n\n")
            if paragraph.strip()
            and paragraph.strip() not in shared
            and not is_boilerplate(paragraph)
        ]
        cleaned.append(replace(page, text="\n\n".join(kept)))
    return cleaned


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Ingest Amrita admissions pages")
    parser.add_argument("--urls", nargs="*", default=config.CORPUS_URLS)
    args = parser.parse_args(argv)

    embedder = get_embedder()
    pages: list[Page] = []

    for url in args.urls:
        try:
            pages.append(fetch_page(url))
        except Exception as error:  # one bad page should not kill the run
            print(f"skip {url}: {error}")

    if not pages:
        print("no pages fetched; nothing written")
        return 1

    chunks = []
    for page in drop_shared_boilerplate(pages):
        page_chunks = chunk_page(page)
        chunks.extend(page_chunks)
        print(f"{len(page_chunks):>3} chunks  {page.url}")

    if not chunks:
        print("no chunks produced; nothing written")
        return 1

    index = Index.build(chunks, embedder)
    index.save(config.INDEX_PATH, config.CHUNKS_PATH)
    print(
        f"\nindexed {len(chunks)} chunks from {len({c.url for c in chunks})} pages "
        f"with {embedder.name} -> {config.INDEX_PATH}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
