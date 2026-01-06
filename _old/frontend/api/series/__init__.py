#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Series API module.
Handles series CRUD operations, search, move, and scan functionality.
"""

from flask import Blueprint
from .routes import series_routes

# Create series blueprint
series_bp = Blueprint('series', __name__)

# Register routes
series_bp.register_blueprint(series_routes)

__all__ = ['series_bp']
