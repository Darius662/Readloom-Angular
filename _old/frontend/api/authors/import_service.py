#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Authors import service.
Handles importing authors from external sources.
"""

from backend.internals.db import execute_query
from backend.base.logging import LOGGER


def import_author_from_openlibrary(author_name):
    """Import author from OpenLibrary.
    
    Args:
        author_name (str): Author name.
        
    Returns:
        dict: Imported author or error.
    """
    try:
        # Check if author already exists
        existing = execute_query(
            "SELECT * FROM authors WHERE name = ?",
            (author_name,)
        )
        
        if existing:
            return existing[0], 200
        
        # Try to fetch from OpenLibrary
        try:
            from backend.features.author_openlibrary_fetcher import fetch_author_from_openlibrary
            author_data = fetch_author_from_openlibrary(author_name)
            
            if author_data:
                # Create new author
                author_id = execute_query("""
                    INSERT INTO authors (name, bio, photo_url)
                    VALUES (?, ?, ?)
                """, (
                    author_data.get('name', author_name),
                    author_data.get('bio'),
                    author_data.get('photo_url')
                ), commit=True)
                
                author = execute_query("SELECT * FROM authors WHERE id = ?", (author_id,))
                return author[0] if author else {"error": "Failed to create author"}, 201
        except Exception as e:
            LOGGER.warning(f"Could not fetch author from OpenLibrary: {e}")
        
        # Create author with just the name
        author_id = execute_query("""
            INSERT INTO authors (name)
            VALUES (?)
        """, (author_name,), commit=True)
        
        author = execute_query("SELECT * FROM authors WHERE id = ?", (author_id,))
        return author[0] if author else {"error": "Failed to create author"}, 201
    except Exception as e:
        LOGGER.error(f"Error importing author: {e}")
        return {"error": str(e)}, 500


def import_authors_batch(author_names):
    """Import multiple authors.
    
    Args:
        author_names (list): List of author names.
        
    Returns:
        dict: Import results.
    """
    try:
        results = {
            "imported": [],
            "existing": [],
            "failed": []
        }
        
        for name in author_names:
            try:
                author, status = import_author_from_openlibrary(name)
                
                if status == 201:
                    results["imported"].append(author)
                elif status == 200:
                    results["existing"].append(author)
                else:
                    results["failed"].append({"name": name, "error": author.get("error")})
            except Exception as e:
                results["failed"].append({"name": name, "error": str(e)})
        
        return results, 200
    except Exception as e:
        LOGGER.error(f"Error importing authors batch: {e}")
        return {"error": str(e)}, 500
