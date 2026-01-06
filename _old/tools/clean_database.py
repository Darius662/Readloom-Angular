#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script to clean the database - remove all manga, books, and authors.
"""

import sys
sys.path.insert(0, 'c:\\Users\\dariu\\Documents\\GitHub\\Readloom')

from backend.internals.db import execute_query
from backend.base.logging import LOGGER

def clean_database():
    """Clean all entries from the database."""
    try:
        LOGGER.info("Starting database cleanup...")
        
        # Get all table names
        tables = execute_query("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name NOT LIKE 'sqlite_%'
        """)
        
        table_names = [t['name'] for t in tables]
        LOGGER.info(f"Found tables: {table_names}")
        
        # Tables to clean (in order to respect foreign keys)
        tables_to_clean = [
            'ebook_files',
            'volumes',
            'author_books',
            'series_collections',
            'series',
            'authors',
            'collections',
            'root_folders',
            'settings'
        ]
        
        for table in tables_to_clean:
            if table in table_names:
                try:
                    execute_query(f"DELETE FROM {table}", commit=True)
                    LOGGER.info(f"✓ Cleaned table: {table}")
                except Exception as e:
                    LOGGER.warning(f"Could not clean table {table}: {e}")
        
        LOGGER.info("✓ Database cleanup complete!")
        print("\n✓ Database cleanup complete!")
        print("All manga, books, authors, and collections have been removed.")
        print("You can now start fresh.\n")
        
    except Exception as e:
        LOGGER.error(f"Error cleaning database: {e}")
        print(f"\n✗ Error cleaning database: {e}\n")
        return False
    
    return True

if __name__ == "__main__":
    clean_database()
