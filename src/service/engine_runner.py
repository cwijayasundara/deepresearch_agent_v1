"""Engine runner functions for executing research engines."""

import logging
import time
from datetime import datetime, timezone

from src.repo.gemini_client import GeminiResearchClient
from src.repo.langchain_client import LangChainResearchClient
from src.service.report_parser import ReportParser
from src.types.enums import EngineType, ResearchStatus
from src.types.report import EngineResult

logger = logging.getLogger(__name__)
_parser = ReportParser()


async def run_gemini_engine(
    client: GeminiResearchClient, prompt: str
) -> EngineResult:
    """Run the Gemini research engine and return structured result."""
    return await _run_engine(
        engine_type=EngineType.GEMINI,
        run_fn=client.run_research,
        prompt=prompt,
    )


async def run_langchain_engine(
    client: LangChainResearchClient, prompt: str
) -> EngineResult:
    """Run the LangChain research engine and return structured result."""
    return await _run_engine(
        engine_type=EngineType.LANGCHAIN,
        run_fn=client.run_research,
        prompt=prompt,
    )


async def _run_engine(
    engine_type: EngineType,
    run_fn: object,
    prompt: str,
) -> EngineResult:
    """Generic engine runner with timing and error handling."""
    started_at = datetime.now(timezone.utc)
    start_time = time.monotonic()

    try:
        raw_markdown = await run_fn(prompt)
        completed_at = datetime.now(timezone.utc)
        duration = time.monotonic() - start_time

        tldr = _parser.parse_tldr(raw_markdown)
        viral_events = _parser.parse_viral_events(raw_markdown)
        deep_dives = _parser.parse_deep_dives(raw_markdown)
        audit = _parser.parse_completeness_audit(raw_markdown)

        logger.info(
            "%s engine completed in %.1fs", engine_type.value, duration
        )
        return EngineResult(
            engine=engine_type,
            status=ResearchStatus.COMPLETED,
            raw_markdown=raw_markdown,
            tldr=tldr,
            viral_events=viral_events,
            deep_dives=deep_dives,
            completeness_audit=audit,
            started_at=started_at,
            completed_at=completed_at,
            duration_seconds=duration,
            error_message=None,
        )
    except Exception as exc:
        completed_at = datetime.now(timezone.utc)
        duration = time.monotonic() - start_time
        logger.error("%s engine failed: %s", engine_type.value, exc)
        return EngineResult(
            engine=engine_type,
            status=ResearchStatus.FAILED,
            raw_markdown="",
            tldr=None,
            viral_events=[],
            deep_dives=[],
            completeness_audit=None,
            started_at=started_at,
            completed_at=completed_at,
            duration_seconds=duration,
            error_message=str(exc),
        )
