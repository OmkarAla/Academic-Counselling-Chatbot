from app.chunking import Chunk
from app.embedding import HashingEmbedder
from app.index import Index


def chunk(index: int, text: str, url: str = "https://example.edu/a") -> Chunk:
    return Chunk(
        id=f"c{index}",
        url=url,
        title="Admissions",
        fetched_at="2026-11-26T00:00:00+00:00",
        text=text,
    )


def test_search_returns_the_matching_chunk_first():
    chunks = [
        chunk(0, "Hostel accommodation and mess facilities for students."),
        chunk(1, "B.Tech applications open in November and the AEEE exam runs in April."),
        chunk(2, "Sports facilities include a swimming pool and athletics track."),
    ]
    index = Index.build(chunks, HashingEmbedder())

    hits = index.search("when is the AEEE exam", HashingEmbedder(), k=2, max_per_source=2)

    assert hits[0].chunk.id == "c1"
    assert hits[0].score >= hits[1].score


def test_empty_index_returns_no_hits():
    index = Index.build([], HashingEmbedder())

    assert index.search("anything", HashingEmbedder()) == []


def test_round_trip_save_and_load(tmp_path):
    chunks = [chunk(0, "Eligibility for B.Tech requires Physics, Chemistry and Mathematics.")]
    index = Index.build(chunks, HashingEmbedder())

    index.save(tmp_path / "index.npz", tmp_path / "chunks.json")
    loaded = Index.load(tmp_path / "index.npz", tmp_path / "chunks.json")

    assert loaded.embedder == "hashing"
    assert len(loaded.chunks) == 1
    assert loaded.chunks[0].text.startswith("Eligibility")
