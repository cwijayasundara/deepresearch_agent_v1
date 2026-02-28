"""Pydantic models for viral events, deep dives, and audits."""

from pydantic import BaseModel, Field

from backend.types.enums import ConfidenceLevel, EventCategory


class ViralEvent(BaseModel):
    """A single viral AI event detected by a research engine."""

    headline: str
    category: EventCategory
    impact_rating: int = Field(ge=1, le=10)
    confidence: ConfidenceLevel
    source: str


class DeepDive(BaseModel):
    """A strategic deep-dive analysis section."""

    title: str
    priority: str
    summary: str
    key_findings: list[str]


class CompletenessAudit(BaseModel):
    """Audit of research completeness and signal coverage."""

    verified_signals: int
    sources_checked: int
    confidence_score: float = Field(ge=0.0, le=1.0)
    gaps: list[str]
