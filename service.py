import json
import os
import time
from collections import Counter
from collections.abc import Callable

from dotenv import load_dotenv
from google import genai
from google.genai import types
from parallel import Parallel
from pydantic import BaseModel, Field

from models import Claim, Dossier, ResearchTrace, Source, Stance, Verdict


load_dotenv()
ProgressCallback = Callable[[str, str, int, int], None]


class SourceAssessment(BaseModel):
    source_id: str
    stance: Stance


class CoverageResult(BaseModel):
    claim_id: str
    status: str
    rationale: str
    refined_queries: list[str] = Field(default_factory=list, max_length=2)


class VerificationResult(BaseModel):
    claim_id: str
    status: str
    confidence: int = Field(ge=0, le=100)
    finding: str
    correction: str | None = None
    citations: list[str] = Field(default_factory=list)
    source_assessments: list[SourceAssessment] = Field(default_factory=list)


EXTRACTION_PROMPT = """You are the claim extraction stage of Dramaturg, an accuracy agent for screenwriters.
Extract only concrete, externally verifiable real-world claims from the screenplay scene. Focus on dates, historical events, geography, technology availability, law, professional procedure, and period culture. Do not judge accuracy yet. Ignore fictional emotions and invented characters. Return no more than 5 high-value claims. For script_quote, copy the shortest exact, character-for-character substring from the screenplay that expresses the claim. Never paraphrase script_quote. Each search query must be a concise 3-6 word keyword query. IDs must be C1, C2, and so on. Leave offsets null; the application computes them deterministically."""

COVERAGE_PROMPT = """You are the evidence coverage director in a screenplay research agent. Audit whether the attached Parallel Search excerpts are sufficient to judge each claim without relying on model memory. Status must be exactly SUFFICIENT or NEEDS_MORE. Use NEEDS_MORE only when a specific missing fact, primary source, date, jurisdiction, or credible counter-source could materially change the verdict. For NEEDS_MORE, provide one or two concise 3-6 word refined search queries targeting that gap. Select at most two claims for NEEDS_MORE across the entire batch; prioritize the highest production risk. Explain the evidence gap in one compact sentence. Do not judge whether the screenplay claim is true yet."""

VERIFICATION_PROMPT = """You are the verification stage of Dramaturg. Judge every supplied screenplay claim only from the web evidence attached to that claim. Evidence may include an initial search and a coverage-directed second search. Return exactly one result per claim_id. Never use unsupported memory. Status must be exactly VERIFIED, INACCURATE, CONFLICTED, or UNVERIFIED. Use CONFLICTED when credible sources materially disagree and explain both sides. Use UNVERIFIED when evidence is insufficient. For every source, classify its stance as SUPPORTS, REFUTES, CONTEXT, or CONFLICTS. Include only source IDs that directly justify the finding in citations, and cite those IDs inline like [S1]. State each finding compactly. For inaccurate claims, give one production-ready correction that preserves dramatic intent. Do not invent citations or facts."""


def _gemini_client() -> genai.Client:
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY or GOOGLE_API_KEY is required for live analysis")
    return genai.Client(api_key=api_key)


def _parallel_client() -> Parallel:
    api_key = os.getenv("PARALLEL_API_KEY")
    if not api_key:
        raise RuntimeError("PARALLEL_API_KEY is required for live analysis")
    return Parallel(api_key=api_key)


def locate_claim(scene: str, claim: Claim) -> Claim:
    located = claim.model_copy(deep=True)
    if not located.script_quote:
        return located
    start = scene.lower().find(located.script_quote.lower())
    if start >= 0:
        located.start_offset = start
        located.end_offset = start + len(located.script_quote)
    return located


def extract_claims(scene: str) -> list[Claim]:
    client = _gemini_client()
    response = client.models.generate_content(
        model=os.getenv("GEMINI_MODEL", "gemini-3.5-flash"),
        contents=scene,
        config=types.GenerateContentConfig(
            system_instruction=EXTRACTION_PROMPT,
            response_mime_type="application/json",
            response_schema=list[Claim],
            temperature=0.1,
        ),
    )
    claims = response.parsed
    if claims is None:
        claims = [Claim.model_validate(item) for item in json.loads(response.text)]
    return [locate_claim(scene, claim) for claim in claims[:5]]


def search_claim(claim: Claim, search_queries: list[str] | None = None) -> list[Source]:
    queries = search_queries or claim.search_queries
    objective = "Resolve the identified evidence gap for" if search_queries else "Find authoritative evidence to verify"
    search = _parallel_client().search(
        objective=f"{objective} this screenplay claim: {claim.question}",
        search_queries=queries,
        mode="fast",
    )
    sources = []
    for index, result in enumerate(search.results[:3], 1):
        excerpt = " ".join(result.excerpts[:2]).strip()
        if excerpt:
            sources.append(Source(id=f"S{index}", title=result.title or result.url, url=result.url, excerpt=excerpt[:900]))
    return sources


def merge_sources(initial: list[Source], follow_up: list[Source]) -> list[Source]:
    merged = []
    seen = set()
    for source in initial + follow_up:
        normalized_url = source.url.lower().rstrip("/")
        if normalized_url in seen:
            continue
        seen.add(normalized_url)
        merged.append(source.model_copy(update={"id": f"S{len(merged) + 1}"}))
    return merged[:6]


def research_targets(audits: list[CoverageResult]) -> list[CoverageResult]:
    return [audit for audit in audits if audit.status.upper() == "NEEDS_MORE" and audit.refined_queries][:2]


def audit_coverage(claims: list[Claim], evidence_by_claim: dict[str, list[Source]]) -> list[CoverageResult]:
    payload = [{
        "claim_id": claim.id,
        "claim": claim.text,
        "question": claim.question,
        "evidence": [source.model_dump() for source in evidence_by_claim[claim.id]],
    } for claim in claims]
    time.sleep(max(0, float(os.getenv("GEMINI_REQUEST_DELAY_SECONDS", "30"))))
    client = _gemini_client()
    response = client.models.generate_content(
        model=os.getenv("GEMINI_MODEL", "gemini-3.5-flash"),
        contents=json.dumps(payload, ensure_ascii=False),
        config=types.GenerateContentConfig(
            system_instruction=COVERAGE_PROMPT,
            response_mime_type="application/json",
            response_schema=list[CoverageResult],
            temperature=0.1,
        ),
    )
    audits = response.parsed
    if audits is None:
        audits = [CoverageResult.model_validate(item) for item in json.loads(response.text)]
    known_ids = {claim.id for claim in claims}
    return [audit for audit in audits if audit.claim_id in known_ids]


def expand_evidence(claims: list[Claim], evidence_by_claim: dict[str, list[Source]], audits: list[CoverageResult], progress: ProgressCallback | None = None) -> tuple[dict[str, list[Source]], list[ResearchTrace]]:
    target_list = research_targets(audits)
    targets = {audit.claim_id: audit for audit in target_list}
    audit_map = {audit.claim_id: audit for audit in audits}
    traces = []
    researched_count = 0
    for claim in claims:
        initial_count = len(evidence_by_claim[claim.id])
        audit = audit_map.get(claim.id)
        if audit is None:
            traces.append(ResearchTrace(claim_id=claim.id, status="INSUFFICIENT", rationale="The coverage audit returned no result for this claim.", initial_source_count=initial_count))
            continue
        target = targets.get(claim.id)
        if target is None:
            status = "SUFFICIENT" if audit.status.upper() == "SUFFICIENT" else "INSUFFICIENT"
            traces.append(ResearchTrace(claim_id=claim.id, status=status, rationale=audit.rationale, initial_source_count=initial_count, refined_queries=audit.refined_queries))
            continue
        if progress:
            progress("targeted_search", f"Parallel is researching the evidence gap for {claim.id}", researched_count, len(target_list))
        follow_up = search_claim(claim, target.refined_queries)
        researched_count += 1
        if progress:
            progress("targeted_search", f"Parallel completed the second pass for {claim.id}", researched_count, len(target_list))
        merged = merge_sources(evidence_by_claim[claim.id], follow_up)
        added_count = len(merged) - initial_count
        evidence_by_claim[claim.id] = merged
        traces.append(ResearchTrace(
            claim_id=claim.id,
            status="RESEARCHED" if added_count else "INSUFFICIENT",
            rationale=target.rationale,
            initial_source_count=initial_count,
            refined_queries=target.refined_queries,
            added_source_count=max(0, added_count),
        ))
    return evidence_by_claim, traces


def verify_claims(claims: list[Claim], evidence_by_claim: dict[str, list[Source]]) -> list[Verdict]:
    payload = []
    for claim in claims:
        sources = evidence_by_claim[claim.id]
        payload.append({
            "claim_id": claim.id,
            "claim": claim.text,
            "question": claim.question,
            "evidence": [source.model_dump() for source in sources],
        })
    time.sleep(max(0, float(os.getenv("GEMINI_REQUEST_DELAY_SECONDS", "30"))))
    client = _gemini_client()
    response = client.models.generate_content(
        model=os.getenv("GEMINI_MODEL", "gemini-3.5-flash"),
        contents=json.dumps(payload, ensure_ascii=False),
        config=types.GenerateContentConfig(
            system_instruction=VERIFICATION_PROMPT,
            response_mime_type="application/json",
            response_schema=list[VerificationResult],
            temperature=0.1,
        ),
    )
    parsed = response.parsed
    if parsed is None:
        parsed = [VerificationResult.model_validate(item) for item in json.loads(response.text)]
    results = {item.claim_id: item for item in parsed}
    allowed = {"VERIFIED", "INACCURATE", "CONFLICTED", "UNVERIFIED"}
    verdicts = []
    for claim in claims:
        sources = evidence_by_claim[claim.id]
        result = results.get(claim.id)
        if not sources or result is None:
            verdicts.append(Verdict(
                claim=claim,
                status="UNVERIFIED",
                confidence=0,
                finding="Parallel Search returned no usable evidence for this claim." if not sources else "No verification result was returned for this claim.",
                correction=None,
                citations=[],
                sources=sources,
            ))
            continue
        assessments = {item.source_id: item.stance for item in result.source_assessments}
        sources = [source.model_copy(update={"stance": assessments.get(source.id, "CONTEXT")}) for source in sources]
        source_ids = {source.id for source in sources}
        citations = [citation for citation in result.citations if citation in source_ids]
        status = result.status.upper() if result.status.upper() in allowed else "UNVERIFIED"
        verdicts.append(Verdict(
            claim=claim,
            status=status,
            confidence=result.confidence,
            finding=result.finding,
            correction=result.correction,
            citations=citations,
            sources=sources,
        ))
    return verdicts


def analyze_scene(scene: str, progress: ProgressCallback | None = None) -> Dossier:
    if progress:
        progress("extracting", "Gemini is identifying verifiable screenplay claims", 0, 1)
    claims = extract_claims(scene)
    if not claims:
        raise ValueError("No externally verifiable claims were found in this scene")
    evidence_by_claim = {}
    for index, claim in enumerate(claims, 1):
        if progress:
            progress("initial_search", f"Parallel is researching {claim.id} of {len(claims)}", index - 1, len(claims))
        evidence_by_claim[claim.id] = search_claim(claim)
        if progress:
            progress("initial_search", f"Parallel completed {claim.id} of {len(claims)}", index, len(claims))
    if progress:
        progress("coverage_audit", "Gemini is auditing evidence coverage", 0, 1)
    audits = audit_coverage(claims, evidence_by_claim)
    evidence_by_claim, research_trace = expand_evidence(claims, evidence_by_claim, audits, progress)
    if progress:
        progress("verification", "Gemini is verifying the completed evidence record", 0, 1)
    verdicts = verify_claims(claims, evidence_by_claim)
    counts = Counter(verdict.status.lower() for verdict in verdicts)
    dossier = Dossier(
        title="Live screenplay accuracy dossier",
        mode="live",
        scene=scene,
        verdicts=verdicts,
        research_trace=research_trace,
        summary={
            "total": len(verdicts),
            "verified": counts["verified"],
            "inaccurate": counts["inaccurate"],
            "conflicted": counts["conflicted"],
            "unverified": counts["unverified"],
        },
    )
    if progress:
        progress("complete", "The accuracy dossier is ready for human review", 1, 1)
    return dossier
