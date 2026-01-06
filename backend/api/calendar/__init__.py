"""Calendar API module."""

from flask import Blueprint
from backend.api.calendar.routes import calendar_bp

__all__ = ['calendar_bp']
