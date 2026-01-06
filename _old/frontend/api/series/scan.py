#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Series scan service.
Handles scanning for e-books and updating series data.
"""

from backend.features.ebook_files import scan_for_ebooks
from backend.internals.db import execute_query
from backend.base.logging import LOGGER


def scan_series_for_ebooks(series_id):
    """Scan a series for e-books.
    
    Args:
        series_id (int): Series ID.
        
    Returns:
        dict: Scan result or error.
    """
    try:
        # Get series
        series = execute_query("SELECT id, title FROM series WHERE id = ?", (series_id,))
        if not series:
            return {"error": "Series not found"}, 404
        
        # Scan for ebooks
        result = scan_for_ebooks(series_id)
        
        return {
            "success": True,
            "series_id": series_id,
            "series_title": series[0]['title'],
            "scan_result": result
        }, 200
    except Exception as e:
        LOGGER.error(f"Error scanning series for ebooks: {e}")
        return {"error": str(e)}, 500


def validate_scan_request(series_id):
    """Validate a scan request.
    
    Args:
        series_id (int): Series ID.
        
    Returns:
        tuple: (is_valid, error_message)
    """
    try:
        if not series_id:
            return False, "Series ID is required"
        
        # Check if series exists
        series = execute_query("SELECT id FROM series WHERE id = ?", (series_id,))
        if not series:
            return False, "Series not found"
        
        return True, None
    except Exception as e:
        LOGGER.error(f"Error validating scan request: {e}")
        return False, str(e)
