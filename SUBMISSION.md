# Devpost submission draft

**Live product:** https://dramaturg.onrender.com

**Source code:** https://github.com/Georgefifth/dramaturg

## Inspiration

Film production has many creative tools, but one quiet bottleneck remains manual: checking whether a scene's real-world details are actually true. A wrong date, border procedure, medical step, or period technology can survive until props, locations, and dialogue are already expensive to change. We built the AI equivalent of a dramaturg—the production specialist who protects factual integrity.

## What it does

Dramaturg reads a screenplay scene and creates a source-linked accuracy dossier. Gemini isolates claims that can be checked externally, and Parallel Search retrieves live evidence for each one. A Gemini coverage director then asks whether that evidence can actually support a verdict. It selects at most two consequential gaps, rewrites their search queries, and dispatches targeted second-pass Parallel searches before final verification. Exact claims are highlighted in the original screenplay, every source is classified by evidentiary stance, and findings cite source IDs directly. Writers close the review with Accept fix, Keep as written, or Needs research; the exported Decision Log preserves their final authority.

## How we built it

The web application uses FastAPI and a responsive vanilla JavaScript interface deployed as a container on Render. Long analyses execute as background research jobs, while the interface polls genuine stage events from extraction, initial search, coverage audit, targeted re-search, and verification. It uses Google's official `google-genai` SDK for structured claim extraction, evidence coverage auditing, query reformulation, and final verification. It uses Parallel's official `parallel-web` SDK at runtime for every initial search and each agent-directed follow-up. Typed Pydantic contracts carry claims, sources, coverage decisions, research traces, verdicts, and the final dossier through the pipeline.

## Challenges we ran into

The central design challenge was avoiding a second hallucination layer in the verifier without turning the agent into a rigid one-shot pipeline. We separated evidence coverage from truth judgment: the coverage director may identify a precise gap and reformulate a search, but the verifier remains constrained to Parallel's retrieved excerpts. Follow-up searches are capped, sources are deduplicated, disagreements remain Conflicted, and insufficient evidence becomes an explicit Unverified result. Live analysis and the curated evidence sample are always labeled separately.

## Accomplishments that we're proud of

- A narrow, complete workflow for a real film-production role instead of another general creative generator.
- Runtime integration of both Gemini and Parallel Search, visible in the source code.
- A bounded agent loop that audits coverage, reformulates weak queries, and dispatches targeted Parallel re-searches.
- Claim-level provenance, exact script highlighting, source stances, and four honest evidence states.
- A human decision loop with production-ready corrections and an exportable audit record.
- Cache, per-IP limits, a global budget ceiling, and single concurrency to protect public API credentials.
- Background jobs with real pipeline progress instead of a simulated loading animation.
- Local `.txt` and `.fountain` import with explicit data-flow disclosure.
- A product experience that turns web research into actionable production corrections while protecting human authorship.

## What we learned

Search is most valuable to a creative agent not only as inspiration, but as a constraint. Parallel's LLM-optimized excerpts make each claim auditable without feeding entire web pages into the model. We also learned that uncertainty is a product feature: preserving conflict and saying Unverified is more useful to a crew than confident but unsupported prose.

## What's next

Next we would add PDF ingestion, scene-level collaboration for art and continuity departments, deeper source extraction for high-risk claims, durable project history, and signed review exports for production handoff.
