#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Dashboard statistics service.
Retrieves and calculates dashboard statistics.
"""

from backend.internals.db import execute_query
from backend.base.logging import LOGGER


def get_manga_series_count():
    """Get count of manga series.
    
    Returns:
        int: Number of manga series.
    """
    try:
        result = execute_query("SELECT COUNT(*) as count FROM series WHERE UPPER(content_type) IN ('MANGA', 'MANHWA', 'MANHUA', 'COMIC')")
        return result[0]["count"] if result else 0
    except Exception as e:
        LOGGER.error(f"Error getting manga series count: {e}")
        return 0


def get_books_count():
    """Get count of books.
    
    Returns:
        int: Number of books.
    """
    try:
        result = execute_query("SELECT COUNT(*) as count FROM series WHERE UPPER(content_type) IN ('BOOK', 'NOVEL')")
        return result[0]["count"] if result else 0
    except Exception as e:
        LOGGER.error(f"Error getting books count: {e}")
        return 0


def get_authors_count():
    """Get count of authors.
    
    Returns:
        int: Number of authors.
    """
    try:
        result = execute_query("SELECT COUNT(*) as count FROM authors")
        return result[0]["count"] if result else 0
    except Exception as e:
        LOGGER.error(f"Error getting authors count: {e}")
        return 0


def get_volume_count():
    """Get total volume count.
    
    Returns:
        int: Total number of volumes.
    """
    try:
        result = execute_query("SELECT COUNT(*) as count FROM volumes")
        return result[0]["count"] if result else 0
    except Exception as e:
        LOGGER.error(f"Error getting volume count: {e}")
        return 0


def get_chapter_count():
    """Get total chapter count.
    
    Returns:
        int: Total number of chapters.
    """
    try:
        result = execute_query("SELECT COUNT(*) as count FROM chapters")
        return result[0]["count"] if result else 0
    except Exception as e:
        LOGGER.error(f"Error getting chapter count: {e}")
        return 0


def get_collection_stats():
    """Get collection statistics.
    
    Returns:
        dict: Collection statistics including owned volumes, read volumes, and total value.
    """
    try:
        owned = execute_query("""
            SELECT COUNT(*) as count
            FROM collection_items
            WHERE item_type = 'VOLUME' AND ownership_status = 'OWNED'
        """)
        
        read = execute_query("""
            SELECT COUNT(*) as count
            FROM collection_items
            WHERE item_type = 'VOLUME' AND read_status = 'READ'
        """)
        
        value = execute_query("""
            SELECT SUM(purchase_price) as total
            FROM collection_items
            WHERE purchase_price IS NOT NULL
        """)
        
        return {
            "owned_volumes": owned[0]["count"] if owned else 0,
            "read_volumes": read[0]["count"] if read else 0,
            "collection_value": value[0]["total"] if value and value[0]["total"] else 0
        }
    except Exception as e:
        LOGGER.error(f"Error getting collection stats: {e}")
        return {
            "owned_volumes": 0,
            "read_volumes": 0,
            "collection_value": 0
        }
