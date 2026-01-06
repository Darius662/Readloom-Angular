#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Calendar API module.
Handles calendar events and refresh functionality.
"""

from flask import Blueprint
from .routes import calendar_routes

# Create calendar blueprint
calendar_bp = Blueprint('calendar', __name__)

# Register routes
calendar_bp.register_blueprint(calendar_routes)

__all__ = ['calendar_bp']
