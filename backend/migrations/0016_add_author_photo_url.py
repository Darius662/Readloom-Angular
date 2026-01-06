#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Migration 0016: Add photo_url column to authors table.
"""

from backend.base.logging import LOGGER
from backend.internals.db import execute_query


def migrate():
    """Add photo_url column to authors table if it doesn't exist."""
    try:
        LOGGER.info("Running migration 0016: Add photo_url column to authors table")
        
        # Check if column already exists
        columns = execute_query("PRAGMA table_info(authors)")
        column_names = [col['name'] for col in columns]
        
        if 'photo_url' in column_names:
            LOGGER.info("photo_url column already exists in authors table")
            return
        
        # Add photo_url column
        execute_query("""
            ALTER TABLE authors 
            ADD COLUMN photo_url TEXT
        """, commit=True)
        
        LOGGER.info("Successfully added photo_url column to authors table")
    
    except Exception as e:
        LOGGER.error(f"Error in migration 0016: {e}")
        raise
