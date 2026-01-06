"""Notifications API module."""

from flask import Blueprint
from backend.api.notifications.routes import notifications_api_bp

__all__ = ['notifications_api_bp']
