"""Research orchestrator — runs both engines in parallel."""

import asyncio
import logging
from datetime import datetime, timezone

from src.config.prompts import build_research_prompt
from src.repo.firestore_client import FirestoreRepo
from src.repo.gemini_client import GeminiResearchClient
from src.repo.langchain_client import LangChainResearchClient
from src.service.engine_runner import run_gemini_engine, run_langchain_engine
from src.types.report import ResearchReport

logger = logging.getLogger(__name__)


class ResearchOrchestrator:
    """Orchestrates daily research across both engines."""

    def __init__(
        self,
        gemini_client: GeminiResearchClient,
        langchain_client: LangChainResearchClient,
        firestore_repo: FirestoreRepo,
    ) -> None:
        self._gemini = gemini_client
        self._langchain = langchain_client
        self._firestore = firestore_repo

    async def run_daily_research(self, date: str) -> ResearchReport:
        """Run both engines in parallel and save the report."""
        prompt = build_research_prompt(date)
        report_id = f"rpt-{date}"
        logger.info("Starting daily research for %s", date)

        gemini_result, langchain_result = await asyncio.gather(
            run_gemini_engine(self._gemini, prompt),
            run_langchain_engine(self._langchain, prompt),
        )

        now = datetime.now(timezone.utc)
        report = ResearchReport(
            report_id=report_id,
            run_date=now,
            gemini_result=gemini_result,
            langchain_result=langchain_result,
            created_at=now,
        )

        await self._firestore.save_report(report)
        logger.info("Daily research complete: %s", report_id)
        return report
