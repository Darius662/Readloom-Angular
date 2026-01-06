#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
API endpoints for series.
"""

from flask import Blueprint, jsonify, request

from backend.base.logging import LOGGER
from backend.internals.db import execute_query
from frontend.middleware import setup_required


# Create Blueprint for series API
api_series_bp = Blueprint('api_series', __name__)


@api_series_bp.route('/api/series', methods=['GET'])
@setup_required
def get_all_series():
    """Get all series.
    
    Query parameters:
        content_type: Filter by content type (book, manga)
        search: Search by title or author
        isbn: Search by ISBN (for books only)
    
    Returns:
        Response: All series.
    """
    try:
        # Get query parameters
        content_type = request.args.get('content_type', None)
        search = request.args.get('search', None)
        isbn = request.args.get('isbn', None)
        
        # Build base query
        query = "SELECT * FROM series WHERE 1=1"
        params = []
        
        # Apply content type filter
        if content_type == 'book':
            query += " AND UPPER(content_type) IN ('BOOK', 'NOVEL')"
        elif content_type == 'manga':
            query += " AND UPPER(content_type) IN ('MANGA', 'MANHWA', 'MANHUA', 'COMIC')"
        
        # Apply search filter
        if search:
            query += " AND (LOWER(title) LIKE LOWER(?) OR LOWER(author) LIKE LOWER(?))"
            search_term = f"%{search}%"
            params.extend([search_term, search_term])
        
        # Apply ISBN filter (books only)
        if isbn:
            query += " AND isbn = ?"
            params.append(isbn)
        
        query += " ORDER BY title"
        
        series = execute_query(query, tuple(params)) if params else execute_query(query)
        
        return jsonify({"series": series})
    except Exception as e:
        LOGGER.error(f"Error getting series: {e}")
        return jsonify({"error": str(e)}), 500


@api_series_bp.route('/api/series/<int:series_id>', methods=['GET'])
@setup_required
def get_series(series_id: int):
    """Get a series by ID.
    
    Args:
        series_id: The series ID.
        
    Returns:
        Response: The series.
    """
    try:
        series = execute_query("""
            SELECT * FROM series WHERE id = ?
        """, (series_id,))
        
        if not series:
            return jsonify({"error": "Series not found"}), 404
        
        return jsonify({"series": series[0]})
    except Exception as e:
        LOGGER.error(f"Error getting series: {e}")
        return jsonify({"error": str(e)}), 500


@api_series_bp.route('/api/series/recent', methods=['GET'])
@setup_required
def get_recent_series():
    """Get recent series.
    
    Returns:
        Response: The recent series.
    """
    try:
        # Get query parameters
        content_type = request.args.get('content_type', 'all')
        limit = request.args.get('limit', 10, type=int)
        
        LOGGER.debug(f"get_recent_series called with content_type={content_type}, limit={limit}")
        
        # Ensure limit is reasonable
        if limit <= 0 or limit > 100:
            limit = 10
        
        # Build the query - simple and efficient
        if content_type == 'book':
            query = "SELECT * FROM series WHERE UPPER(content_type) IN ('BOOK', 'NOVEL') ORDER BY id DESC LIMIT ?"
        elif content_type == 'manga':
            query = "SELECT * FROM series WHERE UPPER(content_type) IN ('MANGA', 'MANHWA', 'MANHUA', 'COMIC') ORDER BY id DESC LIMIT ?"
        else:
            query = "SELECT * FROM series ORDER BY id DESC LIMIT ?"
        
        LOGGER.debug(f"Executing query: {query} with limit={limit}")
        
        # Execute the query
        series = execute_query(query, (limit,))
        
        LOGGER.debug(f"Query returned {len(series) if series else 0} series")
        
        return jsonify({
            "success": True,
            "series": series if series else []
        })
    except Exception as e:
        LOGGER.error(f"Error getting recent series: {e}", exc_info=True)
        return jsonify({
            "success": False,
            "message": f"Error getting recent series: {str(e)}",
            "series": []
        }), 500
