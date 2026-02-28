"""Tests for src.runtime.dependencies."""

from unittest.mock import MagicMock, patch

from src.config.settings import Settings
from src.runtime.dependencies import (
    get_auth_service,
    get_firestore_repo,
    get_settings,
)


class TestGetSettings:
    def test_returns_settings(self) -> None:
        settings = get_settings()
        assert isinstance(settings, Settings)


class TestGetAuthService:
    def test_returns_auth_service(self) -> None:
        service = get_auth_service()
        assert service is not None


class TestGetFirestoreRepo:
    def test_returns_repo(self) -> None:
        with patch(
            "google.cloud.firestore.AsyncClient"
        ) as mock_cls:
            mock_cls.return_value = MagicMock()
            repo = get_firestore_repo()
            assert repo is not None
            assert repo.collection_name == "research_reports"
