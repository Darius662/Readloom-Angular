#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Series search and filtering service.
Handles series search, filtering, and listing operations.
"""

from backend.internals.db import execute_query
from backend.base.logging import LOGGER


def get_series_list(content_type=None, limit=None, sort_by='title', sort_order='asc'):
    """Get list of series with optional filtering and sorting.
    
    Args:
        content_type (str, optional): Filter by content type.
        limit (int, optional): Limit results.
        sort_by (str): Field to sort by (default: 'title').
        sort_order (str): Sort order 'asc' or 'desc' (default: 'asc').
        
    Returns:
        list: Series list.
    """
    try:
        # Validate sort order
        if sort_order not in ['asc', 'desc']:
            sort_order = 'asc'
        
        # Build query
        query = """
            SELECT 
                id, title, description, author, publisher, cover_url, status, 
                content_type, metadata_source, metadata_id, created_at, updated_at
            FROM series
        """
        
        params = []
        
        # Add content type filter
        if content_type:
            query += " WHERE UPPER(content_type) = ?"
            params.append(content_type.upper())
        
        # Add sorting
        query += f" ORDER BY {sort_by} {sort_order.upper()}"
        
        # Add limit
        if limit and limit > 0:
            query += " LIMIT ?"
            params.append(limit)
        
        series = execute_query(query, tuple(params))
        return series if series else []
    except Exception as e:
        LOGGER.error(f"Error getting series list: {e}")
        return []


def search_series_by_title(title, limit=None):
    """Search series by title.
    
    Args:
        title (str): Title to search for.
        limit (int, optional): Limit results.
        
    Returns:
        list: Matching series.
    """
    try:
        query = """
            SELECT 
                id, title, description, author, publisher, cover_url, status, 
                content_type, metadata_source, metadata_id, created_at, updated_at
            FROM series
            WHERE LOWER(title) LIKE LOWER(?)
            ORDER BY title ASC
        """
        
        params = [f"%{title}%"]
        
        if limit and limit > 0:
            query += " LIMIT ?"
            params.append(limit)
        
        series = execute_query(query, tuple(params))
        return series if series else []
    except Exception as e:
        LOGGER.error(f"Error searching series by title: {e}")
        return []


def filter_by_content_type(content_type):
    """Filter series by content type.
    
    Args:
        content_type (str): Content type to filter by.
        
    Returns:
        list: Series of specified content type.
    """
    try:
        series = execute_query("""
            SELECT 
                id, title, description, author, publisher, cover_url, status, 
                content_type, metadata_source, metadata_id, created_at, updated_at
            FROM series
            WHERE UPPER(content_type) = ?
            ORDER BY title ASC
        """, (content_type.upper(),))
        
        return series if series else []
    except Exception as e:
        LOGGER.error(f"Error filtering by content type: {e}")
        return []
