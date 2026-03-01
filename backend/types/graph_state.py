"""TypedDict state definitions for LangGraph research pipeline."""

import operator
from typing import Annotated, TypedDict


class SectionResult(TypedDict):
    """Output from a single LLM section generation."""

    section_name: str
    content: str


class SectionGenerateState(TypedDict):
    """Input state sent to each parallel section generator via Send()."""

    section_name: str
    preamble: str
    full_prompt: str


class ResearchGraphState(TypedDict):
    """Top-level state flowing through the LangGraph research pipeline."""

    prompt: str
    search_context: str
    full_prompt: str
    section_results: Annotated[list[SectionResult], operator.add]
    combined_markdown: str
    run_id: str
    date: str
