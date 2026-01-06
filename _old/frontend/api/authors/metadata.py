#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Authors metadata service.
Handles author metadata retrieval and management.
"""

from backend.internals.db import execute_query
from backend.base.logging import LOGGER


def get_author_metadata(author_id):
    """Get author metadata.
    
    Args:
        author_id (int): Author ID.
        
    Returns:
        dict: Author metadata or error.
    """
    try:
        author = execute_query("SELECT * FROM authors WHERE id = ?", (author_id,))
        if not author:
            return {"error": "Author not found"}, 404
        
        author_data = author[0]
        
        # Get book count
        books = execute_query("""
            SELECT COUNT(*) as count FROM author_books WHERE author_id = ?
        """, (author_id,))
        
        book_count = books[0]['count'] if books else 0
        
        # Get series
        series = execute_query("""
            SELECT s.* FROM series s
            JOIN author_books ab ON s.id = ab.series_id
            WHERE ab.author_id = ?
            ORDER BY s.title ASC
        """, (author_id,))
        
        return {
            "author": author_data,
            "book_count": book_count,
            "series": series if series else []
        }, 200
    except Exception as e:
        LOGGER.error(f"Error getting author metadata: {e}")
        return {"error": str(e)}, 500


def update_author_metadata(author_id, data):
    """Update author metadata.
    
    Args:
        author_id (int): Author ID.
        data (dict): Metadata to update.
        
    Returns:
        dict: Status or error.
    """
    try:
        author = execute_query("SELECT id FROM authors WHERE id = ?", (author_id,))
        if not author:
            return {"error": "Author not found"}, 404
        
        # Update author fields
        update_fields = []
        params = []
        
        for field in ["name", "bio", "photo_url"]:
            if field in data:
                update_fields.append(f"{field} = ?")
                params.append(data[field])
        
        if update_fields:
            params.append(author_id)
            execute_query(f"""
                UPDATE authors
                SET {", ".join(update_fields)}
                WHERE id = ?
            """, tuple(params), commit=True)
        
        return {"success": True, "message": "Author metadata updated"}, 200
    except Exception as e:
        LOGGER.error(f"Error updating author metadata: {e}")
        return {"error": str(e)}, 500
