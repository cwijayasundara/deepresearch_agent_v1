"""Tests for src.service.engine_runner — RED phase."""

from unittest.mock import AsyncMock

import pytest

from backend.repo.gemini_client import GeminiResearchClient
from backend.repo.langchain_client import LangChainResearchClient
from backend.service.engine_runner import run_gemini_engine, run_langchain_engine
from backend.types.enums import EngineType, ResearchStatus
from backend.types.errors import GeminiApiError, LangChainError


class TestRunGeminiEngine:
    @pytest.mark.asyncio
    async def test_success(self) -> None:
        client = AsyncMock(spec=GeminiResearchClient)
        client.run_research.return_value = "# Gemini Report\nContent"

        result = await run_gemini_engine(client, "test prompt")
        assert result.engine == EngineType.GEMINI
        assert result.status == ResearchStatus.COMPLETED
        assert "Gemini Report" in result.raw_markdown
        assert result.error_message is None
        assert result.duration_seconds >= 0

    @pytest.mark.asyncio
    async def test_failure(self) -> None:
        client = AsyncMock(spec=GeminiResearchClient)
        client.run_research.side_effect = GeminiApiError("timeout")

        result = await run_gemini_engine(client, "test prompt")
        assert result.engine == EngineType.GEMINI
        assert result.status == ResearchStatus.FAILED
        assert result.error_message is not None
        assert "timeout" in result.error_message


class TestRunLangChainEngine:
    @pytest.mark.asyncio
    async def test_success(self) -> None:
        client = AsyncMock(spec=LangChainResearchClient)
        client.run_research.return_value = "# LC Report\nContent"

        result = await run_langchain_engine(client, "test prompt")
        assert result.engine == EngineType.LANGCHAIN
        assert result.status == ResearchStatus.COMPLETED
        assert "LC Report" in result.raw_markdown

    @pytest.mark.asyncio
    async def test_failure(self) -> None:
        client = AsyncMock(spec=LangChainResearchClient)
        client.run_research.side_effect = LangChainError("failed")

        result = await run_langchain_engine(client, "test prompt")
        assert result.engine == EngineType.LANGCHAIN
        assert result.status == ResearchStatus.FAILED
        assert "failed" in result.error_message
