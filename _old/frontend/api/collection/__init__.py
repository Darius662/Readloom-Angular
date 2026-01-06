#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Collection API module.
Handles collection management and tracking.
"""

from flask import Blueprint
from .routes import collection_routes

# Create collection blueprint
collection_bp = Blueprint('collection', __name__)

# Register routes
collection_bp.register_blueprint(collection_routes)

__all__ = ['collection_bp']
