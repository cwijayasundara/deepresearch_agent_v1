"""Tests for src.types.report — RED phase."""

from datetime import datetime, timezone

from src.types.enums import EngineType, ResearchStatus
from src.types.events import CompletenessAudit
from src.types.report import EngineResult, ResearchReport


class TestEngineResult:
    def test_create(self) -> None:
        result = EngineResult(
            engine=EngineType.GEMINI,
            status=ResearchStatus.COMPLETED,
            raw_markdown="# Report\nContent here",
            tldr="Quick summary",
            viral_events=[],
            deep_dives=[],
            completeness_audit=None,
            started_at=datetime(2026, 2, 28, tzinfo=timezone.utc),
            completed_at=datetime(2026, 2, 28, tzinfo=timezone.utc),
            duration_seconds=120.5,
            error_message=None,
        )
        assert result.engine == EngineType.GEMINI
        assert result.status == ResearchStatus.COMPLETED
        assert result.duration_seconds == 120.5

    def test_failed_result(self) -> None:
        result = EngineResult(
            engine=EngineType.LANGCHAIN,
            status=ResearchStatus.FAILED,
            raw_markdown="",
            tldr=None,
            viral_events=[],
            deep_dives=[],
            completeness_audit=None,
            started_at=datetime(2026, 2, 28, tzinfo=timezone.utc),
            completed_at=datetime(2026, 2, 28, tzinfo=timezone.utc),
            duration_seconds=5.0,
            error_message="API timeout",
        )
        assert result.status == ResearchStatus.FAILED
        assert result.error_message == "API timeout"


class TestResearchReport:
    def test_create_full(self) -> None:
        now = datetime(2026, 2, 28, tzinfo=timezone.utc)
        gemini_result = EngineResult(
            engine=EngineType.GEMINI,
            status=ResearchStatus.COMPLETED,
            raw_markdown="# Gemini report",
            tldr="Gemini summary",
            viral_events=[],
            deep_dives=[],
            completeness_audit=CompletenessAudit(
                verified_signals=10,
                sources_checked=5,
                confidence_score=0.9,
                gaps=[],
            ),
            started_at=now,
            completed_at=now,
            duration_seconds=60.0,
            error_message=None,
        )
        report = ResearchReport(
            report_id="rpt-2026-02-28",
            run_date=now,
            gemini_result=gemini_result,
            langchain_result=None,
            created_at=now,
        )
        assert report.report_id == "rpt-2026-02-28"
        assert report.gemini_result is not None
        assert report.langchain_result is None

    def test_serialization_round_trip(self) -> None:
        now = datetime(2026, 2, 28, tzinfo=timezone.utc)
        report = ResearchReport(
            report_id="rpt-test",
            run_date=now,
            gemini_result=None,
            langchain_result=None,
            created_at=now,
        )
        data = report.model_dump()
        restored = ResearchReport.model_validate(data)
        assert restored.report_id == report.report_id
