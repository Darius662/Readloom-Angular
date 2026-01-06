#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Authors search service.
Handles author search and filtering operations.
"""

from backend.internals.db import execute_query
from backend.base.logging import LOGGER


def search_authors(query):
    """Search authors by name or bio.
    
    Args:
        query (str): Search query.
        
    Returns:
        list: Matching authors.
    """
    try:
        search_term = f"%{query}%"
        authors = execute_query("""
            SELECT * FROM authors
            WHERE name LIKE ? OR bio LIKE ?
            ORDER BY name ASC
        """, (search_term, search_term))
        return authors if authors else []
    except Exception as e:
        LOGGER.error(f"Error searching authors: {e}")
        return []


def get_authors_by_book_count(limit=10):
    """Get authors sorted by book count.
    
    Args:
        limit (int): Limit results.
        
    Returns:
        list: Authors with book counts.
    """
    try:
        authors = execute_query("""
            SELECT a.*, COUNT(ab.series_id) as book_count
            FROM authors a
            LEFT JOIN author_books ab ON a.id = ab.author_id
            GROUP BY a.id
            ORDER BY book_count DESC
            LIMIT ?
        """, (limit,))
        return authors if authors else []
    except Exception as e:
        LOGGER.error(f"Error getting authors by book count: {e}")
        return []


def get_popular_authors(limit=5):
    """Get popular authors.
    
    Args:
        limit (int): Limit results.
        
    Returns:
        list: Popular authors.
    """
    try:
        authors = execute_query("""
            SELECT a.*, COUNT(ab.series_id) as book_count
            FROM authors a
            LEFT JOIN author_books ab ON a.id = ab.author_id
            GROUP BY a.id
            ORDER BY book_count DESC
            LIMIT ?
        """, (limit,))
        return authors if authors else []
    except Exception as e:
        LOGGER.error(f"Error getting popular authors: {e}")
        return []
