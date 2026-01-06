#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Core UI routes.
Handles home, setup, about, and other core pages.
"""

from flask import Blueprint, render_template, redirect, url_for, send_from_directory
from backend.base.logging import LOGGER
from frontend.middleware import setup_required

# Create routes blueprint
core_routes = Blueprint('core_routes', __name__)


@core_routes.route('/')
def home():
    """Home page."""
    return render_template('dashboard.html')


@core_routes.route('/setup')
@core_routes.route('/setup-wizard')
def setup_wizard():
    """Setup wizard page."""
    # Check if setup is already complete
    from backend.features.setup_check import is_setup_complete
    if is_setup_complete():
        return redirect(url_for('ui.home'))
    
    # Get root folders for the setup wizard
    from backend.internals.settings import Settings
    settings = Settings().get_settings()
    root_folders = settings.root_folders
    
    return render_template('setup_wizard.html', root_folders=root_folders)


@core_routes.route('/about')
def about():
    """About page."""
    return render_template('about.html')


@core_routes.route('/favicon.ico')
def favicon():
    """Serve the favicon."""
    return send_from_directory('static/img', 'favicon.ico')


@core_routes.route('/search')
@setup_required
def search():
    """Search page (backward compatibility).
    
    Redirects to books search page.
    """
    return redirect(url_for('ui.books_search'))


@core_routes.route('/notifications')
@setup_required
def notifications():
    """Notifications page."""
    return render_template('notifications.html')


@core_routes.route('/offline')
def offline():
    """Offline fallback page."""
    return render_template('offline.html')
