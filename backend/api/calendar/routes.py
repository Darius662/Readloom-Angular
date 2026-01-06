#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
API endpoints for calendar events.
"""

from flask import Blueprint, jsonify, request
from datetime import datetime

from backend.base.logging import LOGGER
from backend.internals.db import execute_query

# Create Blueprint for calendar API
calendar_bp = Blueprint('calendar', __name__, url_prefix='/api/calendar')


@calendar_bp.route('', methods=['GET'])
def get_calendar_events():
    """Get calendar events for a date range.
    
    Query parameters:
        start_date: Start date (YYYY-MM-DD format)
        end_date: End date (YYYY-MM-DD format)
        content_type: Filter by content type (optional)
        collection_id: Filter by collection (optional)
    
    Returns:
        Response: Calendar events for the date range.
    """
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        content_type = request.args.get('content_type')
        collection_id = request.args.get('collection_id')
        
        if not start_date or not end_date:
            return jsonify({"error": "start_date and end_date are required"}), 400
        
        # Build query for calendar events
        query = """
            SELECT 
                c.id,
                c.series_id,
                s.title as series_title,
                s.content_type,
                c.release_date,
                c.chapter_number,
                c.title as chapter_title
            FROM chapters c
            JOIN series s ON c.series_id = s.id
            WHERE c.release_date BETWEEN ? AND ?
        """
        
        params = [start_date, end_date]
        
        # Add content type filter if provided
        if content_type:
            query += " AND s.content_type = ?"
            params.append(content_type)
        
        # Add collection filter if provided
        if collection_id:
            query += """
                AND s.id IN (
                    SELECT series_id FROM collection_series 
                    WHERE collection_id = ?
                )
            """
            params.append(collection_id)
        
        query += " ORDER BY c.release_date ASC"
        
        events = execute_query(query, tuple(params))
        
        # Transform database results to calendar event format
        calendar_events = []
        if events:
            for event in events:
                calendar_events.append({
                    'id': event.get('id'),
                    'seriesId': event.get('series_id'),
                    'seriesTitle': event.get('series_title'),
                    'contentType': event.get('content_type'),
                    'releaseDate': event.get('release_date'),
                    'chapterNumber': event.get('chapter_number'),
                    'title': event.get('chapter_title')
                })
        
        return jsonify({
            "success": True,
            "events": calendar_events
        })
    except Exception as e:
        LOGGER.error(f"Error getting calendar events: {e}")
        return jsonify({"error": str(e)}), 500


@calendar_bp.route('/series/<int:series_id>', methods=['GET'])
def get_series_calendar_events(series_id: int):
    """Get calendar events for a specific series.
    
    Args:
        series_id: The series ID.
    
    Returns:
        Response: Calendar events for the series.
    """
    try:
        query = """
            SELECT 
                c.id,
                c.series_id,
                s.title as series_title,
                s.content_type,
                c.release_date,
                c.chapter_number,
                c.title as chapter_title
            FROM chapters c
            JOIN series s ON c.series_id = s.id
            WHERE c.series_id = ?
            ORDER BY c.release_date ASC
        """
        
        events = execute_query(query, (series_id,))
        
        calendar_events = []
        if events:
            for event in events:
                calendar_events.append({
                    'id': event.get('id'),
                    'seriesId': event.get('series_id'),
                    'seriesTitle': event.get('series_title'),
                    'contentType': event.get('content_type'),
                    'releaseDate': event.get('release_date'),
                    'chapterNumber': event.get('chapter_number'),
                    'title': event.get('chapter_title')
                })
        
        return jsonify({
            "success": True,
            "events": calendar_events
        })
    except Exception as e:
        LOGGER.error(f"Error getting series calendar events: {e}")
        return jsonify({"error": str(e)}), 500


@calendar_bp.route('/<int:event_id>', methods=['GET'])
def get_calendar_event(event_id: int):
    """Get a specific calendar event.
    
    Args:
        event_id: The event ID.
    
    Returns:
        Response: The calendar event.
    """
    try:
        query = """
            SELECT 
                c.id,
                c.series_id,
                s.title as series_title,
                s.content_type,
                c.release_date,
                c.chapter_number,
                c.title as chapter_title
            FROM chapters c
            JOIN series s ON c.series_id = s.id
            WHERE c.id = ?
        """
        
        event = execute_query(query, (event_id,))
        
        if not event:
            return jsonify({"error": "Event not found"}), 404
        
        event_data = event[0]
        calendar_event = {
            'id': event_data.get('id'),
            'seriesId': event_data.get('series_id'),
            'seriesTitle': event_data.get('series_title'),
            'contentType': event_data.get('content_type'),
            'releaseDate': event_data.get('release_date'),
            'chapterNumber': event_data.get('chapter_number'),
            'title': event_data.get('chapter_title')
        }
        
        return jsonify({
            "success": True,
            "event": calendar_event
        })
    except Exception as e:
        LOGGER.error(f"Error getting calendar event: {e}")
        return jsonify({"error": str(e)}), 500
