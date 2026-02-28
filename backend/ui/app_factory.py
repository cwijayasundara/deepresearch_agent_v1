"""FastAPI application factory — lives in UI layer."""

import logging
import os
import warnings

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.ui.router import register_routes

# Suppress noisy Google ADC quota-project warning (harmless with gcloud auth)
warnings.filterwarnings("ignore", message=".*end user credentials.*quota project.*")

logger = logging.getLogger(__name__)


def _configure_logging() -> None:
    """Set up structured logging for the whole app."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)-8s [%(name)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    # Quiet down noisy third-party loggers
    logging.getLogger("google").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("langchain").setLevel(logging.WARNING)


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    _configure_logging()

    app = FastAPI(
        title="Deep Research Agent",
        description="AI Intelligence Tracker API",
        version="1.0.0",
    )

    origins = os.environ.get(
        "CORS_ORIGINS", "http://localhost:3000"
    ).split(",")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    register_routes(app)
    logger.info("Application created successfully")
    return app
