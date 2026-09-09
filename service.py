import json
import os
import time
from collections import Counter

from dotenv import load_dotenv
from google import genai
from google.genai import types
from parallel import Parallel
from pydantic import BaseModel, Field

from models import Claim, Dossier, Source, Verdict


load_dotenv()


class VerificationResult(BaseModel):
    claim_id: str
    status: str
    confidence: int = Field(ge=0, le=100)
    finding: str
    correction: str | None = None


EXTRACTION_PROMPT = """You are the claim extraction stage of Dramaturg, an accuracy agent for screenwriters.
Extract only concrete, externally verifiable real-world claims from the screenplay scene. Focus on dates, historical events, geography, technology availability, law, professional procedure, and period culture. Do not judge accuracy yet. Ignore fictional emotions and invented characters. Return no more than 5 high-value claims. Each search query must be a concise 3-6 word keyword query. IDs must be C1, C2, and so on."""

VERIFICATION_PROMPT = """You are the verification stage of Dramaturg. Judge every supplied screenplay claim only from the web evidence attached to that claim. Return exactly one result per claim_id. Never use unsupported memory. Status must be exactly VERIFIED, INACCURATE, CONFLICTED, or UNVERIFIED. Use CONFLICTED when credible sources materially disagree and explain both sides. Use UNVERIFIED when evidence is insufficient. State each finding compactly. For inaccurate claims, give one production-ready correction that preserves dramatic intent. Do not invent citations or facts."""


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
    return claims[:5]


def search_claim(claim: Claim) -> list[Source]:
    search = _parallel_client().search(
        objective=f"Find authoritative evidence to verify this screenplay claim: {claim.question}",
        search_queries=claim.search_queries,
        mode="fast",
    )
    sources = []
    for result in search.results[:3]:
        excerpt = " ".join(result.excerpts[:2]).strip()
        if excerpt:
            sources.append(Source(title=result.title or result.url, url=result.url, excerpt=excerpt[:900]))
    return sources


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
                sources=sources,
            ))
            continue
        status = result.status.upper() if result.status.upper() in allowed else "UNVERIFIED"
        verdicts.append(Verdict(
            claim=claim,
            status=status,
            confidence=result.confidence,
            finding=result.finding,
            correction=result.correction,
            sources=sources,
        ))
    return verdicts


def analyze_scene(scene: str) -> Dossier:
    claims = extract_claims(scene)
    if not claims:
        raise ValueError("No externally verifiable claims were found in this scene")
    evidence_by_claim = {claim.id: search_claim(claim) for claim in claims}
    verdicts = verify_claims(claims, evidence_by_claim)
    counts = Counter(verdict.status.lower() for verdict in verdicts)
    return Dossier(
        title="Live screenplay accuracy dossier",
        mode="live",
        scene=scene,
        verdicts=verdicts,
        summary={
            "total": len(verdicts),
            "verified": counts["verified"],
            "inaccurate": counts["inaccurate"],
            "conflicted": counts["conflicted"],
            "unverified": counts["unverified"],
        },
    )
