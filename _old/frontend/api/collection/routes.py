#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Collection API routes.
Defines all collection endpoints.
"""

from flask import Blueprint, jsonify, request
from backend.base.logging import LOGGER
from frontend.middleware import root_folders_required

from .items import get_items, add_item, remove_item, update_item
from .stats import get_stats
from .formats import update_item_format, update_item_digital_format

# Create routes blueprint
collection_routes = Blueprint('collection_routes', __name__)


@collection_routes.route('/api/collection', methods=['GET'])
def get_collection():
    """Get collection items."""
    try:
        filters = {}
        if request.args.get('item_type'):
            filters['item_type'] = request.args.get('item_type')
        if request.args.get('ownership_status'):
            filters['ownership_status'] = request.args.get('ownership_status')
        
        items, status = get_items(filters)
        return jsonify({"items": items}), status
    except Exception as e:
        LOGGER.error(f"Error getting collection: {e}")
        return jsonify({"error": str(e)}), 500


@collection_routes.route('/api/collection/stats', methods=['GET'])
def get_collection_stats():
    """Get collection statistics."""
    try:
        stats, status = get_stats()
        return jsonify(stats), status
    except Exception as e:
        LOGGER.error(f"Error getting collection stats: {e}")
        return jsonify({"error": str(e)}), 500


@collection_routes.route('/api/collection', methods=['POST'])
@root_folders_required
def add_to_collection_endpoint():
    """Add item to collection."""
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        result, status = add_item(data)
        return jsonify(result), status
    except Exception as e:
        LOGGER.error(f"Error adding to collection: {e}")
        return jsonify({"error": str(e)}), 500


@collection_routes.route('/api/collection/<int:item_id>', methods=['PUT'])
def update_collection_item_endpoint(item_id):
    """Update collection item."""
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        result, status = update_item(item_id, data)
        return jsonify(result), status
    except Exception as e:
        LOGGER.error(f"Error updating collection item: {e}")
        return jsonify({"error": str(e)}), 500


@collection_routes.route('/api/collection/<int:item_id>', methods=['DELETE'])
def remove_from_collection_endpoint(item_id):
    """Remove item from collection."""
    try:
        result, status = remove_item(item_id)
        return jsonify(result), status
    except Exception as e:
        LOGGER.error(f"Error removing from collection: {e}")
        return jsonify({"error": str(e)}), 500


@collection_routes.route('/api/collection/item/<int:item_id>/format', methods=['PUT'])
def update_format(item_id):
    """Update collection item format."""
    try:
        data = request.json
        if not data or "format" not in data:
            return jsonify({"error": "Format is required"}), 400
        
        result, status = update_item_format(item_id, data["format"])
        return jsonify(result), status
    except Exception as e:
        LOGGER.error(f"Error updating format: {e}")
        return jsonify({"error": str(e)}), 500


@collection_routes.route('/api/collection/item/<int:item_id>/digital-format', methods=['PUT'])
def update_digital_format(item_id):
    """Update collection item digital format."""
    try:
        data = request.json
        if not data or "digital_format" not in data:
            return jsonify({"error": "Digital format is required"}), 400
        
        result, status = update_item_digital_format(item_id, data["digital_format"])
        return jsonify(result), status
    except Exception as e:
        LOGGER.error(f"Error updating digital format: {e}")
        return jsonify({"error": str(e)}), 500
