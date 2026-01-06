#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Library UI routes.
Handles unified library view for books and manga volumes.
"""

from flask import Blueprint, render_template, jsonify, request
from backend.base.logging import LOGGER
from backend.internals.db import execute_query
from frontend.middleware import setup_required

# Create routes blueprint
library_routes = Blueprint('library_routes', __name__)


def get_library_items(content_type=None, ownership_status=None, format_type=None, limit=None):
    """Get all library items (series and volumes).
    
    Args:
        content_type (str, optional): Filter by content type (BOOK, MANGA, etc.)
        ownership_status (str, optional): Filter by ownership status (OWNED, WANTED, etc.)
        format_type (str, optional): Filter by format (PHYSICAL, DIGITAL, BOTH)
        limit (int, optional): Limit results
        
    Returns:
        list: Library items with series and volume information
    """
    try:
        query = """
        SELECT 
            s.id as series_id,
            s.title as series_title,
            s.description,
            s.author,
            s.publisher,
            s.cover_url,
            s.status,
            s.content_type,
            s.metadata_source,
            s.created_at,
            COUNT(DISTINCT v.id) as volume_count,
            COUNT(DISTINCT ci.id) as owned_count,
            SUM(CASE WHEN ci.ownership_status = 'OWNED' THEN 1 ELSE 0 END) as owned_volumes,
            SUM(CASE WHEN ci.purchase_price IS NOT NULL THEN ci.purchase_price ELSE 0 END) as total_value
        FROM series s
        LEFT JOIN volumes v ON s.id = v.series_id
        LEFT JOIN collection_items ci ON s.id = ci.series_id AND ci.item_type = 'VOLUME'
        LEFT JOIN series_collections sc ON s.id = sc.series_id
        LEFT JOIN collections c ON sc.collection_id = c.id
        WHERE 1=1
        AND (c.name IS NOT NULL AND c.name != 'Want to read')
        """
        params = []
        
        if content_type:
            query += " AND UPPER(s.content_type) = ?"
            params.append(content_type.upper())
        
        if ownership_status:
            query += " AND ci.ownership_status = ?"
            params.append(ownership_status)
        
        if format_type:
            query += " AND ci.format = ?"
            params.append(format_type)
        
        query += " GROUP BY s.id ORDER BY s.title"
        
        if limit:
            query += " LIMIT ?"
            params.append(limit)
        
        items = execute_query(query, tuple(params))
        return items
    
    except Exception as e:
        LOGGER.error(f"Error getting library items: {e}")
        return []


def get_library_stats():
    """Get library statistics.
    
    Returns:
        dict: Library statistics
    """
    try:
        # Total series (only items in collections that are not want-to-read)
        total_series = execute_query("""
            SELECT COUNT(DISTINCT s.id) as count FROM series s
            LEFT JOIN series_collections sc ON s.id = sc.series_id
            LEFT JOIN collections c ON sc.collection_id = c.id
            WHERE c.name IS NOT NULL AND c.name != 'Want to read'
        """)
        
        # Total volumes
        total_volumes = execute_query("""
            SELECT COUNT(*) as count FROM volumes
        """)
        
        # Books count (only items in collections that are not want-to-read)
        books_count = execute_query("""
            SELECT COUNT(DISTINCT s.id) as count FROM series s
            LEFT JOIN series_collections sc ON s.id = sc.series_id
            LEFT JOIN collections c ON sc.collection_id = c.id
            WHERE UPPER(s.content_type) IN ('BOOK', 'NOVEL') AND c.name IS NOT NULL AND c.name != 'Want to read'
        """)
        
        # Manga count (only items in collections that are not want-to-read)
        manga_count = execute_query("""
            SELECT COUNT(DISTINCT s.id) as count FROM series s
            LEFT JOIN series_collections sc ON s.id = sc.series_id
            LEFT JOIN collections c ON sc.collection_id = c.id
            WHERE UPPER(s.content_type) IN ('MANGA', 'MANHWA', 'MANHUA', 'COMIC') AND c.name IS NOT NULL AND c.name != 'Want to read'
        """)
        
        # Owned volumes
        owned_volumes = execute_query("""
            SELECT COUNT(*) as count FROM collection_items 
            WHERE item_type = 'VOLUME' AND ownership_status = 'OWNED'
        """)
        
        # Total library value
        total_value = execute_query("""
            SELECT SUM(purchase_price) as total FROM collection_items 
            WHERE purchase_price IS NOT NULL
        """)
        
        return {
            'total_series': total_series[0]['count'] if total_series else 0,
            'total_volumes': total_volumes[0]['count'] if total_volumes else 0,
            'books_count': books_count[0]['count'] if books_count else 0,
            'manga_count': manga_count[0]['count'] if manga_count else 0,
            'owned_volumes': owned_volumes[0]['count'] if owned_volumes else 0,
            'total_value': total_value[0]['total'] if total_value and total_value[0]['total'] else 0.0
        }
    
    except Exception as e:
        LOGGER.error(f"Error getting library stats: {e}")
        return {}


@library_routes.route('/library')
@setup_required
def library_home():
    """Library home page."""
    try:
        # Get all library items
        library_items = get_library_items()
        
        # Get statistics
        stats = get_library_stats()
        
        return render_template(
            'library/home.html',
            library_items=library_items,
            stats=stats
        )
    except Exception as e:
        LOGGER.error(f"Error loading library: {e}")
        return render_template('library/home.html', library_items=[], stats={})


@library_routes.route('/library/api/items')
@setup_required
def api_library_items():
    """API endpoint to get library items with filters."""
    try:
        content_type = request.args.get('content_type')
        ownership_status = request.args.get('ownership_status')
        format_type = request.args.get('format')
        
        items = get_library_items(
            content_type=content_type,
            ownership_status=ownership_status,
            format_type=format_type
        )
        
        return jsonify({
            'success': True,
            'items': items,
            'count': len(items)
        }), 200
    
    except Exception as e:
        LOGGER.error(f"Error fetching library items: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@library_routes.route('/library/api/stats')
@setup_required
def api_library_stats():
    """API endpoint to get library statistics."""
    try:
        stats = get_library_stats()
        return jsonify({
            'success': True,
            'stats': stats
        }), 200
    
    except Exception as e:
        LOGGER.error(f"Error fetching library stats: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@library_routes.route('/want-to-read')
@setup_required
def want_to_read():
    """Want to read collection page."""
    return render_template('want_to_read.html')
