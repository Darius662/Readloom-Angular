#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Authors CRUD service.
Handles author create, read, update, delete operations.
"""

from backend.internals.db import execute_query
from backend.base.logging import LOGGER


def create_author(data):
    """Create an author.
    
    Args:
        data (dict): Author data.
        
    Returns:
        dict: Created author or error.
    """
    try:
        author_id = execute_query("""
            INSERT INTO authors (name, bio, photo_url)
            VALUES (?, ?, ?)
        """, (
            data.get("name"),
            data.get("bio"),
            data.get("photo_url")
        ), commit=True)
        
        author = execute_query("SELECT * FROM authors WHERE id = ?", (author_id,))
        return author[0] if author else {"error": "Failed to retrieve created author"}, 201
    except Exception as e:
        LOGGER.error(f"Error creating author: {e}")
        return {"error": str(e)}, 500


def read_author(author_id):
    """Read an author.
    
    Args:
        author_id (int): Author ID.
        
    Returns:
        dict: Author data or error.
    """
    try:
        author = execute_query("SELECT * FROM authors WHERE id = ?", (author_id,))
        if not author:
            return {"error": "Author not found"}, 404
        return author[0], 200
    except Exception as e:
        LOGGER.error(f"Error reading author: {e}")
        return {"error": str(e)}, 500


def update_author(author_id, data):
    """Update an author.
    
    Args:
        author_id (int): Author ID.
        data (dict): Update data.
        
    Returns:
        dict: Updated author or error.
    """
    try:
        # Get current author data
        author = execute_query("SELECT id, name FROM authors WHERE id = ?", (author_id,))
        if not author:
            return {"error": "Author not found"}, 404
        
        old_name = author[0]['name']
        
        update_fields = []
        params = []
        
        for field in ["name", "bio", "photo_url"]:
            if field in data:
                update_fields.append(f"{field} = ?")
                params.append(data[field])
        
        if not update_fields:
            return {"error": "No fields to update"}, 400
        
        params.append(author_id)
        
        execute_query(f"""
            UPDATE authors
            SET {", ".join(update_fields)}
            WHERE id = ?
        """, tuple(params), commit=True)
        
        # If name was changed, rename the folder
        if "name" in data and data["name"] != old_name:
            try:
                from backend.base.helpers import rename_author_folder
                rename_author_folder(author_id, old_name, data["name"])
            except Exception as e:
                LOGGER.warning(f"Failed to rename author folder for author {author_id}: {e}")
        
        updated = execute_query("SELECT * FROM authors WHERE id = ?", (author_id,))
        return updated[0] if updated else {"error": "Failed to retrieve updated author"}, 200
    except Exception as e:
        LOGGER.error(f"Error updating author: {e}")
        return {"error": str(e)}, 500


def delete_author(author_id):
    """Delete an author and all associated books.
    
    Args:
        author_id (int): Author ID.
        
    Returns:
        dict: Status or error.
    """
    try:
        author = execute_query("SELECT id FROM authors WHERE id = ?", (author_id,))
        if not author:
            return {"error": "Author not found"}, 404
        
        # Get all series/books associated with this author
        author_books = execute_query(
            "SELECT series_id FROM author_books WHERE author_id = ?", 
            (author_id,)
        )
        
        # Delete all series/books associated with this author
        for book in author_books:
            series_id = book['series_id']
            execute_query("DELETE FROM series WHERE id = ?", (series_id,), commit=True)
        
        # Delete author_books associations
        execute_query("DELETE FROM author_books WHERE author_id = ?", (author_id,), commit=True)
        
        # Delete the author
        execute_query("DELETE FROM authors WHERE id = ?", (author_id,), commit=True)
        
        return {"success": True, "message": "Author and all associated books deleted successfully"}, 200
    except Exception as e:
        LOGGER.error(f"Error deleting author: {e}")
        return {"error": str(e)}, 500


def get_all_authors(limit=None, offset=0):
    """Get all authors.
    
    Args:
        limit (int, optional): Limit results.
        offset (int): Offset for pagination.
        
    Returns:
        list: Authors.
    """
    try:
        if limit:
            authors = execute_query(
                "SELECT * FROM authors ORDER BY name ASC LIMIT ? OFFSET ?",
                (limit, offset)
            )
        else:
            authors = execute_query("SELECT * FROM authors ORDER BY name ASC")
        return authors if authors else []
    except Exception as e:
        LOGGER.error(f"Error getting authors: {e}")
        return []
