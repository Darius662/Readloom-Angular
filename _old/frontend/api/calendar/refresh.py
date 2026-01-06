#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Calendar refresh service.
Handles calendar data refresh operations.
"""

from backend.features.calendar import update_calendar
from backend.base.logging import LOGGER


def refresh_calendar_data():
    """Refresh calendar data.
    
    Returns:
        dict: Status of refresh operation.
    """
    try:
        update_calendar()
        return {
            "success": True,
            "message": "Calendar refreshed successfully"
        }
    except Exception as e:
        LOGGER.error(f"Error refreshing calendar: {e}")
        return {
            "success": False,
            "message": f"Error refreshing calendar: {str(e)}"
        }


def validate_refresh_request():
    """Validate refresh request.
    
    Returns:
        tuple: (is_valid, error_message)
    """
    try:
        # Add any validation logic here if needed
        return True, None
    except Exception as e:
        LOGGER.error(f"Error validating refresh request: {e}")
        return False, str(e)
