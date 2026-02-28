"""Tests for src.config.prompts — RED phase."""

from src.config.prompts import RESEARCH_PROMPT_TEMPLATE, build_research_prompt


class TestResearchPromptTemplate:
    def test_template_contains_placeholder(self) -> None:
        assert "{date}" in RESEARCH_PROMPT_TEMPLATE

    def test_template_mentions_viral(self) -> None:
        assert "viral" in RESEARCH_PROMPT_TEMPLATE.lower()


class TestBuildResearchPrompt:
    def test_injects_date(self) -> None:
        prompt = build_research_prompt("2026-02-28")
        assert "2026-02-28" in prompt

    def test_returns_string(self) -> None:
        result = build_research_prompt("2026-01-01")
        assert isinstance(result, str)
        assert len(result) > 50
