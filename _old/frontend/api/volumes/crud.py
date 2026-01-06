#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Volumes CRUD service.
Handles volume operations.
"""

from backend.internals.db import execute_query
from backend.base.logging import LOGGER


def create_volume(series_id, data):
    """Create a volume.
    
    Args:
        series_id (int): Series ID.
        data (dict): Volume data.
        
    Returns:
        dict: Created volume or error.
    """
    try:
        volume_id = execute_query("""
            INSERT INTO volumes (series_id, volume_number, title, description, release_date, status)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            series_id,
            data.get("volume_number"),
            data.get("title"),
            data.get("description"),
            data.get("release_date"),
            data.get("status", "UNKNOWN")
        ), commit=True)
        
        volume = execute_query("SELECT * FROM volumes WHERE id = ?", (volume_id,))
        return volume[0] if volume else {"error": "Failed to retrieve created volume"}, 201
    except Exception as e:
        LOGGER.error(f"Error creating volume: {e}")
        return {"error": str(e)}, 500


def read_volume(volume_id):
    """Read a volume.
    
    Args:
        volume_id (int): Volume ID.
        
    Returns:
        dict: Volume data or error.
    """
    try:
        volume = execute_query("SELECT * FROM volumes WHERE id = ?", (volume_id,))
        if not volume:
            return {"error": "Volume not found"}, 404
        return volume[0], 200
    except Exception as e:
        LOGGER.error(f"Error reading volume: {e}")
        return {"error": str(e)}, 500


def update_volume(volume_id, data):
    """Update a volume.
    
    Args:
        volume_id (int): Volume ID.
        data (dict): Update data.
        
    Returns:
        dict: Updated volume or error.
    """
    try:
        # Check if volume exists
        volume = execute_query("SELECT id FROM volumes WHERE id = ?", (volume_id,))
        if not volume:
            return {"error": "Volume not found"}, 404
        
        # Build update query
        update_fields = []
        params = []
        
        for field in ["volume_number", "title", "description", "release_date", "status"]:
            if field in data:
                update_fields.append(f"{field} = ?")
                params.append(data[field])
        
        if not update_fields:
            return {"error": "No fields to update"}, 400
        
        params.append(volume_id)
        
        execute_query(f"""
            UPDATE volumes
            SET {", ".join(update_fields)}
            WHERE id = ?
        """, tuple(params), commit=True)
        
        updated = execute_query("SELECT * FROM volumes WHERE id = ?", (volume_id,))
        return updated[0] if updated else {"error": "Failed to retrieve updated volume"}, 200
    except Exception as e:
        LOGGER.error(f"Error updating volume: {e}")
        return {"error": str(e)}, 500


def delete_volume(volume_id):
    """Delete a volume.
    
    Args:
        volume_id (int): Volume ID.
        
    Returns:
        dict: Status or error.
    """
    try:
        # Check if volume exists
        volume = execute_query("SELECT id FROM volumes WHERE id = ?", (volume_id,))
        if not volume:
            return {"error": "Volume not found"}, 404
        
        execute_query("DELETE FROM volumes WHERE id = ?", (volume_id,), commit=True)
        return {"success": True, "message": "Volume deleted successfully"}, 200
    except Exception as e:
        LOGGER.error(f"Error deleting volume: {e}")
        return {"error": str(e)}, 500
