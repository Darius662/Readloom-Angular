#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Integrations UI routes.
Handles integration-related pages.
"""

from flask import Blueprint, render_template

# Create routes blueprint
integrations_routes = Blueprint('integrations_routes', __name__)


@integrations_routes.route('/integrations')
def integrations():
    """Integrations page."""
    return render_template('integrations.html')


@integrations_routes.route('/integrations/home-assistant')
def home_assistant():
    """Home Assistant integration page."""
    return render_template('home_assistant.html')


@integrations_routes.route('/integrations/homarr')
def homarr():
    """Homarr integration page."""
    return render_template('homarr.html')


@integrations_routes.route('/integrations/providers')
def provider_config():
    """Provider configuration page."""
    return render_template('provider_config.html')


@integrations_routes.route('/integrations/ai-providers')
def ai_providers_config():
    """AI providers configuration page."""
    return render_template('ai_providers_config.html')
