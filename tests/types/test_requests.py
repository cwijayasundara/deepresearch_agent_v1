"""Tests for src.types.requests — RED phase."""

from datetime import datetime, timezone

from src.types.enums import ResearchStatus
from src.types.requests import (
    AuthRequest,
    AuthToken,
    ReportListResponse,
    ReportSummary,
    ResearchRequest,
)


class TestResearchRequest:
    def test_create_with_date(self) -> None:
        req = ResearchRequest(date="2026-02-28")
        assert req.date == "2026-02-28"

    def test_default_date_is_none(self) -> None:
        req = ResearchRequest()
        assert req.date is None


class TestReportSummary:
    def test_create(self) -> None:
        summary = ReportSummary(
            report_id="rpt-001",
            run_date=datetime(2026, 2, 28, tzinfo=timezone.utc),
            status=ResearchStatus.COMPLETED,
            gemini_tldr="Gemini found stuff",
            langchain_tldr="LangChain found stuff",
        )
        assert summary.report_id == "rpt-001"
        assert summary.status == ResearchStatus.COMPLETED


class TestReportListResponse:
    def test_create_with_items(self) -> None:
        resp = ReportListResponse(
            reports=[
                ReportSummary(
                    report_id="rpt-001",
                    run_date=datetime(2026, 2, 28, tzinfo=timezone.utc),
                    status=ResearchStatus.COMPLETED,
                    gemini_tldr="Summary",
                    langchain_tldr=None,
                ),
            ],
            total=1,
        )
        assert resp.total == 1
        assert len(resp.reports) == 1


class TestAuthRequest:
    def test_create(self) -> None:
        req = AuthRequest(password="secret123")
        assert req.password == "secret123"


class TestAuthToken:
    def test_create(self) -> None:
        token = AuthToken(access_token="jwt.token.here", token_type="bearer")
        assert token.access_token == "jwt.token.here"
        assert token.token_type == "bearer"
