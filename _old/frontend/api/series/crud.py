#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Series CRUD operations service.
Handles create, read, update, delete operations for series.
"""

from backend.internals.db import execute_query
from backend.features.collection import add_series_to_collection, get_default_collection
from backend.base.helpers import create_series_folder_structure
from backend.base.logging import LOGGER


def create_series(data):
    """Create a new series.
    
    Args:
        data (dict): Series data.
        
    Returns:
        dict: Created series data or error.
    """
    try:
        # Validate required fields
        if not data.get("title"):
            return {"error": "Title is required"}, 400
        
        # Set default content type
        content_type = (data.get("content_type") or "MANGA").upper()
        
        LOGGER.info(f"Creating series with content type: {content_type}")
        
        # Check if series already exists (prevent duplicates)
        # First check by metadata_id if available (most reliable)
        metadata_id = data.get("metadata_id")
        metadata_source = data.get("metadata_source")
        
        if metadata_id and metadata_source:
            existing_series = execute_query("""
                SELECT id FROM series 
                WHERE metadata_id = ? AND metadata_source = ?
            """, (metadata_id, metadata_source))
            
            if existing_series:
                LOGGER.warning(f"Series with metadata_id {metadata_id} from {metadata_source} already exists with ID {existing_series[0]['id']}")
                return existing_series[0], 200  # Return existing series instead of creating duplicate
        
        # If not found by metadata, check by title
        existing_series = execute_query("""
            SELECT id FROM series 
            WHERE LOWER(title) = LOWER(?) AND content_type = ?
        """, (data.get("title"), content_type))
        
        if existing_series:
            LOGGER.warning(f"Series '{data.get('title')}' ({content_type}) already exists with ID {existing_series[0]['id']}")
            return existing_series[0], 200  # Return existing series instead of creating duplicate
        
        # Prepare genres/subjects as comma-separated string
        genres = data.get("genres", [])
        subjects_str = ",".join(genres) if isinstance(genres, list) else genres
        
        # Insert series
        series_id = execute_query("""
            INSERT INTO series (
                title, description, author, publisher, cover_url, status, 
                content_type, metadata_source, metadata_id, isbn, published_date, subjects
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data.get("title"),
            data.get("description"),
            data.get("author"),
            data.get("publisher"),
            data.get("cover_url"),
            data.get("status"),
            content_type,
            data.get("metadata_source"),
            data.get("metadata_id"),
            data.get("isbn", ""),
            data.get("published_date", ""),
            subjects_str
        ), commit=True)
        
        # Sync author if provided
        try:
            author_name = data.get("author")
            if author_name:
                from backend.features.authors_sync import sync_author_for_series
                sync_author_for_series(series_id, author_name)
        except Exception as e:
            LOGGER.warning(f"Failed to sync author for series {series_id}: {e}")
        
        # Link to collection
        try:
            collection_id = data.get("collection_id")
            if collection_id:
                try:
                    collection_id = int(collection_id)
                except Exception:
                    collection_id = None
            
            if collection_id:
                add_series_to_collection(collection_id, series_id)
            else:
                # Auto-link to default collection
                try:
                    default_coll = get_default_collection(content_type)
                    if default_coll and default_coll.get('id'):
                        add_series_to_collection(default_coll['id'], series_id)
                except Exception as e:
                    LOGGER.warning(f"Could not auto-link series to default collection: {e}")
        except Exception as e:
            LOGGER.warning(f"Link to collection failed: {e}")
        
        # Create folder structure with all metadata
        try:
            # Prepare metadata dict to pass to folder creation
            metadata_dict = {
                'metadata_source': data.get("metadata_source"),
                'metadata_id': data.get("metadata_id"),
                'author': data.get("author"),
                'publisher': data.get("publisher"),
                'isbn': data.get("isbn", ""),
                'published_date': data.get("published_date", ""),
                'subjects': subjects_str,  # Already prepared as comma-separated string
                'cover_url': data.get("cover_url")
            }
            
            series_path = create_series_folder_structure(
                series_id,
                data.get("title"),
                content_type,
                collection_id=data.get("collection_id"),
                root_folder_id=data.get("root_folder_id"),
                metadata=metadata_dict
            )
            LOGGER.info(f"Folder structure created at: {series_path}")
        except Exception as e:
            LOGGER.error(f"Error creating folder structure: {e}")
        
        # Get created series
        series = execute_query("""
            SELECT 
                id, title, description, author, publisher, cover_url, status, 
                content_type, metadata_source, metadata_id, created_at, updated_at
            FROM series
            WHERE id = ?
        """, (series_id,))
        
        return series[0] if series else {"error": "Failed to retrieve created series"}, 201
    except Exception as e:
        LOGGER.error(f"Error creating series: {e}")
        return {"error": str(e)}, 500


def read_series(series_id):
    """Read a series by ID with related data.
    
    Args:
        series_id (int): Series ID.
        
    Returns:
        dict: Series data with volumes and chapters or error.
    """
    try:
        series = execute_query("""
            SELECT 
                id, title, description, author, publisher, cover_url, status, 
                content_type, metadata_source, metadata_id, isbn, published_date, subjects,
                star_rating, reading_progress, user_description, custom_path,
                created_at, updated_at
            FROM series
            WHERE id = ?
        """, (series_id,))
        
        if not series:
            return {"error": "Series not found"}, 404
        
        series_data = series[0]
        
        # Convert subjects to genres for frontend compatibility
        if series_data.get('subjects'):
            subjects_list = [s.strip() for s in series_data['subjects'].split(',')] if isinstance(series_data['subjects'], str) else series_data['subjects']
            series_data['genres'] = subjects_list
        else:
            series_data['genres'] = []
        
        # Get volumes for this series
        volumes = execute_query("""
            SELECT * FROM volumes
            WHERE series_id = ?
            ORDER BY CAST(volume_number AS INTEGER)
        """, (series_id,))
        
        # Get chapters for this series
        chapters = execute_query("""
            SELECT * FROM chapters
            WHERE series_id = ?
            ORDER BY CAST(chapter_number AS REAL)
        """, (series_id,))
        
        # Get upcoming events (if available)
        upcoming_events = []
        try:
            upcoming_events = execute_query("""
                SELECT * FROM releases
                WHERE series_id = ?
                AND release_date >= DATE('now')
                ORDER BY release_date
                LIMIT 5
            """, (series_id,)) or []
        except Exception as e:
            LOGGER.debug(f"Could not fetch upcoming events (releases table may not exist): {e}")
            upcoming_events = []
        
        return {
            "series": series_data,
            "volumes": volumes or [],
            "chapters": chapters or [],
            "upcoming_events": upcoming_events or []
        }, 200
    except Exception as e:
        LOGGER.error(f"Error reading series: {e}")
        return {"error": str(e)}, 500


def update_series(series_id, data):
    """Update a series.
    
    Args:
        series_id (int): Series ID.
        data (dict): Update data.
        
    Returns:
        dict: Updated series data or error.
    """
    try:
        # Check if series exists and get current data
        series = execute_query("SELECT id, title, content_type FROM series WHERE id = ?", (series_id,))
        if not series:
            return {"error": "Series not found"}, 404
        
        old_title = series[0]['title']
        content_type = series[0]['content_type']
        
        # Build update query
        update_fields = []
        params = []
        
        # Handle genres -> subjects conversion
        if "genres" in data:
            genres = data["genres"]
            subjects_str = ",".join(genres) if isinstance(genres, list) else genres
            update_fields.append("subjects = ?")
            params.append(subjects_str)
        
        for field in ["title", "description", "author", "publisher", "cover_url", "status", "content_type", "metadata_source", "metadata_id", "custom_path", "isbn", "published_date"]:
            if field in data:
                update_fields.append(f"{field} = ?")
                params.append(data[field])
        
        if not update_fields:
            return {"error": "No fields to update"}, 400
        
        # Add updated_at and series_id
        update_fields.append("updated_at = CURRENT_TIMESTAMP")
        params.append(series_id)
        
        # Execute update
        execute_query(f"""
            UPDATE series
            SET {", ".join(update_fields)}
            WHERE id = ?
        """, tuple(params), commit=True)
        
        # Get updated series
        updated_series = execute_query("""
            SELECT 
                id, title, description, author, publisher, cover_url, status, 
                content_type, metadata_source, metadata_id, isbn, published_date, subjects,
                star_rating, reading_progress, user_description, custom_path,
                created_at, updated_at
            FROM series
            WHERE id = ?
        """, (series_id,))
        
        # Convert subjects to genres for frontend compatibility
        if updated_series and updated_series[0].get('subjects'):
            subjects_list = [s.strip() for s in updated_series[0]['subjects'].split(',')] if isinstance(updated_series[0]['subjects'], str) else updated_series[0]['subjects']
            updated_series[0]['genres'] = subjects_list
        elif updated_series:
            updated_series[0]['genres'] = []
        
        # If title was changed, rename the folder
        if "title" in data and data["title"] != old_title:
            try:
                from backend.base.helpers import rename_series_folder
                rename_series_folder(series_id, old_title, data["title"], content_type)
            except Exception as e:
                LOGGER.warning(f"Failed to rename series folder for series {series_id}: {e}")
        
        # Sync README.txt with updated metadata
        try:
            from backend.features.readme_sync import sync_series_to_readme
            sync_series_to_readme(series_id)
        except Exception as e:
            LOGGER.warning(f"Failed to sync README for series {series_id}: {e}")
        
        if updated_series:
            return {"success": True, "series": updated_series[0]}, 200
        else:
            return {"error": "Failed to retrieve updated series"}, 500
    except Exception as e:
        LOGGER.error(f"Error updating series: {e}")
        return {"error": str(e)}, 500


def delete_series(series_id):
    """Delete a series.
    
    Args:
        series_id (int): Series ID.
        
    Returns:
        dict: Status or error.
    """
    try:
        # Check if series exists
        series = execute_query("SELECT id, title FROM series WHERE id = ?", (series_id,))
        if not series:
            return {"error": "Series not found"}, 404
        
        series_title = series[0]['title']
        LOGGER.info(f"Deleting series {series_id}: {series_title} from database (README.txt will be preserved)")
        
        # Delete series from database only
        # NOTE: The series folder and README.txt file are NOT deleted - only the database entry
        execute_query("DELETE FROM series WHERE id = ?", (series_id,), commit=True)
        
        LOGGER.info(f"Series {series_id} deleted from database. Folder and README.txt preserved for manual recovery.")
        
        return {"success": True, "message": "Series deleted successfully. Folder and README.txt file preserved."}, 200
    except Exception as e:
        LOGGER.error(f"Error deleting series: {e}")
        return {"error": str(e)}, 500
