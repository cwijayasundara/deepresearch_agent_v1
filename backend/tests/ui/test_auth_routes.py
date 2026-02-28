"""Tests for src.ui.auth_routes — RED phase."""

from fastapi.testclient import TestClient

from backend.ui.app_factory import create_app


class TestAuthRoutes:
    def setup_method(self) -> None:
        app = create_app()
        self.client = TestClient(app)

    def test_login_success(self) -> None:
        resp = self.client.post(
            "/api/auth/login", json={"password": "test-password"}
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_wrong_password(self) -> None:
        resp = self.client.post(
            "/api/auth/login", json={"password": "wrong"}
        )
        assert resp.status_code == 401
