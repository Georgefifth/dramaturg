from typing import Literal

from pydantic import BaseModel, Field, model_validator


Status = Literal["VERIFIED", "INACCURATE", "CONFLICTED", "UNVERIFIED"]
Stance = Literal["SUPPORTS", "REFUTES", "CONTEXT", "CONFLICTS"]


class Claim(BaseModel):
    id: str
    text: str
    script_quote: str = ""
    start_offset: int | None = None
    end_offset: int | None = None
    category: Literal["HISTORY", "LOCATION", "TECHNOLOGY", "LAW", "PROFESSION", "CULTURE", "OTHER"]
    question: str
    search_queries: list[str] = Field(min_length=1, max_length=3)


class Source(BaseModel):
    id: str = "S1"
    title: str
    url: str
    excerpt: str
    stance: Stance = "CONTEXT"


class Verdict(BaseModel):
    claim: Claim
    status: Status
    confidence: int = Field(ge=0, le=100)
    finding: str
    correction: str | None = None
    replacement_text: str | None = None
    citations: list[str] = Field(default_factory=list)
    sources: list[Source]


class ResearchTrace(BaseModel):
    claim_id: str
    status: Literal["SUFFICIENT", "RESEARCHED", "INSUFFICIENT"]
    rationale: str
    initial_source_count: int = Field(ge=0)
    refined_queries: list[str] = Field(default_factory=list)
    added_source_count: int = Field(default=0, ge=0)


class Dossier(BaseModel):
    title: str
    mode: Literal["live", "sample"]
    scene: str
    verdicts: list[Verdict]
    research_trace: list[ResearchTrace] = Field(default_factory=list)
    summary: dict[str, int]

    @model_validator(mode="after")
    def locate_quotes(self):
        lower_scene = self.scene.lower()
        for verdict in self.verdicts:
            claim = verdict.claim
            if not claim.script_quote or claim.start_offset is not None:
                continue
            start = lower_scene.find(claim.script_quote.lower())
            if start >= 0:
                claim.start_offset = start
                claim.end_offset = start + len(claim.script_quote)
        return self


class AnalysisRequest(BaseModel):
    scene: str = Field(min_length=80, max_length=12000)
