#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Migration to create trending_manga table for storing trending manga from AniList.
"""

from backend.base.logging import LOGGER
from backend.internals.db import execute_query


def migrate():
    """Create the trending_manga table."""
    LOGGER.info("Creating trending_manga table...")
    
    try:
        execute_query("""
        CREATE TABLE IF NOT EXISTS trending_manga (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            anilist_id INTEGER NOT NULL UNIQUE,
            title TEXT NOT NULL,
            cover_url TEXT,
            trending_score INTEGER DEFAULT 0,
            popularity INTEGER DEFAULT 0,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """, commit=True)
        
        LOGGER.info("trending_manga table created successfully")
    except Exception as e:
        LOGGER.error(f"Error creating trending_manga table: {e}")
        raise


if __name__ == "__main__":
    migrate()
