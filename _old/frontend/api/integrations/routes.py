#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Integrations API routes.
Defines all integration endpoints.
"""

from flask import Blueprint, jsonify
from backend.base.logging import LOGGER

from flask import request
from .home_assistant import get_ha_sensor_data, get_ha_setup_instructions
from .homarr import get_homarr_dashboard_data, get_homarr_setup_info
from .kavita import get_kavita_settings, save_kavita_settings, test_kavita_connection, get_kavita_libraries

# Create routes blueprint
integrations_routes = Blueprint('integrations_routes', __name__)


@integrations_routes.route('/api/integrations/home-assistant', methods=['GET'])
def get_home_assistant_data():
    """Get Home Assistant integration data."""
    try:
        data, status = get_ha_sensor_data()
        return jsonify(data), status
    except Exception as e:
        LOGGER.error(f"Error getting Home Assistant data: {e}")
        return jsonify({"error": str(e)}), 500


@integrations_routes.route('/api/integrations/home-assistant/setup', methods=['GET'])
def get_home_assistant_setup():
    """Get Home Assistant setup instructions."""
    try:
        instructions, status = get_ha_setup_instructions()
        return jsonify(instructions), status
    except Exception as e:
        LOGGER.error(f"Error getting Home Assistant setup: {e}")
        return jsonify({"error": str(e)}), 500


@integrations_routes.route('/api/integrations/homarr', methods=['GET'])
def get_homarr_data_endpoint():
    """Get Homarr integration data."""
    try:
        data, status = get_homarr_dashboard_data()
        return jsonify(data), status
    except Exception as e:
        LOGGER.error(f"Error getting Homarr data: {e}")
        return jsonify({"error": str(e)}), 500


@integrations_routes.route('/api/integrations/homarr/setup', methods=['GET'])
def get_homarr_setup_endpoint():
    """Get Homarr setup instructions."""
    try:
        instructions, status = get_homarr_setup_info()
        return jsonify(instructions), status
    except Exception as e:
        LOGGER.error(f"Error getting Homarr setup: {e}")
        return jsonify({"error": str(e)}), 500


@integrations_routes.route('/api/integrations/kavita/settings', methods=['GET'])
def get_kavita_settings_endpoint():
    """Get Kavita integration settings."""
    try:
        settings = get_kavita_settings()
        if settings:
            # Don't return password in response for security
            settings.pop('password', None)
            return jsonify({"success": True, "settings": settings}), 200
        else:
            return jsonify({"success": True, "settings": None}), 200
    except Exception as e:
        LOGGER.error(f"Error getting Kavita settings: {e}")
        return jsonify({"error": str(e)}), 500


@integrations_routes.route('/api/integrations/kavita/settings', methods=['POST'])
def save_kavita_settings_endpoint():
    """Save Kavita integration settings."""
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        url = data.get('url')
        username = data.get('username')
        password = data.get('password')
        enabled = data.get('enabled', True)
        
        if not url or not username or not password:
            return jsonify({"error": "URL, username, and password are required"}), 400
        
        if save_kavita_settings(url, username, password, enabled):
            return jsonify({"success": True, "message": "Settings saved successfully"}), 200
        else:
            return jsonify({"error": "Failed to save settings"}), 500
    except Exception as e:
        LOGGER.error(f"Error saving Kavita settings: {e}")
        return jsonify({"error": str(e)}), 500


@integrations_routes.route('/api/integrations/kavita/test', methods=['POST'])
def test_kavita_connection_endpoint():
    """Test Kavita server connection."""
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        url = data.get('url')
        username = data.get('username')
        password = data.get('password')
        
        if not url or not username or not password:
            return jsonify({"error": "URL, username, and password are required"}), 400
        
        success, message = test_kavita_connection(url, username, password)
        
        if success:
            return jsonify({"success": True, "message": message}), 200
        else:
            return jsonify({"success": False, "error": message}), 400
    except Exception as e:
        LOGGER.error(f"Error testing Kavita connection: {e}")
        return jsonify({"error": str(e)}), 500


@integrations_routes.route('/api/integrations/kavita/libraries', methods=['GET'])
def get_kavita_libraries_endpoint():
    """Get Kavita libraries."""
    try:
        settings = get_kavita_settings()
        if not settings:
            return jsonify({"error": "Kavita not configured"}), 400
        
        libraries, error = get_kavita_libraries(
            settings['url'],
            settings['username'],
            settings['password']
        )
        
        if error:
            return jsonify({"error": error}), 400
        
        return jsonify({"success": True, "libraries": libraries}), 200
    except Exception as e:
        LOGGER.error(f"Error getting Kavita libraries: {e}")
        return jsonify({"error": str(e)}), 500
