#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Dashboard API module.
Handles dashboard statistics and data retrieval.
"""

from flask import Blueprint
from .routes import dashboard_routes

# Create dashboard blueprint
dashboard_bp = Blueprint('dashboard', __name__)

# Register routes
dashboard_bp.register_blueprint(dashboard_routes)

__all__ = ['dashboard_bp']
