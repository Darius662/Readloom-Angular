#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Chapters CRUD service.
Handles chapter operations.
"""

from backend.internals.db import execute_query
from backend.base.logging import LOGGER


def create_chapter(series_id, data):
    """Create a chapter.
    
    Args:
        series_id (int): Series ID.
        data (dict): Chapter data.
        
    Returns:
        dict: Created chapter or error.
    """
    try:
        chapter_id = execute_query("""
            INSERT INTO chapters (series_id, chapter_number, title, description, release_date, status)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            series_id,
            data.get("chapter_number"),
            data.get("title"),
            data.get("description"),
            data.get("release_date"),
            data.get("status", "UNKNOWN")
        ), commit=True)
        
        chapter = execute_query("SELECT * FROM chapters WHERE id = ?", (chapter_id,))
        return chapter[0] if chapter else {"error": "Failed to retrieve created chapter"}, 201
    except Exception as e:
        LOGGER.error(f"Error creating chapter: {e}")
        return {"error": str(e)}, 500


def read_chapter(chapter_id):
    """Read a chapter.
    
    Args:
        chapter_id (int): Chapter ID.
        
    Returns:
        dict: Chapter data or error.
    """
    try:
        chapter = execute_query("SELECT * FROM chapters WHERE id = ?", (chapter_id,))
        if not chapter:
            return {"error": "Chapter not found"}, 404
        return chapter[0], 200
    except Exception as e:
        LOGGER.error(f"Error reading chapter: {e}")
        return {"error": str(e)}, 500


def update_chapter(chapter_id, data):
    """Update a chapter.
    
    Args:
        chapter_id (int): Chapter ID.
        data (dict): Update data.
        
    Returns:
        dict: Updated chapter or error.
    """
    try:
        # Check if chapter exists
        chapter = execute_query("SELECT id FROM chapters WHERE id = ?", (chapter_id,))
        if not chapter:
            return {"error": "Chapter not found"}, 404
        
        # Build update query
        update_fields = []
        params = []
        
        for field in ["chapter_number", "title", "description", "release_date", "status"]:
            if field in data:
                update_fields.append(f"{field} = ?")
                params.append(data[field])
        
        if not update_fields:
            return {"error": "No fields to update"}, 400
        
        params.append(chapter_id)
        
        execute_query(f"""
            UPDATE chapters
            SET {", ".join(update_fields)}
            WHERE id = ?
        """, tuple(params), commit=True)
        
        updated = execute_query("SELECT * FROM chapters WHERE id = ?", (chapter_id,))
        return updated[0] if updated else {"error": "Failed to retrieve updated chapter"}, 200
    except Exception as e:
        LOGGER.error(f"Error updating chapter: {e}")
        return {"error": str(e)}, 500


def delete_chapter(chapter_id):
    """Delete a chapter.
    
    Args:
        chapter_id (int): Chapter ID.
        
    Returns:
        dict: Status or error.
    """
    try:
        # Check if chapter exists
        chapter = execute_query("SELECT id FROM chapters WHERE id = ?", (chapter_id,))
        if not chapter:
            return {"error": "Chapter not found"}, 404
        
        execute_query("DELETE FROM chapters WHERE id = ?", (chapter_id,), commit=True)
        return {"success": True, "message": "Chapter deleted successfully"}, 200
    except Exception as e:
        LOGGER.error(f"Error deleting chapter: {e}")
        return {"error": str(e)}, 500
