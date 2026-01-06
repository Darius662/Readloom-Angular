#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Dashboard events service.
Handles calendar events for dashboard display.
"""

from datetime import datetime
from backend.features.calendar import get_calendar_events
from backend.base.logging import LOGGER


def get_today_events():
    """Get calendar events for today.
    
    Returns:
        list: List of events for today.
    """
    try:
        today = datetime.now().strftime('%Y-%m-%d')
        events = get_calendar_events(today, today)
        return events if events else []
    except Exception as e:
        LOGGER.error(f"Error getting today's events: {e}")
        return []


def format_events(events):
    """Format events for dashboard display.
    
    Args:
        events (list): List of raw events.
        
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
                "series": e.get("series")
            }
            for e in events
        ]
    except Exception as e:
        LOGGER.error(f"Error formatting events: {e}")
        return []


def get_releases_today_count():
    """Get count of releases today.
    
    Returns:
        int: Number of releases today.
    """
    try:
        events = get_today_events()
        return len(events)
    except Exception as e:
        LOGGER.error(f"Error getting releases today count: {e}")
        return 0
