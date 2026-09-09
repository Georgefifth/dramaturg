# Devpost submission draft

**Live product:** https://dramaturg.onrender.com

**Source code:** https://github.com/Georgefifth/dramaturg

## Inspiration

Film production has many creative tools, but one quiet bottleneck remains manual: checking whether a scene's real-world details are actually true. A wrong date, border procedure, medical step, or period technology can survive until props, locations, and dialogue are already expensive to change. We built the AI equivalent of a dramaturg—the production specialist who protects factual integrity.

## What it does

Dramaturg reads a screenplay scene and creates a source-linked accuracy dossier. Gemini first isolates claims that can be checked externally. Parallel Search then retrieves live web evidence for each claim. Gemini compares each claim only against that evidence and marks it Verified, Inaccurate, Conflicted, or Unverified. Exact claims are highlighted in the original screenplay, every source is classified by evidentiary stance, and findings cite source IDs directly. Writers close the review with Accept fix, Keep as written, or Needs research; the exported Decision Log preserves their final authority.

## How we built it

The web application uses FastAPI and a responsive vanilla JavaScript interface deployed in a container suitable for Google Cloud Run. It uses Google's official `google-genai` SDK for structured claim extraction and evidence-constrained verification. It uses Parallel's official `parallel-web` SDK at runtime, executing one focused Search API request for every extracted claim. Typed Pydantic contracts carry claims, sources, verdicts, and the final dossier through the pipeline.

## Challenges we ran into

The central design challenge was avoiding a second hallucination layer in the verifier. We constrained verification to retrieved excerpts, exposed every source, preserved disagreements as Conflicted, and made insufficient evidence an explicit Unverified result. We also separated live analysis from a clearly labeled evidence sample so evaluators are never misled about whether an API call occurred.

## Accomplishments that we're proud of

- A narrow, complete workflow for a real film-production role instead of another general creative generator.
- Runtime integration of both Gemini and Parallel Search, visible in the source code.
- Claim-level provenance, exact script highlighting, source stances, and four honest evidence states.
- A human decision loop with production-ready corrections and an exportable audit record.
- Cache, per-IP limits, a global budget ceiling, and single concurrency to protect public API credentials.
- A product experience that turns web research into actionable production corrections while protecting human authorship.

## What we learned

Search is most valuable to a creative agent not only as inspiration, but as a constraint. Parallel's LLM-optimized excerpts make each claim auditable without feeding entire web pages into the model. We also learned that uncertainty is a product feature: preserving conflict and saying Unverified is more useful to a crew than confident but unsupported prose.

## What's next

Next we would add Fountain and PDF ingestion, scene-level collaboration for art and continuity departments, deeper source extraction for high-risk claims, and a decision log that records which findings a writer accepts or intentionally overrides.
