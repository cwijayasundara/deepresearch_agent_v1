"""Enumerations for the deep research agent."""

from enum import Enum


class EngineType(str, Enum):
    """Research engine type."""

    GEMINI = "gemini"
    LANGCHAIN = "langchain"


class ResearchStatus(str, Enum):
    """Status of a research run."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class ConfidenceLevel(str, Enum):
    """Confidence level for an event or finding."""

    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class EventCategory(str, Enum):
    """Category of a viral AI event."""

    PRODUCT_LAUNCH = "product_launch"
    FUNDING = "funding"
    PARTNERSHIP = "partnership"
    REGULATION = "regulation"
    RESEARCH = "research"
    OPEN_SOURCE = "open_source"
