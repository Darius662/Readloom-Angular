#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
API endpoints for serving local cover art files.
"""

import os
from pathlib import Path
from flask import Blueprint, send_file, abort, request, jsonify
from backend.base.logging import LOGGER
from backend.internals.db import execute_query

# Create API blueprint
cover_art_api_bp = Blueprint('api_cover_art', __name__)

# Log that the blueprint was created
LOGGER.info("Cover Art API blueprint created")


@cover_art_api_bp.route('/api/cover-art/<path:filename>')
def serve_cover_art(filename):
    """Serve a cover art file from the local storage.
    
    Args:
        filename: The relative path to the cover file (legacy format)
    """
    try:
        # Construct the full path to the cover file (legacy format)
        from backend.base.helpers import get_data_dir
        data_dir = get_data_dir()
        file_path = data_dir / filename
        
        # Security check: ensure the file is within the cover_art directory
        if not str(file_path).startswith(str(data_dir / "cover_art")):
            LOGGER.warning(f"Attempted access to file outside cover_art directory: {filename}")
            abort(403)
        
        # Check if file exists
        if not file_path.exists():
            LOGGER.warning(f"Cover file not found: {file_path}")
            abort(404)
        
        # Check if file is actually a file (not directory)
        if not file_path.is_file():
            LOGGER.warning(f"Requested path is not a file: {file_path}")
            abort(404)
        
        # Serve the file
        LOGGER.debug(f"Serving cover file: {file_path}")
        return send_file(
            file_path,
            mimetype='image/png',  # Assume PNG, can be made dynamic
            as_attachment=False,
            download_name=file_path.name
        )
        
    except Exception as e:
        LOGGER.error(f"Error serving cover art {filename}: {e}")
        abort(500)


@cover_art_api_bp.route('/api/cover-art/volume/<int:volume_id>')
def serve_volume_cover(volume_id):
    """Serve a cover art file for a specific volume by database ID.
    
    Args:
        volume_id: The ID of the volume in the database
    """
    try:
        # Get volume info from database
        volumes = execute_query(
            "SELECT cover_path FROM volumes WHERE id = ?",
            (volume_id,)
        )
        
        if not volumes:
            LOGGER.warning(f"Volume {volume_id} not found")
            abort(404)
        
        volume = volumes[0]
        cover_path = volume.get('cover_path')
        
        if not cover_path:
            LOGGER.warning(f"No cover path for volume {volume_id}")
            abort(404)
        
        # Handle both absolute and relative paths
        path_obj = Path(cover_path)
        if not path_obj.is_absolute():
            # Legacy format: relative to data directory
            from backend.base.helpers import get_data_dir
            full_path = get_data_dir() / cover_path
        else:
            # New format: absolute path
            full_path = path_obj
        
        # Check if file exists
        if not full_path.exists():
            LOGGER.warning(f"Cover file not found: {full_path}")
            abort(404)
        
        # Check if file is actually a file (not directory)
        if not full_path.is_file():
            LOGGER.warning(f"Requested path is not a file: {full_path}")
            abort(404)
        
        # Serve the file
        LOGGER.debug(f"Serving cover file for volume {volume_id}: {full_path}")
        return send_file(
            full_path,
            mimetype='image/png',  # Assume PNG, can be made dynamic
            as_attachment=False,
            download_name=full_path.name
        )
        
    except Exception as e:
        LOGGER.error(f"Error serving cover art for volume {volume_id}: {e}")
        abort(500)


@cover_art_api_bp.route('/api/cover-art/scan', methods=['POST'])
def scan_for_covers():
    """Scan for manual covers and link them to volumes.
    
    This endpoint runs the manual cover detection and linking system.
    """
    try:
        # Import the manual cover system from backend features folder
        from backend.features.cover_art.manual_cover_system import ManualCoverSystem
        
        # Run the manual cover system
        manual_system = ManualCoverSystem()
        results = manual_system.scan_all_series_for_manual_covers()
        
        return jsonify({
            "success": True,
            "message": "Cover scan completed successfully",
            "results": {
                "series_processed": results.get('series_processed', 0),
                "covers_found": results.get('covers_found', 0),
                "covers_linked": results.get('covers_linked', 0),
                "unlinked_covers": results.get('unlinked_covers', 0)
            }
        })
        
    except Exception as e:
        LOGGER.error(f"Error scanning for covers: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500
