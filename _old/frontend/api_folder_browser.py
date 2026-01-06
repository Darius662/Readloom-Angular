#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from pathlib import Path
from flask import Blueprint, jsonify, request

from backend.base.logging import LOGGER

# Create folder browser API blueprint
folder_browser_api_bp = Blueprint('folder_browser_api', __name__, url_prefix='/api/folders')


@folder_browser_api_bp.route('/browse', methods=['POST'])
def browse_folders():
    """Browse folders in the filesystem.
    
    Request body:
        {
            "path": "/path/to/browse"  # Optional, defaults to home directory
        }
    
    Returns:
        {
            "success": True,
            "current_path": "/path/to/browse",
            "parent_path": "/path/to",
            "folders": [
                {"name": "folder1", "path": "/path/to/browse/folder1"},
                {"name": "folder2", "path": "/path/to/browse/folder2"}
            ],
            "drives": ["C:", "D:", ...],  # Windows only
            "can_go_up": True,  # Whether parent directory is accessible
            "is_root": False  # Whether current path is filesystem root
        }
    """
    try:
        data = request.json or {}
        current_path = data.get('path') or str(Path.home())
        
        # Normalize the path
        try:
            current_path = str(Path(current_path).resolve())
        except Exception as e:
            LOGGER.error(f"Invalid path: {current_path}: {e}")
            return jsonify({
                "success": False,
                "error": f"Invalid path: {current_path}"
            }), 400
        
        # Check if path exists
        if not os.path.exists(current_path):
            return jsonify({
                "success": False,
                "error": f"Path does not exist: {current_path}"
            }), 400
        
        # Check if it's a directory
        if not os.path.isdir(current_path):
            return jsonify({
                "success": False,
                "error": f"Path is not a directory: {current_path}"
            }), 400
        
        # Determine if we're at filesystem root
        is_root = False
        if os.name == 'nt':  # Windows
            # On Windows, root is like "C:\" or "D:\"
            is_root = len(current_path) == 3 and current_path[1:] == ':\\'
        else:  # Unix/Linux/Mac
            # On Unix systems, root is "/"
            is_root = current_path == '/'
        
        # Get parent path (but don't go above filesystem root)
        parent_path = str(Path(current_path).parent)
        # can_go_up is False only when we're at the filesystem root
        can_go_up = not is_root
        
        # List folders in current directory
        folders = []
        try:
            for item in os.listdir(current_path):
                item_path = os.path.join(current_path, item)
                try:
                    if os.path.isdir(item_path):
                        folders.append({
                            "name": item,
                            "path": item_path
                        })
                except (PermissionError, OSError):
                    # Skip folders we can't access
                    pass
        except PermissionError:
            LOGGER.warning(f"Permission denied reading directory: {current_path}")
            return jsonify({
                "success": False,
                "error": f"Permission denied: Cannot read directory {current_path}"
            }), 403
        
        # Sort folders alphabetically
        folders.sort(key=lambda x: x['name'].lower())
        
        # Get available drives on Windows
        drives = []
        if os.name == 'nt':  # Windows
            import string
            for drive in string.ascii_uppercase:
                drive_path = f"{drive}:\\"
                if os.path.exists(drive_path):
                    drives.append(drive_path)
        else:  # Unix/Linux/Mac - add root option
            drives = ['/']
        
        return jsonify({
            "success": True,
            "current_path": current_path,
            "parent_path": parent_path,
            "folders": folders,
            "drives": drives,
            "can_go_up": can_go_up,
            "is_root": is_root,
            "is_home": current_path == str(Path.home())
        })
    
    except Exception as e:
        LOGGER.error(f"Error browsing folders: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@folder_browser_api_bp.route('/validate', methods=['POST'])
def validate_folder():
    """Validate if a folder path exists and is readable.
    
    Request body:
        {
            "path": "/path/to/validate"
        }
    
    Returns:
        {
            "success": True,
            "path": "/path/to/validate",
            "exists": True,
            "is_directory": True,
            "is_readable": True,
            "is_writable": True
        }
    """
    try:
        data = request.json or {}
        path = data.get('path')
        
        if not path:
            return jsonify({
                "success": False,
                "error": "Path is required"
            }), 400
        
        # Normalize the path
        try:
            path = str(Path(path).resolve())
        except Exception as e:
            LOGGER.error(f"Invalid path: {path}: {e}")
            return jsonify({
                "success": False,
                "error": f"Invalid path: {path}"
            }), 400
        
        exists = os.path.exists(path)
        is_directory = os.path.isdir(path) if exists else False
        is_readable = os.access(path, os.R_OK) if exists else False
        is_writable = os.access(path, os.W_OK) if exists else False
        
        return jsonify({
            "success": True,
            "path": path,
            "exists": exists,
            "is_directory": is_directory,
            "is_readable": is_readable,
            "is_writable": is_writable
        })
    
    except Exception as e:
        LOGGER.error(f"Error validating folder: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500
