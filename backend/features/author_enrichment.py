#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Author enrichment module - fetches and stores author metadata from AI providers.
"""

from backend.base.logging import LOGGER
from backend.internals.db import execute_query


def enrich_author_with_metadata(author_id: int, author_name: str) -> bool:
    """
    Enrich author with metadata from AI providers.
    
    Fetches:
    - Author biography
    - Author photo/image URL
    - Best selling books info
    
    Args:
        author_id: Author ID
        author_name: Author name
    
    Returns:
        bool: True if successful
    """
    try:
        # Try to get author metadata from AI provider
        metadata = get_author_metadata_from_ai(author_name)
        
        if metadata:
            # Update author with metadata
            execute_query("""
                UPDATE authors 
                SET biography = ?, photo_url = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (
                metadata.get('biography'),
                metadata.get('photo_url'),
                author_id
            ), commit=True)
            
            LOGGER.info(f"Enriched author {author_name} with metadata")
            return True
        
        return False
    
    except Exception as e:
        LOGGER.warning(f"Failed to enrich author {author_name}: {e}")
        return False


def get_author_metadata_from_ai(author_name: str) -> dict:
    """
    Get author metadata from AI provider.
    
    Args:
        author_name: Author name
    
    Returns:
        dict: Author metadata (biography, photo_url, etc.)
    """
    try:
        from backend.features.ai_providers import get_ai_provider_manager
        
        manager = get_ai_provider_manager()
        provider = manager.get_primary_provider()
        
        if not provider or not provider.is_available():
            return None
        
        # Create a prompt to get author information
        prompt = f"""
        Provide information about the author "{author_name}". 
        Return ONLY a JSON object with these fields (or null if unknown):
        {{
            "biography": "Brief biography (2-3 sentences)",
            "birth_year": "Birth year as number or null",
            "nationality": "Country/nationality",
            "best_books": ["Book 1", "Book 2", "Book 3"],
            "genres": ["Genre 1", "Genre 2"]
        }}
        
        Return ONLY the JSON object, no other text.
        """
        
        # Call AI provider
        # Note: This is a simplified version - actual implementation would depend on provider API
        LOGGER.debug(f"Fetching metadata for author: {author_name}")
        
        # For now, return None - this can be enhanced with actual AI calls
        return None
    
    except Exception as e:
        LOGGER.debug(f"Error getting author metadata from AI: {e}")
        return None


def get_author_with_books(author_id: int) -> dict:
    """
    Get author details with their books and statistics.
    
    Args:
        author_id: Author ID
    
    Returns:
        dict: Author details with books
    """
    try:
        # Get author
        author = execute_query("""
            SELECT id, name, biography, birth_date, photo_url, created_at
            FROM authors
            WHERE id = ?
        """, (author_id,))
        
        if not author:
            return None
        
        author_data = author[0]
        
        # Get author's books with statistics
        books = execute_query("""
            SELECT 
                s.id, 
                s.title, 
                s.content_type,
                s.cover_url,
                COUNT(DISTINCT v.id) as volumes,
                COUNT(DISTINCT c.id) as chapters,
                s.status,
                s.description
            FROM series s
            JOIN author_books ab ON s.id = ab.series_id
            LEFT JOIN volumes v ON s.id = v.series_id
            LEFT JOIN chapters c ON s.id = c.series_id
            WHERE ab.author_id = ?
            GROUP BY s.id
            ORDER BY s.title ASC
        """, (author_id,))
        
        # Calculate statistics
        total_books = len(books) if books else 0
        total_volumes = sum(b['volumes'] for b in books) if books else 0
        total_chapters = sum(b['chapters'] for b in books) if books else 0
        
        # Find best selling (most volumes)
        best_book = max(books, key=lambda x: x['volumes']) if books else None
        
        return {
            "author": author_data,
            "books": books if books else [],
            "statistics": {
                "total_books": total_books,
                "total_volumes": total_volumes,
                "total_chapters": total_chapters,
                "best_book": best_book
            }
        }
    
    except Exception as e:
        LOGGER.error(f"Error getting author with books: {e}")
        return None
