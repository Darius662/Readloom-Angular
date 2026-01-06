"""AI Providers API module."""

from flask import Blueprint
from backend.api.ai_providers.routes import ai_providers_api_bp

__all__ = ['ai_providers_api_bp']
