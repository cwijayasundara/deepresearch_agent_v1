"""Tests for src.repo.langchain_client — RED phase."""

from unittest.mock import AsyncMock, patch

import pytest

from src.repo.langchain_client import LangChainResearchClient
from src.types.errors import LangChainError


class TestLangChainResearchClient:
    def test_init(self) -> None:
        client = LangChainResearchClient(
            openai_api_key="test-openai",
            tavily_api_key="test-tavily",
            model="gpt-4.1",
        )
        assert client.model == "gpt-4.1"

    @pytest.mark.asyncio
    async def test_run_research_returns_markdown(self) -> None:
        client = LangChainResearchClient(
            openai_api_key="test-openai",
            tavily_api_key="test-tavily",
            model="gpt-4.1",
        )
        with patch.object(
            client, "_execute_research", new_callable=AsyncMock
        ) as mock_exec:
            mock_exec.return_value = "# LangChain Report\nFindings"
            result = await client.run_research("Test prompt")
            assert "LangChain Report" in result

    @pytest.mark.asyncio
    async def test_run_research_raises_on_failure(self) -> None:
        client = LangChainResearchClient(
            openai_api_key="test-openai",
            tavily_api_key="test-tavily",
            model="gpt-4.1",
        )
        with patch.object(
            client, "_execute_research", new_callable=AsyncMock
        ) as mock_exec:
            mock_exec.side_effect = LangChainError("Chain failed")
            with pytest.raises(LangChainError, match="Chain failed"):
                await client.run_research("Test prompt")
