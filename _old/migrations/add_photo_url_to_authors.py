#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Migration: Add photo_url column to authors table

This migration adds the photo_url column to the authors table for existing databases.
"""

from backend.base.logging import LOGGER
from backend.internals.db import execute_query


def migrate():
    """Add photo_url column to authors table if it doesn't exist."""
    try:
        LOGGER.info("Running migration: add_photo_url_to_authors")
        
        # Check if photo_url column already exists
        result = execute_query("""
            PRAGMA table_info(authors)
        """)
        
        columns = [row['name'] for row in result] if result else []
        
        if 'photo_url' in columns:
            LOGGER.info("photo_url column already exists in authors table")
            return True
        
        # Add photo_url column
        LOGGER.info("Adding photo_url column to authors table...")
        execute_query("""
            ALTER TABLE authors 
            ADD COLUMN photo_url TEXT
        """, commit=True)
        
        LOGGER.info("✓ Successfully added photo_url column to authors table")
        return True
    
    except Exception as e:
        LOGGER.error(f"✗ Error adding photo_url column: {e}")
        import traceback
        LOGGER.error(traceback.format_exc())
        return False


if __name__ == "__main__":
    migrate()
