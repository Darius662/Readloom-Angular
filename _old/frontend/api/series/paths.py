#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Series path management service.
Handles folder paths and custom path operations.
"""

from pathlib import Path
from backend.internals.db import execute_query
from backend.internals.settings import Settings
from backend.base.helpers import get_safe_folder_name, get_ebook_storage_dir
from backend.base.logging import LOGGER


def get_series_folder_path(series_id, title, content_type, collection_id=None, root_folder_id=None):
    """Get the folder path for a series.
    
    Args:
        series_id (int): Series ID.
        title (str): Series title.
        content_type (str): Content type.
        collection_id (int, optional): Collection ID.
        root_folder_id (int, optional): Root folder ID.
        
    Returns:
        str: Folder path.
    """
    try:
        # Check for custom path
        custom_path = execute_query("SELECT custom_path FROM series WHERE id = ?", (series_id,))
        
        if custom_path and custom_path[0].get('custom_path'):
            LOGGER.info(f"Using custom path for series {series_id}: {custom_path[0]['custom_path']}")
            return custom_path[0]['custom_path']
        
        # Create safe folder name
        safe_title = get_safe_folder_name(title)
        LOGGER.info(f"Original title: '{title}', Safe title: '{safe_title}'")
        
        # Get settings
        settings = Settings().get_settings()
        chosen_root_path = None
        
        # 1) Explicit root folder ID
        if root_folder_id:
            try:
                rf = execute_query("SELECT path FROM root_folders WHERE id = ?", (int(root_folder_id),))
                if rf:
                    chosen_root_path = Path(rf[0]['path'])
            except Exception:
                pass
        
        # 2) Collection's root folders
        if chosen_root_path is None and collection_id:
            try:
                rows = execute_query("""
                    SELECT rf.path FROM root_folders rf
                    JOIN collection_root_folders crf ON rf.id = crf.root_folder_id
                    WHERE crf.collection_id = ?
                    ORDER BY rf.name ASC
                """, (int(collection_id),))
                if rows:
                    chosen_root_path = Path(rows[0]['path'])
            except Exception:
                pass
        
        # 3) Default collection for content type
        if chosen_root_path is None:
            try:
                rows = execute_query("""
                    SELECT rf.path FROM root_folders rf
                    JOIN collection_root_folders crf ON rf.id = crf.root_folder_id
                    JOIN collections c ON c.id = crf.collection_id
                    WHERE c.is_default = 1 AND UPPER(c.content_type) = ?
                    ORDER BY rf.name ASC
                """, (content_type.upper(),))
                if rows:
                    chosen_root_path = Path(rows[0]['path'])
            except Exception:
                pass
        
        # 4) Settings root folder matching type
        if chosen_root_path is None and settings.root_folders:
            try:
                rf = next((rf for rf in settings.root_folders if (rf.get('content_type') or 'MANGA').upper() == content_type), None)
                if rf:
                    chosen_root_path = Path(rf['path'])
            except Exception:
                pass
        
        # 5) Fallback
        if chosen_root_path is None:
            if settings.root_folders:
                chosen_root_path = Path(settings.root_folders[0]['path'])
            else:
                chosen_root_path = get_ebook_storage_dir()
        
        series_dir = chosen_root_path / safe_title
        return str(series_dir)
    except Exception as e:
        LOGGER.error(f"Error getting series folder path: {e}")
        return None


def set_custom_path(series_id, custom_path):
    """Set a custom path for a series.
    
    Args:
        series_id (int): Series ID.
        custom_path (str): Custom path.
        
    Returns:
        dict: Status or error.
    """
    try:
        # Validate path
        if not custom_path:
            return {"error": "Custom path is required"}, 400
        
        # Update series
        execute_query("""
            UPDATE series
            SET custom_path = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (custom_path, series_id), commit=True)
        
        return {"success": True, "message": "Custom path set successfully"}, 200
    except Exception as e:
        LOGGER.error(f"Error setting custom path: {e}")
        return {"error": str(e)}, 500


def validate_path(path):
    """Validate a file path.
    
    Args:
        path (str): Path to validate.
        
    Returns:
        bool: True if valid, False otherwise.
    """
    try:
        Path(path)
        return True
    except Exception:
        return False
