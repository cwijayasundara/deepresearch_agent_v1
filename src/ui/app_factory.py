"""FastAPI application factory — lives in UI layer."""

import logging
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.ui.router import register_routes

logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
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
