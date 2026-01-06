#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Volumes API module.
Handles volume CRUD and format management.
"""

from flask import Blueprint
from .routes import volumes_routes

# Create volumes blueprint
volumes_bp = Blueprint('volumes', __name__)

# Register routes
volumes_bp.register_blueprint(volumes_routes)

__all__ = ['volumes_bp']
