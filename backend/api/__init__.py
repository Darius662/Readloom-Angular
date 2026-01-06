"""
Backend API module.
Organizes all REST API endpoints by domain.
"""

from flask import Blueprint

# Import all API blueprints from their respective modules
from backend.api.collections.routes import collections_api
from backend.api.series.routes import api_series_bp
from backend.api.authors.routes import authors_api_bp
from backend.api.root_folders.routes import rootfolders_api_bp
from backend.api.metadata.routes import metadata_api_bp
from backend.api.ai_providers.routes import ai_providers_api_bp
from backend.api.notifications.routes import notifications_api_bp
from backend.api.books.routes import get_books_routes

__all__ = [
    'collections_api',
    'api_series_bp',
    'authors_api_bp',
    'rootfolders_api_bp',
    'metadata_api_bp',
    'ai_providers_api_bp',
    'notifications_api_bp',
    'get_books_routes',
]
