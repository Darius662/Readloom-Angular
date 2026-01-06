#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Series move service.
Handles moving series between collections and root folders.
"""

from backend.features.move_service import plan_series_move, move_series_db_only
from backend.base.logging import LOGGER


def plan_series_move_operation(series_id, target_collection_id=None, target_root_folder_id=None):
    """Plan a series move operation.
    
    Args:
        series_id (int): Series ID.
        target_collection_id (int, optional): Target collection ID.
        target_root_folder_id (int, optional): Target root folder ID.
        
    Returns:
        dict: Move plan or error.
    """
    try:
        plan = plan_series_move(series_id, target_collection_id, target_root_folder_id)
        return plan, 200
    except Exception as e:
        LOGGER.error(f"Error planning series move: {e}")
        return {"error": str(e)}, 500


def execute_series_move(series_id, target_collection_id=None, target_root_folder_id=None):
    """Execute a series move operation.
    
    Args:
        series_id (int): Series ID.
        target_collection_id (int, optional): Target collection ID.
        target_root_folder_id (int, optional): Target root folder ID.
        
    Returns:
        dict: Move result or error.
    """
    try:
        result = move_series_db_only(series_id, target_collection_id, target_root_folder_id)
        return result, 200
    except Exception as e:
        LOGGER.error(f"Error executing series move: {e}")
        return {"error": str(e)}, 500


def validate_move_request(series_id, target_collection_id=None, target_root_folder_id=None):
    """Validate a series move request.
    
    Args:
        series_id (int): Series ID.
        target_collection_id (int, optional): Target collection ID.
        target_root_folder_id (int, optional): Target root folder ID.
        
    Returns:
        tuple: (is_valid, error_message)
    """
    try:
        if not series_id:
            return False, "Series ID is required"
        
        if not target_collection_id and not target_root_folder_id:
            return False, "Target collection ID or root folder ID is required"
        
        return True, None
    except Exception as e:
        LOGGER.error(f"Error validating move request: {e}")
        return False, str(e)
