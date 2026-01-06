#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Collection items service.
Handles collection item operations.
"""

from backend.features.collection import (
    add_to_collection,
    remove_from_collection,
    update_collection_item,
    get_collection_items
)
from backend.base.logging import LOGGER


def get_items(filters=None):
    """Get collection items.
    
    Args:
        filters (dict, optional): Filter options.
        
    Returns:
        list: Collection items.
    """
    try:
        if filters is None:
            filters = {}
        
        # Extract individual filter parameters from the dictionary
        items = get_collection_items(
            series_id=filters.get('series_id'),
            item_type=filters.get('item_type'),
            ownership_status=filters.get('ownership_status'),
            read_status=filters.get('read_status'),
            format=filters.get('format')
        )
        return items if items else [], 200
    except Exception as e:
        LOGGER.error(f"Error getting collection items: {e}")
        return {"error": str(e)}, 500


def add_item(data):
    """Add item to collection.
    
    Args:
        data (dict): Item data.
        
    Returns:
        dict: Result or error.
    """
    try:
        if not data.get("collection_id") or not data.get("item_id"):
            return {"error": "Collection ID and item ID are required"}, 400
        
        result = add_to_collection(
            data["collection_id"],
            data["item_id"],
            data.get("item_type", "VOLUME")
        )
        
        return {"success": True, "result": result}, 201
    except Exception as e:
        LOGGER.error(f"Error adding item to collection: {e}")
        return {"error": str(e)}, 500


def remove_item(item_id):
    """Remove item from collection.
    
    Args:
        item_id (int): Item ID.
        
    Returns:
        dict: Result or error.
    """
    try:
        result = remove_from_collection(item_id)
        return {"success": True, "result": result}, 200
    except Exception as e:
        LOGGER.error(f"Error removing item from collection: {e}")
        return {"error": str(e)}, 500


def update_item(item_id, data):
    """Update collection item.
    
    Args:
        item_id (int): Item ID.
        data (dict): Update data.
        
    Returns:
        dict: Result or error.
    """
    try:
        result = update_collection_item(item_id, data)
        return {"success": True, "result": result}, 200
    except Exception as e:
        LOGGER.error(f"Error updating collection item: {e}")
        return {"error": str(e)}, 500
