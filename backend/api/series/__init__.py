"""Series API module."""

from flask import Blueprint
from backend.api.series.routes import api_series_bp

__all__ = ['api_series_bp']
