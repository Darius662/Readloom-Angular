#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Migration 0022: Fix manga_volume_cache table schema.

This migration fixes the manga_volume_cache table to use metadata_id instead of anilist_id,
and adds missing columns (refresh_count, refreshed_at, etc.) that are required by the scraper.
"""

from backend.base.logging import LOGGER
from backend.internals.db import execute_query


def migrate():
    """Fix the manga_volume_cache table schema."""
    LOGGER.info("Fixing manga_volume_cache table schema")
    
    try:
        # Drop the old table if it exists with wrong schema
        execute_query("DROP TABLE IF EXISTS manga_volume_cache", commit=True)
        LOGGER.info("Dropped old manga_volume_cache table")
        
        # Create the new table with correct schema
        execute_query("""
        CREATE TABLE IF NOT EXISTS manga_volume_cache (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            manga_title TEXT NOT NULL,
            manga_title_normalized TEXT NOT NULL,
            metadata_id TEXT,
            mal_id TEXT,
            chapter_count INTEGER NOT NULL DEFAULT 0,
            volume_count INTEGER NOT NULL DEFAULT 0,
            source TEXT NOT NULL,
            status TEXT,
            cached_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            refreshed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            refresh_count INTEGER DEFAULT 0,
            UNIQUE(manga_title_normalized)
        )
        """, commit=True)
        LOGGER.info("Created new manga_volume_cache table with correct schema")
        
        # Create indexes for better performance
        execute_query("""
            CREATE INDEX IF NOT EXISTS idx_manga_cache_metadata 
            ON manga_volume_cache(metadata_id)
        """, commit=True)
        
        execute_query("""
            CREATE INDEX IF NOT EXISTS idx_manga_cache_title 
            ON manga_volume_cache(manga_title_normalized)
        """, commit=True)
        
        execute_query("""
            CREATE INDEX IF NOT EXISTS idx_manga_cache_refreshed 
            ON manga_volume_cache(refreshed_at)
        """, commit=True)
        
        LOGGER.info("Migration completed successfully")
        return True
    
    except Exception as e:
        LOGGER.error(f"Error during migration: {e}")
        import traceback
        LOGGER.error(traceback.format_exc())
        return False


def rollback():
    """Rollback the migration (optional)."""
    LOGGER.info("Rolling back manga_volume_cache table fix")
    try:
        execute_query("DROP TABLE IF EXISTS manga_volume_cache", commit=True)
        LOGGER.info("manga_volume_cache table dropped")
        return True
    except Exception as e:
        LOGGER.error(f"Error during rollback: {e}")
        return False
