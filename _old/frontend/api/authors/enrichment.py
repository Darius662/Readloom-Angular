#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Authors enrichment service.
Handles author data enrichment via AI and external sources.
"""

from backend.internals.db import execute_query
from backend.base.logging import LOGGER


def enrich_author_bio(author_id):
    """Enrich author biography using AI.
    
    Args:
        author_id (int): Author ID.
        
    Returns:
        dict: Enriched author or error.
    """
    try:
        author = execute_query("SELECT * FROM authors WHERE id = ?", (author_id,))
        if not author:
            return {"error": "Author not found"}, 404
        
        author_data = author[0]
        
        # Try to enrich using AI
        try:
            from backend.features.author_enrichment import enrich_author_biography
            enriched = enrich_author_biography(author_data['name'])
            
            if enriched and enriched.get('bio'):
                # Update author bio
                execute_query("""
                    UPDATE authors SET bio = ? WHERE id = ?
                """, (enriched['bio'], author_id), commit=True)
                
                author_data['bio'] = enriched['bio']
        except Exception as e:
            LOGGER.warning(f"Could not enrich author bio: {e}")
        
        return author_data, 200
    except Exception as e:
        LOGGER.error(f"Error enriching author: {e}")
        return {"error": str(e)}, 500


def enrich_author_photo(author_id):
    """Enrich author photo URL.
    
    Args:
        author_id (int): Author ID.
        
    Returns:
        dict: Status or error.
    """
    try:
        author = execute_query("SELECT * FROM authors WHERE id = ?", (author_id,))
        if not author:
            return {"error": "Author not found"}, 404
        
        # Try to get photo from OpenLibrary
        try:
            from backend.features.author_enrichment import get_author_photo
            photo_url = get_author_photo(author[0]['name'])
            
            if photo_url:
                execute_query("""
                    UPDATE authors SET photo_url = ? WHERE id = ?
                """, (photo_url, author_id), commit=True)
        except Exception as e:
            LOGGER.warning(f"Could not enrich author photo: {e}")
        
        return {"success": True, "message": "Author photo enriched"}, 200
    except Exception as e:
        LOGGER.error(f"Error enriching author photo: {e}")
        return {"error": str(e)}, 500


def enrich_author_complete(author_id):
    """Completely enrich an author with all available data.
    
    Args:
        author_id (int): Author ID.
        
    Returns:
        dict: Enriched author or error.
    """
    try:
        # Enrich bio
        bio_result, _ = enrich_author_bio(author_id)
        
        # Enrich photo
        enrich_author_photo(author_id)
        
        # Get final author data
        author = execute_query("SELECT * FROM authors WHERE id = ?", (author_id,))
        if not author:
            return {"error": "Author not found"}, 404
        
        return author[0], 200
    except Exception as e:
        LOGGER.error(f"Error enriching author completely: {e}")
        return {"error": str(e)}, 500
