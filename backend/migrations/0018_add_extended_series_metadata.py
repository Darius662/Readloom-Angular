#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Migration to add extended metadata columns to series table.
Adds: isbn, published_date, subjects
"""

from backend.base.logging import LOGGER
from backend.internals.db import execute_query


def migrate():
    """Add extended metadata columns to series table."""
    LOGGER.info("Adding extended metadata columns to series table...")
    
    try:
        # Check existing columns
        column_check = execute_query("PRAGMA table_info(series)")
        column_names = [col['name'] for col in column_check]
        
        # Add isbn column if missing
        if 'isbn' not in column_names:
            try:
                execute_query("ALTER TABLE series ADD COLUMN isbn TEXT", commit=True)
                LOGGER.info("Added isbn column to series table")
            except Exception as e:
                if 'duplicate column name' in str(e).lower():
                    LOGGER.info("isbn column already exists; skipping add")
                else:
                    raise
        
        # Add published_date column if missing
        if 'published_date' not in column_names:
            try:
                execute_query("ALTER TABLE series ADD COLUMN published_date TEXT", commit=True)
                LOGGER.info("Added published_date column to series table")
            except Exception as e:
                if 'duplicate column name' in str(e).lower():
                    LOGGER.info("published_date column already exists; skipping add")
                else:
                    raise
        
        # Add subjects column if missing
        if 'subjects' not in column_names:
            try:
                execute_query("ALTER TABLE series ADD COLUMN subjects TEXT", commit=True)
                LOGGER.info("Added subjects column to series table")
            except Exception as e:
                if 'duplicate column name' in str(e).lower():
                    LOGGER.info("subjects column already exists; skipping add")
                else:
                    raise
        
        LOGGER.info("Extended metadata columns added successfully to series table")
    except Exception as e:
        LOGGER.error(f"Error adding extended metadata columns: {e}")
        raise


if __name__ == "__main__":
    migrate()
