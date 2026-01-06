#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Integrations API module.
Handles third-party integrations (Home Assistant, Homarr, etc.).
"""

from flask import Blueprint
from .routes import integrations_routes

# Create integrations blueprint
integrations_bp = Blueprint('integrations', __name__)

# Register routes
integrations_bp.register_blueprint(integrations_routes)

__all__ = ['integrations_bp']
