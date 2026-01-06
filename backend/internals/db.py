#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sqlite3
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

from backend.base.custom_exceptions import DatabaseError
from backend.base.definitions import Constants
from backend.base.helpers import ensure_dir_exists, get_data_dir
from backend.base.logging import LOGGER

# These imports will be done inside setup_db to avoid circular imports

# Global variables
DB_PATH: Optional[Path] = None
DB_CONN: Optional[sqlite3.Connection] = None


def set_db_location(db_folder: Optional[str] = None) -> None:
    """Set the location of the database.

    Args:
        db_folder (Optional[str], optional): The folder to store the database in.
            Defaults to None.

    Raises:
        ValueError: If the database location is not a folder.
    """
    global DB_PATH
    
    if db_folder:
        folder_path = Path(db_folder)
        if not folder_path.exists() or not folder_path.is_dir():
            raise ValueError("Database location is not a folder")
    else:
        folder_path = get_data_dir()
    
    DB_PATH = folder_path / Constants.DEFAULT_DB_NAME
    LOGGER.info(f"Database path set to: {DB_PATH}")


def get_db_connection(timeout: int = 30) -> sqlite3.Connection:
    """Get a connection to the database with improved timeout handling.

    Args:
        timeout (int, optional): Connection timeout in seconds. Defaults to 30.

    Returns:
        sqlite3.Connection: A connection to the database.

    Raises:
        DatabaseError: If the database connection could not be established.
    """
    global DB_CONN
    
    if DB_CONN is not None:
        return DB_CONN
    
    if DB_PATH is None:
        set_db_location()
    
    try:
        # Set a longer timeout to help with locked database issues
        DB_CONN = sqlite3.connect(DB_PATH, timeout=timeout, check_same_thread=False, 
                                   isolation_level=None)  # Autocommit mode
        
        # Use DELETE journal mode instead of WAL for Docker compatibility
        # WAL mode doesn't work well with network filesystems and Docker volumes
        result = DB_CONN.execute('PRAGMA journal_mode = DELETE')
        journal_mode = result.fetchone()[0]
        LOGGER.info(f"Database journal mode set to: {journal_mode}")
        
        # Set busy timeout to wait instead of immediately failing
        DB_CONN.execute(f'PRAGMA busy_timeout = {timeout * 1000}')
        
        # Set synchronous mode to NORMAL for better performance while maintaining safety
        DB_CONN.execute('PRAGMA synchronous = NORMAL')
        
        # Enable foreign keys
        DB_CONN.execute('PRAGMA foreign_keys = ON')
        
        DB_CONN.row_factory = sqlite3.Row
        LOGGER.info("Database connection established successfully")
        return DB_CONN
    except Exception as e:
        LOGGER.error(f"Could not connect to database: {e}")
        raise DatabaseError(f"Could not connect to database: {e}")


def close_db_connection() -> None:
    """Close the database connection."""
    global DB_CONN
    
    if DB_CONN is not None:
        DB_CONN.close()
        DB_CONN = None


def execute_query(query: str, params: Tuple = (), commit: bool = False, max_retries: int = 5, retry_delay: float = 0.5) -> List[Dict[str, Any]]:
    """Execute a SQL query with retry logic for handling database locks.

    Args:
        query (str): The SQL query to execute.
        params (Tuple, optional): The parameters for the query. Defaults to ().
        commit (bool, optional): Whether to commit the transaction. Defaults to False.
        max_retries (int, optional): Maximum number of retries if database is locked. Defaults to 5.
        retry_delay (float, optional): Delay between retries in seconds. Defaults to 0.5.

    Returns:
        List[Dict[str, Any]]: The results of the query.

    Raises:
        DatabaseError: If the query could not be executed after all retries.
    """
    conn = get_db_connection()
    retries = 0
    
    while retries <= max_retries:
        try:
            cursor = conn.cursor()
            cursor.execute(query, params)
            
            # Note: commit parameter is ignored since we're using autocommit mode (isolation_level=None)
            # This is intentional for Docker compatibility
            
            if query.strip().upper().startswith("SELECT"):
                return [dict(row) for row in cursor.fetchall()]
            return []
        except sqlite3.OperationalError as e:
            if "database is locked" in str(e) and retries < max_retries:
                retries += 1
                LOGGER.warning(f"Database locked, retrying ({retries}/{max_retries}) in {retry_delay}s: {e}")
                time.sleep(retry_delay)
                # Increase delay with each retry
                retry_delay *= 1.5
            else:
                LOGGER.error(f"Database query error after {retries} retries: {e}")
                raise DatabaseError(f"Database query error: {e}")
        except Exception as e:
            LOGGER.error(f"Database query error: {e}")
            raise DatabaseError(f"Database query error: {e}")


def setup_db() -> None:
    """Set up the database schema."""
    LOGGER.info("Setting up database schema")
    
    # Clean up problematic indexes from old schema - MUST run on every startup
    # Use direct connection to avoid issues with execute_query
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DROP INDEX IF EXISTS idx_unique_default")
        cursor.execute("DROP INDEX IF EXISTS idx_unique_default_per_type")
        LOGGER.info("Dropped problematic indexes if they existed")
    except Exception as e:
        LOGGER.debug(f"Could not drop indexes: {e}")
    
    # Create series table with all columns
    execute_query("""
    CREATE TABLE IF NOT EXISTS series (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT,
        author TEXT,
        publisher TEXT,
        cover_url TEXT,
        status TEXT,
        content_type TEXT DEFAULT 'MANGA',
        metadata_source TEXT,
        metadata_id TEXT,
        custom_path TEXT,
        isbn TEXT,
        published_date TEXT,
        subjects TEXT,
        user_description TEXT,
        star_rating REAL DEFAULT 0,
        reading_progress INTEGER DEFAULT 0,
        in_library INTEGER DEFAULT 0,
        want_to_read INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """, commit=True)
    
    # Check and add any missing columns for existing databases
    try:
        column_check = execute_query("PRAGMA table_info(series)")
        column_names = [col['name'] for col in column_check]
        
        # List of columns that should exist with their definitions
        required_columns = [
            ('isbn', 'TEXT'),
            ('published_date', 'TEXT'),
            ('subjects', 'TEXT'),
            ('user_description', 'TEXT'),
            ('star_rating', 'REAL DEFAULT 0'),
            ('reading_progress', 'INTEGER DEFAULT 0'),
            ('in_library', 'INTEGER DEFAULT 0'),
            ('want_to_read', 'INTEGER DEFAULT 0'),
            ('is_book', 'INTEGER DEFAULT 0'),
        ]
        
        for col_name, col_type in required_columns:
            if col_name not in column_names:
                try:
                    execute_query(f"ALTER TABLE series ADD COLUMN {col_name} {col_type}", commit=True)
                    LOGGER.info(f"Added {col_name} column to series table")
                except Exception as add_err:
                    if 'duplicate column name' in str(add_err).lower():
                        LOGGER.debug(f"{col_name} column already exists; skipping add")
                    else:
                        LOGGER.warning(f"Could not add {col_name} column: {add_err}")
    except Exception as e:
        LOGGER.warning(f"Error checking/adding columns to series table: {e}")
    
    # Create volumes table
    execute_query("""
    CREATE TABLE IF NOT EXISTS volumes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        series_id INTEGER NOT NULL,
        volume_number TEXT NOT NULL,
        title TEXT,
        description TEXT,
        cover_url TEXT,
        cover_path TEXT,
        release_date TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (series_id) REFERENCES series (id) ON DELETE CASCADE
    )
    """, commit=True)
    
    # Check and add cover_path column to existing volumes table
    try:
        column_check = execute_query("PRAGMA table_info(volumes)")
        column_names = [col['name'] for col in column_check]
        
        if 'cover_path' not in column_names:
            try:
                execute_query("ALTER TABLE volumes ADD COLUMN cover_path TEXT", commit=True)
                LOGGER.info("Added cover_path column to volumes table")
            except Exception as add_err:
                if 'duplicate column name' in str(add_err).lower():
                    LOGGER.debug("cover_path column already exists; skipping add")
                else:
                    LOGGER.warning(f"Could not add cover_path column: {add_err}")
        else:
            LOGGER.info("cover_path column already exists in volumes table")
    except Exception as e:
        LOGGER.warning(f"Error checking volumes table columns: {e}")
    
    # Create chapters table
    execute_query("""
    CREATE TABLE IF NOT EXISTS chapters (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        series_id INTEGER NOT NULL,
        volume_id INTEGER,
        chapter_number TEXT NOT NULL,
        title TEXT,
        description TEXT,
        release_date TEXT,
        status TEXT,
        read_status TEXT DEFAULT 'UNREAD',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (series_id) REFERENCES series (id) ON DELETE CASCADE,
        FOREIGN KEY (volume_id) REFERENCES volumes (id) ON DELETE SET NULL
    )
    """, commit=True)
    
    # Create releases table
    execute_query("""
    CREATE TABLE IF NOT EXISTS releases (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        series_id INTEGER NOT NULL,
        type TEXT NOT NULL CHECK(type IN ('chapter', 'volume')),
        number TEXT NOT NULL,
        title TEXT,
        release_date TEXT NOT NULL,
        is_confirmed INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (series_id) REFERENCES series (id) ON DELETE CASCADE
    )
    """, commit=True)
    
    # Enable foreign key support
    execute_query("PRAGMA foreign_keys = ON;")

    # Create calendar_events table
    execute_query("""
    CREATE TABLE IF NOT EXISTS calendar_events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        series_id INTEGER REFERENCES series(id) ON DELETE CASCADE,
        volume_id INTEGER REFERENCES volumes(id) ON DELETE CASCADE,
        chapter_id INTEGER,
        title TEXT NOT NULL,
        description TEXT,
        event_date TEXT NOT NULL,
        event_type TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (series_id) REFERENCES series (id) ON DELETE CASCADE,
        FOREIGN KEY (volume_id) REFERENCES volumes (id) ON DELETE CASCADE,
        FOREIGN KEY (chapter_id) REFERENCES chapters (id) ON DELETE CASCADE
    )
    """, commit=True)
    
    # Create settings table
    execute_query("""
    CREATE TABLE IF NOT EXISTS settings (
        key TEXT PRIMARY KEY,
        value TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """, commit=True)
    
    # Create metadata_cache table
    execute_query("""
    CREATE TABLE IF NOT EXISTS metadata_cache (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        source TEXT NOT NULL,
        source_id TEXT NOT NULL,
        data TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(source, source_id)
    )
    """, commit=True)
    
    # Create ebook_files table
    execute_query("""
    CREATE TABLE IF NOT EXISTS ebook_files (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        series_id INTEGER NOT NULL,
        volume_id INTEGER NOT NULL,
        file_path TEXT NOT NULL,
        file_name TEXT NOT NULL,
        file_size INTEGER,
        file_type TEXT,
        original_name TEXT,
        added_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (series_id) REFERENCES series (id) ON DELETE CASCADE,
        FOREIGN KEY (volume_id) REFERENCES volumes (id) ON DELETE CASCADE
    )
    """, commit=True)
    
    # Create authors table
    execute_query("""
    CREATE TABLE IF NOT EXISTS authors (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT,
        biography TEXT,
        birth_date TEXT,
        death_date TEXT,
        photo_url TEXT,
        provider TEXT,
        provider_id TEXT,
        folder_path TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """, commit=True)
    
    # Check and add any missing columns for authors table
    try:
        column_check = execute_query("PRAGMA table_info(authors)")
        column_names = [col['name'] for col in column_check]
        
        # List of columns that should exist with their definitions
        required_author_columns = [
            ('biography', 'TEXT'),
            ('birth_date', 'TEXT'),
            ('death_date', 'TEXT'),
            ('photo_url', 'TEXT'),
            ('provider', 'TEXT'),
            ('provider_id', 'TEXT'),
            ('folder_path', 'TEXT'),
            ('description', 'TEXT'),
        ]
        
        for col_name, col_type in required_author_columns:
            if col_name not in column_names:
                try:
                    execute_query(f"ALTER TABLE authors ADD COLUMN {col_name} {col_type}", commit=True)
                    LOGGER.info(f"Added {col_name} column to authors table")
                except Exception as add_err:
                    if 'duplicate column name' in str(add_err).lower():
                        LOGGER.debug(f"{col_name} column already exists; skipping add")
                    else:
                        LOGGER.warning(f"Could not add {col_name} column to authors: {add_err}")
    except Exception as e:
        LOGGER.warning(f"Error checking/adding columns to authors table: {e}")
    
    # Create author_books table
    execute_query("""
    CREATE TABLE IF NOT EXISTS author_books (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        author_id INTEGER NOT NULL,
        series_id INTEGER NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (author_id) REFERENCES authors (id) ON DELETE CASCADE,
        FOREIGN KEY (series_id) REFERENCES series (id) ON DELETE CASCADE
    )
    """, commit=True)
    
    # Create recommendation_cache table
    execute_query("""
    CREATE TABLE IF NOT EXISTS recommendation_cache (
        book_id INTEGER PRIMARY KEY,
        recommendations TEXT NOT NULL,
        method TEXT NOT NULL,
        book_hash TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """, commit=True)
    
    # Create manga_volume_cache table
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
    
    # Create trending_manga table
    execute_query("""
    CREATE TABLE IF NOT EXISTS trending_manga (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        anilist_id INTEGER NOT NULL UNIQUE,
        title TEXT NOT NULL,
        description TEXT,
        cover_url TEXT,
        rank INTEGER,
        popularity INTEGER,
        score REAL,
        status TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """, commit=True)
    
    # Create want_to_read_cache table with correct structure
    try:
        # First check if table exists and has wrong structure
        existing_table = execute_query("SELECT sql FROM sqlite_master WHERE type='table' AND name='want_to_read_cache'")
        
        if existing_table and 'UNIQUE(series_id)' in existing_table[0].get('sql', ''):
            # Table exists with wrong structure, recreate it
            LOGGER.info("Recreating want_to_read_cache table with correct structure")
            try:
                execute_query("DROP TABLE want_to_read_cache", commit=True)
            except Exception as drop_err:
                LOGGER.warning(f"Could not drop old table: {drop_err}")
        
        execute_query("""
        CREATE TABLE IF NOT EXISTS want_to_read_cache (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            series_id INTEGER,
            title TEXT NOT NULL,
            author TEXT,
            cover_url TEXT,
            metadata_source TEXT NOT NULL,
            metadata_id TEXT NOT NULL,
            content_type TEXT DEFAULT 'MANGA',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(metadata_source, metadata_id)
        )
        """, commit=True)
        LOGGER.info("want_to_read_cache table created or verified with correct structure")
    except Exception as e:
        LOGGER.warning(f"Error creating want_to_read_cache table: {e}")
    
    # Add content_type column to want_to_read_cache if it doesn't exist
    try:
        column_check = execute_query("PRAGMA table_info(want_to_read_cache)")
        column_names = [col['name'] for col in column_check]
        
        if 'content_type' not in column_names:
            try:
                execute_query("ALTER TABLE want_to_read_cache ADD COLUMN content_type TEXT DEFAULT 'MANGA'", commit=True)
                LOGGER.info("Added content_type column to want_to_read_cache table")
            except Exception as add_err:
                if 'duplicate column name' in str(add_err).lower():
                    LOGGER.info("content_type column already exists; skipping add")
                else:
                    LOGGER.warning(f"Could not add content_type column: {add_err}")
        else:
            LOGGER.info("content_type column already exists in want_to_read_cache")
    except Exception as e:
        LOGGER.warning(f"Error checking want_to_read_cache columns: {e}")
    
    # Import here to avoid circular imports
    from backend.features.collection import setup_collection_tables
    from backend.features.notifications import setup_notifications_tables
    
    # Set up collection tracking tables
    setup_collection_tables()
    
    # Add missing columns to collection_items table for existing databases
    try:
        column_check = execute_query("PRAGMA table_info(collection_items)")
        column_names = [col['name'] for col in column_check]
        
        missing_columns = [
            ('has_file', 'INTEGER DEFAULT 0'),
            ('digital_format', "TEXT CHECK(digital_format IN ('PDF', 'EPUB', 'CBZ', 'CBR', 'MOBI', 'AZW', 'NONE'))"),
            ('ebook_file_id', 'INTEGER'),
        ]
        
        for col_name, col_type in missing_columns:
            if col_name not in column_names:
                try:
                    execute_query(f"ALTER TABLE collection_items ADD COLUMN {col_name} {col_type}", commit=True)
                    LOGGER.info(f"Added {col_name} column to collection_items table")
                except Exception as add_err:
                    if 'duplicate column name' in str(add_err).lower():
                        LOGGER.debug(f"{col_name} column already exists; skipping add")
                    else:
                        LOGGER.warning(f"Could not add {col_name} column: {add_err}")
    except Exception as e:
        LOGGER.warning(f"Error checking/adding columns to collection_items table: {e}")
    
    # Set up notifications tables
    setup_notifications_tables()
    
    LOGGER.info("Database schema setup complete")
