"""Tests for src.service.research_orchestrator — RED phase."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from backend.repo.firestore_client import FirestoreRepo
from backend.repo.gemini_client import GeminiResearchClient
from backend.repo.langchain_client import LangChainResearchClient
from backend.service.research_orchestrator import ResearchOrchestrator
from backend.types.enums import ResearchStatus


class TestResearchOrchestrator:
    def setup_method(self) -> None:
        self.gemini_client = AsyncMock(spec=GeminiResearchClient)
        self.langchain_client = AsyncMock(spec=LangChainResearchClient)
        self.firestore_repo = AsyncMock(spec=FirestoreRepo)
        self.orchestrator = ResearchOrchestrator(
            gemini_client=self.gemini_client,
            langchain_client=self.langchain_client,
            firestore_repo=self.firestore_repo,
        )

    @pytest.mark.asyncio
    async def test_run_daily_research_both_succeed(self) -> None:
        self.gemini_client.run_research.return_value = "# Gemini\nReport"
        self.langchain_client.run_research.return_value = "# LC\nReport"

        report = await self.orchestrator.run_daily_research("2026-02-28")
        assert report.report_id.startswith("rpt-2026-02-28")
        assert report.gemini_result is not None
        assert report.langchain_result is not None
        assert report.gemini_result.status == ResearchStatus.COMPLETED
        self.firestore_repo.save_report.assert_called_once()

    @pytest.mark.asyncio
    async def test_run_daily_research_gemini_fails(self) -> None:
        self.gemini_client.run_research.side_effect = Exception("Gemini down")
        self.langchain_client.run_research.return_value = "# LC\nReport"

        report = await self.orchestrator.run_daily_research("2026-02-28")
        assert report.gemini_result is not None
        assert report.gemini_result.status == ResearchStatus.FAILED
        assert report.langchain_result.status == ResearchStatus.COMPLETED

    @pytest.mark.asyncio
    async def test_run_daily_research_saves_to_firestore(self) -> None:
        self.gemini_client.run_research.return_value = "# Report"
        self.langchain_client.run_research.return_value = "# Report"

        await self.orchestrator.run_daily_research("2026-02-28")
        self.firestore_repo.save_report.assert_called_once()
