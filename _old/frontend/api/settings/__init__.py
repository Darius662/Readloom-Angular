#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Settings API module.
Handles application settings and configuration.
"""

from flask import Blueprint
from .routes import settings_routes

# Create settings blueprint
settings_bp = Blueprint('settings', __name__)

# Register routes
settings_bp.register_blueprint(settings_routes)

__all__ = ['settings_bp']
