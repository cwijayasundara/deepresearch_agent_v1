"""LangGraph research client with parallel search and LLM fan-out."""

import asyncio
import logging
import os
import uuid

from langgraph.graph import END, START, StateGraph
from langgraph.types import Send

from backend.config.prompts import (
    DIVES_AUDIT_PREAMBLE,
    EVENTS_PREAMBLE,
    TLDR_PREAMBLE,
)
from backend.repo.context_trimmer import trim_context
from backend.types.errors import LangChainError
from backend.types.graph_state import (
    ResearchGraphState,
    SectionGenerateState,
)

logger = logging.getLogger(__name__)

SECTION_ORDER = ["tldr", "events", "dives_audit"]

SECTION_PREAMBLES: dict[str, str] = {
    "tldr": TLDR_PREAMBLE,
    "events": EVENTS_PREAMBLE,
    "dives_audit": DIVES_AUDIT_PREAMBLE,
}


def _build_search_queries(prompt: str) -> list[str]:
    """Create 3 diverse search queries from the prompt topic."""
    topic = prompt[:200]
    return [
        f"{topic} latest news today",
        f"{topic} breakthroughs announcements",
        f"{topic} funding partnerships",
    ]


def _dedup_results(raw_results: list[object]) -> str:
    """Deduplicate search results by URL."""
    seen_urls: set[str] = set()
    combined: list[str] = []
    for batch in raw_results:
        if isinstance(batch, Exception):
            logger.warning("Search query failed: %s", batch)
            continue
        if not isinstance(batch, list):
            continue
        for item in batch:
            url = item.get("url", "")
            if url and url not in seen_urls:
                seen_urls.add(url)
                combined.append(
                    f"Title: {item.get('title', '')}\n"
                    f"URL: {url}\n"
                    f"Content: {item.get('content', '')}"
                )
    logger.info("Search collected %d unique results", len(combined))
    return "\n---\n".join(combined)


def _build_initial_state(
    prompt: str, run_id: str
) -> ResearchGraphState:
    """Create the initial state dict for the pipeline."""
    return {
        "prompt": prompt,
        "search_context": "",
        "full_prompt": "",
        "section_results": [],
        "combined_markdown": "",
        "run_id": run_id,
        "date": "",
    }


class LangChainResearchClient:
    """Research client using LangGraph StateGraph pipeline."""

    def __init__(
        self,
        openai_api_key: str,
        tavily_api_key: str,
        model: str,
        checkpoint_path: str = ":memory:",
    ) -> None:
        self.model = model
        self._openai_api_key = openai_api_key
        self._tavily_api_key = tavily_api_key
        self._checkpoint_path = checkpoint_path

    def _build_graph(self) -> object:
        """Construct and compile the LangGraph StateGraph."""
        graph = StateGraph(ResearchGraphState)
        graph.add_node("search", self._search_node)
        graph.add_node("compose_context", self._compose_context_node)
        graph.add_node(
            "generate_section", self._generate_section_node
        )
        graph.add_node("combine_results", self._combine_results_node)
        self._add_graph_edges(graph)
        return graph.compile()

    def _add_graph_edges(self, graph: StateGraph) -> None:
        """Wire up the graph edges and conditional routing."""
        graph.add_edge(START, "search")
        graph.add_edge("search", "compose_context")
        graph.add_conditional_edges(
            "compose_context",
            self._route_to_sections,
            ["generate_section"],
        )
        graph.add_edge("generate_section", "combine_results")
        graph.add_edge("combine_results", END)

    def _compose_context_node(
        self, state: ResearchGraphState
    ) -> dict[str, str]:
        """Combine prompt + trimmed search context."""
        trimmed = trim_context(state["prompt"], state["search_context"])
        return {
            "full_prompt": (
                f"{state['prompt']}\n\nSearch context:\n{trimmed}"
            )
        }

    def _route_to_sections(
        self, state: ResearchGraphState
    ) -> list[Send]:
        """Fan out to 3 parallel LLM section generators."""
        return [
            Send(
                "generate_section",
                SectionGenerateState(
                    section_name=name,
                    preamble=preamble,
                    full_prompt=state["full_prompt"],
                ),
            )
            for name, preamble in SECTION_PREAMBLES.items()
        ]

    def _combine_results_node(
        self, state: ResearchGraphState
    ) -> dict[str, str]:
        """Merge section outputs in canonical order."""
        by_name = {
            r["section_name"]: r["content"]
            for r in state["section_results"]
        }
        parts = [by_name.get(s, "") for s in SECTION_ORDER]
        return {"combined_markdown": "\n\n".join(parts)}

    async def run_research(self, prompt: str) -> str:
        """Execute the LangGraph research pipeline."""
        logger.info(
            "Starting LangGraph research with model %s", self.model
        )
        try:
            return await self._execute_research(prompt)
        except LangChainError:
            raise
        except Exception as exc:
            logger.error("LangChain research failed: %s", exc)
            raise LangChainError(
                f"LangChain research failed: {exc}"
            ) from exc

    def _build_run_config(self, run_id: str) -> dict[str, object]:
        """Build RunnableConfig with metadata and thread ID."""
        return {
            "metadata": {"run_id": run_id},
            "tags": ["research"],
            "configurable": {"thread_id": run_id},
        }

    async def _execute_research(self, prompt: str) -> str:
        """Run the compiled LangGraph pipeline."""
        graph = self._build_graph()
        run_id = str(uuid.uuid4())
        config = self._build_run_config(run_id)
        result = await graph.ainvoke(
            _build_initial_state(prompt, run_id), config=config
        )
        return result["combined_markdown"]

    async def _search_node(
        self, state: ResearchGraphState
    ) -> dict[str, str]:
        """Run 3 parallel Tavily searches and deduplicate."""
        from langchain_tavily import TavilySearch

        os.environ["TAVILY_API_KEY"] = self._tavily_api_key
        search_tool = TavilySearch(max_results=10)
        queries = _build_search_queries(state["prompt"])
        logger.info(
            "Starting parallel search (%d queries)", len(queries)
        )
        results = await asyncio.gather(
            *[search_tool.ainvoke(q) for q in queries],
            return_exceptions=True,
        )
        return {"search_context": _dedup_results(results)}

    def _build_section_messages(
        self, state: SectionGenerateState
    ) -> list[dict[str, str]]:
        """Build system/user message pair for a section call."""
        return [
            {"role": "system", "content": state["preamble"]},
            {"role": "user", "content": state["full_prompt"]},
        ]

    async def _generate_section_node(
        self, state: SectionGenerateState
    ) -> dict[str, list[dict[str, str]]]:
        """Call LLM with a specialized preamble for one section."""
        from langchain_openai import ChatOpenAI

        llm = ChatOpenAI(
            model=self.model, api_key=self._openai_api_key
        )
        messages = self._build_section_messages(state)
        response = await llm.ainvoke(messages)
        return {
            "section_results": [
                {
                    "section_name": state["section_name"],
                    "content": str(response.content),
                }
            ]
        }
