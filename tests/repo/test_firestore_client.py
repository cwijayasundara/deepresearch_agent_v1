"""Tests for src.repo.firestore_client — RED phase."""

from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.repo.firestore_client import FirestoreRepo
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


class TestFirestoreRepo:
    def test_init(self) -> None:
        mock_db = MagicMock()
        repo = FirestoreRepo(db=mock_db, collection_name="test_reports")
        assert repo.collection_name == "test_reports"

    @pytest.mark.asyncio
    async def test_save_report(self) -> None:
        mock_db = MagicMock()
        mock_collection = MagicMock()
        mock_doc = MagicMock()
        mock_doc.set = AsyncMock()
        mock_collection.document.return_value = mock_doc
        mock_db.collection.return_value = mock_collection

        repo = FirestoreRepo(db=mock_db, collection_name="reports")
        report = _make_report()
        await repo.save_report(report)

        mock_db.collection.assert_called_once_with("reports")
        mock_collection.document.assert_called_once_with("rpt-001")
        mock_doc.set.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_report_found(self) -> None:
        mock_db = MagicMock()
        mock_collection = MagicMock()
        mock_doc_ref = MagicMock()
        mock_snapshot = MagicMock()
        mock_snapshot.exists = True
        report = _make_report()
        mock_snapshot.to_dict.return_value = report.model_dump(mode="json")
        mock_doc_ref.get = AsyncMock(return_value=mock_snapshot)
        mock_collection.document.return_value = mock_doc_ref
        mock_db.collection.return_value = mock_collection

        repo = FirestoreRepo(db=mock_db, collection_name="reports")
        result = await repo.get_report("rpt-001")
        assert result is not None
        assert result.report_id == "rpt-001"

    @pytest.mark.asyncio
    async def test_get_report_not_found(self) -> None:
        mock_db = MagicMock()
        mock_collection = MagicMock()
        mock_doc_ref = MagicMock()
        mock_snapshot = AsyncMock()
        mock_snapshot.exists = False
        mock_doc_ref.get = AsyncMock(return_value=mock_snapshot)
        mock_collection.document.return_value = mock_doc_ref
        mock_db.collection.return_value = mock_collection

        repo = FirestoreRepo(db=mock_db, collection_name="reports")
        result = await repo.get_report("rpt-nonexist")
        assert result is None

    @pytest.mark.asyncio
    async def test_list_reports(self) -> None:
        mock_db = MagicMock()
        mock_collection = MagicMock()
        report = _make_report()
        mock_doc = MagicMock()
        mock_doc.to_dict.return_value = report.model_dump(mode="json")

        mock_query = MagicMock()
        mock_query.order_by = MagicMock(return_value=mock_query)
        mock_query.limit = MagicMock(return_value=mock_query)
        mock_query.get = AsyncMock(return_value=[mock_doc])
        mock_collection.order_by = MagicMock(return_value=mock_query)
        mock_db.collection.return_value = mock_collection

        repo = FirestoreRepo(db=mock_db, collection_name="reports")
        results = await repo.list_reports(limit=10)
        assert len(results) == 1
