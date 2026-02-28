"""Pydantic models for engine results and research reports."""

from datetime import datetime

from pydantic import BaseModel

from src.types.enums import EngineType, ResearchStatus
from src.types.events import CompletenessAudit, DeepDive, ViralEvent


class EngineResult(BaseModel):
    """Result from a single research engine run."""

    engine: EngineType
    status: ResearchStatus
    raw_markdown: str
    tldr: str | None
    viral_events: list[ViralEvent]
    deep_dives: list[DeepDive]
    completeness_audit: CompletenessAudit | None
    started_at: datetime
    completed_at: datetime
    duration_seconds: float
    error_message: str | None


class ResearchReport(BaseModel):
    """A daily research report combining both engine results."""

    report_id: str
    run_date: datetime
    gemini_result: EngineResult | None
    langchain_result: EngineResult | None
    created_at: datetime
