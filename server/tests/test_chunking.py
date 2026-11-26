from app.chunking import chunk_page
from app.fetch import Page


def page(text: str) -> Page:
    return Page(
        url="https://example.edu/admissions/",
        title="Admissions",
        text=text,
        fetched_at="2026-11-26T00:00:00+00:00",
    )


def test_splits_and_keeps_all_text():
    text = "\n\n".join(f"Paragraph {i} " + "x" * 200 for i in range(6))

    chunks = chunk_page(page(text), size=500, overlap=100)

    assert len(chunks) > 1
    assert all(len(chunk.text) <= 500 for chunk in chunks)
    joined = " ".join(chunk.text for chunk in chunks)
    assert "Paragraph 0" in joined
    assert "Paragraph 5" in joined


def test_chunks_carry_source_metadata_and_unique_ids():
    text = "\n\n".join("y" * 300 for _ in range(4))

    chunks = chunk_page(page(text), size=400, overlap=50)

    assert all(chunk.url.endswith("/admissions/") for chunk in chunks)
    assert all(chunk.fetched_at for chunk in chunks)
    assert len({chunk.id for chunk in chunks}) == len(chunks)


def test_long_paragraph_is_split():
    chunks = chunk_page(page("z" * 2000), size=500, overlap=50)

    assert len(chunks) >= 4
    assert all(len(chunk.text) <= 500 for chunk in chunks)


def test_empty_page_produces_no_chunks():
    assert chunk_page(page("   ")) == []
