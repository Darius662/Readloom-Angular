#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import time
import hashlib
import re
from typing import Dict, List, Optional, Union, Tuple
from pathlib import Path

from backend.base.helpers import (
    get_ebook_storage_dir, organize_ebook_path, 
    copy_file_to_storage, ensure_dir_exists, get_safe_folder_name,
    read_metadata_from_readme
)
from backend.base.logging import LOGGER
from backend.internals.db import execute_query
from backend.features.collection import add_to_collection, update_collection_item


def add_ebook_file(series_id: int, volume_id: int, file_path: str, file_type: Optional[str] = None, max_retries: int = 5) -> Dict:
    """Add an e-book file to the database and storage.
    
    Args:
        series_id (int): The series ID.
        volume_id (int): The volume ID.
        file_path (str): The path to the e-book file.
        file_type (Optional[str]): The file type. If None, it will be detected from the file extension.
        max_retries (int, optional): Maximum number of retries for database operations. Defaults to 5.
        
    Returns:
        Dict: The file information if successful, empty dict otherwise.
    """
    retries = 0
    retry_delay = 0.5
    
    # Check if the file exists before entering retry loop
    source_path = Path(file_path)
    if not source_path.exists() or not source_path.is_file():
        LOGGER.error(f"File does not exist: {file_path}")
        return {}
    
    # Get file info
    file_name = source_path.name
    file_size = source_path.stat().st_size
    
    # Detect file type from extension if not provided
    if file_type is None:
        ext = source_path.suffix.lower()
        if ext in ['.pdf']:
            file_type = 'PDF'
        elif ext in ['.epub']:
            file_type = 'EPUB'
        elif ext in ['.cbz']:
            file_type = 'CBZ'
        elif ext in ['.cbr']:
            file_type = 'CBR'
        elif ext in ['.mobi']:
            file_type = 'MOBI'
        elif ext in ['.azw', '.azw3']:
            file_type = 'AZW'
        else:
            file_type = ext.lstrip('.')
    
    # Check if the file is already in a managed location
    from backend.internals.settings import Settings
    from backend.base.helpers import get_safe_folder_name as safe_folder_name
    settings = Settings().get_settings()
    root_folders = settings.root_folders
    
    # Get the series info for folder name comparison
    series_info = execute_query("SELECT title FROM series WHERE id = ?", (series_id,))
    if not series_info:
        LOGGER.error(f"Series with ID {series_id} not found")
        return {}
    
    series_title = series_info[0]['title']
    safe_series_title = safe_folder_name(series_title)
    
    # Check if the file is already in a managed location
    is_already_managed = False
    file_in_correct_location = False
    
    # Convert source_path to absolute path
    source_path_abs = source_path.absolute()
    LOGGER.info(f"Checking if file is already managed: {source_path_abs}")
    
    # Special case: if the source path contains the series name, consider it already managed
    if safe_series_title in str(source_path_abs):
        is_already_managed = True
        file_in_correct_location = True
        LOGGER.info(f"File is already in a folder with the series name: {source_path_abs}")
    else:
        # Check if file is in any root folder
        for root_folder in root_folders:
            root_path = Path(root_folder['path'])
            if str(source_path_abs).startswith(str(root_path)):
                # File is in a managed root folder
                is_already_managed = True
                
                # Check if it's in the correct series folder
                expected_series_path = root_path / safe_series_title
                if str(source_path_abs).startswith(str(expected_series_path)):
                    file_in_correct_location = True
                    LOGGER.info(f"File is already in the correct location: {source_path_abs}")
                    break
    
    if is_already_managed and file_in_correct_location:
        # Use the existing file path without copying
        target_path = source_path_abs
        unique_file_name = source_path.name
        LOGGER.info(f"Using existing file in managed location: {target_path}")
    else:
        # Generate a unique filename to prevent overwriting
        unique_file_name = file_name  # Use original filename without timestamp
        
        # Organize the file path
        target_path = organize_ebook_path(series_id, volume_id, unique_file_name)
        
        # Copy the file to the storage location if it's not already there
        if source_path_abs != target_path:
            LOGGER.info(f"Copying file from {source_path_abs} to {target_path}")
            if not copy_file_to_storage(source_path, target_path):
                LOGGER.error(f"Failed to copy file: {file_path}")
                return {}
        else:
            LOGGER.info(f"File is already at target path: {target_path}")

    
    # Start retry loop for database operations
    while retries <= max_retries:
        try:
            # Add file to the database
            try:
                # First try with RETURNING id
                result = execute_query("""
                INSERT INTO ebook_files (
                    series_id, volume_id, file_path, file_name, file_size,
                    file_type, original_name
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                RETURNING id
                """, (
                    series_id,
                    volume_id,
                    str(target_path),
                    unique_file_name,
                    file_size,
                    file_type,
                    file_name
                ), commit=True)
                
                # Get the inserted ID
                if result and len(result) > 0:
                    file_id = result[0]['id']
                    # Get the created file
                    file_info = get_ebook_file(file_id)
                else:
                    # If RETURNING id didn't work, get the last inserted ID
                    LOGGER.info(f"RETURNING id didn't work, trying to get last_insert_rowid() for: {Path(target_path).name}")
                    last_id_result = execute_query("SELECT last_insert_rowid() as id")
                    if last_id_result and len(last_id_result) > 0:
                        file_id = last_id_result[0]['id']
                        file_info = get_ebook_file(file_id)
                    else:
                        LOGGER.error(f"Failed to get ID for inserted file: {Path(target_path).name}")
                        file_info = None
            except Exception as e:
                LOGGER.error(f"Error during file insertion: {e}")
                # Try a simpler insert without RETURNING
                execute_query("""
                INSERT INTO ebook_files (
                    series_id, volume_id, file_path, file_name, file_size,
                    file_type, original_name
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    series_id,
                    volume_id,
                    str(target_path),
                    unique_file_name,
                    file_size,
                    file_type,
                    file_name
                ), commit=True)
                
                # Get the last inserted ID
                last_id_result = execute_query("SELECT last_insert_rowid() as id")
                if last_id_result and len(last_id_result) > 0:
                    file_id = last_id_result[0]['id']
                    file_info = get_ebook_file(file_id)
                else:
                    LOGGER.error(f"Failed to get ID for inserted file after fallback: {target_path}")
                    file_info = None
            
            if file_info:
                # Update the collection item to link to this file
                execute_query("""
                UPDATE collection_items 
                SET has_file = 1, ebook_file_id = ?,
                    digital_format = ?,
                    format = CASE
                        WHEN format = 'PHYSICAL' THEN 'BOTH'
                        ELSE 'DIGITAL'
                    END
                WHERE series_id = ? AND volume_id = ? AND item_type = 'VOLUME'
                """, (file_id, file_type, series_id, volume_id), commit=True)
            
            return file_info
        
        except Exception as e:
            if "database is locked" in str(e) and retries < max_retries:
                retries += 1
                LOGGER.warning(f"Database locked while adding e-book file, retrying ({retries}/{max_retries}) in {retry_delay}s")
                time.sleep(retry_delay)
                retry_delay *= 1.5
            else:
                LOGGER.error(f"Error adding e-book file: {e}")
                return {}
    
    LOGGER.error(f"Failed to add e-book file after {max_retries} retries")
    return {}


def get_ebook_file(file_id: int) -> Dict:
    """Get an e-book file by ID.
    
    Args:
        file_id (int): The file ID.
        
    Returns:
        Dict: The file information.
    """
    try:
        file_info = execute_query("""
        SELECT 
            id, series_id, volume_id, file_path, file_name, file_size,
            file_type, original_name, added_date, created_at, updated_at
        FROM ebook_files
        WHERE id = ?
        """, (file_id,))
        
        if file_info:
            return file_info[0]
        
        return {}
    
    except Exception as e:
        LOGGER.error(f"Error getting e-book file {file_id}: {e}")
        return {}


def get_ebook_files_for_volume(volume_id: int) -> List[Dict]:
    """Get all e-book files for a volume.
    
    Args:
        volume_id (int): The volume ID.
        
    Returns:
        List[Dict]: The file information.
    """
    try:
        files = execute_query("""
        SELECT 
            id, series_id, volume_id, file_path, file_name, file_size,
            file_type, original_name, added_date, created_at, updated_at
        FROM ebook_files
        WHERE volume_id = ?
        ORDER BY added_date DESC
        """, (volume_id,))
        
        return files
    
    except Exception as e:
        LOGGER.error(f"Error getting e-book files for volume {volume_id}: {e}")
        return []


def get_ebook_files_for_series(series_id: int) -> List[Dict]:
    """Get all e-book files for a series.
    
    Args:
        series_id (int): The series ID.
        
    Returns:
        List[Dict]: The file information.
    """
    try:
        files = execute_query("""
        SELECT 
            ef.id, ef.series_id, ef.volume_id, ef.file_path, ef.file_name, ef.file_size,
            ef.file_type, ef.original_name, ef.added_date, ef.created_at, ef.updated_at,
            v.volume_number, v.title as volume_title
        FROM ebook_files ef
        JOIN volumes v ON ef.volume_id = v.id
        WHERE ef.series_id = ?
        ORDER BY CAST(v.volume_number AS REAL), ef.added_date DESC
        """, (series_id,))
        
        return files
    
    except Exception as e:
        LOGGER.error(f"Error getting e-book files for series {series_id}: {e}")
        return []


def delete_ebook_file(file_id: int) -> bool:
    """Delete an e-book file.
    
    Args:
        file_id (int): The file ID.
        
    Returns:
        bool: True if successful, False otherwise.
    """
    try:
        # Get the file info
        file_info = get_ebook_file(file_id)
        
        if not file_info:
            return False
        
        # Delete the file from storage
        file_path = file_info.get('file_path')
        if file_path and os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception as e:
                LOGGER.error(f"Error deleting file {file_path}: {e}")
        
        # Update the collection item to unlink this file
        execute_query("""
        UPDATE collection_items 
        SET has_file = 0, ebook_file_id = NULL
        WHERE ebook_file_id = ?
        """, (file_id,), commit=True)
        
        # Delete the file from the database
        execute_query("""
        DELETE FROM ebook_files
        WHERE id = ?
        """, (file_id,), commit=True)
        
        return True
    
    except Exception as e:
        LOGGER.error(f"Error deleting e-book file {file_id}: {e}")
        return False


def fix_file_permissions(file_path: Path) -> bool:
    """Attempt to fix file permissions to make them readable.
    
    Args:
        file_path (Path): The file path.
        
    Returns:
        bool: True if permissions were fixed or file is already readable, False otherwise.
    """
    try:
        # Check if file is already readable
        if os.access(str(file_path), os.R_OK):
            return True
        
        # Try to make the file readable
        try:
            # Try chmod 644 (rw-r--r--)
            os.chmod(str(file_path), 0o644)
            LOGGER.info(f"Fixed permissions for file: {file_path}")
            return True
        except PermissionError:
            # If we don't have permission to change the file, try the parent directory
            try:
                parent_dir = file_path.parent
                if not os.access(str(parent_dir), os.R_OK | os.X_OK):
                    os.chmod(str(parent_dir), 0o755)
                    LOGGER.info(f"Fixed permissions for directory: {parent_dir}")
                    # Try again with the file
                    if os.access(str(file_path), os.R_OK):
                        return True
            except PermissionError:
                LOGGER.warning(f"Cannot fix permissions for {file_path}: Permission denied")
                return False
        
        return False
    except Exception as e:
        LOGGER.warning(f"Error attempting to fix file permissions for {file_path}: {e}")
        return False


def get_status_from_provider(metadata_source: str, metadata_id: str, content_type: str) -> Optional[str]:
    """Fetch the actual status from metadata provider using metadata_id.
    
    Args:
        metadata_source (str): The metadata provider (e.g., 'AniList', 'OpenLibrary')
        metadata_id (str): The ID from the metadata provider
        content_type (str): The content type (MANGA or BOOK)
        
    Returns:
        Optional[str]: The status from provider, or None if not found
    """
    try:
        if not metadata_source or not metadata_id:
            LOGGER.warning(f"Missing metadata_source or metadata_id: source={metadata_source}, id={metadata_id}")
            return None
        
        LOGGER.info(f"Fetching status from {metadata_source} for metadata_id {metadata_id}")
        
        if metadata_source == 'AniList' and content_type == 'MANGA':
            from backend.features.metadata_providers.anilist import AniListProvider
            provider = AniListProvider()
            
            # Get manga details by ID
            manga = provider.get_manga_details(str(metadata_id))
            if manga:
                status = manga.get('status')
                LOGGER.info(f"AniList returned status: {status} for metadata_id {metadata_id}")
                if status and status != 'Unknown':
                    LOGGER.info(f"Got status '{status}' from AniList for metadata_id {metadata_id}")
                    return status
            else:
                LOGGER.warning(f"No manga details returned from AniList for metadata_id {metadata_id}")
        
        elif metadata_source == 'OpenLibrary' and content_type == 'BOOK':
            from backend.features.metadata_providers.openlibrary import OpenLibraryProvider
            provider = OpenLibraryProvider()
            
            # Get book details by ID
            book = provider.get_manga_details(str(metadata_id))
            if book:
                status = book.get('status')
                LOGGER.info(f"OpenLibrary returned status: {status} for metadata_id {metadata_id}")
                if status and status != 'Unknown':
                    LOGGER.info(f"Got status '{status}' from OpenLibrary for metadata_id {metadata_id}")
                    return status
            else:
                LOGGER.warning(f"No book details returned from OpenLibrary for metadata_id {metadata_id}")
        
        LOGGER.warning(f"Could not fetch status from {metadata_source} (content_type={content_type})")
        return None
    except Exception as e:
        LOGGER.error(f"Error fetching status from {metadata_source} for metadata_id {metadata_id}: {e}", exc_info=True)
        return None


def enrich_series_metadata(series_id: int, series_title: str, content_type: str = 'MANGA') -> bool:
    """Enrich series metadata from appropriate metadata provider based on content type.
    
    This function now checks for existing metadata_id and metadata_source first,
    then uses those to fetch complete data from the provider (same as search import).
    
    Args:
        series_id (int): The series ID.
        series_title (str): The series title.
        content_type (str): The content type (MANGA or BOOK). Defaults to MANGA.
        
    Returns:
        bool: True if metadata was found and updated, False otherwise.
    """
    try:
        # Get current series data to preserve existing metadata from README
        current_series = execute_query(
            "SELECT status, author, description, cover_url, metadata_id, metadata_source FROM series WHERE id = ?",
            (series_id,)
        )
        current_status = current_series[0]['status'] if current_series else None
        current_author = current_series[0]['author'] if current_series else None
        current_description = current_series[0]['description'] if current_series else None
        current_cover_url = current_series[0]['cover_url'] if current_series else None
        existing_metadata_id = current_series[0].get('metadata_id') if current_series else None
        existing_metadata_source = current_series[0].get('metadata_source') if current_series else None
        
        # If we already have metadata_id and metadata_source, use them directly (faster path)
        if existing_metadata_id and existing_metadata_source:
            LOGGER.info(f"Using existing metadata_id={existing_metadata_id} from {existing_metadata_source} for series {series_id}")
            metadata_id = existing_metadata_id
            metadata_source = existing_metadata_source
            manga_details = None
            
            # Fetch full details directly using the metadata_id
            try:
                if metadata_source == 'AniList' and content_type == 'MANGA':
                    from backend.features.metadata_providers.anilist import AniListProvider
                    provider_instance = AniListProvider()
                    manga_details = provider_instance.get_manga_details(metadata_id)
                    if manga_details:
                        title = manga_details.get('title', series_title)
                        description = manga_details.get('description', '')
                        cover_url = manga_details.get('cover_url', '')
                        author = manga_details.get('author', 'Unknown')
                        provider_status = manga_details.get('status', 'Unknown')
                        status = provider_status if (not current_status or current_status == 'Unknown') else current_status
                    else:
                        LOGGER.warning(f"Could not fetch details from AniList for metadata_id {metadata_id}")
                        return False
                        
                elif metadata_source == 'OpenLibrary' and content_type == 'BOOK':
                    from backend.features.metadata_providers.openlibrary import OpenLibraryProvider
                    provider_instance = OpenLibraryProvider()
                    manga_details = provider_instance.get_manga_details(metadata_id)
                    if manga_details:
                        title = manga_details.get('title', series_title)
                        description = manga_details.get('description', '')
                        cover_url = manga_details.get('cover_url', '')
                        author = manga_details.get('author', 'Unknown')
                        provider_status = manga_details.get('status', 'Unknown')
                        status = provider_status if (not current_status or current_status == 'Unknown') else current_status
                    else:
                        LOGGER.warning(f"Could not fetch details from OpenLibrary for metadata_id {metadata_id}")
                        return False
                else:
                    LOGGER.warning(f"Unsupported metadata_source {metadata_source} for content_type {content_type}")
                    return False
                    
            except Exception as e:
                LOGGER.warning(f"Error fetching details using existing metadata_id: {e}")
                return False
        else:
            # No existing metadata_id, search for it
            LOGGER.info(f"No existing metadata_id found, searching provider for: {series_title}")
            manga_details = None
            
        if content_type == 'MANGA' and not existing_metadata_id:
            from backend.features.metadata_providers.anilist import AniListProvider
            
            # Create AniList provider instance
            provider = AniListProvider()
            
            # Search for the manga
            LOGGER.info(f"Searching AniList for: {series_title}")
            results = provider.search(series_title)
            
            if not results:
                LOGGER.warning(f"No results found on AniList for: {series_title}")
                return False
            
            # Get the first result (best match)
            manga = results[0]
            manga_details = provider.get_manga_details(manga.get('id', ''))
            
            # Extract metadata (using correct key names from AniListProvider response)
            title = manga_details.get('title', series_title) if manga_details else manga.get('title', series_title)
            description = manga_details.get('description', '') if manga_details else manga.get('description', '')
            cover_url = manga_details.get('cover_url', '') if manga_details else manga.get('cover_url', '')
            author = manga_details.get('author', 'Unknown') if manga_details else manga.get('author', 'Unknown')
            provider_status = manga_details.get('status', 'Unknown') if manga_details else manga.get('status', 'Unknown')
            status = provider_status if (not current_status or current_status == 'Unknown') else current_status
            metadata_id = manga_details.get('id', '') if manga_details else manga.get('id', '')
            metadata_source = 'AniList'
            
            # Preserve README metadata if it exists (prioritize README over provider data)
            if current_author and current_author.strip():
                author = current_author
            if current_description and current_description.strip():
                description = current_description
            if current_cover_url and current_cover_url.strip():
                cover_url = current_cover_url
            
        elif content_type == 'BOOK' and not existing_metadata_id:
            from backend.features.metadata_providers.openlibrary import OpenLibraryProvider
            
            # Create OpenLibrary provider instance
            provider = OpenLibraryProvider()
            
            # Search for the book
            LOGGER.info(f"Searching OpenLibrary for: {series_title}")
            results = provider.search(series_title)
            
            if not results:
                LOGGER.warning(f"No results found on OpenLibrary for: {series_title}")
                return False
            
            # Get the first result (best match)
            book_search = results[0]
            book_id = book_search.get('id', '')
            
            # Get full details including description
            if book_id:
                manga_details = provider.get_manga_details(book_id)
                if not manga_details:
                    manga_details = book_search
            else:
                manga_details = book_search
            
            # Extract metadata (using correct key names from OpenLibraryProvider response)
            title = manga_details.get('title', series_title)
            description = manga_details.get('description', '')
            cover_url = manga_details.get('cover_url', '')
            author = manga_details.get('author', 'Unknown')
            provider_status = manga_details.get('status', 'Unknown')
            status = provider_status if (not current_status or current_status == 'Unknown') else current_status
            metadata_id = manga_details.get('id', '')
            metadata_source = 'OpenLibrary'
            
            # Preserve README metadata if it exists (prioritize README over provider data)
            if current_author and current_author.strip():
                author = current_author
            if current_description and current_description.strip():
                description = current_description
            if current_cover_url and current_cover_url.strip():
                cover_url = current_cover_url
        elif not existing_metadata_id:
            LOGGER.warning(f"Unknown content type: {content_type}")
            return False
        
        # Update series in database with all metadata including status and metadata_id
        execute_query(
            """UPDATE series SET description = ?, cover_url = ?, author = ?, status = ?, metadata_source = ?, metadata_id = ?, updated_at = CURRENT_TIMESTAMP
               WHERE id = ?""",
            (description, cover_url, author, status, metadata_source, metadata_id, series_id),
            commit=True
        )
        
        LOGGER.info(f"Updated metadata for series {series_id}: {title} with cover, author, status ({status}), and metadata_id={metadata_id}")
        
        # Now populate volumes and chapters with release dates (same logic as search import)
        try:
            LOGGER.info(f"Fetching detailed metadata for series {series_id} to populate volumes and chapters")
            
            # Get full manga details including volumes and chapters
            if content_type == 'MANGA':
                from backend.features.metadata_providers.anilist import AniListProvider
                provider_instance = AniListProvider()
                manga_details = provider_instance.get_manga_details(metadata_id)
            elif content_type == 'BOOK':
                from backend.features.metadata_providers.openlibrary import OpenLibraryProvider
                provider_instance = OpenLibraryProvider()
                manga_details = provider_instance.get_manga_details(metadata_id)
            else:
                manga_details = None
            
            if manga_details:
                # Use the new helper function to populate volumes and chapters
                from backend.features.metadata_service.facade import populate_volumes_and_chapters
                chapters_added = populate_volumes_and_chapters(series_id, manga_details, metadata_source, metadata_id)
                LOGGER.info(f"Populated {chapters_added} chapters for series {series_id} during enrichment")
            else:
                LOGGER.warning(f"Could not fetch detailed metadata for series {series_id} to populate volumes/chapters")
        except Exception as e:
            LOGGER.warning(f"Error populating volumes and chapters for series {series_id}: {e}")
            # Continue anyway - we don't want to fail enrichment if volume population fails
        
        # Update calendar to include the newly populated volumes and chapters
        try:
            from backend.features.calendar import update_calendar
            LOGGER.info(f"Updating calendar for enriched series {series_id}")
            update_calendar(series_id=series_id)
        except Exception as e:
            LOGGER.warning(f"Error updating calendar after enrichment for series {series_id}: {e}")
            # Continue anyway - we don't want to fail enrichment if calendar update fails
        
        return True
        
    except Exception as e:
        LOGGER.warning(f"Error enriching metadata for series {series_id}: {e}")
        return False


def _process_series_directory(series_dir: Path) -> int:
    """Process a single series directory and create it if needed.
    
    Args:
        series_dir (Path): The series directory to process.
        
    Returns:
        int: 1 if a new series was created, 0 otherwise.
    """
    created_count = 0
    series_dir_name = series_dir.name
    
    # Read metadata from README if it exists
    readme_metadata = read_metadata_from_readme(series_dir)
    metadata_id = readme_metadata.get('metadata_id')
    metadata_source = readme_metadata.get('metadata_source')
    
    # Skip series if README.txt is not present (no metadata to import)
    if not readme_metadata or (not metadata_id and not metadata_source):
        LOGGER.info(f"Skipping series {series_dir_name}: README.txt not found or missing metadata")
        LOGGER.debug(f"  readme_metadata: {readme_metadata}")
        LOGGER.debug(f"  metadata_id: {metadata_id}, metadata_source: {metadata_source}")
        return created_count
    
    # Check if series already exists
    series_info = None
    
    # First, check by metadata_id if available (most reliable)
    if metadata_id and metadata_source:
        series_info = execute_query(
            "SELECT id, content_type FROM series WHERE metadata_id = ? AND metadata_source = ?",
            (metadata_id, metadata_source)
        )
        if series_info:
            LOGGER.info(f"Series already exists with metadata_id {metadata_id}: {series_info[0]['id']}")
            # Even though series exists, we still need to enrich it with volumes/chapters if not already done
            existing_series_id = series_info[0]['id']
            existing_content_type = series_info[0].get('content_type', 'MANGA')
            
            # Check if this series already has volumes
            existing_volumes = execute_query(
                "SELECT COUNT(*) as count FROM volumes WHERE series_id = ?",
                (existing_series_id,)
            )
            volume_count = existing_volumes[0]['count'] if existing_volumes else 0
            
            if volume_count == 0:
                LOGGER.info(f"Series {existing_series_id} has no volumes yet, enriching metadata to populate volumes/chapters")
                enrich_series_metadata(existing_series_id, series_dir_name, existing_content_type)
            else:
                LOGGER.info(f"Series {existing_series_id} already has {volume_count} volumes, skipping enrichment")
            
            return created_count
    
    # If not found by metadata, try by title (exact match)
    if not series_info:
        series_info = execute_query(
            "SELECT id, content_type FROM series WHERE title = ?",
            (series_dir_name,)
        )
    
    # If not found, try case-insensitive match
    if not series_info:
        series_info = execute_query(
            "SELECT id, content_type FROM series WHERE LOWER(title) = LOWER(?)",
            (series_dir_name,)
        )
    
    if not series_info:
        # Determine content type: first check README, then parent folder
        content_type = readme_metadata.get('type')
        if not content_type:
            # Fall back to parent folder name
            parent_name = series_dir.parent.name.upper()
            if 'BOOK' in parent_name or 'NOVEL' in parent_name:
                content_type = 'BOOK'
            else:
                content_type = 'MANGA'
        else:
            # Normalize the type from README
            content_type = content_type.upper()
        
        # Extract metadata from README if available
        description = readme_metadata.get('description', f"Auto-imported from {series_dir}")
        author = readme_metadata.get('author', '')
        publisher = readme_metadata.get('publisher', '')
        isbn = readme_metadata.get('isbn', '')
        cover_url = readme_metadata.get('cover_url', '')
        published_date = readme_metadata.get('published_date', '')
        
        # Convert subjects list to comma-separated string if it's a list
        subjects = readme_metadata.get('subjects', '')
        if isinstance(subjects, list):
            subjects = ','.join(subjects) if subjects else ''
        
        # Create new series with all metadata from README
        try:
            # Always start with 'ONGOING' - will be updated by enrich_series_metadata if needed
            status = 'ONGOING'
            
            # Use series title from README if available, otherwise use directory name
            series_title = readme_metadata.get('title') or series_dir_name
            
            # Get user data from README if available
            star_rating = readme_metadata.get('star_rating')
            reading_progress = readme_metadata.get('reading_progress')
            user_description = readme_metadata.get('user_description')
            
            execute_query(
                """INSERT INTO series (title, description, author, publisher, cover_url, status, content_type, 
                   metadata_source, metadata_id, isbn, published_date, subjects, star_rating, reading_progress, 
                   user_description, created_at, updated_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)""",
                (series_title, description, author, publisher, cover_url, status, content_type, 
                 metadata_source, metadata_id, isbn, published_date, subjects, star_rating, reading_progress, 
                 user_description),
                commit=True
            )
            LOGGER.info(f"Created new series: {series_title} ({content_type}) with metadata_id={metadata_id} and README metadata")
            created_count = 1
            
            # Get the newly created series ID - use a more specific query to avoid duplicates
            new_series = execute_query(
                "SELECT id FROM series WHERE title = ? AND content_type = ? ORDER BY id DESC LIMIT 1",
                (series_title, content_type)
            )
            
            if new_series:
                series_id = new_series[0]['id']
                
                # Sync author for this series
                if author:
                    try:
                        from backend.features.authors_sync import sync_author_for_series
                        LOGGER.info(f"Syncing author '{author}' for series {series_id}")
                        sync_author_for_series(series_id, author)
                    except Exception as e:
                        LOGGER.warning(f"Failed to sync author for series {series_id}: {e}")
                
                # Add series to the appropriate collection based on content type
                try:
                    from backend.features.collection import add_series_to_collection, get_default_collection
                    default_collection = get_default_collection(content_type)
                    if default_collection and default_collection.get('id'):
                        add_series_to_collection(default_collection['id'], series_id)
                        LOGGER.info(f"Added series {series_id} to {content_type} collection {default_collection['id']}")
                except Exception as e:
                    LOGGER.warning(f"Failed to add series to collection: {e}")
                
                # Always enrich metadata to get the correct status from provider
                # Even if we have complete metadata from README, we still need the real status
                LOGGER.info(f"Enriching metadata for series {series_id} to fetch status from provider")
                enrich_series_metadata(series_id, series_dir_name, content_type)
        except Exception as e:
            LOGGER.error(f"Error creating new series for {series_dir_name}: {e}")
    
    return created_count


def discover_and_create_series(root_path: Path) -> int:
    """Discover new series folders and create them in the database.
    
    Args:
        root_path (Path): The root path to scan for series folders.
        
    Returns:
        int: Number of new series created.
    """
    created_count = 0
    
    if not root_path.exists() or not root_path.is_dir():
        LOGGER.warning(f"Root folder does not exist or is not a directory: {root_path}")
        return created_count
    
    # Get all series directories directly in the root folder
    for series_dir in root_path.iterdir():
        if not series_dir.is_dir():
            continue
        
        series_dir_name = series_dir.name
        
        # Read metadata from README if it exists
        readme_metadata = read_metadata_from_readme(series_dir)
        metadata_id = readme_metadata.get('metadata_id')
        metadata_source = readme_metadata.get('metadata_source')
        
        # Check if this is an author folder (has book subdirectories with README files)
        # Do this FIRST before skipping
        has_book_subdirs = False
        book_subdirs = []
        try:
            for subdir in series_dir.iterdir():
                if subdir.is_dir():
                    # Check if subdirectory has a book README
                    sub_readme = read_metadata_from_readme(subdir)
                    if sub_readme.get('metadata_id') or sub_readme.get('metadata_source'):
                        has_book_subdirs = True
                        book_subdirs.append(subdir)
        except Exception:
            pass
        
        # If this is an author folder, process book subdirectories
        if has_book_subdirs:
            LOGGER.info(f"Detected author folder: {series_dir_name}, processing {len(book_subdirs)} book subdirectories")
            # Process each book subdirectory directly
            for book_dir in book_subdirs:
                created_count += _process_series_directory(book_dir)
            continue
        
        # Skip series if README.txt is not present (no metadata to import)
        if not readme_metadata or (not metadata_id and not metadata_source):
            LOGGER.info(f"Skipping series {series_dir_name}: README.txt not found or missing metadata")
            LOGGER.debug(f"  readme_metadata: {readme_metadata}")
            LOGGER.debug(f"  metadata_id: {metadata_id}, metadata_source: {metadata_source}")
            continue
        
        # Check if series already exists
        series_info = None
        
        # First, check by metadata_id if available (most reliable)
        if metadata_id and metadata_source:
            series_info = execute_query(
                "SELECT id, content_type FROM series WHERE metadata_id = ? AND metadata_source = ?",
                (metadata_id, metadata_source)
            )
            if series_info:
                LOGGER.info(f"Series already exists with metadata_id {metadata_id}: {series_info[0]['id']}")
                # Even though series exists, we still need to enrich it with volumes/chapters if not already done
                existing_series_id = series_info[0]['id']
                existing_content_type = series_info[0].get('content_type', 'MANGA')
                
                # Check if this series already has volumes
                existing_volumes = execute_query(
                    "SELECT COUNT(*) as count FROM volumes WHERE series_id = ?",
                    (existing_series_id,)
                )
                volume_count = existing_volumes[0]['count'] if existing_volumes else 0
                
                if volume_count == 0:
                    LOGGER.info(f"Series {existing_series_id} has no volumes yet, enriching metadata to populate volumes/chapters")
                    enrich_series_metadata(existing_series_id, series_dir_name, existing_content_type)
                else:
                    LOGGER.info(f"Series {existing_series_id} already has {volume_count} volumes, skipping enrichment")
                
                continue
        
        # If not found by metadata, try by title (exact match)
        if not series_info:
            series_info = execute_query(
                "SELECT id FROM series WHERE title = ?",
                (series_dir_name,)
            )
        
        # If not found, try case-insensitive match
        if not series_info:
            series_info = execute_query(
                "SELECT id FROM series WHERE LOWER(title) = LOWER(?)",
                (series_dir_name,)
            )
        
        if not series_info:
            # Determine content type based on parent folder
            parent_name = series_dir.parent.name.upper()
            if 'BOOK' in parent_name or 'NOVEL' in parent_name:
                content_type = 'BOOK'
            else:
                content_type = 'MANGA'
            
            # Extract metadata from README if available
            description = readme_metadata.get('description', f"Auto-imported from {series_dir}")
            author = readme_metadata.get('author', '')
            publisher = readme_metadata.get('publisher', '')
            isbn = readme_metadata.get('isbn', '')
            cover_url = readme_metadata.get('cover_url', '')
            published_date = readme_metadata.get('published_date', '')
            
            # Convert subjects list to comma-separated string if it's a list
            subjects = readme_metadata.get('subjects', '')
            if isinstance(subjects, list):
                subjects = ','.join(subjects) if subjects else ''
            
            # Create new series with all metadata from README
            try:
                # Use series title from README if available, otherwise use directory name
                series_title = readme_metadata.get('title') or series_dir_name
                
                execute_query(
                    """INSERT INTO series (title, description, author, publisher, cover_url, content_type, 
                       metadata_source, metadata_id, isbn, published_date, subjects, created_at, updated_at)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)""",
                    (series_title, description, author, publisher, cover_url, content_type, 
                     metadata_source, metadata_id, isbn, published_date, subjects),
                    commit=True
                )
                LOGGER.info(f"Created new series: {series_title} ({content_type}) with metadata_id={metadata_id} and README metadata")
                
                # Get the newly created series ID - use a more specific query to avoid duplicates
                new_series = execute_query(
                    "SELECT id FROM series WHERE title = ? AND content_type = ? ORDER BY id DESC LIMIT 1",
                    (series_title, content_type)
                )
                
                if new_series:
                    series_id = new_series[0]['id']
                    
                    # Sync author for this series
                    if author:
                        try:
                            from backend.features.authors_sync import sync_author_for_series
                            LOGGER.info(f"Syncing author '{author}' for series {series_id}")
                            sync_author_for_series(series_id, author)
                        except Exception as e:
                            LOGGER.warning(f"Failed to sync author for series {series_id}: {e}")
                    
                    # Always enrich metadata to get the correct status from provider
                    # Even if we have complete metadata from README, we still need the real status
                    LOGGER.info(f"Enriching metadata for series {series_id} to fetch status from provider")
                    enrich_series_metadata(series_id, series_dir_name, content_type)
                
                created_count += 1
            except Exception as e:
                LOGGER.error(f"Error creating new series for {series_dir_name}: {e}")
    
    return created_count


def scan_for_ebooks(specific_series_id: Optional[int] = None, custom_path: Optional[str] = None, content_type_filter: Optional[str] = None) -> Dict:
    """Scan the data directory for e-book files and add them to the database.
    
    Args:
        specific_series_id (Optional[int]): If provided, only scan for this specific series.
        custom_path (Optional[str]): Custom path for series-specific scanning.
        content_type_filter (Optional[str]): Filter by content type ('book' or 'manga').
        
    Returns:
        Dict: Statistics about the scan.
    """
    LOGGER.info(f"Starting e-book scan with specific_series_id={specific_series_id}, custom_path={custom_path}, content_type_filter={content_type_filter}")
    try:
        stats = {
            'scanned': 0,
            'added': 0,
            'skipped': 0,
            'errors': 0,
            'series_processed': 0
        }
        
        # Get root folders from settings
        from backend.internals.settings import Settings
        settings = Settings().get_settings()
        root_folders = settings.root_folders
        
        # If no root folders configured, use default ebook storage
        if not root_folders:
            LOGGER.warning("No root folders configured, using default ebook storage")
            # Get the e-book storage directory
            ebook_dir = get_ebook_storage_dir()
            root_paths = [ebook_dir]
        else:
            # Use all configured root folders
            root_paths = [Path(folder['path']) for folder in root_folders]
            LOGGER.info(f"Using {len(root_paths)} root folders for scanning")
        
        # Separate root folders by content type
        manga_root_paths = []
        book_root_paths = []
        for folder in root_folders:
            content_type = (folder.get('content_type') or 'MANGA').upper()
            if content_type == 'MANGA':
                manga_root_paths.append(Path(folder['path']))
            elif content_type == 'BOOK':
                book_root_paths.append(Path(folder['path']))
        
        # Apply content type filter if specified
        if content_type_filter:
            content_type_filter = content_type_filter.upper()
            LOGGER.info(f"Applying content type filter: {content_type_filter}")
            
            if content_type_filter == 'MANGA':
                book_root_paths = []  # Only scan manga folders
                LOGGER.info("Content type filter: Only scanning manga folders")
            elif content_type_filter == 'BOOK':
                manga_root_paths = []  # Only scan book folders
                LOGGER.info("Content type filter: Only scanning book folders")
            else:
                LOGGER.warning(f"Unknown content type filter: {content_type_filter}. Scanning all folders.")
        
        LOGGER.info(f"Manga root folders: {len(manga_root_paths)}, Book root folders: {len(book_root_paths)}")
        
        # If scanning for a specific series, get its details
        if specific_series_id:
            # Get series info with all needed fields
            series_info = execute_query(
                "SELECT title, content_type, custom_path FROM series WHERE id = ?", 
                (specific_series_id,)
            )
            
            if not series_info:
                return {'error': f"Series with ID {specific_series_id} not found"}
            
            # Get series title and content type
            series_title = series_info[0]['title']
            content_type = series_info[0]['content_type']
            
            # Get custom path if it exists
            try:
                series_custom_path = series_info[0]['custom_path']
                if series_custom_path:
                    LOGGER.info(f"Found custom path for series {specific_series_id}: {series_custom_path}")
            except (KeyError, IndexError):
                LOGGER.warning(f"No custom path found for series {specific_series_id}")
                series_custom_path = None
            from backend.base.helpers import get_safe_folder_name
            safe_title = get_safe_folder_name(series_title)
            
            LOGGER.info(f"Scanning for series: {series_title} (ID: {specific_series_id})")
            LOGGER.info(f"Safe folder name: {safe_title}")
            
            # Only scan this specific series directory in all root folders
            series_dirs = []
            
            # Check if a custom path was provided in the function call
            if custom_path:
                LOGGER.info(f"Using provided custom path from function call: {custom_path}")
                custom_path_obj = Path(custom_path)
                if custom_path_obj.exists() and custom_path_obj.is_dir():
                    LOGGER.info(f"Custom path exists: {custom_path}")
                    series_dirs.append((custom_path_obj, content_type, specific_series_id))
                    # If we have a custom path, we don't need to check the standard paths
            # Check if the series has a custom path in the database
            elif series_custom_path:
                LOGGER.info(f"Using custom path from database: {series_custom_path}")
                custom_path_obj = Path(series_custom_path)
                if custom_path_obj.exists() and custom_path_obj.is_dir():
                    LOGGER.info(f"Custom path exists: {series_custom_path}")
                    series_dirs.append((custom_path_obj, content_type, specific_series_id))
                    # If we have a custom path, we don't need to check the standard paths
                else:
                    LOGGER.warning(f"Custom path does not exist or is not a directory: {custom_path}")
            
            # Also check standard root folders if no custom path was found
            if not series_dirs:
                for root_path in root_paths:
                    LOGGER.info(f"Checking root path: {root_path}")
                    series_dir = root_path / safe_title
                    LOGGER.info(f"Looking for series directory: {series_dir}")
                    
                    if series_dir.exists() and series_dir.is_dir():
                        LOGGER.info(f"Found series directory: {series_dir}")
                        series_dirs.append((series_dir, content_type, specific_series_id))
                    else:
                        LOGGER.warning(f"Series directory not found: {series_dir}")
                    
            # If no directories found, try to look for the exact path
            if not series_dirs and specific_series_id:
                # Try the exact path that might be stored in the database
                exact_path = execute_query(
                    "SELECT folder_path FROM series_folders WHERE series_id = ?",
                    (specific_series_id,)
                )
                
                if exact_path and exact_path[0]['folder_path']:
                    path_obj = Path(exact_path[0]['folder_path'])
                    LOGGER.info(f"Trying exact path from database: {path_obj}")
                    if path_obj.exists() and path_obj.is_dir():
                        LOGGER.info(f"Exact path exists: {path_obj}")
                        series_dirs.append((path_obj, content_type, specific_series_id))
                    else:
                        LOGGER.warning(f"Exact path does not exist or is not a directory: {path_obj}")
        else:
            # Initialize series directories
            series_dirs = []
            
            # First, discover and create any new series (separate manga and books)
            LOGGER.info("Discovering new series folders...")
            LOGGER.info(f"Manga root paths: {manga_root_paths}")
            LOGGER.info(f"Book root paths: {book_root_paths}")
            
            for root_path in manga_root_paths:
                LOGGER.info(f"Scanning manga root folder: {root_path}")
                created = discover_and_create_series(root_path)
                if created > 0:
                    LOGGER.info(f"Created {created} new manga series in {root_path}")
            for root_path in book_root_paths:
                LOGGER.info(f"Scanning book root folder: {root_path}")
                created = discover_and_create_series(root_path)
                if created > 0:
                    LOGGER.info(f"Created {created} new book series in {root_path}")
            
            LOGGER.info("Series discovery complete, now processing for e-book files...")
            
            # Process each manga root folder
            for root_path in manga_root_paths:
                if not root_path.exists() or not root_path.is_dir():
                    LOGGER.warning(f"Root folder does not exist or is not a directory: {root_path}")
                    continue
                    
                # Get all series directories directly in the root folder
                for series_dir in root_path.iterdir():
                    if not series_dir.is_dir():
                        continue
                    
                    # Check if this is an author folder by looking for book subdirectories
                    # Author folders are identified by having subdirectories with book READMEs
                    has_book_subdirs = False
                    book_subdirs = []
                    try:
                        for subdir in series_dir.iterdir():
                            if subdir.is_dir():
                                sub_readme = read_metadata_from_readme(subdir)
                                if sub_readme.get('metadata_id'):
                                    has_book_subdirs = True
                                    book_subdirs.append(subdir)
                    except Exception:
                        pass
                    
                    if has_book_subdirs:
                        LOGGER.info(f"Detected author folder: {series_dir.name}, processing {len(book_subdirs)} book subdirectories")
                        # Process each book subdirectory directly
                        for book_dir in book_subdirs:
                            # Try to find the series in the database
                            book_dir_name = book_dir.name
                            book_readme = read_metadata_from_readme(book_dir)
                            book_metadata_id = book_readme.get('metadata_id')
                            book_metadata_source = book_readme.get('metadata_source')
                            
                            book_series_info = None
                            if book_metadata_id and book_metadata_source:
                                book_series_info = execute_query(
                                    "SELECT id, content_type FROM series WHERE metadata_id = ? AND metadata_source = ?",
                                    (book_metadata_id, book_metadata_source)
                                )
                            
                            if book_series_info:
                                series_dirs.append((book_dir, book_series_info[0]['content_type'], book_series_info[0]['id']))
                        continue
                    
                    # If not an author folder, treat it as a direct book folder
                    # Try to find the series in the database
                    series_dir_name = series_dir.name
                    LOGGER.info(f"Checking if {series_dir_name} is a book series (not an author folder)")
                    
                    # First, try to read metadata from README if it exists
                    readme_metadata = read_metadata_from_readme(series_dir)
                    metadata_id = readme_metadata.get('metadata_id')
                    metadata_source = readme_metadata.get('metadata_source')
                    
                    # Skip if README.txt is not present (no metadata to import)
                    if not readme_metadata or (not metadata_id and not metadata_source):
                        LOGGER.debug(f"Skipping book series {series_dir_name}: README.txt not found or missing metadata")
                        continue
                    
                    series_info = None
                    
                    # If metadata is available, check by metadata_id first (most reliable)
                    if metadata_id and metadata_source:
                        LOGGER.info(f"Found metadata in README: {metadata_source} ID {metadata_id}")
                        series_info = execute_query(
                            "SELECT id, content_type FROM series WHERE metadata_id = ? AND metadata_source = ?",
                            (metadata_id, metadata_source)
                        )
                        if series_info:
                            LOGGER.info(f"Found book series by metadata_id: {series_info[0]['id']}")
                    
                    # If not found by metadata, try exact match by title
                    if not series_info:
                        series_info = execute_query(
                            "SELECT id, content_type FROM series WHERE title = ?", 
                            (series_dir_name,)
                        )
                    
                    # If not found, try case-insensitive match
                    if not series_info:
                        series_info = execute_query(
                            "SELECT id, content_type FROM series WHERE LOWER(title) = LOWER(?)", 
                            (series_dir_name,)
                        )
                    
                    if series_info:
                        series_dirs.append((series_dir, series_info[0]['content_type'], series_info[0]['id']))
                        LOGGER.info(f"Added book series {series_info[0]['id']} to processing list")
                    else:
                        LOGGER.debug(f"Book series not found in database: {series_dir_name}")
            
            # Process each book root folder
            for root_path in book_root_paths:
                if not root_path.exists() or not root_path.is_dir():
                    LOGGER.warning(f"Root folder does not exist or is not a directory: {root_path}")
                    continue
                    
                # Get all series directories directly in the root folder (author folders for books)
                for series_dir in root_path.iterdir():
                    if not series_dir.is_dir():
                        continue
                    
                    # Check if this is an author folder by looking for book subdirectories
                    has_book_subdirs = False
                    book_subdirs = []
                    try:
                        for subdir in series_dir.iterdir():
                            if subdir.is_dir():
                                sub_readme = read_metadata_from_readme(subdir)
                                if sub_readme.get('metadata_id'):
                                    has_book_subdirs = True
                                    book_subdirs.append(subdir)
                    except Exception:
                        pass
                    
                    if has_book_subdirs:
                        LOGGER.info(f"Detected author folder: {series_dir.name}, processing {len(book_subdirs)} book subdirectories")
                        # Process each book subdirectory directly
                        for book_dir in book_subdirs:
                            # Try to find the series in the database
                            book_dir_name = book_dir.name
                            book_readme = read_metadata_from_readme(book_dir)
                            book_metadata_id = book_readme.get('metadata_id')
                            book_metadata_source = book_readme.get('metadata_source')
                            
                            book_series_info = None
                            if book_metadata_id and book_metadata_source:
                                book_series_info = execute_query(
                                    "SELECT id, content_type FROM series WHERE metadata_id = ? AND metadata_source = ?",
                                    (book_metadata_id, book_metadata_source)
                                )
                            
                            if book_series_info:
                                series_dirs.append((book_dir, book_series_info[0]['content_type'], book_series_info[0]['id']))
        
        # Define supported file extensions
        supported_extensions = {
            '.pdf': 'PDF',
            '.epub': 'EPUB',
            '.cbz': 'CBZ',
            '.cbr': 'CBR',
            '.mobi': 'MOBI',
            '.azw': 'AZW',
            '.azw3': 'AZW'
        }
        
        # Process each series directory
        for series_dir, content_type, series_id in series_dirs:
            if not series_dir.is_dir():
                LOGGER.warning(f"Skipping {series_dir} as it's not a directory")
                continue
            
            LOGGER.info(f"Processing directory: {series_dir} for series ID: {series_id}")
            
            if not series_id:
                stats['errors'] += 1
                continue
            
            # Get series title and metadata from database
            series_title_info = execute_query("SELECT title, metadata_source, metadata_id, author, cover_url, description, content_type FROM series WHERE id = ?", (series_id,))
            series_title = series_title_info[0]['title'] if series_title_info else series_dir.name
            series_content_type = series_title_info[0]['content_type'] if series_title_info else 'UNKNOWN'
            
            # Apply content type filter if specified
            if content_type_filter:
                content_type_filter = content_type_filter.upper()
                if series_content_type.upper() != content_type_filter:
                    LOGGER.info(f"Skipping series {series_id} ({series_title}) - content type {series_content_type} does not match filter {content_type_filter}")
                    continue
            
            # Enrich metadata if not already enriched (for MANGA and BOOK content types)
            if series_title_info and content_type in ('MANGA', 'BOOK'):
                metadata_source = series_title_info[0].get('metadata_source')
                metadata_id = series_title_info[0].get('metadata_id')
                author = series_title_info[0].get('author')
                cover_url = series_title_info[0].get('cover_url')
                description = series_title_info[0].get('description')
                
                # Only enrich if we're missing important display fields (description, author, cover)
                # Always enrich metadata to get the correct status from provider
                # Even if we have complete metadata from README, we still need the real status
                LOGGER.info(f"Enriching metadata for series {series_id}: {series_title} to fetch status from provider")
                enrich_series_metadata(series_id, series_title, content_type)
            
            stats['series_processed'] += 1
            LOGGER.info(f"Processing series: {series_title} (ID: {series_id})")
            
            # Keep track of processed files to avoid duplicates
            processed_files = set()
            
            # Process each file in the series directory (recursive)
            LOGGER.info(f"Scanning directory {series_dir} for e-book files")
            try:
                # Check if we have permission to access the directory
                if not os.access(str(series_dir), os.R_OK):
                    LOGGER.error(f"No read permission for directory: {series_dir}")
                    stats['errors'] += 1
                    all_files = []
                else:
                    LOGGER.info(f"Have read permission for directory: {series_dir}")
                    all_files = list(series_dir.glob('**/*'))
                    LOGGER.info(f"Found {len(all_files)} total files/directories")
                    # Log the first 10 files for debugging
                    for i, f in enumerate(all_files[:10]):
                        LOGGER.debug(f"File {i}: {f} (is_file: {f.is_file()})")
            except Exception as e:
                LOGGER.error(f"Error listing files in directory {series_dir}: {e}")
                all_files = []
            
            for file_path in all_files:
                if not file_path.is_file():
                    continue
                    
                LOGGER.debug(f"Checking file: {file_path.name}")
                    
                # Skip if already processed (can happen with symlinks)
                file_key = str(file_path.resolve())
                if file_key in processed_files:
                    LOGGER.debug(f"Skipping already processed file: {file_path.name}")
                    continue
                    
                processed_files.add(file_key)
                
                # Try to fix file permissions if not readable
                if not os.access(str(file_path), os.R_OK):
                    LOGGER.debug(f"File not readable, attempting to fix permissions: {file_path.name}")
                    if fix_file_permissions(file_path):
                        LOGGER.debug(f"Successfully fixed permissions for: {file_path.name}")
                    else:
                        LOGGER.warning(f"Could not fix permissions for: {file_path.name}, skipping")
                        stats['skipped'] = stats.get('skipped', 0) + 1
                        continue
                
                # Get file extension and check if supported
                file_ext = file_path.suffix.lower()
                
                # Special handling for CBZ files
                if file_ext == '.cbz':
                    LOGGER.debug(f"Found CBZ file: {file_path.name}")
                
                if file_ext not in supported_extensions:
                    LOGGER.debug(f"Skipping unsupported file type: {file_path.name}")
                    stats['skipped'] = stats.get('skipped', 0) + 1
                    continue
                else:
                    LOGGER.debug(f"Found supported file type: {file_ext} for file {file_path.name}")
                    # Count this file as scanned
                    stats['scanned'] = stats.get('scanned', 0) + 1
                    
                LOGGER.info(f"Found supported file: {file_path.name} with extension {file_ext}")
                
                # Extract volume number from filename or path
                LOGGER.debug(f"Attempting to extract volume number from {file_path.name}")
                volume_number = extract_volume_number(file_path)
                
                if not volume_number:
                    LOGGER.warning(f"Could not extract volume number from {file_path}")
                    stats['skipped'] = stats.get('skipped', 0) + 1
                    continue
                
                LOGGER.info(f"Successfully extracted volume number: {volume_number} from {file_path}")
                
                # Get or create volume
                volume_id = get_or_create_volume(series_id, volume_number)
                
                if not volume_id:
                    LOGGER.error(f"Failed to get or create volume for series {series_id}, volume {volume_number}")
                    stats['errors'] = stats.get('errors', 0) + 1
                    continue
                    
                LOGGER.info(f"Using volume ID: {volume_id} for volume {volume_number}")
                
                # Check if file already exists in database
                existing_files = get_ebook_files_for_volume(volume_id)
                LOGGER.info(f"Found {len(existing_files)} existing files for volume {volume_id}")
                
                # Check if file path matches or if file is identical (same path after resolving symlinks)
                file_exists = False
                for ef in existing_files:
                    if not os.path.exists(ef['file_path']):
                        LOGGER.debug(f"Existing file path not found: {ef['file_path']}")
                        continue
                        
                    try:
                        if os.path.samefile(file_path, Path(ef['file_path'])):
                            LOGGER.info(f"File already exists in database: {file_path}")
                            file_exists = True
                            break
                    except OSError as e:
                        LOGGER.warning(f"Error comparing files: {e}")
                        # Handle case where files can't be compared
                        pass
                
                if file_exists:
                    LOGGER.info(f"Skipping existing file: {file_path}")
                    stats['skipped'] = stats.get('skipped', 0) + 1
                    continue
                
                # Get file type from extension
                file_type = supported_extensions[file_ext]
                LOGGER.info(f"File type: {file_type} for file: {file_path}")
                
                # Add file to database
                LOGGER.info(f"Adding file to database: {file_path}")
                file_info = add_ebook_file(series_id, volume_id, str(file_path), file_type)
                
                if file_info:
                    stats['added'] = stats.get('added', 0) + 1
                    LOGGER.info(f"Successfully added file: {file_path.name} as Volume {volume_number}")
                    
                    # Update collection item to mark it as having a file
                    update_collection_for_volume(series_id, volume_id, file_type)
                else:
                    LOGGER.error(f"Failed to add file to database: {file_path.name}")
                    stats['errors'] = stats.get('errors', 0) + 1
        
        # Also scan for folder-based structures (Volume folders with Individual Images)
        LOGGER.info("Scanning for folder-based volume structures...")
        for series_dir, content_type, series_id in series_dirs:
            if series_dir.is_dir():
                folder_stats = scan_folder_structure(series_id, series_dir)
                # Merge folder stats into main stats
                if folder_stats.get('volumes_found', 0) > 0:
                    stats['added'] = stats.get('added', 0) + folder_stats.get('volumes_found', 0)
                if folder_stats.get('errors', 0) > 0:
                    stats['errors'] = stats.get('errors', 0) + folder_stats.get('errors', 0)
        
        # Log the final stats
        LOGGER.info(f"Scan completed with stats: {stats}")
        
        # Update the calendar to include any newly discovered series with release dates
        try:
            from backend.features.calendar import update_calendar
            LOGGER.info("Updating calendar after e-book scan...")
            update_calendar()
            LOGGER.info("Calendar updated successfully after e-book scan")
        except Exception as e:
            LOGGER.error(f"Error updating calendar after e-book scan: {e}")
            # Continue anyway - we don't want to fail the scan if calendar update fails
        
        # Convert any None values to 0 to avoid 'undefined' in the UI
        for key in stats:
            if stats[key] is None:
                stats[key] = 0
                
        # Make sure all required keys exist
        required_keys = ['scanned', 'added', 'skipped', 'errors', 'series_processed']
        for key in required_keys:
            if key not in stats:
                stats[key] = 0
                
        LOGGER.info(f"Final stats after cleanup: {stats}")
        return stats
    
    except Exception as e:
        LOGGER.error(f"Error scanning for e-books: {e}")
        return {'error': str(e), 'scanned': 0, 'added': 0, 'skipped': 0, 'errors': 1, 'series_processed': 0}


def get_or_create_series(title: str, content_type: str) -> Optional[int]:
    """Get or create a series with the given title and content type.
    
    Args:
        title (str): The series title.
        content_type (str): The content type.
        
    Returns:
        Optional[int]: The series ID, or None if an error occurred.
    """
    try:
        # Check if series exists
        series = execute_query("""
        SELECT id FROM series WHERE title = ?
        """, (title,))
        
        if series:
            # Update content type if needed
            execute_query("""
            UPDATE series SET content_type = ? WHERE id = ?
            """, (content_type, series[0]['id']), commit=True)
            
            return series[0]['id']
        
        # Create new series
        series_id = execute_query("""
        INSERT INTO series (title, content_type)
        VALUES (?, ?)
        """, (title, content_type), commit=True)
        
        return series_id
    
    except Exception as e:
        LOGGER.error(f"Error getting/creating series: {e}")
        return None


def update_collection_for_volume(series_id: int, volume_id: int, file_type: str) -> bool:
    """Update the collection item for a volume when a file is found.
    
    Args:
        series_id (int): The series ID.
        volume_id (int): The volume ID.
        file_type (str): The file type (PDF, EPUB, etc.).
        
    Returns:
        bool: True if successful, False otherwise.
    """
    try:
        # Check if collection item exists
        collection_item = execute_query("""
        SELECT id, format, digital_format, has_file FROM collection_items 
        WHERE series_id = ? AND volume_id = ? AND item_type = 'VOLUME'
        """, (series_id, volume_id))
        
        if collection_item:
            # Update existing collection item
            item_id = collection_item[0]['id']
            current_format = collection_item[0]['format']
            
            # Determine the new format
            new_format = current_format
            if current_format == 'PHYSICAL':
                new_format = 'BOTH'
            elif current_format == 'NONE' or not current_format:
                new_format = 'DIGITAL'
            
            # Update the collection item
            update_collection_item(
                item_id=item_id,
                format=new_format,
                digital_format=file_type,
                has_file=1
            )
        else:
            # Create new collection item
            add_to_collection(
                series_id=series_id,
                volume_id=volume_id,
                item_type='VOLUME',
                ownership_status='OWNED',
                read_status='UNREAD',
                format='DIGITAL',
                digital_format=file_type,
                has_file=1
            )
        
        return True
    
    except Exception as e:
        LOGGER.error(f"Error updating collection for volume {volume_id}: {e}")
        return False


def get_or_create_volume(series_id: int, volume_number: str, max_retries: int = 5) -> Optional[int]:
    """Get or create a volume with the given series ID and volume number.
    
    Args:
        series_id (int): The series ID.
        volume_number (str): The volume number.
        max_retries (int, optional): Maximum number of retries. Defaults to 5.
        
    Returns:
        Optional[int]: The volume ID, or None if an error occurred.
    """
    retries = 0
    retry_delay = 0.5
    
    while retries <= max_retries:
        try:
            # Check if volume exists
            volume = execute_query("""
            SELECT id FROM volumes WHERE series_id = ? AND volume_number = ?
            """, (series_id, volume_number))
            
            if volume:
                return volume[0]['id']
            
            # Create new volume
            volume_id = execute_query("""
            INSERT INTO volumes (series_id, volume_number)
            VALUES (?, ?)
            """, (series_id, volume_number), commit=True)
            
            return volume_id
        
        except Exception as e:
            if "database is locked" in str(e) and retries < max_retries:
                retries += 1
                LOGGER.warning(f"Database locked while getting/creating volume, retrying ({retries}/{max_retries}) in {retry_delay}s")
                time.sleep(retry_delay)
                retry_delay *= 1.5
            else:
                LOGGER.error(f"Error getting/creating volume: {e}")
                return None
    
    LOGGER.error(f"Failed to get/create volume after {max_retries} retries")
    return None


def scan_folder_structure(series_id: int, series_dir: Path) -> Dict:
    """Scan for folder-based volume structure with individual images.
    
    Identifies Volume folders and creates them as Digital volumes with Individual Images format.
    Does NOT scan chapters or individual image files.
    
    Supports structures like:
    MangaTitle/
        Volume1/
            (any files/folders inside)
        Volume2/
            (any files/folders inside)
    
    Args:
        series_id (int): The series ID.
        series_dir (Path): The series directory.
        
    Returns:
        Dict: Statistics about the scan.
    """
    stats = {
        'volumes_found': 0,
        'errors': 0
    }
    
    try:
        # Look for volume folders (first level subdirectories)
        volume_folders = [d for d in series_dir.iterdir() if d.is_dir()]
        
        if not volume_folders:
            LOGGER.info(f"No volume folders found in {series_dir.name}")
            return stats
        
        for volume_folder in volume_folders:
            volume_folder_name = volume_folder.name
            LOGGER.info(f"Found volume folder: {volume_folder_name}")
            
            # Try to extract volume number from folder name
            volume_number = extract_volume_number(volume_folder)
            
            if not volume_number:
                LOGGER.debug(f"Could not extract volume number from folder: {volume_folder_name}")
                continue
            
            LOGGER.info(f"Extracted volume number: {volume_number} from folder: {volume_folder_name}")
            
            # Get or create volume
            volume_id = get_or_create_volume(series_id, volume_number)
            
            if not volume_id:
                LOGGER.error(f"Failed to create volume {volume_number} for series {series_id}")
                stats['errors'] += 1
                continue
            
            stats['volumes_found'] += 1
            LOGGER.info(f"Created/found volume ID: {volume_id} for volume {volume_number}")
            
            # Update collection item for this volume with Digital format and Individual Images
            try:
                # Check if collection item exists
                collection_item = execute_query("""
                    SELECT id FROM collection_items 
                    WHERE series_id = ? AND volume_id = ? AND item_type = 'VOLUME'
                """, (series_id, volume_id))
                
                if collection_item:
                    # Update existing collection item
                    item_id = collection_item[0]['id']
                    execute_query("""
                        UPDATE collection_items 
                        SET format = 'DIGITAL', digital_format = 'Individual Images', has_file = 1
                        WHERE id = ?
                    """, (item_id,), commit=True)
                    LOGGER.info(f"Updated collection item {item_id} with Digital/Individual Images format")
                else:
                    # Create new collection item
                    execute_query("""
                        INSERT INTO collection_items (series_id, volume_id, item_type, ownership_status, format, digital_format, has_file)
                        VALUES (?, ?, 'VOLUME', 'OWNED', 'DIGITAL', 'Individual Images', 1)
                    """, (series_id, volume_id), commit=True)
                    LOGGER.info(f"Created collection item for volume {volume_id} with Digital/Individual Images format")
            
            except Exception as e:
                LOGGER.warning(f"Error updating collection item for volume {volume_id}: {e}")
                # Continue anyway, volume was created
        
        LOGGER.info(f"Folder structure scan completed: {stats}")
        return stats
    
    except Exception as e:
        LOGGER.error(f"Error scanning folder structure: {e}")
        stats['errors'] += 1
        return stats


def extract_volume_number(file_path: Path) -> Optional[str]:
    """Extract the volume number from a file path.
    
    Args:
        file_path (Path): The file path.
        
    Returns:
        Optional[str]: The volume number, or None if it couldn't be extracted.
    """
    # Try to extract from filename without extension
    filename = file_path.stem  # Get filename without extension
    LOGGER.debug(f"Extracting volume number from filename: {filename}")
    
    # Special case for filenames like "Vol 1.cbz", "Vol 2.cbz", etc.
    if filename.startswith("Vol ") and filename[4:].isdigit():
        vol_num = filename[4:]
        LOGGER.debug(f"Direct match for 'Vol N' pattern: {vol_num}")
        return vol_num
    
    # Common patterns for volume numbers (in order of specificity)
    patterns = [
        # Explicit volume indicators
        r'[vV]ol(?:ume)?[\s._-]*(\d+(?:\.\d+)?)',  # Vol 1, Volume 1, Vol.1, Vol 1.5, etc.
        r'[vV](\d+(?:\.\d+)?)',                     # v1, V1, v1.5, etc.
        
        # Common abbreviations
        r'\bv[\s._-]*(\d+(?:\.\d+)?)',              # v 1, v.1, v_1, v-1, v1.5, etc.
        r'\btome[\s._-]*(\d+(?:\.\d+)?)',           # tome 1, tome.1, etc.
        r'\bch(?:apter)?[\s._-]*(\d+(?:\.\d+)?)',    # ch 1, chapter 1, ch.1, etc.
        
        # Numbers with context
        r'\#(\d+(?:\.\d+)?)',                        # #1, #1.5, etc.
        r'\b(\d+(?:\.\d+)?)\s*(?:of|\/|\\)\s*\d+\b',    # 1 of 10, 1/10, etc.
        
        # Standalone numbers (last resort)
        r'^(\d+(?:\.\d+)?)$',                       # Filename is just a number like "1" or "1.5"
        r'\b(\d+(?:\.\d+)?)\b',                     # Any number in the filename
    ]
    
    # First try the filename
    for pattern in patterns:
        match = re.search(pattern, filename)
        if match:
            vol_num = match.group(1)
            LOGGER.debug(f"Found volume number {vol_num} using pattern {pattern} in filename")
            return vol_num
    
    # Then try the full filename with extension
    full_filename = file_path.name
    LOGGER.debug(f"Trying full filename: {full_filename}")
    for pattern in patterns:
        match = re.search(pattern, full_filename)
        if match:
            vol_num = match.group(1)
            LOGGER.debug(f"Found volume number {vol_num} using pattern {pattern} in full filename")
            return vol_num
    
    # If no match in filename, try parent directory name
    parent_dir = file_path.parent.name
    LOGGER.debug(f"Trying parent directory name: {parent_dir}")
    for pattern in patterns:
        match = re.search(pattern, parent_dir)
        if match:
            vol_num = match.group(1)
            LOGGER.debug(f"Found volume number {vol_num} using pattern {pattern} in parent directory")
            return vol_num
    
    # If still no match, check if the filename itself is a number or starts with a number
    if filename.isdigit():
        LOGGER.debug(f"Filename is a digit: {filename}")
        return filename
    
    # Extract leading digits if filename starts with numbers
    match = re.match(r'^(\d+)', filename)
    if match:
        vol_num = match.group(1)
        LOGGER.debug(f"Found volume number {vol_num} from leading digits in filename")
        return vol_num
    
    # If still no match, use a default
    LOGGER.debug(f"No volume number found, defaulting to 1")
    return '1'  # Default to volume 1