#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
API module for Readloom.
Organizes all API endpoints into focused sub-modules.
"""

from flask import Blueprint

# Import all sub-module blueprints
from frontend.api.dashboard import dashboard_bp
from frontend.api.calendar import calendar_bp
from frontend.api.series import series_bp
from frontend.api.volumes import volumes_bp
from frontend.api.chapters import chapters_bp
from frontend.api.settings import settings_bp
from frontend.api.collection import collection_bp
from frontend.api.integrations import integrations_bp
from frontend.api.authors import authors_bp

# Create main API blueprint
api_modules_bp = Blueprint('api_modules', __name__)

# Register all sub-blueprints
api_modules_bp.register_blueprint(dashboard_bp)
api_modules_bp.register_blueprint(calendar_bp)
api_modules_bp.register_blueprint(series_bp)
api_modules_bp.register_blueprint(volumes_bp)
api_modules_bp.register_blueprint(chapters_bp)
api_modules_bp.register_blueprint(settings_bp)
api_modules_bp.register_blueprint(collection_bp)
api_modules_bp.register_blueprint(integrations_bp)
api_modules_bp.register_blueprint(authors_bp)

__all__ = ['api_modules_bp']
