#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
API endpoints for series.
"""

from flask import Blueprint, jsonify, request

from backend.base.logging import LOGGER
from backend.internals.db import execute_query


# Create Blueprint for series API
api_series_bp = Blueprint('api_series', __name__)


@api_series_bp.route('/api/series/<int:series_id>/scan', methods=['POST'])
def scan_series_for_ebooks(series_id: int):
    """Scan for e-books for a specific series.

    Args:
        series_id (int): The series ID.

    Returns:
        Response: The scan results.
    """
    try:
        LOGGER.info(f"Received scan request for series ID: {series_id}")
        
        # Check if series exists
        series = execute_query("SELECT id, title, content_type FROM series WHERE id = ?", (series_id,))
        if not series:
            LOGGER.error(f"Series with ID {series_id} not found")
            return jsonify({"error": "Series not found"}), 404
        
        LOGGER.info(f"Found series: {series[0]['title']} (ID: {series_id}, Type: {series[0]['content_type']})")
        
        # Get custom path from request body if provided
        custom_path = None
        if request.is_json:
            data = request.json or {}
            custom_path = data.get('custom_path')
            LOGGER.info(f"Request has JSON content, custom_path: {custom_path}")
        else:
            LOGGER.info("Request does not have JSON content")
        
        # Import scan function
        from backend.features.ebook_files import scan_for_ebooks
        
        # Scan for e-books
        LOGGER.info(f"Starting scan for series ID {series_id} with custom_path: {custom_path}")
        scan_results = scan_for_ebooks(specific_series_id=series_id, custom_path=custom_path)
        LOGGER.info(f"Scan completed with results: {scan_results}")
        
        # Add success flag
        scan_results['success'] = 'error' not in scan_results
        
        return jsonify(scan_results)
    
    except Exception as e:
        import traceback
        LOGGER.error(f"Error scanning for e-books for series {series_id}: {e}")
        LOGGER.error(traceback.format_exc())
        return jsonify({"error": str(e)}), 500


@api_series_bp.route('/api/series/scan', methods=['POST'])
def scan_all_ebooks():
    """Scan for all e-books in all configured root folders.

    Returns:
        Response: The scan results.
    """
    try:
        LOGGER.info("Received general scan request for all e-books")
        
        # Get content type filter from request body (optional)
        content_type = None
        if request.is_json:
            data = request.json or {}
            content_type = data.get('content_type')
            LOGGER.info(f"Content type filter from request: {content_type}")
            LOGGER.info(f"Request data: {data}")
        else:
            LOGGER.warning("Request is not JSON format")
        
        # Import scan function
        from backend.features.ebook_files import scan_for_ebooks
        
        # Scan for all e-books with content type filter
        LOGGER.info("Starting general scan for all e-books")
        scan_results = scan_for_ebooks(content_type_filter=content_type)
        LOGGER.info(f"General scan completed with results: {scan_results}")
        
        # Add success flag
        scan_results['success'] = 'error' not in scan_results
        
        return jsonify(scan_results)
    
    except Exception as e:
        import traceback
        LOGGER.error(f"Error scanning for all e-books: {e}")
        LOGGER.error(traceback.format_exc())
        return jsonify({"error": str(e)}), 500


@api_series_bp.route('/api/series', methods=['GET'])
def get_all_series():
    """Get all series.
    
    Query parameters:
        content_type: Filter by content type (book, manga)
        search: Search by title or author
        isbn: Search by ISBN (for books only)
    
    Returns:
        Response: All series.
    """
    try:
        # Get query parameters
        content_type = request.args.get('content_type', None)
        search = request.args.get('search', None)
        isbn = request.args.get('isbn', None)
        
        # Build base query
        query = "SELECT * FROM series WHERE 1=1"
        params = []
        
        # Apply content type filter
        if content_type == 'book':
            query += " AND UPPER(content_type) IN ('BOOK', 'NOVEL')"
        elif content_type == 'manga':
            query += " AND UPPER(content_type) IN ('MANGA', 'MANHWA', 'MANHUA', 'COMIC')"
        
        # Apply search filter
        if search:
            query += " AND (LOWER(title) LIKE LOWER(?) OR LOWER(author) LIKE LOWER(?))"
            search_term = f"%{search}%"
            params.extend([search_term, search_term])
        
        # Apply ISBN filter (books only)
        if isbn:
            query += " AND isbn = ?"
            params.append(isbn)
        
        query += " ORDER BY title"
        
        series = execute_query(query, tuple(params)) if params else execute_query(query)
        
        return jsonify({"series": series})
    except Exception as e:
        LOGGER.error(f"Error getting series: {e}")
        return jsonify({"error": str(e)}), 500


@api_series_bp.route('/api/series/<int:series_id>', methods=['GET'])
def get_series(series_id: int):
    """Get a series by ID.
    
    Args:
        series_id: The series ID.
        
    Returns:
        Response: The series.
    """
    try:
        series = execute_query("""
            SELECT * FROM series WHERE id = ?
        """, (series_id,))
        
        if not series:
            return jsonify({"error": "Series not found"}), 404
        
        return jsonify({"series": series[0]})
    except Exception as e:
        LOGGER.error(f"Error getting series: {e}")
        return jsonify({"error": str(e)}), 500


@api_series_bp.route('/api/series/<int:series_id>', methods=['PUT'])
def update_series(series_id: int):
    """Update a series with new data.
    
    Args:
        series_id: The series ID.
        
    Request Body:
        star_rating (int, optional): Star rating (1-5)
        reading_progress (float, optional): Reading progress (0-1)
        user_description (str, optional): User notes
        status (str, optional): Reading status
        
    Returns:
        Response: Updated series data or error message.
    """
    try:
        LOGGER.info(f"Received update request for series {series_id}")
        
        # Check if series exists
        series = execute_query("SELECT id, title, content_type FROM series WHERE id = ?", (series_id,))
        if not series:
            return jsonify({"error": "Series not found"}), 404
        
        # Get update data from request body
        if not request.is_json:
            return jsonify({"error": "Request must be JSON"}), 400
            
        data = request.json or {}
        LOGGER.info(f"Update data: {data}")
        
        # Build update query dynamically based on provided fields
        update_fields = []
        update_values = []
        
        if 'star_rating' in data:
            rating = data['star_rating']
            if rating is not None and (not isinstance(rating, int) or rating < 0 or rating > 5):
                return jsonify({"error": "Star rating must be an integer between 0 and 5"}), 400
            update_fields.append("star_rating = ?")
            update_values.append(rating)
            LOGGER.info(f"Updating star_rating to: {rating}")
        
        if 'reading_progress' in data:
            progress = data['reading_progress']
            # Handle both string percentages and decimal values
            if isinstance(progress, str):
                if progress.endswith('%'):
                    progress = float(progress.rstrip('%')) / 100
                else:
                    try:
                        progress = float(progress)
                    except ValueError:
                        return jsonify({"error": "Reading progress must be a number or percentage"}), 400
            elif not isinstance(progress, (int, float)):
                return jsonify({"error": "Reading progress must be a number"}), 400
            
            # Convert percentage to decimal if needed
            if progress > 1:
                progress = progress / 100
                
            if progress < 0 or progress > 1:
                return jsonify({"error": "Reading progress must be between 0 and 1 (or 0% to 100%)"}), 400
                
            # Convert to integer (0-100) since database column is INTEGER
            progress_int = int(progress * 100)
            update_fields.append("reading_progress = ?")
            update_values.append(progress_int)
            LOGGER.info(f"Updating reading_progress to: {progress_int}")
        
        if 'user_description' in data:
            description = data['user_description']
            if description is not None and not isinstance(description, str):
                return jsonify({"error": "User description must be a string"}), 400
            update_fields.append("user_description = ?")
            update_values.append(description)
            LOGGER.info(f"Updating user_description to: {description[:100] if description else None}...")
        
        if 'status' in data:
            status = data['status']
            if status is not None and not isinstance(status, str):
                return jsonify({"error": "Status must be a string"}), 400
            update_fields.append("status = ?")
            update_values.append(status)
            LOGGER.info(f"Updating status to: {status}")
        
        if not update_fields:
            return jsonify({"error": "No valid fields to update"}), 400
        
        # Add series_id to update values
        update_values.append(series_id)
        
        # Execute update query
        update_query = f"UPDATE series SET {', '.join(update_fields)} WHERE id = ?"
        LOGGER.info(f"Executing update query: {update_query}")
        
        execute_query(update_query, tuple(update_values), commit=True)
        LOGGER.info(f"Successfully updated series {series_id}")
        
        # Return updated series data
        updated_series = execute_query("SELECT * FROM series WHERE id = ?", (series_id,))
        if updated_series:
            return jsonify({"success": True, "series": updated_series[0]}), 200
        else:
            return jsonify({"error": "Failed to retrieve updated series"}), 500
    
    except Exception as e:
        import traceback
        LOGGER.error(f"Error updating series {series_id}: {e}")
        LOGGER.error(traceback.format_exc())
        return jsonify({"error": str(e)}), 500


@api_series_bp.route('/api/series/<int:series_id>', methods=['DELETE'])
def delete_series(series_id: int):
    """Delete a series and optionally its files.
    
    Args:
        series_id: The series ID.
        
    Request Body:
        remove_files (bool): Whether to also delete the series folder and files.
        
    Returns:
        Response: Success or error message.
    """
    try:
        # Get request body for remove_files option
        remove_files = False
        if request.is_json:
            data = request.json or {}
            remove_files = data.get('remove_files', False)
            LOGGER.info(f"Delete request for series {series_id} with remove_files={remove_files}")
        
        # Check if series exists
        series = execute_query("SELECT id, title, content_type, author FROM series WHERE id = ?", (series_id,))
        if not series:
            return jsonify({"error": "Series not found"}), 404
        
        series_data = series[0]  # Store the full series data
        series_title = series_data['title']
        content_type = series_data['content_type']
        
        LOGGER.info(f"Deleting series {series_id}: {series_title} (remove_files={remove_files})")
        
        # Start database transaction
        try:
            # Delete related records first (foreign key constraints)
            # Delete chapters
            execute_query("DELETE FROM chapters WHERE series_id = ?", (series_id,))
            LOGGER.info(f"Deleted chapters for series {series_id}")
            
            # Delete volumes
            execute_query("DELETE FROM volumes WHERE series_id = ?", (series_id,))
            LOGGER.info(f"Deleted volumes for series {series_id}")
            
            # Delete the series itself
            execute_query("DELETE FROM series WHERE id = ?", (series_id,), commit=True)
            LOGGER.info(f"Deleted series {series_id} from database")
            
            # If remove_files is True, also delete the folder
            if remove_files:
                try:
                    from backend.base.helpers import get_series_folder_path, get_book_folder_path
                    import os
                    import shutil
                    
                    # Debug logging
                    LOGGER.info(f"Attempting to delete files for {content_type}: {series_title} (ID: {series_id})")
                    LOGGER.info(f"Series data: {series_data}")
                    
                    # Get the appropriate folder path based on content type
                    if content_type and content_type.lower() in ['book', 'novel']:
                        # Books use root_folder/author_folder/book_folder structure
                        LOGGER.info(f"Using book folder path for content type: {content_type}")
                        folder_path = get_book_folder_path(series_id, series_title, series_data.get('author'))
                    else:
                        # Manga and others use root_folder/series_folder structure
                        LOGGER.info(f"Using series folder path for content type: {content_type}")
                        folder_path = get_series_folder_path(series_id, series_title, content_type)
                    
                    LOGGER.info(f"Determined folder path: {folder_path}")
                    LOGGER.info(f"Folder exists: {folder_path.exists() if folder_path else 'None path'}")
                    
                    if folder_path and folder_path.exists():
                        # Convert Path to string for shutil.rmtree
                        shutil.rmtree(str(folder_path))
                        LOGGER.info(f"Deleted {content_type} folder: {folder_path}")
                        
                        # For books, also check if author folder should be removed
                        if content_type and content_type.lower() in ['book', 'novel']:
                            author_folder = folder_path.parent
                            if author_folder.exists() and author_folder.is_dir():
                                try:
                                    # Check if author folder is empty (no book folders, but allow README.md)
                                    author_folder_contents = list(author_folder.iterdir())
                                    LOGGER.info(f"Author folder '{author_folder}' contains {len(author_folder_contents)} items")
                                    
                                    # Filter out README.md files - we only care about book folders
                                    book_folders = [item for item in author_folder_contents 
                                                  if item.is_dir() and not item.name.lower().endswith('.md')]
                                    
                                    LOGGER.info(f"Author folder '{author_folder}' contains {len(book_folders)} book folders")
                                    
                                    # Only remove author folder if there are no book folders
                                    if len(book_folders) == 0:
                                        # Check if only README.md files remain
                                        readme_files = [item for item in author_folder_contents 
                                                       if item.name.lower() == 'readme.md']
                                        
                                        if len(readme_files) > 0:
                                            LOGGER.info(f"Author folder '{author_folder}' only contains README.md files, keeping folder")
                                            message = f"{content_type.title()} '{series_title}' and all its files have been deleted successfully. Author folder preserved with README.md."
                                        else:
                                            # Truly empty folder - remove it
                                            shutil.rmtree(str(author_folder))
                                            LOGGER.info(f"Deleted empty author folder: {author_folder}")
                                            message = f"{content_type.title()} '{series_title}' and its empty author folder have been deleted successfully."
                                    else:
                                        LOGGER.info(f"Author folder '{author_folder}' has {len(book_folders)} book folders, keeping it")
                                        message = f"{content_type.title()} '{series_title}' and all its files have been deleted successfully."
                                except Exception as e:
                                    LOGGER.warning(f"Error checking/removing author folder {author_folder}: {e}")
                                    message = f"{content_type.title()} '{series_title}' and all its files have been deleted successfully."
                            else:
                                LOGGER.info(f"Author folder '{author_folder}' does not exist or is not a directory")
                                message = f"{content_type.title()} '{series_title}' and all its files have been deleted successfully."
                        else:
                            message = f"{content_type.title()} '{series_title}' and all its files have been deleted successfully."
                    else:
                        LOGGER.warning(f"{content_type.title()} folder not found for deletion: {folder_path}")
                        message = f"{content_type.title()} '{series_title}' deleted from database, but folder was not found."
                        
                except Exception as e:
                    LOGGER.error(f"Error deleting {content_type} folder for {series_id}: {e}")
                    import traceback
                    LOGGER.error(traceback.format_exc())
                    # Don't fail the whole operation if folder deletion fails
                    message = f"{content_type.title()} '{series_title}' deleted from database, but there was an error deleting the folder: {str(e)}"
            else:
                message = f"{content_type.title()} '{series_title}' deleted from database successfully. Folder and files preserved."
            
            return jsonify({
                "success": True,
                "message": message
            }), 200
            
        except Exception as e:
            LOGGER.error(f"Database error during series deletion: {e}")
            return jsonify({"error": f"Database error: {str(e)}"}), 500
            
    except Exception as e:
        LOGGER.error(f"Error deleting series {series_id}: {e}")
        return jsonify({"error": str(e)}), 500


@api_series_bp.route('/api/series/recent', methods=['GET'])
def get_recent_series():
    """Get recent series.
    
    Returns:
        Response: The recent series.
    """
    try:
        # Get query parameters
        content_type = request.args.get('content_type', 'all')
        limit = request.args.get('limit', 10, type=int)
        
        LOGGER.debug(f"get_recent_series called with content_type={content_type}, limit={limit}")
        
        # Ensure limit is reasonable
        if limit <= 0 or limit > 100:
            limit = 10
        
        # Build the query - simple and efficient
        if content_type == 'book':
            query = "SELECT * FROM series WHERE UPPER(content_type) IN ('BOOK', 'NOVEL') ORDER BY id DESC LIMIT ?"
        elif content_type == 'manga':
            query = "SELECT * FROM series WHERE UPPER(content_type) IN ('MANGA', 'MANHWA', 'MANHUA', 'COMIC') ORDER BY id DESC LIMIT ?"
        else:
            query = "SELECT * FROM series ORDER BY id DESC LIMIT ?"
        
        LOGGER.debug(f"Executing query: {query} with limit={limit}")
        
        # Execute the query
        series = execute_query(query, (limit,))
        
        LOGGER.debug(f"Query returned {len(series) if series else 0} series")
        
        return jsonify({
            "success": True,
            "series": series if series else []
        })
    except Exception as e:
        LOGGER.error(f"Error getting recent series: {e}", exc_info=True)
        return jsonify({
            "success": False,
            "message": f"Error getting recent series: {str(e)}",
            "series": []
        }), 500


@api_series_bp.route('/api/series/<int:series_id>/chapters', methods=['GET'])
def get_series_chapters(series_id: int):
    """Get all chapters for a series.
    
    Args:
        series_id: The ID of the series.
        
    Returns:
        Response: List of chapters for the series.
    """
    try:
        chapters = execute_query("""
            SELECT id, series_id, chapter_number, title, release_date, status, read_status
            FROM chapters 
            WHERE series_id = ?
            ORDER BY CAST(chapter_number AS INTEGER) ASC
        """, (series_id,))
        
        return jsonify(chapters if chapters else [])
    except Exception as e:
        LOGGER.error(f"Error getting chapters for series {series_id}: {e}")
        return jsonify({"error": str(e)}), 500


@api_series_bp.route('/api/series/<int:series_id>/volumes', methods=['GET'])
def get_series_volumes(series_id: int):
    """Get all volumes for a series.
    
    Args:
        series_id: The ID of the series.
        
    Returns:
        Response: List of volumes for the series.
    """
    try:
        volumes = execute_query("""
            SELECT id, series_id, volume_number, title, release_date, cover_url, cover_path
            FROM volumes 
            WHERE series_id = ?
            ORDER BY CAST(volume_number AS INTEGER) ASC
        """, (series_id,))
        
        return jsonify(volumes if volumes else [])
    except Exception as e:
        LOGGER.error(f"Error getting volumes for series {series_id}: {e}")
        return jsonify({"error": str(e)}), 500
