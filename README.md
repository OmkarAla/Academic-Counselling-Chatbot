# Amrita Admissions Assistant

An unofficial assistant that answers prospective-student questions about Amrita Vishwa Vidyapeetham admissions, **from the official pages, with citations and a publication date on every answer**.

Built for the admission process only: eligibility, entrance exams, dates, campuses, application steps. If the answer isn't in the indexed pages, it says so instead of guessing.

> Not affiliated with Amrita Vishwa Vidyapeetham. Admission rules and dates change every cycle — every answer carries the URL and the time it was fetched.

## How it works

```
amrita.edu pages ──fetch──> strip nav/footer ──> chunk (900 chars, 150 overlap)
     ──embed (fastembed, bge-small)──> index (npz + json)
question ──embed──> top-k with per-source diversity ──> evidence selection
     ──> extractive answer (default) or Cohere rewrite (if key set)
     ──> {answer, citations[url,title,fetched_at,score], grounded}
```

Design decisions worth knowing:

- **URL ingestion, not committed PDFs.** The corpus is fetched live into `server/data/` (gitignored) so dates stay current and no copyrighted material sits in the repo.
- **Evidence selection is paragraph-level.** Program pages are full of course lists; sentence-level scoring produced incoherent answers, so the answer is a whole paragraph that overlaps the question.
- **It refuses.** Below the similarity threshold, or when no paragraph overlaps the question, the API returns `grounded: false` and points at the admissions office.
- **No API key required.** `fastembed` runs locally (ONNX, no torch); the extractive answer needs no model. `COHERE_API_KEY` upgrades the wording, not the facts.

## Run

```bash
cd server
python -m pip install -r requirements.txt
python -m app.ingest                 # fetch 8 admissions pages, build the index
python -m uvicorn app.main:app --port 8080
```

```bash
curl -s localhost:8080/chat -H 'content-type: application/json' \
  -d '{"query":"When is the AEEE 2027 exam?"}'
```

Endpoints: `GET /health`, `GET /documents`, `POST /chat`.

Environment: `EMBEDDINGS=fastembed|hashing`, `MIN_SCORE` (default 0.45), `DATA_DIR`, `COHERE_API_KEY` (optional).

## Deploy

One Vercel project at the repo root, two services (`vercel.json`):

| Service | Root | Framework | Public path |
|---|---|---|---|
| `api` | `server` | FastAPI | `/api/*` |
| `web` | `chatbot` | Create React App | everything else |

The API service runs `pip install -r requirements.txt && python -m app.ingest` at build time, so the index ships with the deployment. The front end calls `/api` on the same origin, so no `REACT_APP_API_URL` is needed.

If the Python bundle with `fastembed` exceeds Vercel's function size limit, run `server/` on Render, Railway or Fly instead and set `REACT_APP_API_URL` to that origin.

## Quality

- `pytest -q` → **12 passed** (chunking, index search and persistence, API contract, refusal path).
- `python -m eval.run_eval` → **recall@3: 8/8** on eight admission questions with an expected source page.

## Honest limitations

- **Extractive answers quote.** The default answer is the best-matching paragraph, so it can be broader than a human would phrase it. Cohere improves this; without a key the trade-off is deliberate — it cannot invent a fee or a date.
- **Eligibility wording is buried on program pages.** Retrieval finds the page; the quoted paragraph may be a programme overview rather than the marks table. Heading-aware chunking is the next fix.
- **The corpus is eight pages.** Topics outside it (fees, scholarships, hostel charges) correctly fall back to "not in the indexed pages".
- **No auth or rate limiting**, and no scheduled re-ingestion yet. Both are required before this is more than a demo.
- **Unofficial.** Always verify against amrita.edu before acting.
