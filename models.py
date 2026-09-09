from typing import Literal

from pydantic import BaseModel, Field


Status = Literal["VERIFIED", "INACCURATE", "CONFLICTED", "UNVERIFIED"]


class Claim(BaseModel):
    id: str
    text: str
    category: Literal["HISTORY", "LOCATION", "TECHNOLOGY", "LAW", "PROFESSION", "CULTURE", "OTHER"]
    question: str
    search_queries: list[str] = Field(min_length=1, max_length=3)


class Source(BaseModel):
    title: str
    url: str
    excerpt: str


class Verdict(BaseModel):
    claim: Claim
    status: Status
    confidence: int = Field(ge=0, le=100)
    finding: str
    correction: str | None = None
    sources: list[Source]


class Dossier(BaseModel):
    title: str
    mode: Literal["live", "sample"]
    scene: str
    verdicts: list[Verdict]
    summary: dict[str, int]


class AnalysisRequest(BaseModel):
    scene: str = Field(min_length=80, max_length=12000)
