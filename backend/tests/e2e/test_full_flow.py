"""End-to-end test for the full API flow."""

from datetime import datetime, timezone
from unittest.mock import AsyncMock

from fastapi.testclient import TestClient

from backend.runtime.dependencies import get_firestore_repo, get_orchestrator
from backend.types.enums import EngineType, ResearchStatus
from backend.types.report import EngineResult, ResearchReport
from backend.ui.app_factory import create_app


def _make_report(report_id: str = "rpt-2026-02-28") -> ResearchReport:
    now = datetime(2026, 2, 28, tzinfo=timezone.utc)
    return ResearchReport(
        report_id=report_id,
        run_date=now,
        gemini_result=EngineResult(
            engine=EngineType.GEMINI,
            status=ResearchStatus.COMPLETED,
            raw_markdown="# Gemini Report\nAI news",
            tldr="Gemini found important AI news",
            viral_events=[],
            deep_dives=[],
            completeness_audit=None,
            started_at=now,
            completed_at=now,
            duration_seconds=45.0,
            error_message=None,
        ),
        langchain_result=EngineResult(
            engine=EngineType.LANGCHAIN,
            status=ResearchStatus.COMPLETED,
            raw_markdown="# LangChain Report\nAI findings",
            tldr="LangChain found key developments",
            viral_events=[],
            deep_dives=[],
            completeness_audit=None,
            started_at=now,
            completed_at=now,
            duration_seconds=30.0,
            error_message=None,
        ),
        created_at=now,
    )


class TestFullFlow:
    """E2E test: login -> list reports -> get report -> trigger."""

    def setup_method(self) -> None:
        self.app = create_app()
        self.mock_repo = AsyncMock()
        self.mock_orchestrator = AsyncMock()
        self.app.dependency_overrides[get_firestore_repo] = (
            lambda: self.mock_repo
        )
        self.app.dependency_overrides[get_orchestrator] = (
            lambda: self.mock_orchestrator
        )
        self.client = TestClient(self.app)

    def teardown_method(self) -> None:
        self.app.dependency_overrides.clear()

    def test_health_check(self) -> None:
        resp = self.client.get("/health")
        assert resp.status_code == 200
        assert resp.json()["status"] == "ok"

    def test_full_authenticated_flow(self) -> None:
        login_resp = self.client.post(
            "/api/auth/login", json={"password": "test-password"}
        )
        assert login_resp.status_code == 200
        token = login_resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        report = _make_report()
        self.mock_repo.list_reports.return_value = [report]
        list_resp = self.client.get("/api/reports/", headers=headers)
        assert list_resp.status_code == 200
        data = list_resp.json()
        assert data["total"] == 1
        assert data["reports"][0]["report_id"] == "rpt-2026-02-28"

        self.mock_repo.get_report.return_value = report
        detail_resp = self.client.get(
            "/api/reports/rpt-2026-02-28", headers=headers
        )
        assert detail_resp.status_code == 200
        detail = detail_resp.json()
        assert detail["gemini_result"] is not None
        assert detail["langchain_result"] is not None

        self.mock_orchestrator.run_daily_research.return_value = report
        trigger_resp = self.client.post(
            "/api/reports/trigger",
            json={"date": "2026-02-28"},
            headers=headers,
        )
        assert trigger_resp.status_code == 200
        assert trigger_resp.json()["report_id"] == "rpt-2026-02-28"

    def test_unauthenticated_access_blocked(self) -> None:
        resp = self.client.get("/api/reports/")
        assert resp.status_code == 401

        resp = self.client.get("/api/reports/rpt-001")
        assert resp.status_code == 401

        resp = self.client.post(
            "/api/reports/trigger", json={"date": "2026-02-28"}
        )
        assert resp.status_code == 401
