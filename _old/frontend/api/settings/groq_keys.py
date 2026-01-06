#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Groq API key management service.
Handles Groq API key operations.
"""

from backend.internals.settings import Settings
from backend.base.logging import LOGGER


def get_groq_key_status():
    """Get Groq API key status (masked for security).
    
    Returns:
        dict: Key status.
    """
    try:
        settings = Settings().get_settings()
        
        # Check if key exists
        groq_key = getattr(settings, 'groq_api_key', None)
        has_key = bool(groq_key)
        
        # Mask the key for security
        masked_key = None
        if has_key and len(groq_key) > 8:
            masked_key = groq_key[:4] + "*" * (len(groq_key) - 8) + groq_key[-4:]
        
        return {
            "has_key": has_key,
            "masked_key": masked_key
        }, 200
    except Exception as e:
        LOGGER.error(f"Error getting Groq key status: {e}")
        return {"error": str(e)}, 500


def set_groq_key(api_key):
    """Set Groq API key.
    
    Args:
        api_key (str): Groq API key.
        
    Returns:
        dict: Status or error.
    """
    try:
        if not api_key:
            return {"error": "API key is required"}, 400
        
        settings = Settings()
        settings.groq_api_key = api_key
        settings.save_settings()
        
        # Reinitialize AI providers
        try:
            from backend.features.ai_providers import initialize_ai_providers
            initialize_ai_providers()
        except Exception as e:
            LOGGER.warning(f"Could not reinitialize AI providers: {e}")
        
        return {"success": True, "message": "Groq API key set successfully"}, 200
    except Exception as e:
        LOGGER.error(f"Error setting Groq key: {e}")
        return {"error": str(e)}, 500


def delete_groq_key():
    """Delete Groq API key.
    
    Returns:
        dict: Status or error.
    """
    try:
        settings = Settings()
        settings.groq_api_key = None
        settings.save_settings()
        
        # Reinitialize AI providers
        try:
            from backend.features.ai_providers import initialize_ai_providers
            initialize_ai_providers()
        except Exception as e:
            LOGGER.warning(f"Could not reinitialize AI providers: {e}")
        
        return {"success": True, "message": "Groq API key deleted successfully"}, 200
    except Exception as e:
        LOGGER.error(f"Error deleting Groq key: {e}")
        return {"error": str(e)}, 500


def validate_key(api_key):
    """Validate API key format.
    
    Args:
        api_key (str): API key to validate.
        
    Returns:
        bool: True if valid, False otherwise.
    """
    try:
        if not api_key or len(api_key) < 10:
            return False
        return True
    except Exception:
        return False
