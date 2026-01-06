#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Collection formats service.
Handles format management for collection items.
"""

from backend.internals.db import execute_query
from backend.base.logging import LOGGER


def update_item_format(item_id, format_type):
    """Update collection item format.
    
    Args:
        item_id (int): Item ID.
        format_type (str): Format type.
        
    Returns:
        dict: Result or error.
    """
    try:
        if not format_type:
            return {"error": "Format is required"}, 400
        
        execute_query("""
            UPDATE collection_items
            SET format = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (format_type, item_id), commit=True)
        
        return {"success": True, "message": "Format updated successfully"}, 200
    except Exception as e:
        LOGGER.error(f"Error updating item format: {e}")
        return {"error": str(e)}, 500


def update_item_digital_format(item_id, digital_format):
    """Update collection item digital format.
    
    Args:
        item_id (int): Item ID.
        digital_format (str): Digital format.
        
    Returns:
        dict: Result or error.
    """
    try:
        if not digital_format:
            return {"error": "Digital format is required"}, 400
        
        execute_query("""
            UPDATE collection_items
            SET digital_format = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (digital_format, item_id), commit=True)
        
        return {"success": True, "message": "Digital format updated successfully"}, 200
    except Exception as e:
        LOGGER.error(f"Error updating item digital format: {e}")
        return {"error": str(e)}, 500


def validate_format(format_str):
    """Validate format string.
    
    Args:
        format_str (str): Format to validate.
        
    Returns:
        bool: True if valid, False otherwise.
    """
    valid_formats = ["HARDCOVER", "PAPERBACK", "DIGITAL", "UNKNOWN"]
    return format_str.upper() in valid_formats if format_str else False
