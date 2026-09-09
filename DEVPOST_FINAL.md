# Devpost final submission material

## Project name

Dramaturg

## Tagline

An evidence-first AI dramaturg that verifies screenplay details against the live web, preserves uncertainty, and turns accepted findings into production-ready revisions and department handoffs.

## Links

- Live product: https://dramaturg.onrender.com
- Source code: https://github.com/Georgefifth/dramaturg
- Demo video: ADD YOUTUBE OR VIMEO URL

## Inspiration

Film production has many tools for generating scripts, storyboards, images, and video, but one quiet bottleneck remains manual: checking whether a scene's real-world details are actually true. A wrong date, border procedure, medical step, location, or period technology can survive until props, dialogue, schedules, and budgets are already expensive to change. We built the AI equivalent of a dramaturg—the production specialist who protects factual integrity.

## What it does

Dramaturg reads a screenplay scene and creates a source-linked accuracy dossier. Gemini extracts exact, externally verifiable claims, and Parallel Search retrieves live evidence for each one. A Gemini coverage director then asks whether the evidence is sufficient to support a verdict. It selects at most two consequential gaps, rewrites their search queries, and dispatches targeted second-pass Parallel searches before final verification.

Each claim is highlighted in the original screenplay and classified as Verified, Inaccurate, Conflicted, or Unverified. Sources receive explicit evidence stances—Supports, Refutes, Context, or Conflicts—and findings cite source IDs directly.

The agent never silently edits the writer's work. The writer chooses Accept fix, Keep as written, or Needs research. Only accepted replacements enter a reversible Revision Workspace. Browser-local project workspaces save multiple reviewed scenes, while unresolved risks are routed into Historical, Locations, Legal, Technical, and Script Coordination handoffs.

## How we built it

The application uses FastAPI, Pydantic, and a responsive vanilla JavaScript interface deployed as a Docker container on Render. Long analyses run as protected background jobs, and the interface polls genuine stage events from extraction, initial search, coverage audit, targeted re-search, and verification.

We use Google's official `google-genai` SDK with Gemini Flash for structured claim extraction and final evidence-constrained verification. Gemini Flash Lite performs the lower-cost coverage audit and query reformulation. Parallel's official `parallel-web` SDK is called at runtime for every initial search and each agent-directed follow-up.

The public deployment includes per-IP limits, a global daily budget ceiling, single concurrency, and a six-hour evidence cache. Repeated scenes do not spend additional provider calls.

## Challenges we ran into

The hardest problem was making the workflow agentic without creating another hallucination layer. We separated evidence coverage from truth judgment. The coverage director may identify a precise missing fact and reformulate a query, but the final verifier can reason only over Parallel's retrieved excerpts.

We also had to balance reliability with public API budgets. Gemini calls are batched and rate-spaced, follow-up searches are capped at two claims, duplicate sources are removed, long work runs in background jobs, and identical scenes use a protected cache.

Finally, we designed human authority as a real workflow rather than a disclaimer. Exact replacements are generated, but nothing changes until the writer explicitly accepts a fix. Original text, overrides, uncertainty, and decision history remain visible.

## Accomplishments that we're proud of

- A differentiated verification product for a real film-production role, not another general creative generator.
- Runtime Gemini and Parallel Search integrations visible in the public source.
- A bounded agent loop that audits evidence, rewrites weak queries, and dispatches targeted web research.
- Exact screenplay highlighting, claim-level provenance, source stances, and honest uncertainty states.
- Real background-job progress instead of simulated loading messages.
- Explicit human decisions and reversible evidence-backed screenplay revisions.
- Browser-local multi-scene projects and department-specific production handoffs.
- Public-deployment safeguards that protect API credentials and budgets.

## What we learned

Search is valuable to a creative agent not only as inspiration, but as a constraint. Parallel's LLM-optimized excerpts let Gemini reason over relevant evidence without ingesting entire web pages. We also learned that uncertainty is a product feature: preserving a conflict or saying Unverified is more useful to a production team than fluent but unsupported certainty.

The strongest human-AI workflow is not “generate and replace.” It is “research, show the evidence, propose a precise change, and let the accountable person decide.”

## What's next

Next we would add PDF ingestion, durable encrypted project history, role-based collaboration for production departments, deeper source extraction for high-risk claims, and signed review exports for formal production handoff.

## Technologies

- Gemini / Google Gen AI SDK
- Parallel Search API / `parallel-web`
- FastAPI
- Pydantic
- Vanilla JavaScript
- Docker
- Render

## Suggested gallery images

1. Hero plus screenplay input and Evidence Pipeline.
2. Marked screenplay beside the claim ledger.
3. Agent Research Trace showing a targeted second pass.
4. A claim card with source IDs and `REFUTES` evidence stance.
5. Revision Workspace showing red deletion and green insertion.
6. Department-grouped Production Handoff.

## Final checklist

- [ ] Record a public video no longer than 3 minutes.
- [ ] Upload it to YouTube or Vimeo with English audio or English subtitles.
- [ ] Replace `ADD YOUTUBE OR VIMEO URL` above.
- [ ] Confirm https://dramaturg.onrender.com loads in a private browser window.
- [ ] Confirm **Load evidence sample** works without authentication.
- [ ] Confirm the GitHub repository is public.
- [ ] Confirm the MIT license is visible at repository root.
- [ ] Add screenshots to the Devpost gallery.
- [ ] Select the Parallel partner track.
- [ ] Submit before 2026-09-09 2:00 PM PDT.
