"""Tests for backend.repo.langchain_client — LangGraph upgrade."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend.repo.langchain_client import LangChainResearchClient
from backend.types.errors import LangChainError


class TestLangChainResearchClientInit:
    def test_init_stores_config(self) -> None:
        client = LangChainResearchClient(
            openai_api_key="test-openai",
            tavily_api_key="test-tavily",
            model="gpt-5-mini",
        )
        assert client.model == "gpt-5-mini"

    def test_init_accepts_checkpoint_path(self) -> None:
        client = LangChainResearchClient(
            openai_api_key="test-openai",
            tavily_api_key="test-tavily",
            model="gpt-5-mini",
            checkpoint_path=":memory:",
        )
        assert client._checkpoint_path == ":memory:"


def _make_client(
    key: str = "k", model: str = "m"
) -> LangChainResearchClient:
    """Create a test client with dummy credentials."""
    return LangChainResearchClient(
        openai_api_key=key, tavily_api_key=key, model=model,
    )


def _make_state(
    prompt: str = "", **overrides: object
) -> dict[str, object]:
    """Create a minimal ResearchGraphState dict for tests."""
    base: dict[str, object] = {
        "prompt": prompt,
        "search_context": "",
        "full_prompt": "",
        "section_results": [],
        "combined_markdown": "",
        "run_id": "r1",
        "date": "2026-02-28",
    }
    base.update(overrides)
    return base


def _patch_tavily(
    side_effect: object = None,
) -> tuple[AsyncMock, MagicMock]:
    """Create a mock TavilySearch for patching."""
    mock_fn = AsyncMock(side_effect=side_effect, return_value=[])
    instance = MagicMock()
    instance.ainvoke = mock_fn
    return mock_fn, instance


class TestRunResearch:
    @pytest.mark.asyncio
    async def test_returns_combined_markdown(self) -> None:
        client = _make_client(key="test-openai", model="gpt-5-mini")
        with patch.object(
            client, "_execute_research", new_callable=AsyncMock
        ) as mock_exec:
            mock_exec.return_value = (
                "## TL;DR\n- Item\n\n## Global Viral Events\n### Event"
            )
            result = await client.run_research("Test prompt")
            assert "TL;DR" in result

    @pytest.mark.asyncio
    async def test_raises_langchain_error_on_failure(self) -> None:
        client = _make_client()
        with patch.object(
            client, "_execute_research", new_callable=AsyncMock
        ) as mock_exec:
            mock_exec.side_effect = RuntimeError("LLM timeout")
            with pytest.raises(LangChainError, match="LLM timeout"):
                await client.run_research("Test prompt")

    @pytest.mark.asyncio
    async def test_reraises_langchain_error_directly(self) -> None:
        client = _make_client()
        with patch.object(
            client, "_execute_research", new_callable=AsyncMock
        ) as mock_exec:
            mock_exec.side_effect = LangChainError("Chain failed")
            with pytest.raises(LangChainError, match="Chain failed"):
                await client.run_research("Test prompt")


def _make_search_results() -> list[list[dict[str, str]]]:
    """Sample search results with overlapping URLs for dedup testing."""
    return [
        [{"url": "https://a.com", "title": "A", "content": "Ca"},
         {"url": "https://b.com", "title": "B", "content": "Cb"}],
        [{"url": "https://a.com", "title": "A dup", "content": "Ca2"},
         {"url": "https://c.com", "title": "C", "content": "Cc"}],
        [{"url": "https://d.com", "title": "D", "content": "Cd"}],
    ]


class TestSearchNode:
    @pytest.mark.asyncio
    async def test_parallel_search_deduplicates_urls(self) -> None:
        mock_fn, instance = _patch_tavily(
            side_effect=_make_search_results()
        )
        with patch("langchain_tavily.TavilySearch", return_value=instance):
            ctx = (await _make_client()._search_node(
                _make_state(prompt="AI research")
            ))["search_context"]
            assert ctx.count("https://a.com") == 1
            assert "https://b.com" in ctx
            assert "https://c.com" in ctx
            assert "https://d.com" in ctx

    @pytest.mark.asyncio
    async def test_search_uses_three_queries(self) -> None:
        mock_fn, instance = _patch_tavily()
        with patch("langchain_tavily.TavilySearch", return_value=instance):
            await _make_client()._search_node(
                _make_state(prompt="AI research")
            )
            assert mock_fn.call_count == 3


class TestComposeContextNode:
    def test_combines_prompt_and_context(self) -> None:
        client = _make_client()
        state = _make_state(
            prompt="Research prompt",
            search_context="Search result data",
        )
        result = client._compose_context_node(state)
        assert "Research prompt" in result["full_prompt"]
        assert "Search result data" in result["full_prompt"]


class TestGenerateSectionNode:
    @pytest.mark.asyncio
    async def test_returns_section_result(self) -> None:
        client = _make_client()
        mock_response = MagicMock()
        mock_response.content = "## TL;DR\n- Item 1"

        with patch(
            "langchain_openai.ChatOpenAI"
        ) as mock_llm_cls:
            mock_llm = AsyncMock()
            mock_llm.ainvoke.return_value = mock_response
            mock_llm_cls.return_value = mock_llm

            section_state = {
                "section_name": "tldr",
                "preamble": "Produce TL;DR only",
                "full_prompt": "Full research prompt",
            }
            result = await client._generate_section_node(section_state)
            assert len(result["section_results"]) == 1
            assert result["section_results"][0]["section_name"] == "tldr"
            assert "TL;DR" in result["section_results"][0]["content"]


class TestCombineResultsNode:
    def test_combines_three_sections(self) -> None:
        state = _make_state(section_results=[
            {"section_name": "tldr", "content": "## TL;DR\n- Item"},
            {"section_name": "events", "content": "## Global Viral Events\n### E1"},
            {"section_name": "dives_audit", "content": "## Strategic Deep Dives\n### D1"},
        ])
        md = _make_client()._combine_results_node(state)["combined_markdown"]
        assert "TL;DR" in md
        assert "Global Viral Events" in md
        assert "Strategic Deep Dives" in md

    def test_handles_missing_sections(self) -> None:
        state = _make_state(section_results=[
            {"section_name": "tldr", "content": "## TL;DR\n- Item"},
        ])
        result = _make_client()._combine_results_node(state)
        assert "TL;DR" in result["combined_markdown"]


class TestGraphRouting:
    def test_route_to_sections_returns_three_sends(self) -> None:
        state = _make_state(full_prompt="Full prompt here")
        sends = _make_client()._route_to_sections(state)
        assert len(sends) == 3
        assert all(s.node == "generate_section" for s in sends)

    def test_route_sections_have_distinct_preambles(self) -> None:
        state = _make_state(full_prompt="Prompt")
        sends = _make_client()._route_to_sections(state)
        section_names = [s.arg["section_name"] for s in sends]
        assert "tldr" in section_names
        assert "events" in section_names
        assert "dives_audit" in section_names
        assert len(set(s.arg["preamble"] for s in sends)) == 3


class TestGraphCompilation:
    def test_build_graph_returns_compiled_graph(self) -> None:
        graph = _make_client()._build_graph()
        assert graph is not None
        assert hasattr(graph, "ainvoke")
