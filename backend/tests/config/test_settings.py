"""Tests for src.config.settings."""

import os

from backend.config.settings import Settings


class TestSettings:
    def test_default_values(self) -> None:
        old = os.environ.pop("APP_ENV", None)
        try:
            s = Settings(
                _env_file=None,
                gemini_api_key="test-gemini",
                openai_api_key="test-openai",
                tavily_api_key="test-tavily",
                app_shared_password="test-pass",
                jwt_secret="test-jwt-secret",
            )
            assert s.app_env == "development"
        finally:
            if old is not None:
                os.environ["APP_ENV"] = old
        assert s.app_port == 8000
        assert s.firestore_project_id == ""
        assert s.firestore_collection == "research_reports"
        assert s.gemini_model == "gemini-3-flash-preview"
        assert s.openai_model == "gpt-5-mini"
        assert s.jwt_algorithm == "HS256"
        assert s.jwt_expire_hours == 24
        assert s.cors_origins == ["http://localhost:3000"]

    def test_custom_values(self) -> None:
        s = Settings(
            app_env="production",
            app_port=9000,
            gemini_api_key="real-key",
            openai_api_key="real-openai",
            tavily_api_key="real-tavily",
            app_shared_password="strong-pass",
            jwt_secret="strong-secret",
            firestore_project_id="my-project",
            cors_origins=["https://app.example.com"],
        )
        assert s.app_env == "production"
        assert s.app_port == 9000
        assert s.firestore_project_id == "my-project"
        assert s.cors_origins == ["https://app.example.com"]

    def test_required_keys_present(self) -> None:
        s = Settings(
            gemini_api_key="g",
            openai_api_key="o",
            tavily_api_key="t",
            app_shared_password="p",
            jwt_secret="j",
        )
        assert s.gemini_api_key == "g"
        assert s.openai_api_key == "o"
        assert s.tavily_api_key == "t"
        assert s.app_shared_password == "p"
        assert s.jwt_secret == "j"
