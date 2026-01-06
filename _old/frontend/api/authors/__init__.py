#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Authors API module.
Handles author management, search, metadata, and enrichment.
"""

from flask import Blueprint
from .routes import authors_routes

# Create authors blueprint
authors_bp = Blueprint('authors', __name__)

# Register routes
authors_bp.register_blueprint(authors_routes)

__all__ = ['authors_bp']
