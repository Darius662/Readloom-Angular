#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
API endpoints for author metadata import.
"""

import os
from pathlib import Path
from flask import Blueprint, request, jsonify

from backend.base.logging import LOGGER
from backend.base.helpers import get_safe_folder_name
from backend.internals.db import execute_query
from backend.internals.settings import Settings
from frontend.middleware import setup_required
import sqlite3

# Create a Blueprint for the author import API
author_import_api_bp = Blueprint('api_author_import', __name__, url_prefix='/api/metadata/author/import')


def ensure_authors_tables_exist():
    """Ensure the authors tables exist in the database."""
    try:
        # Use the execute_query function from the application
        # This function handles the database connection and error handling
        
        # Check if authors table exists
        tables = execute_query("SELECT name FROM sqlite_master WHERE type='table' AND name='authors'")
        if not tables:
            LOGGER.info("Creating authors table")
            execute_query('''
            CREATE TABLE IF NOT EXISTS authors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                provider TEXT NOT NULL,
                provider_id TEXT NOT NULL,
                birth_date TEXT,
                death_date TEXT,
                biography TEXT,
                folder_path TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(provider, provider_id)
            )
            ''')
        
        # Check if collection_authors table exists
        tables = execute_query("SELECT name FROM sqlite_master WHERE type='table' AND name='collection_authors'")
        if not tables:
            LOGGER.info("Creating collection_authors table")
            execute_query('''
            CREATE TABLE IF NOT EXISTS collection_authors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                collection_id INTEGER NOT NULL,
                author_id INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (collection_id) REFERENCES collections(id) ON DELETE CASCADE,
                FOREIGN KEY (author_id) REFERENCES authors(id) ON DELETE CASCADE,
                UNIQUE(collection_id, author_id)
            )
            ''')
        
        # Check if author_books table exists
        tables = execute_query("SELECT name FROM sqlite_master WHERE type='table' AND name='author_books'")
        if not tables:
            LOGGER.info("Creating author_books table")
            execute_query('''
            CREATE TABLE IF NOT EXISTS author_books (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                author_id INTEGER NOT NULL,
                series_id INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (author_id) REFERENCES authors(id) ON DELETE CASCADE,
                FOREIGN KEY (series_id) REFERENCES series(id) ON DELETE CASCADE,
                UNIQUE(author_id, series_id)
            )
            ''')
        
        return True
        
    except Exception as e:
        LOGGER.error(f"Error ensuring authors tables exist: {e}")
        return False


@author_import_api_bp.route('/<provider>/<author_id>', methods=['POST'])
@setup_required
def import_author(provider, author_id):
    """Import an author to the collection.
    
    Args:
        provider: The provider name.
        author_id: The author ID.
        
    Returns:
        Response: The result.
    """
    try:
        # Ensure the authors tables exist
        if not ensure_authors_tables_exist():
            return jsonify({
                "success": False,
                "message": "Failed to ensure authors tables exist"
            }), 500
        
        # Get optional overrides from request
        data = request.json or {}
        collection_id = data.get('collection_id')
        root_folder_id = data.get('root_folder_id')
        
        # Get author details from the provider
        # We need to call the OpenLibrary API directly since get_author_details returns a Response object
        from backend.features.metadata_providers.openlibrary.provider import OpenLibraryProvider
        import requests
        import json
        
        openlibrary_provider = OpenLibraryProvider()
        author_url = f"{openlibrary_provider.base_url}/authors/{author_id}.json"
        response = requests.get(author_url)
        
        if not response.ok:
            return jsonify({
                "success": False,
                "message": f"Failed to fetch author details: {response.status_code}"
            }), 400
            
        author_data = response.json()
        
        # Also get the works data
        works_url = f"{openlibrary_provider.base_url}/authors/{author_id}/works.json"
        works_response = requests.get(works_url)
        works_data = works_response.json() if works_response.ok else {"size": 0, "entries": []}
        
        # Extract author information
        author_name = author_data.get('name', 'Unknown Author')
        
        # Create a safe folder name for the author
        safe_author_name = get_safe_folder_name(author_name)
        
        # Check if author already exists in the database
        author_exists = execute_query(
            "SELECT id, folder_path FROM authors WHERE provider = ? AND provider_id = ?",
            (provider, author_id)
        )
        
        if author_exists:
            author_db_id = author_exists[0]['id']
            existing_folder_path = author_exists[0]['folder_path']
            
            # Return success but indicate the author already exists
            # This allows the frontend to show a different message
            return jsonify({
                "success": True,
                "already_exists": True,
                "message": f"Author '{author_name}' already exists in the collection. You can add individual books to this author.",
                "author_id": author_db_id,
                "folder_path": existing_folder_path
            }), 200
        
        # Get the root folder path using the helper function
        # For authors, we should use BOOK content type to get the book root folder
        from backend.base.helpers_content_service import get_root_folder_path
        
        root_folder_path = get_root_folder_path(
            "BOOK",  # Authors are typically associated with books
            collection_id=collection_id,
            root_folder_id=root_folder_id
        )
        
        if not root_folder_path:
            return jsonify({
                "success": False,
                "message": "No root folder found for the specified collection or content type"
            }), 400
        
        # Create the author folder
        root_path = Path(root_folder_path)
        author_folder_path = root_path / safe_author_name
        
        try:
            if not author_folder_path.exists():
                author_folder_path.mkdir(parents=True, exist_ok=True)
                LOGGER.info(f"Created author folder: {author_folder_path}")
        except Exception as e:
            LOGGER.error(f"Error creating author folder: {e}")
            return jsonify({
                "success": False,
                "message": f"Failed to create author folder: {str(e)}"
            }), 500
        
        # Insert the author into the database
        author_db_id = None
        try:
            author_insert = execute_query(
                """
                INSERT INTO authors (name, provider, provider_id, birth_date, death_date, biography, folder_path)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                RETURNING id
                """,
                (
                    author_name,
                    provider,
                    author_id,
                    author_data.get('birth_date', ''),
                    author_data.get('death_date', ''),
                    author_data.get('biography', ''),
                    str(author_folder_path)
                )
            )
            
            if author_insert:
                author_db_id = author_insert[0]['id']
                LOGGER.info(f"Added author to database with ID: {author_db_id}")
            
            # Add author to the specified collection
            if collection_id and author_db_id:
                execute_query(
                    "INSERT INTO collection_authors (collection_id, author_id) VALUES (?, ?)",
                    (collection_id, author_db_id)
                )
                LOGGER.info(f"Added author {author_db_id} to collection {collection_id}")
            
            # Extract notable works from works data
            notable_works = []
            if works_data and "entries" in works_data:
                for i, work in enumerate(works_data["entries"]):
                    if i >= 5:  # Limit to 5 notable works
                        break
                    if "title" in work:
                        notable_works.append(work["title"])
            
            # Create subfolders for notable works
            for work in notable_works:
                safe_work_name = get_safe_folder_name(work)
                work_folder_path = author_folder_path / safe_work_name
                
                try:
                    if not work_folder_path.exists():
                        work_folder_path.mkdir(parents=True, exist_ok=True)
                        LOGGER.info(f"Created work folder: {work_folder_path}")
                except Exception as e:
                    LOGGER.error(f"Error creating work folder: {e}")
            
            # Create a README.md file with author information using the new format
            try:
                from backend.features.author_readme_sync import ensure_author_readme_file
                from datetime import datetime
                
                # Extract biography
                bio = ""
                if isinstance(author_data.get('bio'), dict) and 'value' in author_data.get('bio', {}):
                    bio = author_data['bio']['value']
                elif isinstance(author_data.get('bio'), str):
                    bio = author_data['bio']
                
                # Create README.md with the new standardized format
                ensure_author_readme_file(
                    author_folder_path,
                    author_db_id,
                    author_name,
                    description=None,
                    biography=bio,
                    birth_date=author_data.get('birth_date'),
                    death_date=author_data.get('death_date'),
                    photo_url=author_data.get('photo_url'),
                    provider=provider,
                    provider_id=author_id,
                    notable_works=notable_works,
                    source_url=None,
                    openlibrary_url=f"https://openlibrary.org/authors/{author_id}"
                )
                
                LOGGER.info(f"Created README.md for author: {author_name}")
            except Exception as e:
                LOGGER.error(f"Error creating README.md: {e}")
            
            return jsonify({
                "success": True,
                "message": f"Author '{author_name}' added to collection",
                "author_id": author_db_id,
                "folder_path": str(author_folder_path)
            })
            
        except Exception as e:
            LOGGER.error(f"Error adding author to database: {e}")
            return jsonify({
                "success": False,
                "message": f"Failed to add author to database: {str(e)}"
            }), 500
        
    except Exception as e:
        LOGGER.error(f"Error importing author: {e}")
        return jsonify({
            "success": False,
            "message": f"Failed to import author: {str(e)}"
        }), 500
