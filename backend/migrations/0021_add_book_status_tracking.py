#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Migration to add book status tracking columns to series table.
Adds: user_description, star_rating, reading_progress
"""

from backend.base.logging import LOGGER
from backend.internals.db import execute_query


def migrate():
    """Add book status tracking columns to series table."""
    LOGGER.info("Adding book status tracking columns to series table...")
    
    try:
        # Check existing columns
        column_check = execute_query("PRAGMA table_info(series)")
        column_names = [col['name'] for col in column_check]
        
        # Add user_description column if missing
        if 'user_description' not in column_names:
            try:
                execute_query("ALTER TABLE series ADD COLUMN user_description TEXT", commit=True)
                LOGGER.info("Added user_description column to series table")
            except Exception as e:
                if 'duplicate column name' in str(e).lower():
                    LOGGER.info("user_description column already exists; skipping add")
                else:
                    raise
        
        # Add star_rating column if missing
        if 'star_rating' not in column_names:
            try:
                execute_query("ALTER TABLE series ADD COLUMN star_rating REAL DEFAULT 0", commit=True)
                LOGGER.info("Added star_rating column to series table")
            except Exception as e:
                if 'duplicate column name' in str(e).lower():
                    LOGGER.info("star_rating column already exists; skipping add")
                else:
                    raise
        
        # Add reading_progress column if missing (0, 25, 50, 75, 100)
        if 'reading_progress' not in column_names:
            try:
                execute_query("ALTER TABLE series ADD COLUMN reading_progress INTEGER DEFAULT 0", commit=True)
                LOGGER.info("Added reading_progress column to series table")
            except Exception as e:
                if 'duplicate column name' in str(e).lower():
                    LOGGER.info("reading_progress column already exists; skipping add")
                else:
                    raise
        
        LOGGER.info("Book status tracking columns added successfully to series table")
        return True
    except Exception as e:
        LOGGER.error(f"Error adding book status tracking columns: {e}")
        import traceback
        LOGGER.error(traceback.format_exc())
        return False
