#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Collection statistics service.
Handles collection statistics and calculations.
"""

from backend.features.collection import get_collection_stats
from backend.base.logging import LOGGER


def get_stats():
    """Get collection statistics.
    
    Returns:
        dict: Collection statistics.
    """
    try:
        stats = get_collection_stats()
        return stats if stats else {}, 200
    except Exception as e:
        LOGGER.error(f"Error getting collection stats: {e}")
        return {"error": str(e)}, 500


def calculate_total_value(items):
    """Calculate total collection value.
    
    Args:
        items (list): Collection items.
        
    Returns:
        float: Total value.
    """
    try:
        total = 0
        for item in items:
            if item.get("purchase_price"):
                total += float(item["purchase_price"])
        return total
    except Exception as e:
        LOGGER.error(f"Error calculating total value: {e}")
        return 0


def calculate_progress(stats):
    """Calculate collection progress.
    
    Args:
        stats (dict): Collection statistics.
        
    Returns:
        dict: Progress data.
    """
    try:
        total_volumes = stats.get("total_volumes", 0)
        owned_volumes = stats.get("owned_volumes", 0)
        read_volumes = stats.get("read_volumes", 0)
        
        progress = {
            "ownership_percent": (owned_volumes / total_volumes * 100) if total_volumes > 0 else 0,
            "read_percent": (read_volumes / total_volumes * 100) if total_volumes > 0 else 0,
            "total_volumes": total_volumes,
            "owned_volumes": owned_volumes,
            "read_volumes": read_volumes
        }
        
        return progress
    except Exception as e:
        LOGGER.error(f"Error calculating progress: {e}")
        return {}
