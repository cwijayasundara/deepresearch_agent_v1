"""Tests for src.config.prompts — RED phase."""

from backend.config.prompts import (
    DIVES_AUDIT_PREAMBLE,
    EVENTS_PREAMBLE,
    RESEARCH_PROMPT_TEMPLATE,
    TLDR_PREAMBLE,
    build_research_prompt,
)


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


class TestTldrPreamble:
    def test_mentions_tldr(self) -> None:
        assert "TL;DR" in TLDR_PREAMBLE

    def test_restricts_to_single_section(self) -> None:
        assert "ONLY" in TLDR_PREAMBLE

    def test_is_nonempty_string(self) -> None:
        assert isinstance(TLDR_PREAMBLE, str)
        assert len(TLDR_PREAMBLE) > 20


class TestEventsPreamble:
    def test_mentions_viral_events(self) -> None:
        assert "Global Viral Events" in EVENTS_PREAMBLE

    def test_restricts_to_single_section(self) -> None:
        assert "ONLY" in EVENTS_PREAMBLE

    def test_specifies_event_format(self) -> None:
        assert "Category" in EVENTS_PREAMBLE
        assert "Impact Rating" in EVENTS_PREAMBLE
        assert "Confidence" in EVENTS_PREAMBLE


class TestDivesAuditPreamble:
    def test_mentions_deep_dives(self) -> None:
        assert "Strategic Deep Dives" in DIVES_AUDIT_PREAMBLE

    def test_mentions_completeness_audit(self) -> None:
        assert "Completeness Audit" in DIVES_AUDIT_PREAMBLE

    def test_restricts_to_sections(self) -> None:
        assert "ONLY" in DIVES_AUDIT_PREAMBLE
