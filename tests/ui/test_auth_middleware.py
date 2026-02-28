"""Tests for src.ui.auth_middleware — RED phase."""

import pytest
from fastapi import HTTPException

from src.service.auth_service import AuthService
from src.ui.auth_middleware import require_auth


class TestRequireAuth:
    def setup_method(self) -> None:
        self.auth_service = AuthService(
            shared_password="pw",
            jwt_secret="secret",
            jwt_algorithm="HS256",
            jwt_expire_hours=24,
        )

    def test_valid_token(self) -> None:
        token = self.auth_service.authenticate("pw")
        payload = require_auth(
            f"Bearer {token.access_token}", self.auth_service
        )
        assert payload["sub"] == "user"

    def test_missing_header(self) -> None:
        with pytest.raises(HTTPException) as exc_info:
            require_auth(None, self.auth_service)
        assert exc_info.value.status_code == 401

    def test_invalid_scheme(self) -> None:
        with pytest.raises(HTTPException) as exc_info:
            require_auth("Basic abc123", self.auth_service)
        assert exc_info.value.status_code == 401

    def test_invalid_token(self) -> None:
        with pytest.raises(HTTPException) as exc_info:
            require_auth("Bearer bad.token.here", self.auth_service)
        assert exc_info.value.status_code == 401
