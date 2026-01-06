#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Dashboard API routes.
Defines all dashboard endpoints.
"""

from flask import Blueprint, jsonify
from backend.base.logging import LOGGER

from .stats import (
    get_manga_series_count,
    get_books_count,
    get_authors_count,
    get_volume_count,
    get_chapter_count,
    get_collection_stats
)
from .events import (
    get_today_events,
    format_events,
    get_releases_today_count
)

# Create routes blueprint
dashboard_routes = Blueprint('dashboard_routes', __name__)


@dashboard_routes.route('/api/dashboard', methods=['GET'])
def get_dashboard():
    """Get dashboard data.
    
    Returns:
        Response: Dashboard statistics and events.
    """
    try:
        stats = {
            "manga_series_count": get_manga_series_count(),
            "books_count": get_books_count(),
            "authors_count": get_authors_count(),
            "volume_count": get_volume_count(),
            "chapter_count": get_chapter_count(),
            "releases_today": get_releases_today_count(),
        }
        
        stats.update(get_collection_stats())
        
        events = get_today_events()
        formatted_events = format_events(events)
        
        return jsonify({
            "stats": stats,
            "today_events": formatted_events
        })
    except Exception as e:
        LOGGER.error(f"Error getting dashboard: {e}")
        return jsonify({"error": str(e)}), 500
