"""Tests for src.repo.gemini_client — RED phase."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.repo.gemini_client import GeminiResearchClient
from src.types.errors import GeminiApiError


class TestGeminiResearchClient:
    def test_init(self) -> None:
        client = GeminiResearchClient(
            api_key="test-key", model="gemini-2.5-flash"
        )
        assert client.model == "gemini-2.5-flash"

    @pytest.mark.asyncio
    async def test_run_research_returns_markdown(self) -> None:
        client = GeminiResearchClient(
            api_key="test-key", model="gemini-2.5-flash"
        )
        mock_response = MagicMock()
        mock_response.text = "# Research Report\nContent here"

        with patch.object(
            client, "_execute_research", new_callable=AsyncMock
        ) as mock_exec:
            mock_exec.return_value = "# Research Report\nContent here"
            result = await client.run_research("Test prompt")
            assert "Research Report" in result

    @pytest.mark.asyncio
    async def test_run_research_raises_on_failure(self) -> None:
        client = GeminiResearchClient(
            api_key="test-key", model="gemini-2.5-flash"
        )
        with patch.object(
            client, "_execute_research", new_callable=AsyncMock
        ) as mock_exec:
            mock_exec.side_effect = GeminiApiError("API failure")
            with pytest.raises(GeminiApiError, match="API failure"):
                await client.run_research("Test prompt")
