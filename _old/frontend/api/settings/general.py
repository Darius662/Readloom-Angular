#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
General settings service.
Handles application settings retrieval and updates.
"""

from backend.internals.settings import Settings
from backend.base.logging import LOGGER


def get_all_settings():
    """Get all settings.
    
    Returns:
        dict: Settings data.
    """
    try:
        settings = Settings().get_settings()
        # Convert NamedTuple to dict using _asdict() method
        return settings._asdict() if settings else {}, 200
    except Exception as e:
        LOGGER.error(f"Error getting settings: {e}")
        return {"error": str(e)}, 500


def update_settings(data):
    """Update settings.
    
    Args:
        data (dict): Settings data to update.
        
    Returns:
        dict: Updated settings or error.
    """
    try:
        settings = Settings()
        
        # Update settings
        for key, value in data.items():
            if hasattr(settings, key):
                setattr(settings, key, value)
        
        # Save settings
        settings.save_settings()
        
        return {"success": True, "message": "Settings updated successfully"}, 200
    except Exception as e:
        LOGGER.error(f"Error updating settings: {e}")
        return {"error": str(e)}, 500


def validate_settings(data):
    """Validate settings data.
    
    Args:
        data (dict): Settings data to validate.
        
    Returns:
        tuple: (is_valid, error_message)
    """
    try:
        if not isinstance(data, dict):
            return False, "Settings must be a dictionary"
        
        return True, None
    except Exception as e:
        LOGGER.error(f"Error validating settings: {e}")
        return False, str(e)
