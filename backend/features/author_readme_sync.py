#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Author README.md synchronization module.

Handles creation and synchronization of README.md files in author folders.
Similar to the book README system, each author has a README.md file containing
all metadata from the database.
"""

import os
from pathlib import Path
from datetime import datetime
from backend.base.logging import LOGGER
from backend.internals.db import execute_query


def ensure_author_readme_file(
    author_dir: Path,
    author_id: int,
    name: str,
    description: str = None,
    biography: str = None,
    birth_date: str = None,
    death_date: str = None,
    photo_url: str = None,
    provider: str = None,
    provider_id: str = None,
    notable_works: list = None,
    source_url: str = None,
    openlibrary_url: str = None,
    merge_with_existing: bool = False
) -> bool:
    """Ensure a README.md file exists in the author directory.

    Args:
        author_dir (Path): The author directory.
        author_id (int): The author ID.
        name (str): The author name.
        description (str, optional): Author description. Defaults to None.
        biography (str, optional): Author biography. Defaults to None.
        birth_date (str, optional): Author birth date. Defaults to None.
        death_date (str, optional): Author death date. Defaults to None.
        photo_url (str, optional): Author photo URL. Defaults to None.
        provider (str, optional): Metadata provider. Defaults to None.
        provider_id (str, optional): Provider ID. Defaults to None.
        notable_works (list, optional): List of notable works. Defaults to None.
        source_url (str, optional): Source URL for the author. Defaults to None.
        openlibrary_url (str, optional): OpenLibrary URL. Defaults to None.
        merge_with_existing (bool, optional): If True, merge with existing README data. Defaults to False.

    Returns:
        bool: True if the README file exists or was created, False otherwise.
    """
    readme_path = author_dir / "README.md"
    
    try:
        # Convert to Path if string
        if isinstance(author_dir, str):
            author_dir = Path(author_dir)
        
        LOGGER.info(f"[README SYNC] Starting README creation for author: {name}")
        LOGGER.info(f"[README SYNC] Target directory: {author_dir}")
        LOGGER.info(f"[README SYNC] Directory exists: {author_dir.exists()}")
        
        # Make sure the directory exists
        if not author_dir.exists():
            LOGGER.info(f"[README SYNC] Creating author directory: {author_dir}")
            try:
                author_dir.mkdir(parents=True, exist_ok=True)
                LOGGER.info(f"[README SYNC] Author directory created successfully")
            except Exception as mkdir_error:
                LOGGER.error(f"[README SYNC] Failed to create directory: {mkdir_error}")
                raise mkdir_error
        else:
            LOGGER.info(f"[README SYNC] Author directory already exists: {author_dir}")
        
        # Verify directory is writable
        if not os.access(author_dir, os.W_OK):
            LOGGER.error(f"[README SYNC] Directory is not writable: {author_dir}")
            raise PermissionError(f"No write permission for directory: {author_dir}")
        
        # If merging with existing, read the existing README first
        existing_data = {}
        if merge_with_existing and readme_path.exists():
            existing_data = read_metadata_from_author_readme(author_dir)
            LOGGER.info(f"[README SYNC] Merging with existing README data for author: {name}")
        
        # Create the README file with standardized format (matching book README.txt format)
        LOGGER.info(f"[README SYNC] Creating README.md file for author: {name} in {author_dir}")
        LOGGER.info(f"[README SYNC] README path: {readme_path}")
        with open(readme_path, 'w', encoding='utf-8') as f:
            # Core metadata fields (matching book format)
            f.write(f"ID: {author_id}\n")
            f.write(f"Type: AUTHOR\n")
            
            # Provider - use DB value if available, otherwise keep existing
            provider_value = provider or existing_data.get('provider', '')
            f.write(f"Provider: {provider_value}\n")
            
            # MetadataID - use DB value if available, otherwise keep existing
            provider_id_value = provider_id or existing_data.get('provider_id', '')
            f.write(f"MetadataID: {provider_id_value}\n")
            
            f.write(f"Author: {name}\n")
            
            # CoverURL - use DB value if available, otherwise keep existing
            photo_url_value = photo_url or existing_data.get('photo_url', '')
            f.write(f"CoverURL: {photo_url_value}\n")
            
            # BirthDate - always write, even if empty
            birth_date_value = birth_date or ''
            f.write(f"BirthDate: {birth_date_value}\n")
            
            # DeathDate - always write, even if empty
            death_date_value = death_date or ''
            f.write(f"DeathDate: {death_date_value}\n")
            
            # Description - always write, even if empty
            description_value = description or ''
            f.write(f"Description: {description_value}\n")
            
            # Biography - always write, even if empty
            biography_value = biography or ''
            f.write(f"Biography: {biography_value}\n")
            
            # Timestamp
            f.write(f"Created: {datetime.now().strftime('%d.%m.%Y')}\n")
            
            # Source URL - use DB value if available, otherwise keep existing
            source_url_value = source_url or existing_data.get('source_url', '')
            f.write(f"Source: {source_url_value}\n")
            
            # Notable Works
            if notable_works and len(notable_works) > 0:
                f.write("NotableWorks:\n")
                for work in notable_works[:5]:  # Top 5 works
                    f.write(f"    {work}\n")
            
            # OpenLibrary URL
            if openlibrary_url:
                f.write(f"OpenLibraryURL: {openlibrary_url}\n")
            
            f.write("\n")
            f.write("This folder is managed by Readloom. Place your e-book files here.\n")
        
        # Verify the file was created
        if readme_path.exists():
            file_size = readme_path.stat().st_size
            LOGGER.info(f"[README SYNC] README.md file created successfully for author: {name}")
            LOGGER.info(f"[README SYNC] File size: {file_size} bytes")
            return True
        else:
            LOGGER.error(f"[README SYNC] Failed to create README.md file for author: {name}")
            LOGGER.error(f"[README SYNC] File path: {readme_path}")
            return False
    
    except Exception as e:
        LOGGER.error(f"[README SYNC] Error creating author README.md file: {e}")
        import traceback
        LOGGER.error(f"[README SYNC] Traceback: {traceback.format_exc()}")
        return False


def read_metadata_from_author_readme(author_dir: Path) -> dict:
    """Read metadata from README.md file in the author directory.

    Args:
        author_dir (Path): The author directory.

    Returns:
        dict: Metadata dictionary with author fields.
    """
    metadata = {
        'id': None,
        'name': None,
        'description': None,
        'biography': None,
        'birth_date': None,
        'death_date': None,
        'photo_url': None,
        'provider': None,
        'provider_id': None,
        'notable_works': [],
        'source_url': None,
        'openlibrary_url': None,
        'created_at': None,
        'updated_at': None
    }
    
    readme_path = author_dir / "README.md"
    
    if not readme_path.exists():
        return metadata
    
    try:
        with open(readme_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
            in_notable_works = False
            
            for line in lines:
                line_stripped = line.strip()
                
                # Skip empty lines
                if not line_stripped:
                    in_notable_works = False
                    continue
                
                # Check for NotableWorks section
                if line_stripped.startswith('NotableWorks:'):
                    in_notable_works = True
                    continue
                
                # Parse notable works (indented lines under NotableWorks)
                if in_notable_works and line.startswith('    '):
                    work = line_stripped
                    if work:
                        metadata['notable_works'].append(work)
                    continue
                
                # Parse key-value pairs (format: Key: Value)
                if ':' in line_stripped and not line_stripped.startswith('This folder'):
                    parts = line_stripped.split(':', 1)
                    if len(parts) == 2:
                        key = parts[0].strip()
                        value = parts[1].strip()
                        
                        if key == 'ID':
                            try:
                                metadata['id'] = int(value)
                            except ValueError:
                                pass
                        elif key == 'Type':
                            pass  # Skip type field
                        elif key == 'Provider':
                            metadata['provider'] = value
                        elif key == 'MetadataID':
                            metadata['provider_id'] = value
                        elif key == 'Author':
                            metadata['name'] = value
                        elif key == 'CoverURL':
                            metadata['photo_url'] = value
                        elif key == 'BirthDate':
                            metadata['birth_date'] = value
                        elif key == 'Description':
                            metadata['description'] = value
                        elif key == 'Biography':
                            metadata['biography'] = value
                        elif key == 'Created':
                            metadata['created_at'] = value
                        elif key == 'Source':
                            metadata['source_url'] = value
                        elif key == 'OpenLibraryURL':
                            metadata['openlibrary_url'] = value
        
        LOGGER.info(f"Read author metadata from README: {metadata}")
        return metadata
    
    except Exception as e:
        LOGGER.warning(f"Error reading author metadata from README: {e}")
        return metadata


def sync_author_readme(author_id: int, author_folder_path: str = None, merge_with_existing: bool = False) -> bool:
    """Sync author README.md file with database.

    Args:
        author_id (int): The author ID.
        author_folder_path (str, optional): Specific author folder path. If None, uses default.
        merge_with_existing (bool, optional): If True, merge with existing README data. Defaults to False.

    Returns:
        bool: True if successful, False otherwise.
    """
    try:
        # Get author data from database
        author = execute_query(
            """SELECT * FROM authors WHERE id = ?""",
            (author_id,)
        )
        
        if not author:
            LOGGER.warning(f"Author {author_id} not found in database")
            return False
        
        author_data = author[0]
        author_name = author_data.get('name')
        
        if not author_name:
            LOGGER.warning(f"Author {author_id} has no name")
            return False
        
        # Determine author folder path
        author_dir = None
        if author_folder_path:
            author_dir = Path(author_folder_path) if not isinstance(author_folder_path, Path) else author_folder_path
            LOGGER.info(f"Using provided author folder path: {author_dir}")
        else:
            # Try to derive folder from any associated series (book folder parent).
            # Older schemas may not have folder_path/custom_path columns, so guard this.
            series_paths = []
            try:
                series_paths = execute_query(
                    """SELECT s.folder_path, s.custom_path FROM series s
                           INNER JOIN author_books ab ON ab.series_id = s.id
                           WHERE ab.author_id = ?
                           ORDER BY s.updated_at DESC, s.created_at DESC
                           LIMIT 1""",
                    (author_id,)
                )
            except Exception as e:
                LOGGER.info(f"Series folder lookup skipped (schema may not have folder_path/custom_path): {e}")

            candidate_path = None
            if series_paths:
                series_row = series_paths[0]
                candidate_path = series_row.get('folder_path') or series_row.get('custom_path')
                if candidate_path:
                    parent_dir = Path(candidate_path).parent
                    if parent_dir.exists():
                        author_dir = parent_dir
                        LOGGER.info(f"Derived author folder from series path: {author_dir}")
            
            if author_dir is None:
                # Get or create author folder in the book root folder
                from backend.base.helpers import get_safe_folder_name
                from backend.base.helpers_content_service import get_root_folder_path
                
                # Try to get the book root folder
                book_root_path = get_root_folder_path("BOOK")
                
                if book_root_path:
                    authors_dir = Path(book_root_path)
                    LOGGER.info(f"Using book root folder for author: {authors_dir}")
                else:
                    # Fallback to default ebook storage if no book root folder is configured
                    from backend.base.helpers import get_ebook_storage_dir
                    ebook_dir = get_ebook_storage_dir()
                    authors_dir = ebook_dir / "Authors"
                    LOGGER.warning(f"No book root folder configured, using default ebook storage: {authors_dir}")
                
                # Create Authors directory if it doesn't exist
                if not authors_dir.exists():
                    authors_dir.mkdir(parents=True, exist_ok=True)
                
                # Create author-specific directory under the book root
                safe_author_name = get_safe_folder_name(author_name)
                author_dir = authors_dir / safe_author_name
        
        if author_dir is None:
            LOGGER.error(f"Unable to resolve author directory for {author_name}")
            return False
        
        # Fetch notable works from the author's books
        notable_works = []
        try:
            books = execute_query(
                """SELECT s.title FROM series s
                   INNER JOIN author_books ab ON s.id = ab.series_id
                   WHERE ab.author_id = ?
                   ORDER BY s.created_at DESC
                   LIMIT 5""",
                (author_id,)
            )
            notable_works = [book['title'] for book in books]
            LOGGER.info(f"Fetched {len(notable_works)} notable works for author {author_name}")
        except Exception as e:
            LOGGER.warning(f"Could not fetch notable works for author {author_name}: {e}")
        
        # Build OpenLibrary URL if provider_id is available
        openlibrary_url = None
        if author_data.get('provider_id'):
            openlibrary_url = f"https://openlibrary.org/authors/{author_data.get('provider_id')}"
        
        # Create README.md file
        success = ensure_author_readme_file(
            author_dir,
            author_id,
            author_name,
            description=author_data.get('description'),
            biography=author_data.get('biography'),
            birth_date=author_data.get('birth_date'),
            death_date=author_data.get('death_date'),
            photo_url=author_data.get('photo_url'),
            provider=author_data.get('provider'),
            provider_id=author_data.get('provider_id'),
            notable_works=notable_works,
            source_url=None,  # Can be added if available
            openlibrary_url=openlibrary_url,
            merge_with_existing=merge_with_existing
        )
        
        if success:
            # Update author folder_path in database (but don't write to README)
            execute_query(
                """UPDATE authors SET folder_path = ? WHERE id = ?""",
                (str(author_dir), author_id),
                commit=True
            )
            LOGGER.info(f"Synced README.md for author {author_name} (ID: {author_id})")
        
        return success
    
    except Exception as e:
        LOGGER.error(f"Error syncing author README: {e}")
        import traceback
        LOGGER.error(traceback.format_exc())
        return False


def sync_all_author_readmes(merge_with_existing: bool = False) -> dict:
    """Sync README.md files for all authors in the database.

    Args:
        merge_with_existing (bool, optional): If True, merge with existing README data. Defaults to False.

    Returns:
        dict: Statistics about the sync operation.
    """
    try:
        # Get all authors with their folder paths
        authors = execute_query("""
            SELECT id, name, folder_path FROM authors
        """)
        
        stats = {
            'total': len(authors),
            'synced': 0,
            'failed': 0,
            'errors': []
        }
        
        LOGGER.info(f"Starting author README sync for {len(authors)} authors with merge_with_existing={merge_with_existing}")
        
        for author in authors:
            author_id = author['id']
            author_name = author.get('name', 'Unknown')
            author_folder_path = author.get('folder_path')
            
            try:
                LOGGER.info(f"[README SYNC] Syncing author {author_id} ({author_name})")
                LOGGER.info(f"[README SYNC] Author folder_path from DB: {author_folder_path}")
                
                # If folder_path exists and is valid, use it; otherwise sync will create default path
                if author_folder_path and Path(author_folder_path).exists():
                    LOGGER.info(f"[README SYNC] Using existing folder path: {author_folder_path}")
                    if sync_author_readme(author_id, author_folder_path=author_folder_path, merge_with_existing=merge_with_existing):
                        stats['synced'] += 1
                        LOGGER.info(f"[README SYNC] Successfully synced author {author_id}")
                    else:
                        stats['failed'] += 1
                        LOGGER.warning(f"[README SYNC] Failed to sync author {author_id}")
                else:
                    # Folder path not set, use default path
                    LOGGER.info(f"[README SYNC] Folder path not set or doesn't exist, using default path")
                    if sync_author_readme(author_id, author_folder_path=None, merge_with_existing=merge_with_existing):
                        stats['synced'] += 1
                        LOGGER.info(f"[README SYNC] Successfully synced author {author_id}")
                    else:
                        stats['failed'] += 1
                        LOGGER.warning(f"[README SYNC] Failed to sync author {author_id}")
            except Exception as e:
                stats['failed'] += 1
                error_msg = f"Author {author_id}: {str(e)}"
                stats['errors'].append(error_msg)
                LOGGER.error(f"[README SYNC] {error_msg}")
        
        LOGGER.info(f"[README SYNC] Author README sync complete: {stats['synced']}/{stats['total']} synced, {stats['failed']} failed")
        return stats
    
    except Exception as e:
        LOGGER.error(f"[README SYNC] Error syncing all author READMEs: {e}")
        import traceback
        LOGGER.error(f"[README SYNC] Traceback: {traceback.format_exc()}")
        return {
            'total': 0,
            'synced': 0,
            'failed': 0,
            'errors': [str(e)]
        }
