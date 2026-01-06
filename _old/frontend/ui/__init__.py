#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
UI module for Readloom.
Organizes all UI routes into focused sub-modules.
"""

from flask import Blueprint

# Import all sub-module blueprints
from frontend.ui.core import core_routes
from frontend.ui.books import books_routes
from frontend.ui.manga import manga_routes
from frontend.ui.authors import authors_routes
from frontend.ui.calendar import calendar_routes
from frontend.ui.collections import collections_routes
from frontend.ui.settings import settings_routes
from frontend.ui.integrations import integrations_routes
from frontend.ui.library import library_routes

# Create main UI blueprint
ui_bp = Blueprint('ui', __name__)

# Register all sub-blueprints
ui_bp.register_blueprint(core_routes)
ui_bp.register_blueprint(books_routes)
ui_bp.register_blueprint(manga_routes)
ui_bp.register_blueprint(authors_routes)
ui_bp.register_blueprint(calendar_routes)
ui_bp.register_blueprint(collections_routes)
ui_bp.register_blueprint(settings_routes)
ui_bp.register_blueprint(integrations_routes)
ui_bp.register_blueprint(library_routes)

# Debug: Add a test route to verify this blueprint is being used
@ui_bp.route('/test-ui-bp')
def test_ui_bp():
    return "UI_BP TEST ROUTE WORKING"

__all__ = ['ui_bp']
