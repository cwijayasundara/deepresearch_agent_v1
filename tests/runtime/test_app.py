"""Tests for src.runtime.app — RED phase."""

from fastapi.testclient import TestClient

from src.ui.app_factory import create_app


class TestCreateApp:
    def test_returns_fastapi_instance(self) -> None:
        app = create_app()
        assert app is not None
        assert app.title == "Deep Research Agent"

    def test_cors_enabled(self) -> None:
        app = create_app()
        client = TestClient(app)
        resp = client.options(
            "/health",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET",
            },
        )
        assert resp.status_code in (200, 204)
