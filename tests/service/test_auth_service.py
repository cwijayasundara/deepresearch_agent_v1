"""Tests for src.service.auth_service — RED phase."""

import pytest

from src.service.auth_service import AuthService
from src.types.errors import AuthError


class TestAuthService:
    def setup_method(self) -> None:
        self.service = AuthService(
            shared_password="correct-password",
            jwt_secret="test-secret",
            jwt_algorithm="HS256",
            jwt_expire_hours=24,
        )

    def test_authenticate_success(self) -> None:
        token = self.service.authenticate("correct-password")
        assert token.token_type == "bearer"
        assert len(token.access_token) > 0

    def test_authenticate_wrong_password(self) -> None:
        with pytest.raises(AuthError, match="Invalid password"):
            self.service.authenticate("wrong-password")

    def test_verify_token_valid(self) -> None:
        token = self.service.authenticate("correct-password")
        payload = self.service.verify_token(token.access_token)
        assert payload["sub"] == "user"

    def test_verify_token_invalid(self) -> None:
        with pytest.raises(AuthError, match="Invalid token"):
            self.service.verify_token("garbage.token.here")

    def test_verify_token_expired(self) -> None:
        service = AuthService(
            shared_password="pw",
            jwt_secret="secret",
            jwt_algorithm="HS256",
            jwt_expire_hours=0,
        )
        token = service.authenticate("pw")
        with pytest.raises(AuthError, match="Invalid token"):
            service.verify_token(token.access_token)
