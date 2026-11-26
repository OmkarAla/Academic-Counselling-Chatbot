# Admissions assistant — design

Date: 2026-11-26
Status: approved (approach A); implemented in `server/`

## Intent

A student-facing assistant for the Amrita admission process only: eligibility,
entrance exams, dates, campuses, how to apply. It answers from official pages,
cites them, and refuses when the pages don't cover the question. It is not a
general counselling chatbot.

## Goals

- Every answer traceable to a URL plus the time it was fetched.
- No invented dates, fees or eligibility rules.
- Runs without an LLM key (local embeddings, extractive answers).
- One service, one corpus, one evaluation set.

## Non-goals

- Fees, scholarships or hostel charges (not in the indexed pages).
- Conversational memory, multi-turn context, accounts.
- Answers about programmes outside the indexed corpus.

## Anti-goals

- A chatbot that answers fluently from model memory.
- Committing Amrita's documents to a public repository.
- Quoting last year's deadline as current.

## Approaches considered

- **A. Consolidate to one FastAPI service** — fetch, chunk, embed, index,
  retrieve, cite, evaluate. Chosen.
- **B. Fix retrieval inside the existing Flask service** — keeps three runtimes
  (React, Express FAQ server, Flask RAG) and the dead Node RAG.
- **C. A plus production layer** — pgvector, ingestion admin, auth, rate limits.
  Deferred: it delays the resume-relevant work and duplicates storage.

## Decisions (A)

| Decision | Call | Why |
|---|---|---|
| Corpus | 8 curated amrita.edu URLs, fetched at ingest | current dates, no copyright in repo |
| Extraction | strip header/footer/nav, keep lines ≥ 30 chars, drop cross-page duplicates | trafilatura picked the mega-menu |
| Chunking | 900 chars, 150 overlap, paragraph-aware | keeps a date with its sentence |
| Embeddings | fastembed `bge-small-en-v1.5`; hashing fallback | no torch, works offline in tests |
| Retrieval | cosine top-8, max 3 per source, small title/URL boost | one page shouldn't crowd out others |
| Answer | paragraph-level extractive; Cohere rewrite if key present | cannot invent facts without a key |
| Refusal | below `MIN_SCORE` or no overlapping paragraph | honesty over coverage |
| Storage | npz + json under `server/data/` (gitignored) | no database dependency yet |

## Evaluation

`server/eval/questions.json` — 8 admission questions with an expected source.
Metric: recall@3. Current: **8/8**. Unit tests: 12.

## Known gaps

- Eligibility answers may quote a programme overview rather than the marks
  table; heading-aware chunking is the next step.
- Corpus is eight pages and not re-ingested on a schedule.
- No auth, rate limiting or feedback capture.
