"""Tests for src.ui.health_routes — RED phase."""

from fastapi.testclient import TestClient

from backend.ui.app_factory import create_app


class TestHealthRoutes:
    def setup_method(self) -> None:
        app = create_app()
        self.client = TestClient(app)

    def test_health_returns_ok(self) -> None:
        resp = self.client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"
