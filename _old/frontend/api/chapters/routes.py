#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Chapters API routes.
Defines all chapter endpoints.
"""

from flask import Blueprint, jsonify, request
from backend.base.logging import LOGGER

from .crud import create_chapter, read_chapter, update_chapter, delete_chapter

# Create routes blueprint
chapters_routes = Blueprint('chapters_routes', __name__)


@chapters_routes.route('/api/series/<int:series_id>/chapters', methods=['POST'])
def add_chapter(series_id):
    """Add a chapter to a series."""
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        chapter, status = create_chapter(series_id, data)
        return jsonify({"chapter": chapter}), status
    except Exception as e:
        LOGGER.error(f"Error adding chapter: {e}")
        return jsonify({"error": str(e)}), 500


@chapters_routes.route('/api/chapters/<int:chapter_id>', methods=['PUT'])
def update_chapter_detail(chapter_id):
    """Update a chapter."""
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        chapter, status = update_chapter(chapter_id, data)
        return jsonify(chapter), status
    except Exception as e:
        LOGGER.error(f"Error updating chapter: {e}")
        return jsonify({"error": str(e)}), 500


@chapters_routes.route('/api/chapters/<int:chapter_id>', methods=['DELETE'])
def delete_chapter_detail(chapter_id):
    """Delete a chapter."""
    try:
        result, status = delete_chapter(chapter_id)
        return jsonify(result), status
    except Exception as e:
        LOGGER.error(f"Error deleting chapter: {e}")
        return jsonify({"error": str(e)}), 500
