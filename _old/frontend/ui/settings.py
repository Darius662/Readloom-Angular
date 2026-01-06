#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Settings UI routes.
Handles settings-related pages.
"""

from flask import Blueprint, render_template

# Create routes blueprint
settings_routes = Blueprint('settings_routes', __name__)


@settings_routes.route('/settings')
def settings():
    """Settings page."""
    return render_template('settings.html')
