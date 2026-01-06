#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
README.txt synchronization module.
Automatically updates README.txt files when series metadata changes.
"""

from pathlib import Path
from typing import Optional

from backend.base.logging import LOGGER
from backend.base.helpers import ensure_readme_file, get_safe_folder_name
from backend.internals.db import execute_query
from backend.internals.settings import Settings


def sync_series_to_readme(series_id: int) -> bool:
    """
    Sync series metadata to README.txt file.
    
    This function:
    1. Fetches series metadata from database
    2. Finds the series folder in root folders or uses custom_path
    3. Updates the README.txt file with current metadata
    
    Args:
        series_id (int): The series ID to sync
        
    Returns:
        bool: True if README was updated, False otherwise
    """
    try:
        # Fetch series metadata from database
        series_data = execute_query(
            """SELECT 
                id, title, description, author, publisher, cover_url, status, 
                content_type, metadata_source, metadata_id, isbn, published_date, subjects,
                star_rating, reading_progress, user_description, custom_path, in_library, want_to_read
            FROM series WHERE id = ?""",
            (series_id,)
        )
        
        if not series_data:
            LOGGER.warning(f"Series {series_id} not found in database")
            return False
        
        series = series_data[0]
        series_dir = None
        
        # Check if series has a custom path
        if series.get('custom_path'):
            custom_path = Path(series['custom_path'])
            if custom_path.exists() and custom_path.is_dir():
                series_dir = custom_path
                LOGGER.debug(f"Using custom path for series {series_id}: {series_dir}")
        
        # If no custom path or custom path doesn't exist, search in root folders
        if not series_dir:
            # Get settings to access root folders
            settings = Settings().get_settings()
            if not settings.root_folders:
                LOGGER.warning(f"No root folders configured, cannot sync README for series {series_id}")
                return False
            
            # Find the series folder
            safe_title = get_safe_folder_name(series['title'])
            
            LOGGER.debug(f"Looking for series folder: {safe_title}")
            
            for root_folder in settings.root_folders:
                root_path = Path(root_folder['path'])
                LOGGER.debug(f"Checking root folder: {root_path}")
                
                # Check direct child
                potential_dir = root_path / safe_title
                if potential_dir.exists():
                    series_dir = potential_dir
                    LOGGER.debug(f"Found series folder at: {series_dir}")
                    break
                
                # Also check for author/series structure (for books with author folders)
                try:
                    for author_dir in root_path.iterdir():
                        if author_dir.is_dir():
                            potential_dir = author_dir / safe_title
                            if potential_dir.exists():
                                series_dir = potential_dir
                                LOGGER.debug(f"Found series folder in author structure at: {series_dir}")
                                break
                except (PermissionError, OSError) as e:
                    LOGGER.debug(f"Could not iterate root folder {root_path}: {e}")
                    continue
                
                if series_dir:
                    break
            
            if not series_dir:
                LOGGER.warning(f"Series folder not found for {series['title']} (ID: {series_id}) - searched in {len(settings.root_folders)} root folders")
                return False
        
        # Convert subjects string to list if needed
        # Subjects are stored as comma-separated string and used as both subjects and genres
        subjects_list = None
        if series.get('subjects'):
            subjects_list = [s.strip() for s in series['subjects'].split(',')] if isinstance(series['subjects'], str) else series['subjects']
        
        # Update README.txt with current metadata
        ensure_readme_file(
            series_dir,
            series['title'],
            series['id'],
            series['content_type'],
            metadata_source=series.get('metadata_source'),
            metadata_id=series.get('metadata_id'),
            author=series.get('author'),
            publisher=series.get('publisher'),
            isbn=series.get('isbn'),
            genres=subjects_list,  # Use subjects as genres
            cover_url=series.get('cover_url'),
            published_date=series.get('published_date'),
            subjects=subjects_list,  # Use subjects for both
            description=series.get('description'),
            star_rating=series.get('star_rating'),
            reading_progress=series.get('reading_progress'),
            user_description=series.get('user_description'),
            in_library=series.get('in_library'),
            want_to_read=series.get('want_to_read')
        )
        
        # Create cover_art folder in the series directory
        try:
            cover_art_dir = series_dir / "cover_art"
            cover_art_dir.mkdir(parents=True, exist_ok=True)
            LOGGER.info(f"Created/verified cover_art folder for series {series_id}: {cover_art_dir}")
        except Exception as cover_err:
            LOGGER.warning(f"Could not create cover_art folder for series {series_id}: {cover_err}")
        
        LOGGER.info(f"Synced README.txt for series {series_id}: {series['title']}")
        return True
        
    except Exception as e:
        LOGGER.error(f"Error syncing README for series {series_id}: {e}")
        import traceback
        LOGGER.error(traceback.format_exc())
        return False


def sync_all_series_readmes(content_type: str = None, merge_with_existing: bool = False) -> dict:
    """Sync README.txt files for all series in the database.
    
    Args:
        content_type (str, optional): Filter by content type (BOOK, MANGA, COMIC). If None, syncs all.
        merge_with_existing (bool, optional): If True, merge with existing README data. Defaults to False.
    
    Returns:
        dict: Statistics about the sync operation.
    """
    try:
        # Query series based on content type
        if content_type:
            series_list = execute_query(
                "SELECT id FROM series WHERE content_type = ?",
                (content_type,)
            )
        else:
            series_list = execute_query("SELECT id FROM series")
        
        stats = {
            'total': len(series_list),
            'synced': 0,
            'failed': 0,
            'errors': []
        }
        
        for series in series_list:
            series_id = series['id']
            try:
                if sync_series_to_readme(series_id):
                    stats['synced'] += 1
                else:
                    stats['failed'] += 1
            except Exception as e:
                stats['failed'] += 1
                stats['errors'].append(f"Series {series_id}: {str(e)}")
        
        LOGGER.info(f"Series README sync complete: {stats['synced']}/{stats['total']} synced")
        return stats
    
    except Exception as e:
        LOGGER.error(f"Error syncing all series READMEs: {e}")
        return {
            'total': 0,
            'synced': 0,
            'failed': 0,
            'errors': [str(e)]
        }
