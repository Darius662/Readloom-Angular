#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Volumes API routes.
Defines all volume endpoints.
"""

from flask import Blueprint, jsonify, request
from backend.base.logging import LOGGER

from .crud import create_volume, read_volume, update_volume, delete_volume
from .formats import update_volume_format, update_volume_digital_format

# Create routes blueprint
volumes_routes = Blueprint('volumes_routes', __name__)


@volumes_routes.route('/api/series/<int:series_id>/volumes', methods=['POST'])
def add_volume(series_id):
    """Add a volume to a series."""
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        volume, status = create_volume(series_id, data)
        return jsonify({"volume": volume}), status
    except Exception as e:
        LOGGER.error(f"Error adding volume: {e}")
        return jsonify({"error": str(e)}), 500


@volumes_routes.route('/api/volumes/<int:volume_id>', methods=['PUT'])
def update_volume_detail(volume_id):
    """Update a volume."""
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        volume, status = update_volume(volume_id, data)
        return jsonify(volume), status
    except Exception as e:
        LOGGER.error(f"Error updating volume: {e}")
        return jsonify({"error": str(e)}), 500


@volumes_routes.route('/api/volumes/<int:volume_id>', methods=['DELETE'])
def delete_volume_detail(volume_id):
    """Delete a volume."""
    try:
        result, status = delete_volume(volume_id)
        return jsonify(result), status
    except Exception as e:
        LOGGER.error(f"Error deleting volume: {e}")
        return jsonify({"error": str(e)}), 500


@volumes_routes.route('/api/collection/volume/<int:volume_id>/format', methods=['PUT'])
def update_format(volume_id):
    """Update volume format."""
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        result, status = update_volume_format(volume_id, data)
        return jsonify(result), status
    except Exception as e:
        LOGGER.error(f"Error updating format: {e}")
        return jsonify({"error": str(e)}), 500


@volumes_routes.route('/api/collection/volume/<int:volume_id>/digital-format', methods=['PUT'])
def update_digital_format(volume_id):
    """Update volume digital format."""
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        result, status = update_volume_digital_format(volume_id, data)
        return jsonify(result), status
    except Exception as e:
        LOGGER.error(f"Error updating digital format: {e}")
        return jsonify({"error": str(e)}), 500
