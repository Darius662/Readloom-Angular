"""Metadata API module."""

from flask import Blueprint
from backend.api.metadata.routes import metadata_api_bp

__all__ = ['metadata_api_bp']
