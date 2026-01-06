#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Collections UI routes.
Handles collection-related pages.
"""

from flask import Blueprint, render_template
from frontend.middleware import setup_required

# Create routes blueprint
collections_routes = Blueprint('collections_routes', __name__)


@collections_routes.route('/collections')
@setup_required
def collections_manager():
    """Collections management page."""
    return render_template('collections_manager.html')


@collections_routes.route('/collection')
@setup_required
def collection():
    """Collection page."""
    return render_template('collection.html')


@collections_routes.route('/collection/<int:collection_id>')
@setup_required
def collection_view(collection_id):
    """Collection detail page."""
    return render_template('collection_view.html', collection_id=collection_id)


@collections_routes.route('/root-folders')
@setup_required
def root_folders():
    """Root folders page."""
    return render_template('root_folders.html')


@collections_routes.route('/series')
@setup_required
def series_list():
    """Series list page."""
    from backend.internals.settings import Settings
    settings = Settings().get_settings()
    root_folders = settings.root_folders
    
    return render_template('series_list.html', root_folders=root_folders)
