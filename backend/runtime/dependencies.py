"""FastAPI dependency injection providers."""

import logging
from functools import lru_cache

from backend.config.settings import Settings
from backend.repo.firestore_client import FirestoreRepo
from backend.repo.gemini_client import GeminiResearchClient
from backend.repo.langchain_client import LangChainResearchClient
from backend.service.auth_service import AuthService
from backend.service.research_orchestrator import ResearchOrchestrator

logger = logging.getLogger(__name__)


@lru_cache
def get_settings() -> Settings:
    """Get application settings (cached)."""
    return Settings()


def get_auth_service() -> AuthService:
    """Build the auth service."""
    settings = get_settings()
    return AuthService(
        shared_password=settings.app_shared_password,
        jwt_secret=settings.jwt_secret,
        jwt_algorithm=settings.jwt_algorithm,
        jwt_expire_hours=settings.jwt_expire_hours,
    )


def get_firestore_repo() -> FirestoreRepo:
    """Build the Firestore repository."""
    from google.cloud import firestore

    settings = get_settings()
    db = firestore.AsyncClient(project=settings.firestore_project_id)
    return FirestoreRepo(db=db, collection_name=settings.firestore_collection)


def get_gemini_client() -> GeminiResearchClient:
    """Build the Gemini research client."""
    settings = get_settings()
    return GeminiResearchClient(
        api_key=settings.gemini_api_key,
        model=settings.gemini_model,
    )


def get_langchain_client() -> LangChainResearchClient:
    """Build the LangChain research client."""
    settings = get_settings()
    return LangChainResearchClient(
        openai_api_key=settings.openai_api_key,
        tavily_api_key=settings.tavily_api_key,
        model=settings.openai_model,
    )


def get_orchestrator() -> ResearchOrchestrator:
    """Build the research orchestrator with all clients."""
    return ResearchOrchestrator(
        gemini_client=get_gemini_client(),
        langchain_client=get_langchain_client(),
        firestore_repo=get_firestore_repo(),
    )
