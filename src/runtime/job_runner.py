"""Cloud Run Job entry point for scheduled research."""

import asyncio
import logging
from datetime import datetime, timezone

from src.runtime.dependencies import get_orchestrator
from src.service.research_orchestrator import ResearchOrchestrator

logger = logging.getLogger(__name__)


def _build_orchestrator() -> ResearchOrchestrator:
    """Build orchestrator with default settings."""
    return get_orchestrator()


async def run_daily_job(date: str | None = None) -> None:
    """Execute the daily research job."""
    if date is None:
        date = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    logger.info("Starting daily job for %s", date)
    orchestrator = _build_orchestrator()
    report = await orchestrator.run_daily_research(date)
    logger.info("Daily job complete: %s", report.report_id)


def main() -> None:
    """CLI entry point for the job runner."""
    logging.basicConfig(level=logging.INFO)
    asyncio.run(run_daily_job())


if __name__ == "__main__":
    main()
