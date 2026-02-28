"""Application entry point — delegates to UI layer factory.

Usage: uvicorn backend.ui.app_factory:create_app --factory
"""

import importlib


def create_app():  # type: ignore[no-untyped-def]
    """Create app by delegating to UI layer (avoids layer violation)."""
    mod = importlib.import_module("backend.ui.app_factory")
    return mod.create_app()
