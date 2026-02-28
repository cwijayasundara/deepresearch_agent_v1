"""Tests for src.types.enums — RED phase."""

from src.types.enums import (
    ConfidenceLevel,
    EngineType,
    EventCategory,
    ResearchStatus,
)


class TestEngineType:
    def test_gemini_value(self) -> None:
        assert EngineType.GEMINI.value == "gemini"

    def test_langchain_value(self) -> None:
        assert EngineType.LANGCHAIN.value == "langchain"

    def test_all_members(self) -> None:
        assert set(EngineType) == {EngineType.GEMINI, EngineType.LANGCHAIN}


class TestResearchStatus:
    def test_pending_value(self) -> None:
        assert ResearchStatus.PENDING.value == "pending"

    def test_running_value(self) -> None:
        assert ResearchStatus.RUNNING.value == "running"

    def test_completed_value(self) -> None:
        assert ResearchStatus.COMPLETED.value == "completed"

    def test_failed_value(self) -> None:
        assert ResearchStatus.FAILED.value == "failed"

    def test_all_members(self) -> None:
        members = {s.value for s in ResearchStatus}
        assert members == {"pending", "running", "completed", "failed"}


class TestConfidenceLevel:
    def test_high_value(self) -> None:
        assert ConfidenceLevel.HIGH.value == "high"

    def test_medium_value(self) -> None:
        assert ConfidenceLevel.MEDIUM.value == "medium"

    def test_low_value(self) -> None:
        assert ConfidenceLevel.LOW.value == "low"


class TestEventCategory:
    def test_product_launch_value(self) -> None:
        assert EventCategory.PRODUCT_LAUNCH.value == "product_launch"

    def test_funding_value(self) -> None:
        assert EventCategory.FUNDING.value == "funding"

    def test_partnership_value(self) -> None:
        assert EventCategory.PARTNERSHIP.value == "partnership"

    def test_regulation_value(self) -> None:
        assert EventCategory.REGULATION.value == "regulation"

    def test_research_value(self) -> None:
        assert EventCategory.RESEARCH.value == "research"

    def test_open_source_value(self) -> None:
        assert EventCategory.OPEN_SOURCE.value == "open_source"
