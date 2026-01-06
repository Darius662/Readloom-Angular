#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Volume formats service.
Handles physical and digital format management.
"""

from backend.internals.db import execute_query
from backend.base.logging import LOGGER


def update_volume_format(volume_id, data):
    """Update volume physical format.
    
    Args:
        volume_id (int): Volume ID.
        data (dict): Format data.
        
    Returns:
        dict: Status or error.
    """
    try:
        if not data.get("format"):
            return {"error": "Format is required"}, 400
        
        execute_query("""
            UPDATE collection_items
            SET format = ?, updated_at = CURRENT_TIMESTAMP
            WHERE volume_id = ? AND item_type = 'VOLUME'
        """, (data["format"], volume_id), commit=True)
        
        return {"success": True, "message": "Format updated successfully"}, 200
    except Exception as e:
        LOGGER.error(f"Error updating volume format: {e}")
        return {"error": str(e)}, 500


def update_volume_digital_format(volume_id, data):
    """Update volume digital format.
    
    Args:
        volume_id (int): Volume ID.
        data (dict): Digital format data.
        
    Returns:
        dict: Status or error.
    """
    try:
        if not data.get("digital_format"):
            return {"error": "Digital format is required"}, 400
        
        # Note: digital_format is stored in collection_items table
        # First, ensure the column exists in the database
        try:
            execute_query("""
                UPDATE collection_items
                SET digital_format = ?, updated_at = CURRENT_TIMESTAMP
                WHERE volume_id = ? AND item_type = 'VOLUME'
            """, (data["digital_format"], volume_id), commit=True)
        except Exception as col_err:
            if "no such column" in str(col_err):
                # Column doesn't exist in database, add it
                LOGGER.warning(f"digital_format column missing, attempting to add it")
                try:
                    execute_query("""
                        ALTER TABLE collection_items ADD COLUMN digital_format TEXT CHECK(digital_format IN ('PDF', 'EPUB', 'CBZ', 'CBR', 'MOBI', 'AZW', 'NONE'))
                    """, commit=True)
                    # Retry the update
                    execute_query("""
                        UPDATE collection_items
                        SET digital_format = ?, updated_at = CURRENT_TIMESTAMP
                        WHERE volume_id = ? AND item_type = 'VOLUME'
                    """, (data["digital_format"], volume_id), commit=True)
                except Exception as alter_err:
                    if "duplicate column name" not in str(alter_err):
                        raise
                    # Column was added by another process, retry update
                    execute_query("""
                        UPDATE collection_items
                        SET digital_format = ?, updated_at = CURRENT_TIMESTAMP
                        WHERE volume_id = ? AND item_type = 'VOLUME'
                    """, (data["digital_format"], volume_id), commit=True)
            else:
                raise
        
        return {"success": True, "message": "Digital format updated successfully"}, 200
    except Exception as e:
        LOGGER.error(f"Error updating volume digital format: {e}")
        return {"error": str(e)}, 500


def validate_format(format_str):
    """Validate format string.
    
    Args:
        format_str (str): Format to validate.
        
    Returns:
        bool: True if valid, False otherwise.
    """
    valid_formats = ["HARDCOVER", "PAPERBACK", "DIGITAL", "UNKNOWN"]
    return format_str.upper() in valid_formats
