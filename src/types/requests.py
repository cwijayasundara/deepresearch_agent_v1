"""Request and response models for the API."""

from datetime import datetime

from pydantic import BaseModel

from src.types.enums import ResearchStatus


class ResearchRequest(BaseModel):
    """Request to trigger a research run."""

    date: str | None = None


class ReportSummary(BaseModel):
    """Summary of a report for list views."""

    report_id: str
    run_date: datetime
    status: ResearchStatus
    gemini_tldr: str | None
    langchain_tldr: str | None


class ReportListResponse(BaseModel):
    """Paginated list of report summaries."""

    reports: list[ReportSummary]
    total: int


class AuthRequest(BaseModel):
    """Login request with shared password."""

    password: str


class AuthToken(BaseModel):
    """JWT token response."""

    access_token: str
    token_type: str
