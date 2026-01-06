#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Chapters API module.
Handles chapter CRUD operations.
"""

from flask import Blueprint
from .routes import chapters_routes

# Create chapters blueprint
chapters_bp = Blueprint('chapters', __name__)

# Register routes
chapters_bp.register_blueprint(chapters_routes)

__all__ = ['chapters_bp']
