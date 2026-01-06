#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Automatic author synchronization.

This module handles automatic syncing of authors from series to the authors table.
When a series is added or updated with an author, this module ensures the author
exists in the authors table and is linked via author_books.
"""

from backend.base.logging import LOGGER
from backend.internals.db import execute_query


def get_or_create_author(author_name: str, enrich: bool = True, create_readme: bool = True) -> int:
    """
    Get an existing author by name (case-insensitive) or create a new one.
    
    This function ensures that duplicate authors are not created when the same
    author is added via different methods (book import vs author search).
    
    Args:
        author_name: Name of the author
        enrich: Whether to enrich the author with metadata (biography, photo, etc.)
        create_readme: Whether to create README.md file (default: True). Set to False when calling from enhanced import.
    
    Returns:
        int: Author ID
    """
    try:
        if not author_name or not author_name.strip():
            return None
        
        author_name = author_name.strip()
        
        # Check if author already exists (case-insensitive)
        author = execute_query(
            "SELECT id FROM authors WHERE LOWER(name) = LOWER(?)",
            (author_name,)
        )
        
        if author:
            author_id = author[0]['id']
            LOGGER.debug(f"Found existing author '{author_name}' (ID: {author_id})")

            # Ensure README/folder structure exists when requested
            if create_readme:
                try:
                    from backend.features.author_readme_sync import sync_author_readme
                    sync_author_readme(author_id)
                except Exception as e:
                    LOGGER.warning(f"Failed to sync README.md for existing author {author_name}: {e}")

            return author_id
        
        # Create new author
        execute_query("""
            INSERT INTO authors (name, created_at, updated_at)
            VALUES (?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        """, (author_name,), commit=True)
        
        # Get the newly created author ID
        author_result = execute_query("SELECT last_insert_rowid() as id")
        author_id = author_result[0]['id'] if author_result else None
        LOGGER.info(f"Created new author '{author_name}' (ID: {author_id})")
        
        # Enrich author metadata if requested
        if enrich and author_id:
            _enrich_author_metadata(author_id, author_name)
        
        # Create README.md file for the author (if requested)
        if author_id and create_readme:
            try:
                from backend.features.author_readme_sync import sync_author_readme
                sync_author_readme(author_id)
            except Exception as e:
                LOGGER.warning(f"Failed to create README.md for author {author_name}: {e}")
        
        return author_id
    
    except Exception as e:
        LOGGER.error(f"Error in get_or_create_author: {e}")
        return None


def sync_author_for_series(series_id: int, author_name: str = None) -> bool:
    """
    Sync an author for a series.
    
    If author_name is provided, creates/links that author.
    If author_name is None, fetches it from the series.
    Automatically fetches author metadata (photo, biography) from AI provider.
    
    NOTE: Manga authors are NOT synced to the authors table (only books).
    
    Args:
        series_id: ID of the series
        author_name: Optional author name. If None, fetches from series.
    
    Returns:
        bool: True if successful, False otherwise.
    """
    try:
        # Check if this is a manga - if so, skip author sync
        series_info = execute_query("SELECT content_type FROM series WHERE id = ?", (series_id,))
        if series_info:
            content_type = series_info[0].get('content_type', '').upper()
            if content_type in ('MANGA', 'MANHWA', 'MANHUA', 'COMIC'):
                LOGGER.debug(f"Skipping author sync for manga series {series_id} (content_type: {content_type})")
                return False
        
        # Get author name from series if not provided
        if not author_name:
            series = execute_query("SELECT author FROM series WHERE id = ?", (series_id,))
            if not series or not series[0]['author']:
                LOGGER.debug(f"Series {series_id} has no author")
                return False
            author_name = series[0]['author']
        
        # Skip if author name is empty
        if not author_name or not author_name.strip():
            LOGGER.debug(f"Author name is empty for series {series_id}")
            return False
        
        author_name = author_name.strip()
        LOGGER.info(f"Syncing author '{author_name}' for series {series_id}")
        
        # Get or create the author using the helper function
        # Pass create_readme=False to avoid creating README in default location during file system import
        author_id = get_or_create_author(author_name, create_readme=False)
        
        if not author_id:
            LOGGER.error(f"Failed to create or get author '{author_name}'")
            return False
        
        LOGGER.info(f"Got author ID {author_id} for '{author_name}'")
        
        # Try to enrich author metadata (photo, biography)
        _enrich_author_metadata(author_id, author_name)
        
        # Check if link already exists
        link = execute_query("""
            SELECT id FROM author_books 
            WHERE author_id = ? AND series_id = ?
        """, (author_id, series_id))
        
        if link:
            LOGGER.debug(f"Author-series link already exists for author {author_id} and series {series_id}")
            return True
        
        # Create link
        execute_query("""
            INSERT INTO author_books (author_id, series_id)
            VALUES (?, ?)
        """, (author_id, series_id), commit=True)
        
        LOGGER.info(f"Linked author '{author_name}' (ID: {author_id}) to series {series_id}")
        return True
    
    except Exception as e:
        LOGGER.error(f"Error syncing author for series {series_id}: {e}")
        import traceback
        LOGGER.error(traceback.format_exc())
        return False


def _enrich_author_metadata(author_id: int, author_name: str) -> bool:
    """
    Enrich author with metadata from external sources.
    
    Priority:
    1. OpenLibrary (most accurate, no API key needed)
    2. Biography from Groq AI (if configured and OpenLibrary didn't provide biography)
    3. Photo URL from OpenLibrary (fallback)
    
    Args:
        author_id: Author ID
        author_name: Author name
    
    Returns:
        bool: True if successful
    """
    try:
        LOGGER.info(f"Starting enrichment for author: {author_name} (ID: {author_id})")
        success = False
        has_biography = False
        
        # Priority 1: Try OpenLibrary first (most accurate, no API key needed)
        try:
            from backend.features.author_openlibrary_fetcher import update_author_from_openlibrary
            LOGGER.info(f"Attempting to fetch author data from OpenLibrary: {author_name}...")
            if update_author_from_openlibrary(author_id, author_name):
                LOGGER.info(f"[OK] Successfully updated author {author_name} from OpenLibrary")
                success = True
                
                # Check if biography was added by OpenLibrary
                author_check = execute_query(
                    "SELECT biography FROM authors WHERE id = ?",
                    (author_id,)
                )
                has_biography = author_check and author_check[0].get('biography')
            else:
                LOGGER.debug(f"Could not fetch author data from OpenLibrary: {author_name}")
                
                # Try to fetch released books count from OpenLibrary even if other data failed
                try:
                    import requests
                    from backend.features.metadata_providers.openlibrary.provider import OpenLibraryProvider
                    provider = OpenLibraryProvider()
                    search_url = f"{provider.base_url}/search/authors.json"
                    response = requests.get(search_url, params={"q": author_name}, timeout=5)
                    
                    if response.ok:
                        data = response.json()
                        if data.get("docs") and len(data["docs"]) > 0:
                            work_count = data["docs"][0].get("work_count", 0)
                            if work_count > 0:
                                # Store work_count in description temporarily (we'll use it for released count)
                                execute_query(
                                    "UPDATE authors SET description = ? WHERE id = ?",
                                    (f"Released: {work_count}", author_id),
                                    commit=True
                                )
                                LOGGER.info(f"Stored released books count ({work_count}) for author {author_name}")
                except Exception as e:
                    LOGGER.debug(f"Could not fetch released books count from OpenLibrary: {e}")
        except Exception as e:
            LOGGER.debug(f"Error fetching from OpenLibrary for {author_name}: {e}")
        
        # Priority 2: Fallback to Groq for biography if still missing
        if not has_biography:
            try:
                from backend.features.author_biography_fetcher import update_author_biography
                LOGGER.info(f"Attempting to fetch biography for {author_name} from Groq...")
                if update_author_biography(author_id, author_name):
                    LOGGER.info(f"[OK] Successfully added biography for author {author_name} from Groq")
                    success = True
                    has_biography = True
                else:
                    LOGGER.debug(f"Could not fetch biography for {author_name} - Groq API key may not be configured")
            except Exception as e:
                LOGGER.debug(f"Error fetching biography from Groq for {author_name}: {e}")
        
        # Priority 3: Try to fetch author photo from OpenLibrary (if not already done)
        try:
            from backend.features.author_photo_fetcher import update_author_photo
            LOGGER.debug(f"Attempting to fetch photo for {author_name} from OpenLibrary...")
            if update_author_photo(author_id, author_name):
                LOGGER.info(f"[OK] Successfully added photo for author {author_name}")
                success = True
            else:
                LOGGER.debug(f"Could not fetch photo for {author_name}")
        except Exception as e:
            LOGGER.debug(f"Error fetching photo for {author_name}: {e}")
        
        if success:
            LOGGER.info(f"[OK] Successfully enriched author {author_name} with metadata")
        else:
            LOGGER.warning(f"Could not enrich author {author_name} with any metadata")
        
        return success
    
    except Exception as e:
        LOGGER.error(f"Error enriching author metadata: {e}")
        import traceback
        LOGGER.error(traceback.format_exc())
        return False


def sync_all_authors() -> dict:
    """
    Sync all authors from series table.
    
    Returns:
        dict: Statistics about the sync operation.
    """
    try:
        stats = {
            "total_series": 0,
            "authors_created": 0,
            "links_created": 0,
            "errors": 0
        }
        
        # Get all series with authors
        series_list = execute_query("""
            SELECT id, author FROM series 
            WHERE author IS NOT NULL AND author != ''
        """)
        
        stats["total_series"] = len(series_list)
        
        for series in series_list:
            try:
                # Check if author exists
                author = execute_query(
                    "SELECT id FROM authors WHERE name = ?",
                    (series['author'],)
                )
                
                if not author:
                    # Create author
                    execute_query("""
                        INSERT INTO authors (name, created_at, updated_at)
                        VALUES (?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                    """, (series['author'],), commit=True)
                    stats["authors_created"] += 1
                    author_id = execute_query(
                        "SELECT id FROM authors WHERE name = ?",
                        (series['author'],)
                    )[0]['id']
                else:
                    author_id = author[0]['id']
                
                # Check if link exists
                link = execute_query("""
                    SELECT id FROM author_books 
                    WHERE author_id = ? AND series_id = ?
                """, (author_id, series['id']))
                
                if not link:
                    # Create link
                    execute_query("""
                        INSERT INTO author_books (author_id, series_id)
                        VALUES (?, ?)
                    """, (author_id, series['id']), commit=True)
                    stats["links_created"] += 1
            
            except Exception as e:
                LOGGER.error(f"Error syncing author for series {series['id']}: {e}")
                stats["errors"] += 1
        
        LOGGER.info(f"Author sync complete: {stats}")
        return stats
    
    except Exception as e:
        LOGGER.error(f"Error in sync_all_authors: {e}")
        return {
            "total_series": 0,
            "authors_created": 0,
            "links_created": 0,
            "errors": 1
        }
