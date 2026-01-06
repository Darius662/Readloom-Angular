#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Home Assistant integration service.
Handles Home Assistant sensor data and setup.
"""

from backend.features.home_assistant import (
    get_home_assistant_sensor_data,
    get_home_assistant_setup_instructions
)
from backend.base.logging import LOGGER


def get_ha_sensor_data():
    """Get Home Assistant sensor data.
    
    Returns:
        dict: Sensor data.
    """
    try:
        data = get_home_assistant_sensor_data()
        return data if data else {}, 200
    except Exception as e:
        LOGGER.error(f"Error getting Home Assistant sensor data: {e}")
        return {"error": str(e)}, 500


def get_ha_setup_instructions():
    """Get Home Assistant setup instructions.
    
    Returns:
        dict: Setup instructions.
    """
    try:
        instructions = get_home_assistant_setup_instructions()
        return instructions if instructions else {}, 200
    except Exception as e:
        LOGGER.error(f"Error getting Home Assistant setup instructions: {e}")
        return {"error": str(e)}, 500
