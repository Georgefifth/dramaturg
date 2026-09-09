# Dramaturg — 3-minute demo script

## Recording setup

1. Use Chrome at 1440×900 and 110% zoom.
2. Open https://dramaturg.onrender.com and close unrelated tabs.
3. Before recording, load the Berlin scene and run live verification once. During recording, the identical scene will return from the evidence cache immediately without spending more API calls.
4. Reset decisions, return to the top, and start recording.
5. Speak naturally; do not exceed 2:50. Add English captions if your spoken audio is not English.

## Shot list and narration

### 0:00–0:18 — Hero

**On screen:** Hero headline and Evidence Pipeline.

**Say:**

> Screenplays can be fictional. Their real-world details should not be. Dramaturg is an AI accuracy agent for screenwriters and production crews. Unlike creative agents that generate more content, Dramaturg verifies what is already on the page.

### 0:18–0:38 — Input and live workflow

**On screen:** Show Project and Scene fields. Click **Load evidence sample**, then **Run live verification**. The warmed live result should load from cache.

**Say:**

> I can paste a scene or import a Fountain file. This scene is set on the night the Berlin Wall opened and deliberately contains period, location, legal, and technology errors. A new run uses Gemini to extract exact claims and Parallel Search to retrieve live, traceable web evidence. This repeated scene is served from our protected evidence cache.

### 0:38–1:02 — Agent research trace

**On screen:** Show score grid and Agent Research Trace. Point to a **Second pass** card.

**Say:**

> This is not a one-shot search-and-summarize pipeline. Gemini audits whether the first evidence pass is sufficient. For consequential gaps, it rewrites the query and dispatches up to two targeted Parallel searches. New sources are deduplicated, and the complete research trace stays visible.

### 1:02–1:35 — Marked screenplay and evidence

**On screen:** Click the SMS highlight. Show the linked claim, finding, source IDs, and `REFUTES` stance. Open one source in a new tab, then return.

**Say:**

> Every finding maps back to the exact screenplay text. Here, a character sends an SMS in 1987. Dramaturg finds that the first SMS was sent in 1992, marks the claim inaccurate, and cites the evidence directly. Sources are classified as supporting, refuting, contextual, or conflicting. If credible sources disagree, the product preserves that conflict instead of inventing certainty.

### 1:35–2:05 — Human authority and revision

**On screen:** Click **Accept fix** on the date and SMS claims. Click **Keep as written** on another claim and type `Intentional dramatic compression`.

**Say:**

> The agent never silently rewrites the screenplay. The writer can accept a fix, intentionally keep the original, or request more research. Only explicitly accepted replacements enter the Revision Workspace, where deletions and insertions remain visible and reversible. Decisions persist locally across refreshes.

### 2:05–2:30 — Project and handoff

**On screen:** Show Revision Workspace, click **Save scene review**, then scroll to Production Handoff.

**Say:**

> Reviews can be saved as scene snapshots inside a browser-local production workspace. Open risks are automatically routed to the department that can resolve them—historical consultants, locations, legal and standards, technical advisors, or script coordination.

### 2:30–2:48 — Export and close

**On screen:** Click **Copy handoff**, then point to **Export dossier + decisions**. End on product name.

**Say:**

> The final export contains the original scene, revised scene, evidence, citations, research trace, department handoff, and the writer's decision log. Dramaturg turns live web evidence into a production gate—while the human keeps the final cut.

## Editing notes

- Keep the cursor moving slowly and deliberately.
- Use one subtle zoom on the SMS evidence card.
- Do not show API keys, the Render dashboard, terminal output, or browser autofill.
- If the cached live request is unavailable, use **Load evidence sample** and say “This curated evidence sample demonstrates the same review interface; the repository and deployment contain the runtime integrations.”
