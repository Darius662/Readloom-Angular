#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Migration: Fix author_books table naming.

This migration ensures the correct author_books table exists and removes
any conflicting book_authors table from older migrations.
"""

from backend.base.logging import LOGGER
from backend.internals.db import execute_query


def migrate():
    """Run the migration."""
    try:
        # Check if book_authors table exists (from old migration)
        tables = execute_query("SELECT name FROM sqlite_master WHERE type='table' AND name='book_authors'")
        
        if tables:
            LOGGER.info("Found old book_authors table, removing it...")
            try:
                execute_query("DROP TABLE IF EXISTS book_authors", commit=True)
                LOGGER.info("Dropped book_authors table")
            except Exception as e:
                LOGGER.warning(f"Could not drop book_authors table: {e}")
        
        # Ensure author_books table exists with correct schema
        result = execute_query("SELECT name FROM sqlite_master WHERE type='table' AND name='author_books'")
        
        if not result:
            LOGGER.info("Creating author_books table...")
            execute_query("""
                CREATE TABLE author_books (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    author_id INTEGER NOT NULL,
                    series_id INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (author_id) REFERENCES authors (id) ON DELETE CASCADE,
                    FOREIGN KEY (series_id) REFERENCES series (id) ON DELETE CASCADE
                )
            """, commit=True)
            LOGGER.info("Created author_books table")
        else:
            LOGGER.info("author_books table already exists")
        
        return True
    
    except Exception as e:
        LOGGER.error(f"Error running migration: {e}")
        import traceback
        LOGGER.error(traceback.format_exc())
        return False


if __name__ == "__main__":
    migrate()
