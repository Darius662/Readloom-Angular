#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Schema setup for collections and their relationships with root folders.
"""

from backend.base.logging import LOGGER
from backend.internals.db import execute_query


def setup_collections_tables():
    """Set up the collections tables if they don't exist."""
    try:
        # Drop problematic indexes first (before creating table)
        try:
            execute_query("DROP INDEX IF EXISTS idx_unique_default", commit=True)
            LOGGER.info("Dropped problematic idx_unique_default index")
        except Exception as e:
            LOGGER.debug(f"Could not drop idx_unique_default: {e}")
        
        try:
            execute_query("DROP INDEX IF EXISTS idx_unique_default_per_type", commit=True)
            LOGGER.debug("Dropped old idx_unique_default_per_type index")
        except Exception as e:
            LOGGER.debug(f"Could not drop idx_unique_default_per_type: {e}")
        
        # Create collections table
        execute_query("""
        CREATE TABLE IF NOT EXISTS collections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            content_type TEXT DEFAULT 'MANGA',
            is_default INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            CHECK (is_default IN (0, 1))
        )
        """, commit=True)
        
        # Create a trigger to enforce only one default per content_type
        # This is more flexible than a unique index
        try:
            execute_query("""
            CREATE TRIGGER IF NOT EXISTS trg_enforce_single_default_per_type
            BEFORE INSERT ON collections
            FOR EACH ROW
            WHEN NEW.is_default = 1
            BEGIN
                UPDATE collections SET is_default = 0 
                WHERE id != NEW.id AND COALESCE(content_type, 'MANGA') = COALESCE(NEW.content_type, 'MANGA');
            END
            """, commit=True)
            LOGGER.debug("Created trigger for enforcing single default per content_type")
        except Exception as e:
            LOGGER.debug(f"Could not create insert trigger: {e}")
        
        # Create trigger for UPDATE as well
        try:
            execute_query("""
            CREATE TRIGGER IF NOT EXISTS trg_enforce_single_default_per_type_update
            BEFORE UPDATE ON collections
            FOR EACH ROW
            WHEN NEW.is_default = 1 AND OLD.is_default = 0
            BEGIN
                UPDATE collections SET is_default = 0 
                WHERE id != NEW.id AND COALESCE(content_type, 'MANGA') = COALESCE(NEW.content_type, 'MANGA');
            END
            """, commit=True)
            LOGGER.debug("Created trigger for enforcing single default per content_type on update")
        except Exception as e:
            LOGGER.debug(f"Could not create update trigger: {e}")
        
        # Create collection_root_folders table for many-to-many relationship
        execute_query("""
        CREATE TABLE IF NOT EXISTS collection_root_folders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            collection_id INTEGER NOT NULL,
            root_folder_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(collection_id, root_folder_id),
            FOREIGN KEY (collection_id) REFERENCES collections(id) ON DELETE CASCADE
        )
        """, commit=True)
        
        # Create root_folders table
        execute_query("""
        CREATE TABLE IF NOT EXISTS root_folders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            path TEXT NOT NULL,
            name TEXT NOT NULL,
            content_type TEXT DEFAULT 'MANGA',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(path)
        )
        """, commit=True)
        
        # Create series_collection table for many-to-many relationship
        execute_query("""
        CREATE TABLE IF NOT EXISTS series_collections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            series_id INTEGER NOT NULL,
            collection_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(series_id, collection_id),
            FOREIGN KEY (series_id) REFERENCES series(id) ON DELETE CASCADE,
            FOREIGN KEY (collection_id) REFERENCES collections(id) ON DELETE CASCADE
        )
        """, commit=True)
        
        # No longer automatically creating a default collection
        # Users will create their own collections through the UI
        LOGGER.info("Collections tables ready for user-created collections")
        
        LOGGER.info("Collections tables set up successfully")
    except Exception as e:
        LOGGER.error(f"Error setting up collections tables: {e}")
        raise
