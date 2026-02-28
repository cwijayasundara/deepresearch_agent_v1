"""Tests for src.types.errors — RED phase."""

from src.types.errors import (
    AppError,
    AuthError,
    EngineError,
    FirestoreError,
    GeminiApiError,
    LangChainError,
)


class TestAppError:
    def test_is_exception(self) -> None:
        err = AppError("something broke")
        assert isinstance(err, Exception)
        assert str(err) == "something broke"


class TestEngineError:
    def test_inherits_app_error(self) -> None:
        err = EngineError("engine failed")
        assert isinstance(err, AppError)


class TestGeminiApiError:
    def test_inherits_engine_error(self) -> None:
        err = GeminiApiError("gemini issue")
        assert isinstance(err, EngineError)
        assert isinstance(err, AppError)


class TestLangChainError:
    def test_inherits_engine_error(self) -> None:
        err = LangChainError("langchain issue")
        assert isinstance(err, EngineError)


class TestFirestoreError:
    def test_inherits_app_error(self) -> None:
        err = FirestoreError("db issue")
        assert isinstance(err, AppError)


class TestAuthError:
    def test_inherits_app_error(self) -> None:
        err = AuthError("auth issue")
        assert isinstance(err, AppError)
