"""Tests for src.ui.router — RED phase."""

from fastapi import FastAPI

from backend.ui.router import register_routes


class TestRegisterRoutes:
    def test_registers_all_routes(self) -> None:
        app = FastAPI()
        register_routes(app)
        paths = [route.path for route in app.routes]
        assert "/health" in paths
        assert "/api/auth/login" in paths
        assert "/api/reports/" in paths
        assert "/api/reports/{report_id}" in paths
        assert "/api/reports/trigger" in paths
