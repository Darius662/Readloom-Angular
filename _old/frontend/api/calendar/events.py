#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Calendar events service.
Retrieves and manages calendar events.
"""

from datetime import datetime, timedelta
from backend.features.calendar import get_calendar_events
from backend.internals.settings import Settings
from backend.base.logging import LOGGER


def get_events_for_date_range(start_date, end_date, series_id=None):
    """Get calendar events for a date range.
    
    Args:
        start_date (str): Start date (YYYY-MM-DD format).
        end_date (str): End date (YYYY-MM-DD format).
        series_id (int, optional): Filter by series ID.
        
    Returns:
        list: Calendar events.
    """
    try:
        events = get_calendar_events(start_date, end_date, series_id)
        return events if events else []
    except Exception as e:
        LOGGER.error(f"Error getting calendar events: {e}")
        return []


def get_default_date_range():
    """Get default calendar date range.
    
    Returns:
        tuple: (start_date, end_date) in YYYY-MM-DD format.
    """
    try:
        start_date = datetime.now().strftime('%Y-%m-%d')
        settings = Settings().get_settings()
        end_date = (datetime.now() + timedelta(days=settings.calendar_range_days)).strftime('%Y-%m-%d')
        return start_date, end_date
    except Exception as e:
        LOGGER.error(f"Error getting default date range: {e}")
        # Fallback to 30 days
        start_date = datetime.now().strftime('%Y-%m-%d')
        end_date = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
        return start_date, end_date


def validate_date_format(date_str):
    """Validate date format (YYYY-MM-DD).
    
    Args:
        date_str (str): Date string to validate.
        
    Returns:
        bool: True if valid, False otherwise.
    """
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return True
    except (ValueError, TypeError):
        return False


def format_calendar_events(events):
    """Format calendar events for API response.
    
    Args:
        events (list): Raw calendar events.
        
    Returns:
        list: Formatted events.
    """
    try:
        return [
            {
                "id": e.get("id"),
                "title": e.get("title"),
                "date": e.get("date"),
                "type": e.get("type"),
                "series": e.get("series"),
                "description": e.get("description")
            }
            for e in events
        ]
    except Exception as e:
        LOGGER.error(f"Error formatting calendar events: {e}")
        return []
