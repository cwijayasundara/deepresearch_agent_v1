"""Application error hierarchy."""


class AppError(Exception):
    """Base application error."""


class EngineError(AppError):
    """Error from a research engine."""


class GeminiApiError(EngineError):
    """Error from the Gemini Deep Research API."""


class LangChainError(EngineError):
    """Error from the LangChain research pipeline."""


class FirestoreError(AppError):
    """Error from Firestore operations."""


class AuthError(AppError):
    """Authentication or authorization error."""
