#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Migration to add in_library and want_to_read flags to series table.
Sets in_library=1 for all series that are in collections.
"""

from backend.base.logging import LOGGER
from backend.internals.db import execute_query


def migrate():
    """Add in_library and want_to_read flags to series table."""
    LOGGER.info("Adding in_library and want_to_read flags to series table...")
    
    try:
        # Check existing columns
        column_check = execute_query("PRAGMA table_info(series)")
        column_names = [col['name'] for col in column_check]
        
        # Add in_library column if missing
        if 'in_library' not in column_names:
            try:
                execute_query("ALTER TABLE series ADD COLUMN in_library INTEGER DEFAULT 0", commit=True)
                LOGGER.info("Added in_library column to series table")
            except Exception as e:
                if 'duplicate column name' in str(e).lower():
                    LOGGER.info("in_library column already exists; skipping add")
                else:
                    raise
        
        # Add want_to_read column if missing
        if 'want_to_read' not in column_names:
            try:
                execute_query("ALTER TABLE series ADD COLUMN want_to_read INTEGER DEFAULT 0", commit=True)
                LOGGER.info("Added want_to_read column to series table")
            except Exception as e:
                if 'duplicate column name' in str(e).lower():
                    LOGGER.info("want_to_read column already exists; skipping add")
                else:
                    raise
        
        # Set in_library=1 for all series that are in collections
        try:
            execute_query("""
                UPDATE series SET in_library = 1 
                WHERE id IN (
                    SELECT DISTINCT series_id FROM series_collections
                )
            """, commit=True)
            LOGGER.info("Set in_library=1 for all series in collections")
        except Exception as e:
            LOGGER.warning(f"Could not update in_library flags: {e}")
        
        LOGGER.info("Library flags added successfully to series table")
        return True
    except Exception as e:
        LOGGER.error(f"Error adding library flags: {e}")
        import traceback
        LOGGER.error(traceback.format_exc())
        return False
