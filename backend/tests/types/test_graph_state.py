"""Tests for backend.types.graph_state — RED phase."""

import operator
from typing import Annotated, get_type_hints

from backend.types.graph_state import (
    ResearchGraphState,
    SectionGenerateState,
    SectionResult,
)


class TestSectionResult:
    def test_create_section_result(self) -> None:
        result: SectionResult = {
            "section_name": "tldr",
            "content": "## TL;DR\n- Item 1",
        }
        assert result["section_name"] == "tldr"
        assert "TL;DR" in result["content"]

    def test_section_result_has_required_keys(self) -> None:
        hints = get_type_hints(SectionResult)
        assert "section_name" in hints
        assert "content" in hints


class TestSectionGenerateState:
    def test_create_section_generate_state(self) -> None:
        state: SectionGenerateState = {
            "section_name": "events",
            "preamble": "You are an analyst...",
            "full_prompt": "Research prompt here",
        }
        assert state["section_name"] == "events"
        assert state["preamble"].startswith("You are")

    def test_has_required_keys(self) -> None:
        hints = get_type_hints(SectionGenerateState)
        assert "section_name" in hints
        assert "preamble" in hints
        assert "full_prompt" in hints


class TestResearchGraphState:
    def test_create_research_graph_state(self) -> None:
        state: ResearchGraphState = {
            "prompt": "Research prompt",
            "search_context": "context",
            "full_prompt": "full prompt",
            "section_results": [],
            "combined_markdown": "",
            "run_id": "run-123",
            "date": "2026-02-28",
        }
        assert state["run_id"] == "run-123"
        assert state["section_results"] == []

    def test_has_all_required_keys(self) -> None:
        hints = get_type_hints(ResearchGraphState, include_extras=True)
        assert "prompt" in hints
        assert "search_context" in hints
        assert "full_prompt" in hints
        assert "section_results" in hints
        assert "combined_markdown" in hints
        assert "run_id" in hints
        assert "date" in hints

    def test_section_results_has_reducer(self) -> None:
        hints = get_type_hints(ResearchGraphState, include_extras=True)
        section_hint = hints["section_results"]
        assert hasattr(section_hint, "__metadata__")
        reducer = section_hint.__metadata__[0]
        assert reducer is operator.add
