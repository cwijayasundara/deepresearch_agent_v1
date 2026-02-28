"""Report API routes."""

import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Header, HTTPException

from backend.runtime.dependencies import (
    get_auth_service,
    get_firestore_repo,
    get_orchestrator,
)
from backend.service.auth_service import AuthService
from backend.repo.firestore_client import FirestoreRepo
from backend.service.research_orchestrator import ResearchOrchestrator
from backend.types.enums import ResearchStatus
from backend.types.report import ResearchReport
from backend.types.requests import (
    ReportListResponse,
    ReportSummary,
    ResearchRequest,
)
from backend.types.errors import FirestoreError
from backend.ui.auth_middleware import require_auth

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
    try:
        reports = await repo.list_reports()
    except FirestoreError as exc:
        logger.error("Firestore unavailable: %s", exc)
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    summaries = [_summarize(r) for r in reports]
    return ReportListResponse(reports=summaries, total=len(summaries))


@router.get("/{report_id}", response_model=ResearchReport)
async def get_report(
    report_id: str,
    _user: dict[str, str] = Depends(_auth_dep),
    repo: FirestoreRepo = Depends(get_firestore_repo),
) -> ResearchReport:
    """Get a single research report by ID."""
    try:
        report = await repo.get_report(report_id)
    except FirestoreError as exc:
        logger.error("Firestore unavailable: %s", exc)
        raise HTTPException(status_code=503, detail=str(exc)) from exc
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
    logger.info("Research trigger requested for date=%s", date)
    try:
        report = await orchestrator.run_daily_research(date)
    except FirestoreError as exc:
        logger.error("Firestore unavailable: %s", exc)
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    logger.info("Research complete report_id=%s", report.report_id)
    return {"report_id": report.report_id, "status": "triggered"}
