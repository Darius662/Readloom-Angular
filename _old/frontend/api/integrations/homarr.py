#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Homarr integration service.
Handles Homarr dashboard data and setup.
"""

from backend.features.homarr import (
    get_homarr_data,
    get_homarr_setup_instructions
)
from backend.base.logging import LOGGER


def get_homarr_dashboard_data():
    """Get Homarr dashboard data.
    
    Returns:
        dict: Dashboard data.
    """
    try:
        data = get_homarr_data()
        return data if data else {}, 200
    except Exception as e:
        LOGGER.error(f"Error getting Homarr data: {e}")
        return {"error": str(e)}, 500


def get_homarr_setup_info():
    """Get Homarr setup instructions.
    
    Returns:
        dict: Setup instructions.
    """
    try:
        instructions = get_homarr_setup_instructions()
        return instructions if instructions else {}, 200
    except Exception as e:
        LOGGER.error(f"Error getting Homarr setup instructions: {e}")
        return {"error": str(e)}, 500
