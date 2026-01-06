#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Settings API routes.
Defines all settings endpoints.
"""

from flask import Blueprint, jsonify, request
from backend.base.logging import LOGGER

from .general import get_all_settings, update_settings, validate_settings
from .groq_keys import get_groq_key_status, set_groq_key, delete_groq_key, validate_key

# Create routes blueprint
settings_routes = Blueprint('settings_routes', __name__)


@settings_routes.route('/api/settings', methods=['GET'])
def get_settings():
    """Get all settings."""
    try:
        settings, status = get_all_settings()
        return jsonify(settings), status
    except Exception as e:
        LOGGER.error(f"Error getting settings: {e}")
        return jsonify({"error": str(e)}), 500


@settings_routes.route('/api/settings', methods=['PUT'])
def update_settings_endpoint():
    """Update settings."""
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        # Validate settings
        is_valid, error = validate_settings(data)
        if not is_valid:
            return jsonify({"error": error}), 400
        
        result, status = update_settings(data)
        return jsonify(result), status
    except Exception as e:
        LOGGER.error(f"Error updating settings: {e}")
        return jsonify({"error": str(e)}), 500


@settings_routes.route('/api/settings/groq-api-key', methods=['GET'])
def get_groq_key():
    """Get Groq API key status."""
    try:
        status_data, status = get_groq_key_status()
        return jsonify(status_data), status
    except Exception as e:
        LOGGER.error(f"Error getting Groq key status: {e}")
        return jsonify({"error": str(e)}), 500


@settings_routes.route('/api/settings/groq-api-key', methods=['PUT'])
def set_groq_key_endpoint():
    """Set Groq API key."""
    try:
        data = request.json
        if not data or "api_key" not in data:
            return jsonify({"error": "API key is required"}), 400
        
        api_key = data["api_key"]
        
        # Validate key
        if not validate_key(api_key):
            return jsonify({"error": "Invalid API key format"}), 400
        
        result, status = set_groq_key(api_key)
        return jsonify(result), status
    except Exception as e:
        LOGGER.error(f"Error setting Groq key: {e}")
        return jsonify({"error": str(e)}), 500


@settings_routes.route('/api/settings/groq-api-key', methods=['DELETE'])
def delete_groq_key_endpoint():
    """Delete Groq API key."""
    try:
        result, status = delete_groq_key()
        return jsonify(result), status
    except Exception as e:
        LOGGER.error(f"Error deleting Groq key: {e}")
        return jsonify({"error": str(e)}), 500
