#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Calendar API routes.
Defines all calendar endpoints.
"""

from flask import Blueprint, jsonify, request
from backend.base.logging import LOGGER

from .events import (
    get_events_for_date_range,
    get_default_date_range,
    validate_date_format,
    format_calendar_events
)
from .refresh import (
    refresh_calendar_data,
    validate_refresh_request
)

# Create routes blueprint
calendar_routes = Blueprint('calendar_routes', __name__)


@calendar_routes.route('/api/calendar', methods=['GET'])
def get_calendar():
    """Get calendar events.
    
    Query Parameters:
        start_date (str, optional): Start date (YYYY-MM-DD).
        end_date (str, optional): End date (YYYY-MM-DD).
        series_id (int, optional): Filter by series ID.
    
    Returns:
        Response: Calendar events.
    """
    try:
        # Get query parameters
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        series_id = request.args.get('series_id', type=int)
        
        # Use default dates if not provided
        if not start_date or not end_date:
            start_date, end_date = get_default_date_range()
        
        # Validate date formats
        if not validate_date_format(start_date) or not validate_date_format(end_date):
            return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400
        
        # Get events
        events = get_events_for_date_range(start_date, end_date, series_id)
        formatted_events = format_calendar_events(events)
        
        return jsonify({"events": formatted_events})
    except Exception as e:
        LOGGER.error(f"Error getting calendar: {e}")
        return jsonify({"error": str(e)}), 500


@calendar_routes.route('/api/calendar/refresh', methods=['POST'])
def refresh_calendar():
    """Refresh calendar data.
    
    Returns:
        Response: Refresh status.
    """
    try:
        # Validate request
        is_valid, error = validate_refresh_request()
        if not is_valid:
            return jsonify({"error": error}), 400
        
        # Refresh calendar
        result = refresh_calendar_data()
        
        if result["success"]:
            return jsonify(result)
        else:
            return jsonify(result), 500
    except Exception as e:
        LOGGER.error(f"Error refreshing calendar: {e}")
        return jsonify({"error": str(e)}), 500
