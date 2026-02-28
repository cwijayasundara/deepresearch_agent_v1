"""Tests for src.types.events — RED phase."""

from backend.types.enums import ConfidenceLevel, EventCategory
from backend.types.events import CompletenessAudit, DeepDive, ViralEvent


class TestViralEvent:
    def test_create_minimal(self) -> None:
        event = ViralEvent(
            headline="GPT-5 Released",
            category=EventCategory.PRODUCT_LAUNCH,
            impact_rating=9,
            confidence=ConfidenceLevel.HIGH,
            source="OpenAI Blog",
        )
        assert event.headline == "GPT-5 Released"
        assert event.category == EventCategory.PRODUCT_LAUNCH
        assert event.impact_rating == 9
        assert event.confidence == ConfidenceLevel.HIGH
        assert event.source == "OpenAI Blog"

    def test_impact_rating_bounds(self) -> None:
        event = ViralEvent(
            headline="Test",
            category=EventCategory.RESEARCH,
            impact_rating=1,
            confidence=ConfidenceLevel.LOW,
            source="arXiv",
        )
        assert 1 <= event.impact_rating <= 10

    def test_serialization_round_trip(self) -> None:
        event = ViralEvent(
            headline="Test",
            category=EventCategory.FUNDING,
            impact_rating=7,
            confidence=ConfidenceLevel.MEDIUM,
            source="TechCrunch",
        )
        data = event.model_dump()
        restored = ViralEvent.model_validate(data)
        assert restored == event


class TestDeepDive:
    def test_create(self) -> None:
        dive = DeepDive(
            title="Multimodal AI Race",
            priority="HIGH",
            summary="Analysis of multimodal competition",
            key_findings=["Finding 1", "Finding 2"],
        )
        assert dive.title == "Multimodal AI Race"
        assert dive.priority == "HIGH"
        assert len(dive.key_findings) == 2


class TestCompletenessAudit:
    def test_create(self) -> None:
        audit = CompletenessAudit(
            verified_signals=42,
            sources_checked=15,
            confidence_score=0.87,
            gaps=["Missing Asian market data"],
        )
        assert audit.verified_signals == 42
        assert audit.sources_checked == 15
        assert audit.confidence_score == 0.87
        assert len(audit.gaps) == 1
