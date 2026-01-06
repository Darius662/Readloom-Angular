"""Authors API module."""

from flask import Blueprint
from backend.api.authors.routes import authors_api_bp

__all__ = ['authors_api_bp']
