# Dramaturg

**Your story can be fictional. Its details shouldn't be.**

Dramaturg is an AI accuracy agent for screenwriters and studio crews. Paste a screenplay scene and it identifies externally verifiable claims, searches the live web for evidence, and returns a source-linked accuracy dossier. It does not silently rewrite the writer's work: every finding stays visible and the human keeps final authority.

Built for the **Parallel track** of [Agentic Cinema: The Blockbuster Hackathon](https://agentic-cinema.devpost.com/).

**Live product:** https://dramaturg.onrender.com

## The problem

Historical, legal, medical, technical, and location details often survive into production before anybody checks them systematically. By then, corrections affect props, locations, dialogue, schedules, and budgets. General-purpose writing assistants can produce plausible prose, but plausibility is not evidence.

Dramaturg inserts an evidence gate before production:

1. **Gemini extracts claims** worth checking from the scene.
2. **Parallel Search runs at runtime** for every claim and returns current, traceable excerpts.
3. **Gemini audits evidence coverage** and identifies the most consequential unresolved gaps.
4. **Parallel runs up to two targeted second searches** using Gemini's refined queries.
5. **Gemini tests each claim against the completed evidence record.**
6. The dossier marks it `VERIFIED`, `INACCURATE`, `CONFLICTED`, or `UNVERIFIED`, with production-ready corrections and clickable sources.

Where most creative agents generate, Dramaturg verifies.

## Product modes

- **Live verification:** available when both API keys are configured. Every new analysis calls Gemini and Parallel Search at runtime.
- **Evidence sample:** a clearly labeled, curated Berlin Wall scene for reliable product evaluation without credentials. Sample results are never presented as live calls.

## Review workflow

- Paste a scene or import a local `.txt` / `.fountain` file; file contents are not uploaded until the writer starts live research.
- Long analyses run as protected background jobs, and the interface polls real pipeline events instead of displaying simulated progress.
- Exact screenplay quotes are located deterministically and highlighted by verdict status.
- Selecting a highlight opens its claim-level finding; selecting a finding returns to the original line.
- Every source is classified as `SUPPORTS`, `REFUTES`, `CONTEXT`, or `CONFLICTS`, and findings carry explicit source IDs.
- Writers close the loop with `Accept fix`, `Keep as written`, or `Needs research`; decisions persist locally across refreshes.
- Accepting a fix applies only its exact replacement to a reversible Revision Workspace with visible deletions and insertions.
- The revised scene can be copied directly, while JSON export includes original text, revised text, evidence, and the complete Decision Log.
- Repeated scenes use an in-memory evidence cache, while per-IP, daily, and concurrency limits protect public provider budgets.

## Architecture

```text
Screenplay scene
      │
      ▼
Gemini structured claim extraction
      │  claim + verification question + search queries
      ▼
Parallel Search API (initial search per claim)
      │  source URL + title + relevant excerpts
      ▼
Gemini coverage audit
      │  sufficient ────────────────┐
      │  evidence gap              │
      ▼                            │
Parallel targeted re-search        │
      │  deduplicated evidence     │
      └────────────────────────────┘
                    │
                    ▼
Gemini evidence-constrained verification
      │
      ▼
Source-linked accuracy dossier + human final decision
```

The backend uses the official `google-genai` and `parallel-web` Python SDKs. No non-Google AI model or external agent framework is used.

## Run locally

Requires Python 3.12+.

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
uvicorn app:app --reload
```

Open <http://127.0.0.1:8000>. The evidence sample works immediately.

For live verification:

```bash
export GEMINI_API_KEY="your-key"
export PARALLEL_API_KEY="your-key"
export GEMINI_MODEL="gemini-3.5-flash"
export GEMINI_AUDIT_MODEL="gemini-3.5-flash-lite"
export GEMINI_REQUEST_DELAY_SECONDS="30"
uvicorn app:app --reload
```

`GOOGLE_API_KEY` is also accepted in place of `GEMINI_API_KEY`. Never commit API keys.

## API

| Endpoint | Purpose |
|---|---|
| `GET /api/health` | Health check |
| `GET /api/config` | Reports whether live services are configured; never exposes keys |
| `GET /api/demo-scene` | Returns the sample screenplay scene |
| `GET /api/demo` | Returns the explicitly labeled sample dossier |
| `POST /api/jobs` | Starts a protected background research job, or immediately returns a cached dossier |
| `GET /api/jobs/{job_id}` | Returns real pipeline phase, progress, failure, or completed dossier |
| `POST /api/analyze` | Synchronous compatibility endpoint for the same live pipeline |

Live request:

```bash
curl -X POST http://127.0.0.1:8000/api/analyze \
  -H 'Content-Type: application/json' \
  -d '{"scene":"INT. NEWSROOM — NIGHT ..."}'
```

## Deploy to Google Cloud Run

```bash
gcloud run deploy dramaturg \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars GEMINI_MODEL=gemini-3.5-flash \
  --set-secrets GEMINI_API_KEY=gemini-api-key:latest,PARALLEL_API_KEY=parallel-api-key:latest
```

Create the referenced secrets in Google Cloud Secret Manager before deployment. Cloud Run builds the included Dockerfile and listens on the injected `$PORT`.

## Verification

```bash
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python -m py_compile app.py models.py service.py demo_data.py
```

## Responsible design

- Findings must be based on retrieved evidence, not unsupported model memory.
- Conflicting credible sources are preserved as `CONFLICTED` rather than collapsed into false certainty.
- Missing evidence becomes `UNVERIFIED`.
- Source URLs, excerpts, evidence stances, and citation IDs remain visible.
- The tool proposes an exact replacement but applies it only after the writer explicitly selects `Accept fix`.
- Original text remains visible beside every accepted change, and all revisions are reversible.
- Writer overrides and research decisions persist locally and are preserved in the exported production record.
- Public analysis is rate-limited, single-concurrency, and cached to protect API budgets.

## License

MIT
