#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Migration: Add folder_path column to authors table.

This migration adds the folder_path column to the authors table to store
the path to the author's folder where README.md files are stored.
"""

from backend.base.logging import LOGGER
from backend.internals.db import execute_query


def migrate():
    """Run the migration."""
    try:
        # Check if folder_path column already exists
        result = execute_query("PRAGMA table_info(authors)")
        columns = [row['name'] for row in result]
        
        if 'folder_path' not in columns:
            LOGGER.info("Adding folder_path column to authors table...")
            execute_query("""
                ALTER TABLE authors ADD COLUMN folder_path TEXT
            """, commit=True)
            LOGGER.info("Successfully added folder_path column to authors table")
        else:
            LOGGER.info("folder_path column already exists in authors table")
        
        return True
    
    except Exception as e:
        LOGGER.error(f"Error running migration: {e}")
        import traceback
        LOGGER.error(traceback.format_exc())
        return False


if __name__ == "__main__":
    migrate()
