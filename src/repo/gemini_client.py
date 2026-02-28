"""Gemini Deep Research API client."""

import logging

from google import genai

from src.types.errors import GeminiApiError

logger = logging.getLogger(__name__)


class GeminiResearchClient:
    """Client for running research via Google Gemini Deep Research."""

    def __init__(self, api_key: str, model: str) -> None:
        self.model = model
        self._client = genai.Client(api_key=api_key)

    async def run_research(self, prompt: str) -> str:
        """Execute a research query and return markdown result."""
        logger.info("Starting Gemini research with model %s", self.model)
        try:
            return await self._execute_research(prompt)
        except GeminiApiError:
            raise
        except Exception as exc:
            logger.error("Gemini research failed: %s", exc)
            raise GeminiApiError(f"Gemini research failed: {exc}") from exc

    async def _execute_research(self, prompt: str) -> str:
        """Execute the actual Gemini API call."""
        response = self._client.models.generate_content(
            model=self.model,
            contents=prompt,
        )
        if response.text is None:
            raise GeminiApiError("Gemini returned empty response")
        return response.text
