"""LangChain research client using Tavily + GPT-4.1."""

import logging

from src.types.errors import LangChainError

logger = logging.getLogger(__name__)


class LangChainResearchClient:
    """Client for running research via LangChain with Tavily and OpenAI."""

    def __init__(
        self, openai_api_key: str, tavily_api_key: str, model: str
    ) -> None:
        self.model = model
        self._openai_api_key = openai_api_key
        self._tavily_api_key = tavily_api_key

    async def run_research(self, prompt: str) -> str:
        """Execute a research query and return markdown result."""
        logger.info("Starting LangChain research with model %s", self.model)
        try:
            return await self._execute_research(prompt)
        except LangChainError:
            raise
        except Exception as exc:
            logger.error("LangChain research failed: %s", exc)
            raise LangChainError(
                f"LangChain research failed: {exc}"
            ) from exc

    async def _execute_research(self, prompt: str) -> str:
        """Execute the LangChain agent pipeline."""
        from langchain_community.tools.tavily_search import (
            TavilySearchResults,
        )
        from langchain_openai import ChatOpenAI

        llm = ChatOpenAI(
            model=self.model,
            api_key=self._openai_api_key,
        )
        search_tool = TavilySearchResults(
            max_results=10,
            api_key=self._tavily_api_key,
        )
        search_results = await search_tool.ainvoke(prompt)
        context = "\n".join(
            str(r) for r in search_results
        )
        full_prompt = (
            f"{prompt}\n\nSearch results for context:\n{context}"
        )
        response = await llm.ainvoke(full_prompt)
        return str(response.content)
