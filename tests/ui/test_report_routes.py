"""Tests for src.ui.report_routes."""

from datetime import datetime, timezone
from unittest.mock import AsyncMock

from fastapi.testclient import TestClient

from src.ui.app_factory import create_app
from src.runtime.dependencies import get_firestore_repo
from src.types.enums import EngineType, ResearchStatus
from src.types.report import EngineResult, ResearchReport


def _make_report(report_id: str = "rpt-001") -> ResearchReport:
    now = datetime(2026, 2, 28, tzinfo=timezone.utc)
    return ResearchReport(
        report_id=report_id,
        run_date=now,
        gemini_result=EngineResult(
            engine=EngineType.GEMINI,
            status=ResearchStatus.COMPLETED,
            raw_markdown="# Report",
            tldr="Summary",
            viral_events=[],
            deep_dives=[],
            completeness_audit=None,
            started_at=now,
            completed_at=now,
            duration_seconds=60.0,
            error_message=None,
        ),
        langchain_result=None,
        created_at=now,
    )


def _get_auth_token(client: TestClient) -> str:
    resp = client.post(
        "/api/auth/login", json={"password": "test-password"}
    )
    return resp.json()["access_token"]


class TestReportRoutes:
    def setup_method(self) -> None:
        self.app = create_app()
        self.mock_repo = AsyncMock()
        self.app.dependency_overrides[get_firestore_repo] = (
            lambda: self.mock_repo
        )
        self.client = TestClient(self.app)
        self.token = _get_auth_token(self.client)
        self.headers = {"Authorization": f"Bearer {self.token}"}

    def teardown_method(self) -> None:
        self.app.dependency_overrides.clear()

    def test_list_reports(self) -> None:
        report = _make_report()
        self.mock_repo.list_reports.return_value = [report]
        resp = self.client.get("/api/reports/", headers=self.headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 1

    def test_get_report_found(self) -> None:
        report = _make_report("rpt-123")
        self.mock_repo.get_report.return_value = report
        resp = self.client.get(
            "/api/reports/rpt-123", headers=self.headers
        )
        assert resp.status_code == 200

    def test_get_report_not_found(self) -> None:
        self.mock_repo.get_report.return_value = None
        resp = self.client.get(
            "/api/reports/rpt-nope", headers=self.headers
        )
        assert resp.status_code == 404

    def test_reports_require_auth(self) -> None:
        resp = self.client.get("/api/reports/")
        assert resp.status_code == 401
