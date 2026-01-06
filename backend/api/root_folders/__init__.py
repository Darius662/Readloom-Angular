"""Root Folders API module."""

from flask import Blueprint
from backend.api.root_folders.routes import rootfolders_api_bp

__all__ = ['rootfolders_api_bp']
