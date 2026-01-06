#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Author photo fetcher - fetches author photos from OpenLibrary and other sources.
"""

import requests
from backend.base.logging import LOGGER
from backend.internals.db import execute_query


def fetch_author_photo_from_openlibrary(author_name: str) -> str:
    """
    Fetch author photo URL from OpenLibrary.
    
    First tries to get author photo, then falls back to book cover.
    
    Args:
        author_name: Author name
    
    Returns:
        str: Photo URL or None
    """
    try:
        # Search for author on OpenLibrary
        search_url = "https://openlibrary.org/search/authors.json"
        params = {
            "q": author_name,
            "limit": 1
        }
        
        response = requests.get(search_url, params=params, timeout=5)
        response.raise_for_status()
        
        data = response.json()
        
        if not data.get("docs") or len(data["docs"]) == 0:
            LOGGER.debug(f"No author found on OpenLibrary for: {author_name}")
            return None
        
        author = data["docs"][0]
        
        # Check if author has a photo
        if author.get("has_photos") and author.get("photos"):
            photo_id = author["photos"][0]
            # Construct OpenLibrary photo URL
            photo_url = f"https://covers.openlibrary.org/a/id/{photo_id}-M.jpg"
            LOGGER.info(f"Found author photo for {author_name}: {photo_url}")
            return photo_url
        
        # Try to get a book cover as fallback
        if author.get("top_work"):
            # Get the top work key
            top_work = author.get("top_work")
            if top_work:
                # Try to fetch cover for this work
                work_key = top_work.replace("/works/", "")
                cover_url = f"https://covers.openlibrary.org/w/id/{work_key}-M.jpg"
                LOGGER.info(f"Using book cover for {author_name}: {cover_url}")
                return cover_url
        
        LOGGER.debug(f"No photo or book cover found on OpenLibrary for: {author_name}")
        return None
    
    except requests.Timeout:
        LOGGER.debug(f"Timeout fetching author photo for {author_name}")
        return None
    except Exception as e:
        LOGGER.debug(f"Error fetching author photo from OpenLibrary: {e}")
        return None


def update_author_photo(author_id: int, author_name: str) -> bool:
    """
    Fetch and update author photo.
    
    Args:
        author_id: Author ID
        author_name: Author name
    
    Returns:
        bool: True if photo was updated
    """
    try:
        # Fetch photo URL
        photo_url = fetch_author_photo_from_openlibrary(author_name)
        
        if not photo_url:
            LOGGER.debug(f"Could not fetch photo for author {author_name}")
            return False
        
        # Try to update author with photo URL
        try:
            execute_query("""
                UPDATE authors 
                SET photo_url = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (photo_url, author_id), commit=True)
            
            LOGGER.info(f"Updated author {author_name} with photo: {photo_url}")
            return True
        except Exception as e:
            # If photo_url column doesn't exist, just log and continue
            if "photo_url" in str(e):
                LOGGER.debug(f"photo_url column doesn't exist in database, skipping photo update: {e}")
                return False
            else:
                raise
    
    except Exception as e:
        LOGGER.error(f"Error updating author photo: {e}")
        return False


def fetch_and_update_all_author_photos() -> dict:
    """
    Fetch and update photos for all authors without photos.
    
    Returns:
        dict: Statistics about the operation
    """
    try:
        stats = {
            "authors_checked": 0,
            "photos_added": 0,
            "errors": 0
        }
        
        # Get all authors without photos
        authors = execute_query("""
            SELECT id, name FROM authors 
            WHERE photo_url IS NULL OR photo_url = ''
        """)
        
        if not authors:
            LOGGER.info("All authors already have photos")
            return stats
        
        stats["authors_checked"] = len(authors)
        
        for author in authors:
            try:
                if update_author_photo(author['id'], author['name']):
                    stats["photos_added"] += 1
            except Exception as e:
                LOGGER.error(f"Error updating photo for author {author['name']}: {e}")
                stats["errors"] += 1
        
        LOGGER.info(f"Author photo fetch complete: {stats}")
        return stats
    
    except Exception as e:
        LOGGER.error(f"Error in fetch_and_update_all_author_photos: {e}")
        return {
            "authors_checked": 0,
            "photos_added": 0,
            "errors": 1
        }
