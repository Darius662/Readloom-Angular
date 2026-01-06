#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple, Union, Dict, Any


def check_min_python_version(major: int, minor: int) -> bool:
    """Check if the current Python version is at least the given version.

    Args:
        major (int): The major version to check.
        minor (int): The minor version to check.

    Returns:
        bool: True if the current Python version is at least the given version.
    """
    current_major, current_minor = sys.version_info[:2]
    if current_major > major:
        return True
    if current_major == major and current_minor >= minor:
        return True
    
    print(f"ERROR: Python {major}.{minor} or higher is required. "
          f"You are using Python {current_major}.{current_minor}.")
    return False


def get_python_exe() -> Optional[str]:
    """Get the path to the Python executable.

    Returns:
        Optional[str]: The path to the Python executable, or None if not found.
    """
    if hasattr(sys, 'executable') and sys.executable:
        return sys.executable
    
    return None


def ensure_dir_exists(path: Union[str, Path]) -> bool:
    """Ensure a directory exists.

    Args:
        path (Union[str, Path]): The directory path.

    Returns:
        bool: True if the directory exists or was created, False otherwise.
    """
    from backend.base.logging import LOGGER
    
    if isinstance(path, str):
        path = Path(path)
    
    LOGGER.info(f"Ensuring directory exists: {path}")
    
    try:
        path.mkdir(parents=True, exist_ok=True)
        LOGGER.info(f"Directory created or already exists: {path}")
        return True
    except Exception as e:
        LOGGER.error(f"Error creating directory {path}: {e}")
        return False


def get_app_dir() -> Path:
    """Get the application directory.

    Returns:
        Path: The application directory.
    """
    return Path(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


def get_data_dir() -> Path:
    """Get the data directory.

    Returns:
        Path: The data directory.
    """
    app_dir = get_app_dir()
    data_dir = app_dir / "data"
    ensure_dir_exists(data_dir)
    return data_dir


def get_config_dir() -> Path:
    """Get the configuration directory.

    Returns:
        Path: The configuration directory.
    """
    data_dir = get_data_dir()
    config_dir = data_dir / "config"
    ensure_dir_exists(config_dir)
    return config_dir


def get_logs_dir() -> Path:
    """Get the logs directory.

    Returns:
        Path: The logs directory.
    """
    data_dir = get_data_dir()
    logs_dir = data_dir / "logs"
    ensure_dir_exists(logs_dir)
    return logs_dir


def get_ebook_storage_dir() -> Path:
    """Get the e-book storage directory.

    Returns:
        Path: The e-book storage directory.
    """
    data_dir = get_data_dir()
    
    # Try to get the ebook_storage setting
    try:
        from backend.internals.settings import Settings
        settings = Settings().get_settings()
        ebook_storage = settings.ebook_storage
    except Exception:
        # If there's an error (e.g., during initial setup), use the default
        from backend.base.definitions import Constants
        ebook_storage = Constants.DEFAULT_EBOOK_STORAGE
    
    # Handle absolute and relative paths
    ebook_path = Path(ebook_storage)
    if ebook_path.is_absolute():
        ebook_dir = ebook_path
    else:
        ebook_dir = data_dir / ebook_storage
    
    ensure_dir_exists(ebook_dir)
    return ebook_dir


def organize_ebook_path(series_id: int, volume_id: int, filename: str) -> Path:
    """Organize e-book path by series title and volume.

    Args:
        series_id (int): The series ID.
        volume_id (int): The volume ID.
        filename (str): The original filename.

    Returns:
        Path: The organized path for the e-book file.
    """
    from backend.internals.db import execute_query
    from backend.base.logging import LOGGER
    from backend.internals.settings import Settings
    
    # Get series info
    series_info = execute_query(
        "SELECT title, content_type, custom_path FROM series WHERE id = ?", 
        (series_id,)
    )
    
    if not series_info:
        # Fallback to old structure if series not found
        ebook_dir = get_ebook_storage_dir()
        series_dir = ebook_dir / f"series_{series_id}"
        ensure_dir_exists(series_dir)
        return series_dir / filename
    
    # Get series title, content type, and custom path
    series_title = series_info[0]['title']
    content_type = series_info[0].get('content_type', 'MANGA')
    custom_path = series_info[0].get('custom_path')
    
    # Get volume info
    volume_info = execute_query(
        "SELECT volume_number FROM volumes WHERE id = ?", 
        (volume_id,)
    )
    volume_number = volume_info[0]['volume_number'] if volume_info else f"volume_{volume_id}"
    
    # Create safe directory name
    safe_series_title = get_safe_folder_name(series_title)
    
    # Check if custom path is set
    if custom_path:
        LOGGER.info(f"Using custom path for series {series_id}: {custom_path}")
        series_dir = Path(custom_path)
    else:
        # Get root folders from settings
        settings = Settings().get_settings()
        root_folders = settings.root_folders
        
        # Determine the series directory
        if not root_folders:
            # If no root folders configured, use default ebook storage
            ebook_dir = get_ebook_storage_dir()
            series_dir = ebook_dir / safe_series_title
        else:
            # Use the first root folder
            root_folder = root_folders[0]
            root_path = Path(root_folder['path'])
            series_dir = root_path / safe_series_title
    
    # Create directories
    ensure_dir_exists(series_dir)
    
    # Return full path without adding Volume_ prefix
    return series_dir / filename


def get_safe_folder_name(name: str) -> str:
    """Create a safe folder name from a string.

    Args:
        name (str): The original name.

    Returns:
        str: A safe folder name that preserves spaces but replaces invalid characters.
    """
    from backend.base.logging import LOGGER
    
    # Characters not allowed in Windows filenames
    invalid_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
    
    # Replace invalid characters with underscores but keep spaces and other valid characters
    safe_name = name
    for char in invalid_chars:
        safe_name = safe_name.replace(char, '_')
    
    # Remove leading/trailing periods and spaces as they can cause issues
    safe_name = safe_name.strip('. ')
    
    # Ensure the name is not empty
    if not safe_name:
        safe_name = "unnamed"
    
    LOGGER.info(f"Original name: '{name}', Safe name: '{safe_name}'")
    return safe_name


def rename_series_folder(series_id: int, old_title: str, new_title: str, content_type: str) -> bool:
    """Rename a series folder when the title changes.
    
    Args:
        series_id (int): The series ID.
        old_title (str): The old series title.
        new_title (str): The new series title.
        content_type (str): The content type (MANGA, BOOK, COMIC).
        
    Returns:
        bool: True if rename was successful or not needed, False if error occurred.
    """
    from backend.base.logging import LOGGER
    from backend.internals.db import execute_query
    from backend.internals.settings import Settings
    import shutil
    
    try:
        # Get safe folder names
        old_safe_name = get_safe_folder_name(old_title)
        new_safe_name = get_safe_folder_name(new_title)
        
        # If names are the same, no need to rename
        if old_safe_name == new_safe_name:
            LOGGER.info(f"Series {series_id}: old and new safe names are identical, no rename needed")
            return True
        
        # Check for custom path first
        custom_path = execute_query("SELECT custom_path FROM series WHERE id = ?", (series_id,))
        if custom_path and custom_path[0].get('custom_path'):
            LOGGER.info(f"Series {series_id} has custom path, skipping automatic rename")
            return True
        
        # Get all root folders to search for the series folder
        settings = Settings().get_settings()
        root_folders = settings.root_folders if settings.root_folders else []
        
        # Try to find and rename the folder
        renamed = False
        for root_folder in root_folders:
            root_path = Path(root_folder['path'])
            old_folder = root_path / old_safe_name
            new_folder = root_path / new_safe_name
            
            if old_folder.exists() and old_folder.is_dir():
                try:
                    # Check if target folder already exists
                    if new_folder.exists():
                        LOGGER.info(f"Target folder already exists: {new_folder}")
                        # Merge contents from old folder to new folder
                        for item in old_folder.iterdir():
                            src = item
                            dst = new_folder / item.name
                            
                            if src.is_dir():
                                # If destination dir exists, merge recursively
                                if dst.exists():
                                    LOGGER.info(f"Merging directory: {src} -> {dst}")
                                    shutil.copytree(src, dst, dirs_exist_ok=True)
                                else:
                                    shutil.move(str(src), str(dst))
                            else:
                                # For files, overwrite if exists
                                if dst.exists():
                                    dst.unlink()
                                shutil.move(str(src), str(dst))
                        
                        # Remove the now-empty old folder
                        try:
                            old_folder.rmdir()
                            LOGGER.info(f"Removed empty old folder: {old_folder}")
                        except Exception as e:
                            LOGGER.warning(f"Could not remove old folder {old_folder}: {e}")
                        
                        LOGGER.info(f"Successfully merged series folder contents: {old_folder} -> {new_folder}")
                    else:
                        # Target doesn't exist, simple rename
                        old_folder.rename(new_folder)
                        LOGGER.info(f"Successfully renamed series folder: {old_folder} -> {new_folder}")
                    
                    renamed = True
                    break
                except Exception as e:
                    LOGGER.error(f"Error renaming/merging series folder {old_folder}: {e}")
                    import traceback
                    LOGGER.error(traceback.format_exc())
                    continue
        
        if not renamed:
            LOGGER.warning(f"Could not find series folder for '{old_title}' (safe name: '{old_safe_name}') to rename")
        
        return True  # Return True even if folder wasn't found (might be using custom path)
    except Exception as e:
        LOGGER.error(f"Error in rename_series_folder: {e}")
        import traceback
        LOGGER.error(traceback.format_exc())
        return False


def rename_author_folder(author_id: int, old_name: str, new_name: str) -> bool:
    """Rename an author folder when the name changes.
    
    Args:
        author_id (int): The author ID.
        old_name (str): The old author name.
        new_name (str): The new author name.
        
    Returns:
        bool: True if rename was successful or not needed, False if error occurred.
    """
    from backend.base.logging import LOGGER
    from backend.internals.settings import Settings
    import shutil
    
    try:
        # Get safe folder names
        old_safe_name = get_safe_folder_name(old_name)
        new_safe_name = get_safe_folder_name(new_name)
        
        # If names are the same, no need to rename
        if old_safe_name == new_safe_name:
            LOGGER.info(f"Author {author_id}: old and new safe names are identical, no rename needed")
            return True
        
        # Get all root folders to search for the author folder
        settings = Settings().get_settings()
        root_folders = settings.root_folders if settings.root_folders else []
        
        # Try to find and rename the folder
        renamed = False
        for root_folder in root_folders:
            root_path = Path(root_folder['path'])
            old_folder = root_path / old_safe_name
            new_folder = root_path / new_safe_name
            
            if old_folder.exists() and old_folder.is_dir():
                try:
                    # Check if target folder already exists
                    if new_folder.exists():
                        LOGGER.info(f"Target author folder already exists: {new_folder}")
                        # Merge contents from old folder to new folder
                        for item in old_folder.iterdir():
                            src = item
                            dst = new_folder / item.name
                            
                            if src.is_dir():
                                # If destination dir exists, merge recursively
                                if dst.exists():
                                    LOGGER.info(f"Merging directory: {src} -> {dst}")
                                    shutil.copytree(src, dst, dirs_exist_ok=True)
                                else:
                                    shutil.move(str(src), str(dst))
                            else:
                                # For files, overwrite if exists
                                if dst.exists():
                                    dst.unlink()
                                shutil.move(str(src), str(dst))
                        
                        # Remove the now-empty old folder
                        try:
                            old_folder.rmdir()
                            LOGGER.info(f"Removed empty old author folder: {old_folder}")
                        except Exception as e:
                            LOGGER.warning(f"Could not remove old author folder {old_folder}: {e}")
                        
                        LOGGER.info(f"Successfully merged author folder contents: {old_folder} -> {new_folder}")
                    else:
                        # Target doesn't exist, simple rename
                        old_folder.rename(new_folder)
                        LOGGER.info(f"Successfully renamed author folder: {old_folder} -> {new_folder}")
                    
                    renamed = True
                    break
                except Exception as e:
                    LOGGER.error(f"Error renaming/merging author folder {old_folder}: {e}")
                    import traceback
                    LOGGER.error(traceback.format_exc())
                    continue
        
        if not renamed:
            LOGGER.warning(f"Could not find author folder for '{old_name}' (safe name: '{old_safe_name}') to rename")
        
        return True  # Return True even if folder wasn't found
    except Exception as e:
        LOGGER.error(f"Error in rename_author_folder: {e}")
        import traceback
        LOGGER.error(traceback.format_exc())
        return False


def ensure_readme_file(series_dir: Path, series_title: str, series_id: int, content_type: str, 
                       metadata_source: str = None, metadata_id: str = None,
                       author: str = None, publisher: str = None, isbn: str = None, 
                       genres: list = None, cover_url: str = None, published_date: str = None,
                       subjects: list = None, description: str = None, star_rating: float = None,
                       reading_progress: int = None, user_description: str = None,
                       in_library: int = None, want_to_read: int = None) -> bool:
    """Ensure a README file exists in the series directory.

    Args:
        series_dir (Path): The series directory.
        series_title (str): The series title.
        series_id (int): The series ID.
        content_type (str): The content type (MANGA, BOOK, COMIC).
        metadata_source (str, optional): The metadata source (e.g., 'AniList'). Defaults to None.
        metadata_id (str, optional): The metadata ID from the source. Defaults to None.
        author (str, optional): The author name. Defaults to None.
        publisher (str, optional): The publisher name. Defaults to None.
        isbn (str, optional): The ISBN number (for books). Defaults to None.
        genres (list, optional): List of genres. Defaults to None.
        cover_url (str, optional): The cover image URL. Defaults to None.
        published_date (str, optional): The publication date. Defaults to None.
        subjects (list, optional): List of subjects/tags. Defaults to None.
        description (str, optional): The series/book description. Defaults to None.
        star_rating (float, optional): User's star rating (0-5). Defaults to None.
        reading_progress (int, optional): Reading progress percentage (0-100). Defaults to None.
        user_description (str, optional): User's personal notes/comments. Defaults to None.
        in_library (int, optional): Whether item is in library (0 or 1). Defaults to None.
        want_to_read (int, optional): Whether item is in want-to-read (0 or 1). Defaults to None.

    Returns:
        bool: True if the README file exists or was created, False otherwise.
    """
    from backend.base.logging import LOGGER
    import os
    
    readme_path = series_dir / "README.txt"
    # Log only the directory name to avoid Unicode encoding issues
    LOGGER.info(f"Ensuring README file exists in: {series_dir.name}")
    
    try:
        # Make sure the directory exists
        if not series_dir.exists():
            LOGGER.warning(f"Series directory does not exist: {series_dir.name}")
            try:
                LOGGER.info(f"Creating series directory: {series_dir.name}")
                os.makedirs(str(series_dir), exist_ok=True)
                LOGGER.info(f"Series directory created: {series_dir.name}")
            except Exception as e:
                LOGGER.error(f"Failed to create series directory: {e}")
                import traceback
                LOGGER.error(traceback.format_exc())
                return False
        
        # Create the README file with standardized format
        LOGGER.info(f"Creating README file in: {series_dir.name}")
        with open(readme_path, 'w', encoding='utf-8') as f:
            # Required fields
            f.write(f"Series: {series_title}\n")
            f.write(f"ID: {series_id}\n")
            f.write(f"Type: {content_type}\n")
            
            # Provider information - always write, even if empty
            f.write(f"Provider: {metadata_source or ''}\n")
            f.write(f"MetadataID: {metadata_id or ''}\n")
            
            # Optional metadata fields - always write, even if empty
            f.write(f"Author: {author or ''}\n")
            f.write(f"Publisher: {publisher or ''}\n")
            f.write(f"ISBN: {isbn or ''}\n")
            
            # Genres
            if genres:
                # Convert list to comma-separated string
                genres_str = ",".join(genres) if isinstance(genres, list) else genres
                f.write(f"Genres: {genres_str}\n")
            else:
                f.write("Genres: \n")
            
            # Cover URL - always write, even if empty
            f.write(f"CoverURL: {cover_url or ''}\n")
            
            # Published Date - always write, even if empty
            f.write(f"PublishedDate: {published_date or ''}\n")
            
            # Subjects
            if subjects:
                # Convert list to comma-separated string
                subjects_str = ",".join(subjects) if isinstance(subjects, list) else subjects
                f.write(f"Subjects: {subjects_str}\n")
            else:
                f.write("Subjects: \n")
            
            # Description - always write, even if empty
            f.write(f"Description: {description or ''}\n")
            
            # User tracking data
            if star_rating is not None:
                f.write(f"StarRating: {star_rating}\n")
            if reading_progress is not None:
                f.write(f"ReadingProgress: {reading_progress}\n")
            if user_description:
                f.write(f"UserNotes: {user_description}\n")
            
            # Library status flags
            if in_library is not None:
                f.write(f"InLibrary: {in_library}\n")
            if want_to_read is not None:
                f.write(f"WantToRead: {want_to_read}\n")
            
            # Timestamp
            f.write(f"Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            
            # Add 2 blank paragraphs for spacing
            f.write("\n\n")
            
            # Footer
            f.write("This folder is managed by Readloom. Place your e-book files here.\n")
        
        # Verify the file was created
        if readme_path.exists():
            LOGGER.info(f"README file created successfully in: {series_dir.name}")
            return True
        else:
            LOGGER.error(f"Failed to create README file in: {series_dir.name}")
            return False
    except Exception as e:
        LOGGER.error(f"Error creating README file: {e}")
        import traceback
        LOGGER.error(traceback.format_exc())
        return False


def read_metadata_from_readme(series_dir: Path) -> dict:
    """Read metadata from README.txt file in the series directory.

    Args:
        series_dir (Path): The series directory.

    Returns:
        dict: Metadata dictionary with keys: metadata_source, metadata_id, series_id, title, type, 
              author, publisher, isbn, genres, cover_url.
    """
    from backend.base.logging import LOGGER
    
    metadata = {
        'metadata_source': None,
        'metadata_id': None,
        'series_id': None,
        'title': None,
        'type': None,
        'author': None,
        'publisher': None,
        'isbn': None,
        'genres': None,
        'cover_url': None,
        'status': None,
        'description': None,
        'custom_path': None,
        'created': None,
        'updated': None,
        'published_date': None,
        'subjects': None,
        'star_rating': None,
        'reading_progress': None,
        'user_description': None
    }
    
    readme_path = series_dir / "README.txt"
    
    if not readme_path.exists():
        return metadata
    
    try:
        with open(readme_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                if ':' in line:
                    key, value = line.split(':', 1)
                    key = key.strip()
                    value = value.strip()
                    
                    # Provider information
                    if key == 'MetadataSource':
                        metadata['metadata_source'] = value
                    elif key == 'MetadataID':
                        metadata['metadata_id'] = value
                    elif key == 'Provider':
                        # For books, "Provider" is the metadata_source
                        metadata['metadata_source'] = value
                    
                    # Core metadata
                    elif key == 'ID':
                        try:
                            metadata['series_id'] = int(value)
                        except ValueError:
                            pass
                    elif key == 'Series':
                        metadata['title'] = value
                    elif key == 'Book':
                        # For books, "Book" is the title
                        metadata['title'] = value
                    elif key == 'Type':
                        metadata['type'] = value
                    
                    # Additional metadata fields
                    elif key == 'Author':
                        metadata['author'] = value
                    elif key == 'Publisher':
                        metadata['publisher'] = value
                    elif key == 'ISBN':
                        metadata['isbn'] = value if value else None
                    elif key == 'Genres':
                        # Parse comma-separated genres into list
                        metadata['genres'] = [g.strip() for g in value.split(',')] if value else None
                    elif key == 'CoverURL':
                        metadata['cover_url'] = value if value else None
                    elif key == 'Status':
                        metadata['status'] = value
                    elif key == 'Description':
                        metadata['description'] = value
                    elif key == 'CustomPath':
                        metadata['custom_path'] = value
                    elif key == 'Created':
                        metadata['created'] = value
                    elif key == 'Updated':
                        metadata['updated'] = value
                    elif key == 'PublishedDate':
                        metadata['published_date'] = value
                    elif key == 'Subjects':
                        # Parse comma-separated subjects into list
                        metadata['subjects'] = [s.strip() for s in value.split(',')] if value else None
                    
                    # User tracking data
                    elif key == 'StarRating':
                        try:
                            metadata['star_rating'] = float(value) if value else None
                        except ValueError:
                            pass
                    elif key == 'ReadingProgress':
                        try:
                            metadata['reading_progress'] = int(value) if value else None
                        except ValueError:
                            pass
                    elif key == 'UserNotes':
                        metadata['user_description'] = value if value else None
        
        LOGGER.info(f"Read metadata from README: {metadata}")
        return metadata
    except Exception as e:
        LOGGER.warning(f"Error reading metadata from README: {e}")
        return metadata


def get_book_folder_path(series_id: int, book_title: str, author_name: str = None) -> Optional[Path]:
    """Get the folder path for a book (root_folder/author_folder/book_folder).
    
    Args:
        series_id (int): The book/series ID.
        book_title (str): The book title.
        author_name (str): The author name (optional).
        
    Returns:
        Optional[Path]: The path to the book folder, or None if not found.
    """
    from backend.base.logging import LOGGER
    from backend.internals.db import execute_query
    
    LOGGER.info(f"Getting folder path for book: {book_title} (ID: {series_id})")
    LOGGER.info(f"Provided author name: {author_name}")
    
    # Create safe folder names
    safe_book_title = get_safe_folder_name(book_title)
    LOGGER.info(f"Safe book title: {safe_book_title}")
    
    # Check if book has custom path
    try:
        custom_path_result = execute_query("SELECT custom_path FROM series WHERE id = ?", (series_id,))
        LOGGER.info(f"Custom path query result: {custom_path_result}")
        if custom_path_result and custom_path_result[0].get('custom_path'):
            custom_path = custom_path_result[0]['custom_path']
            LOGGER.info(f"Book {series_id} has custom path: {custom_path}")
            return Path(custom_path)
    except Exception as e:
        LOGGER.warning(f"Error checking custom path for book {series_id}: {e}")
    
    # Get author name from database if not provided
    if not author_name:
        try:
            author_result = execute_query("SELECT author FROM series WHERE id = ?", (series_id,))
            LOGGER.info(f"Author query result: {author_result}")
            if author_result and author_result[0].get('author'):
                author_name = author_result[0]['author']
                LOGGER.info(f"Retrieved author name from database: {author_name}")
        except Exception as e:
            LOGGER.warning(f"Error getting author name for book {series_id}: {e}")
    
    # Get collection and root folder information using correct table names
    try:
        # Check if book is in a collection using series_collections table
        collection_result = execute_query("""
            SELECT c.name as collection_name, c.root_folder_id, rf.name as root_folder_name, rf.path as root_folder_path
            FROM series_collections sc
            JOIN collections c ON sc.collection_id = c.id
            LEFT JOIN collection_root_folders crf ON c.id = crf.collection_id
            LEFT JOIN root_folders rf ON crf.root_folder_id = rf.id
            WHERE sc.series_id = ?
        """, (series_id,))
        
        LOGGER.info(f"Collection query result: {collection_result}")
        
        if collection_result and collection_result[0]:
            collection = collection_result[0]
            root_folder_path = collection.get('root_folder_path')
            LOGGER.info(f"Root folder path: {root_folder_path}")
            
            if root_folder_path:
                # Structure: root_folder/author_folder/book_folder
                safe_author_name = get_safe_folder_name(author_name or "Unknown Author")
                LOGGER.info(f"Safe author name: {safe_author_name}")
                book_path = Path(root_folder_path) / safe_author_name / safe_book_title
                
                LOGGER.info(f"Book folder path determined: {book_path}")
                LOGGER.info(f"Book folder exists: {book_path.exists()}")
                return book_path
            else:
                LOGGER.warning(f"No root folder path found for book {series_id}")
        else:
            LOGGER.info(f"Book {series_id} not found in any collection")
        
    except Exception as e:
        LOGGER.warning(f"Error getting collection info for book {series_id}: {e}")
        import traceback
        LOGGER.error(traceback.format_exc())
    
    # Fallback: try to get storage path from settings using key/value pairs
    try:
        # Try different possible storage path keys
        storage_keys = ['storage_path', 'library_path', 'books_path', 'root_path']
        storage_path = None
        
        for key in storage_keys:
            storage_result = execute_query("SELECT value FROM settings WHERE key = ?", (key,))
            LOGGER.info(f"Storage path query for key '{key}': {storage_result}")
            if storage_result and storage_result[0].get('value'):
                storage_path = storage_result[0]['value']
                # Remove quotes if present
                if storage_path.startswith('"') and storage_path.endswith('"'):
                    storage_path = storage_path[1:-1]
                LOGGER.info(f"Found storage path with key '{key}': {storage_path}")
                break
        
        if storage_path:
            safe_author_name = get_safe_folder_name(author_name or "Unknown Author")
            book_path = Path(storage_path) / safe_author_name / safe_book_title
            
            LOGGER.info(f"Using fallback storage path: {book_path}")
            LOGGER.info(f"Fallback path exists: {book_path.exists()}")
            return book_path
        else:
            LOGGER.warning(f"No storage path found in settings (tried keys: {storage_keys})")
            
    except Exception as e:
        LOGGER.warning(f"Error getting storage path for book {series_id}: {e}")
    
    # Final fallback: try to get any root folder
    try:
        root_folders_result = execute_query("SELECT path FROM root_folders LIMIT 1")
        LOGGER.info(f"Root folders query result: {root_folders_result}")
        if root_folders_result and root_folders_result[0].get('path'):
            root_path = root_folders_result[0]['path']
            safe_author_name = get_safe_folder_name(author_name or "Unknown Author")
            book_path = Path(root_path) / safe_author_name / safe_book_title
            
            LOGGER.info(f"Using root folder fallback: {book_path}")
            LOGGER.info(f"Root fallback path exists: {book_path.exists()}")
            return book_path
    except Exception as e:
        LOGGER.warning(f"Error getting root folders for book {series_id}: {e}")
    
    LOGGER.error(f"Could not determine folder path for book {series_id}")
    return None


def get_series_folder_path(series_id: int, series_title: str, content_type: str) -> Optional[Path]:
    """Get the folder path for a series.
    
    Args:
        series_id (int): The series ID.
        series_title (str): The series title.
        content_type (str): The content type.
        
    Returns:
        Optional[Path]: The path to the series folder, or None if not found.
    """
    from backend.base.logging import LOGGER
    from backend.internals.db import execute_query
    
    LOGGER.info(f"Getting folder path for series: {series_title} (ID: {series_id}, Type: {content_type})")
    
    # Create safe folder name
    safe_series_title = get_safe_folder_name(series_title)
    
    # Check if series has custom path
    try:
        custom_path_result = execute_query("SELECT custom_path FROM series WHERE id = ?", (series_id,))
        if custom_path_result and custom_path_result[0].get('custom_path'):
            custom_path = custom_path_result[0]['custom_path']
            LOGGER.info(f"Series {series_id} has custom path: {custom_path}")
            return Path(custom_path)
    except Exception as e:
        LOGGER.warning(f"Error checking custom path for series {series_id}: {e}")
    
    # Get root folders for the series
    root_folders = []
    
    # Try to get collection for this series, but handle missing table gracefully
    try:
        collection_result = execute_query("""
            SELECT c.id FROM collections c
            JOIN collection_series cs ON c.id = cs.collection_id
            WHERE cs.series_id = ?
            LIMIT 1
        """, (series_id,))
        
        if collection_result:
            collection_id = collection_result[0]['id']
            LOGGER.info(f"Series {series_id} belongs to collection {collection_id}")
            
            # Get root folders for this collection
            query = """
            SELECT rf.* FROM root_folders rf
            JOIN collection_root_folders crf ON rf.id = crf.root_folder_id
            WHERE crf.collection_id = ?
            ORDER BY rf.name ASC
            """
            root_folders = execute_query(query, (collection_id,))
            LOGGER.info(f"Found {len(root_folders)} root folders for collection {collection_id}")
    except Exception as e:
        LOGGER.warning(f"Error getting collection for series {series_id} (table might not exist): {e}")
        # Continue with fallback logic
    
    # If no collection-specific root folders, try default collection
    if not root_folders:
        try:
            default_collections = execute_query("SELECT id FROM collections WHERE is_default = 1 AND UPPER(content_type) = UPPER(?)", (content_type,))
            if default_collections:
                default_collection_id = default_collections[0]["id"]
                LOGGER.info(f"Using default collection {default_collection_id} for content type {content_type}")
                
                query = """
                SELECT rf.* FROM root_folders rf
                JOIN collection_root_folders crf ON rf.id = crf.root_folder_id
                WHERE crf.collection_id = ?
                ORDER BY rf.name ASC
                """
                root_folders = execute_query(query, (default_collection_id,))
        except Exception as e:
            LOGGER.warning(f"Error getting default collection for {content_type}: {e}")
    
    # If still no root folders, use any available root folder
    if not root_folders:
        try:
            root_folders = execute_query("SELECT * FROM root_folders ORDER BY name ASC LIMIT 1")
            if root_folders:
                LOGGER.info(f"Using first available root folder")
        except Exception as e:
            LOGGER.warning(f"Error getting root folders: {e}")
    
    # If we have root folders, use the first one
    if root_folders:
        root_folder = root_folders[0]
        root_path = Path(root_folder['path'])
        series_dir = root_path / safe_series_title
        LOGGER.info(f"Series folder path: {series_dir}")
        return series_dir
    
    # Fallback to default ebook storage
    LOGGER.warning("No root folders found, using default ebook storage")
    try:
        ebook_dir = get_ebook_storage_dir()
        series_dir = ebook_dir / safe_series_title
        LOGGER.info(f"Series folder path (default): {series_dir}")
        return series_dir
    except Exception as e:
        LOGGER.error(f"Error getting default ebook storage: {e}")
        return None


def create_series_folder_structure(series_id: int, series_title: str, content_type: str, collection_id: Optional[int] = None, root_folder_id: Optional[int] = None, metadata: Optional[Dict[str, Any]] = None) -> Path:
    """Create folder structure for a series.

    Args:
        series_id (int): The series ID.
        series_title (str): The series title.
        content_type (str): The content type.
        collection_id (Optional[int], optional): The collection ID. Defaults to None.

    Returns:
        Path: The path to the series folder.
    """
    from backend.base.logging import LOGGER
    from backend.internals.db import execute_query
    import os
    
    LOGGER.info(f"Creating folder structure for series: {series_title} (ID: {series_id}, Type: {content_type})")
    
    # Create directory name that preserves spaces but replaces invalid characters
    safe_series_title = get_safe_folder_name(series_title)
    LOGGER.info(f"Original series title: '{series_title}', Safe series title for folder: '{safe_series_title}'")
    
    # If an explicit root_folder_id is provided, use it directly
    root_folders = []
    if root_folder_id is not None:
        LOGGER.info(f"Using explicit root_folder_id={root_folder_id}")
        query = "SELECT * FROM root_folders WHERE id = ?"
        root_folders = execute_query(query, (root_folder_id,))
    # Else if collection_id is provided, get root folders for that collection
    elif collection_id is not None:
        LOGGER.info(f"Getting root folders for collection ID: {collection_id}")
        query = """
        SELECT rf.* FROM root_folders rf
        JOIN collection_root_folders crf ON rf.id = crf.root_folder_id
        WHERE crf.collection_id = ?
        ORDER BY rf.name ASC
        """
        root_folders = execute_query(query, (collection_id,))
        LOGGER.info(f"Found {len(root_folders)} root folders for collection ID {collection_id}")
    
    # If no collection specified or no root folders found for the collection, use default root folders
    if not root_folders:
        LOGGER.info("No collection-specific root folders found, checking for per-type default collection")
        # Try to get the default collection for this content_type
        default_collections = execute_query("SELECT id FROM collections WHERE is_default = 1 AND UPPER(content_type) = UPPER(?)", (content_type,))
        if default_collections:
            default_collection_id = default_collections[0]["id"]
            LOGGER.info(f"Using default collection ID: {default_collection_id}")
            query = """
            SELECT rf.* FROM root_folders rf
            JOIN collection_root_folders crf ON rf.id = crf.root_folder_id
            WHERE crf.collection_id = ?
            ORDER BY rf.name ASC
            """
            root_folders = execute_query(query, (default_collection_id,))
            LOGGER.info(f"Found {len(root_folders)} root folders for default collection")
    
    # If still no root folders, use the first root folder from the database
    if not root_folders:
        LOGGER.info("No collection-specific or default root folders found, checking for any root folders")
        root_folders = execute_query("SELECT * FROM root_folders ORDER BY name ASC LIMIT 1")
        LOGGER.info(f"Found {len(root_folders)} root folders in database")
    
    # If still no root folders, use default ebook storage
    if not root_folders:
        LOGGER.warning("No root folders configured, using default ebook storage")
        # Use default ebook storage directory
        ebook_dir = get_ebook_storage_dir()
        LOGGER.info(f"E-book directory: {ebook_dir}")
        
        # Create series directory directly in the ebook directory
        series_dir = ebook_dir / safe_series_title
    else:
        # Use the first root folder
        root_folder = root_folders[0]
        LOGGER.info(f"Using root folder: {root_folder['name']} ({root_folder['path']})")
        
        # Create series directory directly in the root folder
        root_path = Path(root_folder['path'])
        LOGGER.info(f"Root path exists: {root_path.exists()}, is directory: {root_path.is_dir() if root_path.exists() else False}")
        
        # Check if root path exists, if not try to create it
        if not root_path.exists():
            try:
                LOGGER.info(f"Root path doesn't exist, creating: {root_path}")
                root_path.mkdir(parents=True, exist_ok=True)
                LOGGER.info(f"Created root path: {root_path}")
            except Exception as e:
                LOGGER.error(f"Failed to create root path: {e}")
                import traceback
                LOGGER.error(traceback.format_exc())
        
        series_dir = root_path / safe_series_title
    
    LOGGER.info(f"Series directory: {series_dir}")
    
    # Create series directory using os.makedirs for more robust directory creation
    try:
        LOGGER.info(f"Attempting to create directory: {series_dir}")
        os.makedirs(str(series_dir), exist_ok=True)
        LOGGER.info(f"Directory created or already exists: {series_dir}")
        LOGGER.info(f"Directory exists after creation: {series_dir.exists()}, is directory: {series_dir.is_dir() if series_dir.exists() else False}")
    except Exception as e:
        LOGGER.error(f"Error creating series directory: {e}")
        import traceback
        LOGGER.error(traceback.format_exc())
        raise  # Re-raise to ensure caller knows there was an error
    
    # Create a README file with series information
    # Use passed metadata if available, otherwise fetch from database
    if metadata:
        # Use passed metadata directly
        metadata_source = metadata.get('metadata_source')
        metadata_id = metadata.get('metadata_id')
        author = metadata.get('author')
        publisher = metadata.get('publisher')
        isbn = metadata.get('isbn')
        published_date = metadata.get('published_date')
        subjects = metadata.get('subjects')
        cover_url = metadata.get('cover_url')
        
        # Convert subjects string to list if needed
        subjects_list = None
        if subjects:
            subjects_list = [s.strip() for s in subjects.split(',')] if isinstance(subjects, str) else subjects
    else:
        # Fetch all metadata from database as fallback
        series_metadata = execute_query(
            "SELECT metadata_source, metadata_id, author, publisher, isbn, published_date, subjects, cover_url FROM series WHERE id = ?",
            (series_id,)
        )
        
        metadata_source = None
        metadata_id = None
        author = None
        publisher = None
        isbn = None
        published_date = None
        subjects = None
        cover_url = None
        subjects_list = None
        
        if series_metadata:
            metadata_source = series_metadata[0].get('metadata_source')
            metadata_id = series_metadata[0].get('metadata_id')
            author = series_metadata[0].get('author')
            publisher = series_metadata[0].get('publisher')
            isbn = series_metadata[0].get('isbn')
            published_date = series_metadata[0].get('published_date')
            subjects = series_metadata[0].get('subjects')
            cover_url = series_metadata[0].get('cover_url')
            
            # Convert subjects string back to list if needed
            if subjects:
                subjects_list = [s.strip() for s in subjects.split(',')] if isinstance(subjects, str) else subjects
    
    ensure_readme_file(
        series_dir, series_title, series_id, content_type, 
        metadata_source=metadata_source, 
        metadata_id=metadata_id,
        author=author,
        publisher=publisher,
        isbn=isbn,
        published_date=published_date,
        subjects=subjects_list,
        cover_url=cover_url
    )
    
    # Create cover_art folder in the series directory
    try:
        cover_art_dir = series_dir / "cover_art"
        cover_art_dir.mkdir(parents=True, exist_ok=True)
        LOGGER.info(f"Created cover_art folder for series {series_id}: {cover_art_dir}")
    except Exception as cover_err:
        LOGGER.warning(f"Could not create cover_art folder for series {series_id}: {cover_err}")
    
    return series_dir


def copy_file_to_storage(source_path: Union[str, Path], target_path: Union[str, Path]) -> bool:
    """Copy a file to the storage location.

    Args:
        source_path (Union[str, Path]): The source file path.
        target_path (Union[str, Path]): The target file path.

    Returns:
        bool: True if the file was copied successfully, False otherwise.
    """
    try:
        if isinstance(source_path, str):
            source_path = Path(source_path)
        if isinstance(target_path, str):
            target_path = Path(target_path)
            
        if not source_path.exists() or not source_path.is_file():
            return False
        
        # Ensure the target directory exists
        target_path.parent.mkdir(parents=True, exist_ok=True)
        
        shutil.copy2(source_path, target_path)
        return True
    except Exception:
        return False
