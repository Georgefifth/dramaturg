# Dramaturg

**Your story can be fictional. Its details shouldn't be.**

Dramaturg is an AI accuracy agent for screenwriters and studio crews. Paste a screenplay scene and it identifies externally verifiable claims, searches the live web for evidence, and returns a source-linked accuracy dossier. It does not silently rewrite the writer's work: every finding stays visible and the human keeps final authority.

Built for the **Parallel track** of [Agentic Cinema: The Blockbuster Hackathon](https://agentic-cinema.devpost.com/).

## The problem

Historical, legal, medical, technical, and location details often survive into production before anybody checks them systematically. By then, corrections affect props, locations, dialogue, schedules, and budgets. General-purpose writing assistants can produce plausible prose, but plausibility is not evidence.

Dramaturg inserts an evidence gate before production:

1. **Gemini extracts claims** worth checking from the scene.
2. **Parallel Search runs at runtime** for every claim and returns current, traceable excerpts.
3. **Gemini tests the claim against only that retrieved evidence.**
4. The dossier marks it `VERIFIED`, `INACCURATE`, `CONFLICTED`, or `UNVERIFIED`, with production-ready corrections and clickable sources.

Where most creative agents generate, Dramaturg verifies.

## Product modes

- **Live verification:** available when both API keys are configured. Every analysis calls Gemini and Parallel Search at runtime.
- **Evidence sample:** a clearly labeled, curated Berlin Wall scene for reliable product evaluation without credentials. Sample results are never presented as live calls.

## Architecture

```text
Screenplay scene
      │
      ▼
Gemini structured claim extraction
      │  claim + verification question + search queries
      ▼
Parallel Search API (one live search per claim)
      │  source URL + title + relevant excerpts
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
| `POST /api/analyze` | Runs the live Gemini → Parallel → Gemini verification pipeline |

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
- Source URLs and excerpts remain visible.
- The tool proposes corrections but never edits the screenplay automatically.

## License

MIT
