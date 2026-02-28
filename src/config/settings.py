"""Application settings loaded from environment variables."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Central configuration for the deep research agent."""

    app_env: str = "development"
    app_port: int = 8000

    gemini_api_key: str
    openai_api_key: str
    tavily_api_key: str

    app_shared_password: str
    jwt_secret: str
    jwt_algorithm: str = "HS256"
    jwt_expire_hours: int = 24

    firestore_project_id: str = ""
    firestore_collection: str = "research_reports"

    gemini_model: str = "gemini-2.5-flash"
    openai_model: str = "gpt-4.1"

    cors_origins: list[str] = ["http://localhost:3000"]

    model_config = {"env_file": ".env", "extra": "ignore"}
