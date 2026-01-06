"""Collections API module."""

from flask import Blueprint
from backend.api.collections.routes import collections_api

__all__ = ['collections_api']
