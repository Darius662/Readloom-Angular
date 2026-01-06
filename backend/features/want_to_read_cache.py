#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Want-to-read cache management.
Handles caching of want-to-read entries and README.txt generation.
"""

from typing import Dict, List, Any, Optional
from pathlib import Path
from backend.base.logging import LOGGER
from backend.internals.db import execute_query


def add_to_cache(series_id: int, title: str, author: str, cover_url: str, 
                 metadata_source: str, metadata_id: str, content_type: str = "MANGA") -> bool:
    """Add a series to the want-to-read cache.
    
    Args:
        series_id: The series ID (0 if not in series table)
        title: Series title
        author: Series author
        cover_url: Cover image URL
        metadata_source: Metadata provider name
        metadata_id: Metadata provider ID
        content_type: Content type (MANGA, BOOK, etc.)
        
    Returns:
        bool: True if added/updated, False otherwise
    """
    try:
        LOGGER.info(f"Adding to cache: {metadata_source}:{metadata_id}, content_type={content_type}")
        
        # Use metadata_id as unique key since series_id might be 0
        existing = execute_query(
            "SELECT id FROM want_to_read_cache WHERE metadata_source = ? AND metadata_id = ?",
            (metadata_source, metadata_id)
        )
        
        if existing:
            # Update existing cache entry
            LOGGER.info(f"Updating existing cache entry for {metadata_source}:{metadata_id}")
            execute_query(
                """UPDATE want_to_read_cache 
                   SET series_id = ?, title = ?, author = ?, cover_url = ?, 
                       content_type = ?, updated_at = CURRENT_TIMESTAMP
                   WHERE metadata_source = ? AND metadata_id = ?""",
                (series_id, title, author, cover_url, content_type, metadata_source, metadata_id),
                commit=True
            )
            LOGGER.info(f"Updated cache for {metadata_source}:{metadata_id}")
        else:
            # Insert new cache entry
            LOGGER.info(f"Inserting new cache entry for {metadata_source}:{metadata_id}")
            execute_query(
                """INSERT INTO want_to_read_cache 
                   (series_id, title, author, cover_url, metadata_source, metadata_id, content_type)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (series_id, title, author, cover_url, metadata_source, metadata_id, content_type),
                commit=True
            )
            LOGGER.info(f"Added {metadata_source}:{metadata_id} to cache with content_type={content_type}")
        
        return True
    except Exception as e:
        LOGGER.error(f"Error adding to cache: {e}", exc_info=True)
        return False


def remove_from_cache(series_id: int) -> bool:
    """Remove a series from the want-to-read cache.
    
    Args:
        series_id: The series ID
        
    Returns:
        bool: True if removed, False otherwise
    """
    try:
        execute_query(
            "DELETE FROM want_to_read_cache WHERE series_id = ?",
            (series_id,),
            commit=True
        )
        LOGGER.info(f"Removed series {series_id} from cache")
        return True
    except Exception as e:
        LOGGER.error(f"Error removing from cache: {e}")
        return False


def get_cache_entries() -> List[Dict[str, Any]]:
    """Get all want-to-read cache entries.
    
    Returns:
        List of cache entries
    """
    try:
        entries = execute_query(
            """SELECT * FROM want_to_read_cache ORDER BY created_at DESC"""
        )
        return entries if entries else []
    except Exception as e:
        LOGGER.error(f"Error getting cache entries: {e}")
        return []


def generate_want_to_read_readme(root_folder_path: Path, content_type: str = "MANGA") -> bool:
    """Generate a WANT_TO_READ.txt file in root folder with want-to-read entries for specific content type.
    
    Args:
        root_folder_path: Path to the root folder
        content_type: Content type to filter (MANGA, BOOK, etc.)
        
    Returns:
        bool: True if generated successfully, False otherwise
    """
    try:
        # Get want-to-read entries for this content type
        entries = execute_query(
            """SELECT * FROM want_to_read_cache WHERE content_type = ? ORDER BY created_at DESC""",
            (content_type,)
        )
        
        if not entries:
            LOGGER.info(f"No want-to-read entries for {content_type}")
            return True
        
        # Create WANT_TO_READ.txt in root folder
        readme_path = root_folder_path / "WANT_TO_READ.txt"
        
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(f"WANT TO READ LIST - {content_type}\n")
            f.write("=" * 80 + "\n\n")
            f.write(f"Generated: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total entries: {len(entries)}\n\n")
            f.write("-" * 80 + "\n\n")
            
            for entry in entries:
                f.write(f"Title: {entry.get('title', 'Unknown')}\n")
                f.write(f"Author: {entry.get('author', 'Unknown')}\n")
                f.write(f"Cover URL: {entry.get('cover_url', '')}\n")
                f.write(f"Provider: {entry.get('metadata_source', '')}\n")
                f.write(f"Provider ID: {entry.get('metadata_id', '')}\n")
                f.write("-" * 80 + "\n\n")
        
        LOGGER.info(f"Generated want-to-read README for {content_type} at {readme_path}")
        return True
    except Exception as e:
        LOGGER.error(f"Error generating want-to-read README: {e}")
        return False


def sync_cache_to_readme_files(content_type: str = "MANGA") -> bool:
    """Sync want-to-read cache to README files in all root folders for specific content type.
    
    Args:
        content_type: Content type to sync (MANGA, BOOK, etc.)
    
    Returns:
        bool: True if synced successfully, False otherwise
    """
    try:
        # Get root folders for this content type
        root_folders = execute_query(
            """SELECT DISTINCT path FROM root_folders WHERE content_type = ?""",
            (content_type,)
        )
        
        if not root_folders:
            LOGGER.info(f"No root folders found for {content_type}")
            return True
        
        for folder in root_folders:
            folder_path = Path(folder['path'])
            if folder_path.exists() and folder_path.is_dir():
                generate_want_to_read_readme(folder_path, content_type)
        
        LOGGER.info(f"Synced want-to-read cache to {len(root_folders)} root folders for {content_type}")
        return True
    except Exception as e:
        LOGGER.error(f"Error syncing cache to README files: {e}")
        return False
