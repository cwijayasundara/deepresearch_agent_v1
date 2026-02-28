"""Report API routes."""

import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Header, HTTPException

from src.runtime.dependencies import (
    get_auth_service,
    get_firestore_repo,
    get_orchestrator,
)
from src.service.auth_service import AuthService
from src.repo.firestore_client import FirestoreRepo
from src.service.research_orchestrator import ResearchOrchestrator
from src.types.enums import ResearchStatus
from src.types.report import ResearchReport
from src.types.requests import (
    ReportListResponse,
    ReportSummary,
    ResearchRequest,
)
from src.ui.auth_middleware import require_auth

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/reports", tags=["reports"])


def _auth_dep(
    authorization: str | None = Header(None),
    auth_service: AuthService = Depends(get_auth_service),
) -> dict[str, str]:
    return require_auth(authorization, auth_service)


def _summarize(report: ResearchReport) -> ReportSummary:
    gemini_tldr = None
    langchain_tldr = None
    status = ResearchStatus.PENDING

    if report.gemini_result:
        gemini_tldr = report.gemini_result.tldr
        status = report.gemini_result.status
    if report.langchain_result:
        langchain_tldr = report.langchain_result.tldr
        if report.langchain_result.status == ResearchStatus.COMPLETED:
            status = ResearchStatus.COMPLETED

    return ReportSummary(
        report_id=report.report_id,
        run_date=report.run_date,
        status=status,
        gemini_tldr=gemini_tldr,
        langchain_tldr=langchain_tldr,
    )


def _get_date_or_today(date: str | None) -> str:
    """Return provided date or today's date in ISO format."""
    return date or datetime.now(timezone.utc).strftime("%Y-%m-%d")


@router.get("/", response_model=ReportListResponse)
async def list_reports(
    _user: dict[str, str] = Depends(_auth_dep),
    repo: FirestoreRepo = Depends(get_firestore_repo),
) -> ReportListResponse:
    """List all research reports."""
    reports = await repo.list_reports()
    summaries = [_summarize(r) for r in reports]
    return ReportListResponse(reports=summaries, total=len(summaries))


@router.get("/{report_id}", response_model=ResearchReport)
async def get_report(
    report_id: str,
    _user: dict[str, str] = Depends(_auth_dep),
    repo: FirestoreRepo = Depends(get_firestore_repo),
) -> ResearchReport:
    """Get a single research report by ID."""
    report = await repo.get_report(report_id)
    if report is None:
        raise HTTPException(status_code=404, detail="Report not found")
    return report


@router.post("/trigger")
async def trigger_research(
    request: ResearchRequest,
    _user: dict[str, str] = Depends(_auth_dep),
    orchestrator: ResearchOrchestrator = Depends(get_orchestrator),
) -> dict[str, str]:
    """Trigger a new research run."""
    date = _get_date_or_today(request.date)
    report = await orchestrator.run_daily_research(date)
    return {"report_id": report.report_id, "status": "triggered"}
