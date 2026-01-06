#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Enhanced book import functionality that creates author folders.
"""

import os
from pathlib import Path
from flask import Blueprint, request, jsonify

from backend.base.logging import LOGGER
from backend.base.helpers import get_safe_folder_name
from backend.internals.db import execute_query
from backend.internals.settings import Settings
from frontend.middleware import setup_required

# Create a Blueprint for the enhanced book import API
enhanced_book_import_api_bp = Blueprint('api_enhanced_book_import', __name__, url_prefix='/api/metadata/enhanced_import')


@enhanced_book_import_api_bp.route('/<provider>/<book_id>', methods=['POST'])
@setup_required
def import_book_with_author_folder(provider, book_id):
    """Import a book to the collection and create an author folder.
    
    Args:
        provider: The provider name.
        book_id: The book ID.
        
    Returns:
        Response: The result.
    """
    try:
        # Get optional overrides from request
        data = request.json or {}
        collection_id = data.get('collection_id')
        content_type = data.get('content_type', 'BOOK')
        root_folder_id = data.get('root_folder_id')
        
        # If no collection_id provided, get the default BOOK collection
        if not collection_id:
            try:
                from backend.features.collection import get_default_collection
                default_book_collection = get_default_collection("BOOK")
                if default_book_collection and default_book_collection.get('id'):
                    collection_id = default_book_collection['id']
                    LOGGER.info(f"Using default BOOK collection: {collection_id}")
            except Exception as e:
                LOGGER.warning(f"Could not get default BOOK collection: {e}")
        
        # Get book details from the provider
        from backend.features.metadata_service import get_manga_details
        book_data = get_manga_details(book_id, provider)
        
        if not book_data:
            return jsonify({
                "success": False,
                "message": "Failed to fetch book details"
            }), 400
        
        # Extract book and author information
        book_title = book_data.get('title', 'Unknown Book')
        author_name = book_data.get('author', 'Unknown Author')
        
        # Create safe folder names
        safe_author_name = get_safe_folder_name(author_name)
        safe_book_title = get_safe_folder_name(book_title)
        
        # Get the root folder path using the helper function
        from backend.base.helpers_content_service import get_root_folder_path
        
        root_folder_path = get_root_folder_path(
            content_type,
            collection_id=collection_id,
            root_folder_id=root_folder_id
        )
        
        if not root_folder_path:
            return jsonify({
                "success": False,
                "message": "No root folder found for the specified collection or content type"
            }), 400
        
        # Extract author ID from book data if available
        author_id = book_data.get('author_key', '')
        if not author_id and 'authors' in book_data and book_data['authors']:
            # Try to get author ID from the authors list
            for author in book_data['authors']:
                if 'key' in author:
                    # Extract the author ID from the key (format: /authors/OL123456A)
                    key_parts = author['key'].split('/')
                    if len(key_parts) > 1:
                        author_id = key_parts[-1]
                        break
        
        # Check if the author already exists in the database
        author_exists = execute_query(
            "SELECT id, folder_path FROM authors WHERE provider = ? AND provider_id = ?",
            (provider, author_id)
        ) if author_id else None
        
        # Create or get the author folder
        root_path = Path(root_folder_path)
        author_folder_path = root_path / safe_author_name
        
        # If author exists, use their existing folder path
        if author_exists:
            author_db_id = author_exists[0]['id']
            existing_folder_path = author_exists[0]['folder_path']
            
            if existing_folder_path and Path(existing_folder_path).exists():
                author_folder_path = Path(existing_folder_path)
                LOGGER.info(f"Using existing author folder: {author_folder_path}")
            else:
                # If folder doesn't exist, create it
                try:
                    if not author_folder_path.exists():
                        author_folder_path.mkdir(parents=True, exist_ok=True)
                        LOGGER.info(f"Created author folder: {author_folder_path}")
                        
                        # Update the author record with the new folder path
                        execute_query(
                            "UPDATE authors SET folder_path = ? WHERE id = ?",
                            (str(author_folder_path), author_db_id)
                        )
                except Exception as e:
                    LOGGER.error(f"Error creating author folder: {e}")
                    return jsonify({
                        "success": False,
                        "message": f"Failed to create author folder: {str(e)}"
                    }), 500
        else:
            # Author doesn't exist, create the folder
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
        
        # Create the book folder inside the author folder
        book_folder_path = author_folder_path / safe_book_title
        
        try:
            if not book_folder_path.exists():
                book_folder_path.mkdir(parents=True, exist_ok=True)
                LOGGER.info(f"Created book folder: {book_folder_path}")
        except Exception as e:
            LOGGER.error(f"Error creating book folder: {e}")
            return jsonify({
                "success": False,
                "message": f"Failed to create book folder: {str(e)}"
            }), 500
        
        # Import the book using the standard import function (creates series only, no folders)
        from backend.features.metadata_service.facade import import_manga_to_collection
        
        LOGGER.info(f"About to call import_manga_to_collection with root_folder_id={root_folder_id}")
        result = import_manga_to_collection(
            book_id,
            provider,
            collection_id=collection_id,
            content_type=content_type,
            root_folder_id=root_folder_id,
        )
        LOGGER.info(f"import_manga_to_collection returned: {result}")
        
        # If import was successful, handle author information and create README
        if result.get("success") and "series_id" in result:
            series_id = result["series_id"]
            
            # Enrich series metadata with description and other details from book_data
            try:
                description = book_data.get("description", "")
                cover_url = book_data.get("cover_url", "")
                author = book_data.get("author", "Unknown")
                publisher = book_data.get("publisher", "")
                
                # Update series with enriched metadata
                execute_query(
                    """UPDATE series SET description = ?, cover_url = ?, author = ?, publisher = ? 
                       WHERE id = ?""",
                    (description, cover_url, author, publisher, series_id),
                    commit=True
                )
                LOGGER.info(f"Enriched series {series_id} with metadata from OpenLibrary")
            except Exception as e:
                LOGGER.warning(f"Failed to enrich series metadata: {e}")
            
            # Handle author information
            try:
                # Get or create author using the helper function (case-insensitive)
                # Pass create_readme=False because we'll create it with the correct folder path below
                from backend.features.authors_sync import get_or_create_author
                author_db_id = get_or_create_author(author_name, create_readme=False)
                
                if author_db_id:
                    # Create book-author relationship
                    execute_query(
                        "INSERT INTO author_books (series_id, author_id) VALUES (?, ?)",
                        (series_id, author_db_id),
                        commit=True
                    )
                    LOGGER.info(f"Created author relationship for series {series_id} with author {author_db_id}")
                    
                    # Update author's folder_path in database to the correct root folder location
                    try:
                        execute_query(
                            "UPDATE authors SET folder_path = ? WHERE id = ?",
                            (str(author_folder_path), author_db_id),
                            commit=True
                        )
                        LOGGER.info(f"Updated author {author_db_id} folder_path to: {author_folder_path}")
                    except Exception as e:
                        LOGGER.error(f"Failed to update author folder_path: {e}")
                    
                    # Sync author README to the author folder in the current root folder
                    try:
                        from backend.features.author_readme_sync import sync_author_readme
                        
                        # Sync author README with the specific folder path
                        LOGGER.info(f"Syncing author README for {author_name} (ID: {author_db_id}) to {author_folder_path}")
                        readme_result = sync_author_readme(author_db_id, str(author_folder_path))
                        if readme_result:
                            LOGGER.info(f"Created README.md for author {author_name} in {author_folder_path}")
                        else:
                            LOGGER.warning(f"sync_author_readme returned False for author {author_name}")
                    except Exception as e:
                        LOGGER.error(f"Failed to create author README.md: {e}")
                        import traceback
                        LOGGER.error(traceback.format_exc())
            except Exception as e:
                LOGGER.warning(f"Failed to create author relationship: {e}")
        
        # Create comprehensive README file in the book folder using ensure_readme_file
        try:
            from backend.base.helpers import ensure_readme_file
            
            # Prepare genres/subjects as comma-separated string
            genres = book_data.get("genres", [])
            subjects_str = ",".join(genres) if isinstance(genres, list) else genres
            
            # Use ensure_readme_file to create comprehensive README with all metadata
            ensure_readme_file(
                book_folder_path,
                book_data.get('title', 'Unknown Book'),
                series_id,
                'BOOK',
                metadata_source=provider,
                metadata_id=book_data.get('id', ''),
                author=book_data.get('author', ''),
                publisher=book_data.get('publisher', ''),
                isbn=book_data.get('isbn', ''),
                genres=genres,
                cover_url=book_data.get('cover_url', ''),
                published_date=book_data.get('published_date', ''),
                subjects=genres,  # Use genres as subjects
                description=book_data.get('description', '')
            )
            LOGGER.info(f"Created comprehensive README file in: {book_folder_path}")
        except Exception as e:
            LOGGER.warning(f"Failed to create README file: {e}")
        
        # Add folder paths to the result
        result["author_folder_path"] = str(author_folder_path)
        result["book_folder_path"] = str(book_folder_path)
        
        # Update the calendar to include the newly imported book's release dates
        try:
            from backend.features.calendar import update_calendar
            if "series_id" in result:
                LOGGER.info(f"Updating calendar for newly imported series (ID: {result.get('series_id')})")
                update_calendar(series_id=result.get('series_id'))
            else:
                LOGGER.info("Updating calendar after book import")
                update_calendar()
        except Exception as e:
            LOGGER.error(f"Error updating calendar after import: {e}")
            # Continue anyway - we don't want to fail the import if calendar update fails
        
        return jsonify(result)
        
    except Exception as e:
        LOGGER.error(f"Error importing book with author folder: {e}")
        return jsonify({
            "success": False,
            "message": f"Failed to import book: {str(e)}"
        }), 500
