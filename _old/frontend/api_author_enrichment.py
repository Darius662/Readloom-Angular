#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
API endpoints for enriching author metadata.
"""

from flask import Blueprint, jsonify, request
from backend.base.logging import LOGGER
from backend.internals.db import execute_query

# Create API blueprint
author_enrichment_api_bp = Blueprint('author_enrichment', __name__, url_prefix='/api')


@author_enrichment_api_bp.route('/authors/enrich-all', methods=['POST'])
def enrich_all_authors():
    """
    Enrich all authors without complete metadata.
    
    Priority:
    1. OpenLibrary (most accurate)
    2. Groq AI (fallback for missing data)
    3. Manual edits (user corrections)
    
    Returns:
        Response: Statistics about enrichment operation
    """
    try:
        LOGGER.info("Starting author enrichment process...")
        
        stats = {
            "authors_checked": 0,
            "openlibrary_updated": 0,
            "biographies_added": 0,
            "photos_added": 0,
            "errors": 0
        }
        
        # Get all authors without complete metadata
        # Note: photo_url column may not exist in older databases
        try:
            authors = execute_query("""
                SELECT id, name FROM authors 
                WHERE biography IS NULL OR biography = ''
            """)
        except Exception as e:
            LOGGER.warning(f"Could not query authors: {e}")
            authors = []
        
        if not authors:
            LOGGER.info("All authors already have complete metadata")
            return jsonify({
                "success": True,
                "message": "All authors already have complete metadata",
                "stats": stats
            })
        
        stats["authors_checked"] = len(authors)
        LOGGER.info(f"Found {len(authors)} authors to enrich")
        
        for author in authors:
            try:
                author_id = author['id']
                author_name = author['name']
                
                LOGGER.info(f"Enriching author: {author_name}")
                
                # Check if author already has biography
                author_check = execute_query(
                    "SELECT biography FROM authors WHERE id = ?",
                    (author_id,)
                )
                has_biography = author_check and author_check[0].get('biography')
                
                # Priority 1: Try OpenLibrary first (most accurate)
                openlibrary_succeeded = False
                try:
                    from backend.features.author_openlibrary_fetcher import update_author_from_openlibrary
                    if update_author_from_openlibrary(author_id, author_name):
                        stats["openlibrary_updated"] += 1
                        LOGGER.info(f"Updated {author_name} from OpenLibrary")
                        openlibrary_succeeded = True
                        
                        # Check if biography was added by OpenLibrary
                        author_check = execute_query(
                            "SELECT biography FROM authors WHERE id = ?",
                            (author_id,)
                        )
                        has_biography = author_check and author_check[0].get('biography')
                except Exception as e:
                    LOGGER.debug(f"Could not fetch from OpenLibrary for {author_name}: {e}")
                
                # Priority 2: Fallback to Groq AI for biography if still missing
                if not has_biography:
                    try:
                        from backend.features.author_biography_fetcher import update_author_biography
                        if update_author_biography(author_id, author_name):
                            stats["biographies_added"] += 1
                            LOGGER.info(f"Added biography for {author_name} from Groq")
                    except Exception as e:
                        LOGGER.debug(f"Could not fetch biography for {author_name}: {e}")
                
                # Priority 3: Try to fetch photo from OpenLibrary
                try:
                    from backend.features.author_photo_fetcher import update_author_photo
                    if update_author_photo(author_id, author_name):
                        stats["photos_added"] += 1
                        LOGGER.info(f"Added photo for {author_name}")
                except Exception as e:
                    LOGGER.debug(f"Could not fetch photo for {author_name}: {e}")
            
            except Exception as e:
                LOGGER.error(f"Error enriching author {author.get('name', 'Unknown')}: {e}")
                stats["errors"] += 1
        
        LOGGER.info(f"Author enrichment complete: {stats}")
        
        return jsonify({
            "success": True,
            "message": "Author enrichment completed",
            "stats": stats
        })
    
    except Exception as e:
        LOGGER.error(f"Error in enrich_all_authors: {e}")
        import traceback
        LOGGER.error(traceback.format_exc())
        return jsonify({
            "success": False,
            "error": str(e),
            "message": "Failed to enrich authors"
        }), 500


@author_enrichment_api_bp.route('/authors/<int:author_id>/enrich', methods=['POST'])
def enrich_single_author(author_id: int):
    """
    Enrich a single author with metadata.
    
    Args:
        author_id: Author ID to enrich
    
    Returns:
        Response: Enrichment result
    """
    try:
        LOGGER.info(f"Enriching author {author_id}...")
        
        # Get author
        author = execute_query("SELECT id, name FROM authors WHERE id = ?", (author_id,))
        
        if not author:
            return jsonify({"error": "Author not found"}), 404
        
        author_name = author[0]['name']
        stats = {
            "biography_added": False,
            "photo_added": False
        }
        
        # Try to fetch biography
        try:
            from backend.features.author_biography_fetcher import update_author_biography
            if update_author_biography(author_id, author_name):
                stats["biography_added"] = True
                LOGGER.info(f"Added biography for {author_name}")
        except Exception as e:
            LOGGER.debug(f"Could not fetch biography for {author_name}: {e}")
        
        # Try to fetch photo
        try:
            from backend.features.author_photo_fetcher import update_author_photo
            if update_author_photo(author_id, author_name):
                stats["photo_added"] = True
                LOGGER.info(f"Added photo for {author_name}")
        except Exception as e:
            LOGGER.debug(f"Could not fetch photo for {author_name}: {e}")
        
        return jsonify({
            "success": True,
            "message": f"Author {author_name} enriched",
            "stats": stats
        })
    
    except Exception as e:
        LOGGER.error(f"Error enriching author {author_id}: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@author_enrichment_api_bp.route('/authors/<int:author_id>/edit', methods=['PUT'])
def edit_author(author_id: int):
    """
    Manually edit author information.
    
    Request body:
        {
            "name": "Author Name",
            "biography": "Author biography",
            "birth_date": "YYYY-MM-DD",
            "description": "Short description"
        }
    
    Returns:
        Response: Updated author data
    """
    try:
        data = request.json or {}
        
        # Get author
        author = execute_query("SELECT id FROM authors WHERE id = ?", (author_id,))
        if not author:
            return jsonify({"error": "Author not found"}), 404
        
        # Build update query
        updates = []
        params = []
        
        if 'name' in data and data['name']:
            updates.append("name = ?")
            params.append(data['name'].strip())
        
        if 'biography' in data and data['biography']:
            updates.append("biography = ?")
            params.append(data['biography'].strip())
        
        if 'birth_date' in data and data['birth_date']:
            updates.append("birth_date = ?")
            params.append(data['birth_date'].strip())
        
        if 'description' in data and data['description']:
            updates.append("description = ?")
            params.append(data['description'].strip())
        
        if not updates:
            return jsonify({"error": "No fields to update"}), 400
        
        # Add updated_at
        updates.append("updated_at = CURRENT_TIMESTAMP")
        params.append(author_id)
        
        # Execute update
        query = f"""
            UPDATE authors 
            SET {', '.join(updates)}
            WHERE id = ?
        """
        
        execute_query(query, params, commit=True)
        
        LOGGER.info(f"Author {author_id} updated manually")
        
        # Return updated author
        updated_author = execute_query("""
            SELECT id, name, biography, birth_date, description, photo_url
            FROM authors WHERE id = ?
        """, (author_id,))
        
        if updated_author:
            return jsonify({
                "success": True,
                "message": "Author updated successfully",
                "author": updated_author[0]
            })
        else:
            return jsonify({"error": "Failed to retrieve updated author"}), 500
    
    except Exception as e:
        LOGGER.error(f"Error editing author {author_id}: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@author_enrichment_api_bp.route('/authors/check-incomplete', methods=['GET'])
def check_incomplete_authors():
    """
    Check how many authors have incomplete metadata.
    
    Returns:
        Response: Count of incomplete authors
    """
    try:
        # Get count of authors without biography
        no_bio = execute_query("""
            SELECT COUNT(*) as count FROM authors 
            WHERE biography IS NULL OR biography = ''
        """)
        
        # Get count of authors without photo (if column exists)
        no_photo_count = 0
        try:
            no_photo = execute_query("""
                SELECT COUNT(*) as count FROM authors 
                WHERE photo_url IS NULL OR photo_url = ''
            """)
            no_photo_count = no_photo[0]['count'] if no_photo else 0
        except Exception as e:
            LOGGER.debug(f"photo_url column may not exist: {e}")
            no_photo_count = 0
        
        # Get total authors
        total = execute_query("SELECT COUNT(*) as count FROM authors")
        
        incomplete_count = no_bio[0]['count'] if no_bio else 0
        
        return jsonify({
            "total_authors": total[0]['count'] if total else 0,
            "authors_without_biography": no_bio[0]['count'] if no_bio else 0,
            "authors_without_photo": no_photo_count,
            "incomplete_authors": incomplete_count
        })
    
    except Exception as e:
        LOGGER.error(f"Error checking incomplete authors: {e}")
        return jsonify({"error": str(e)}), 500


@author_enrichment_api_bp.route('/readme/update-all', methods=['POST'])
def update_all_readme_files():
    """
    Update all existing README.txt files with new metadata fields.
    
    This endpoint will:
    1. Find all README.txt files in root folders
    2. Read existing metadata
    3. Fetch missing metadata from series database
    4. Update README.txt with new fields (cover_url, author, publisher, isbn, genres)
    
    Returns:
        Response: Statistics about the update operation
    """
    try:
        from pathlib import Path
        from backend.base.helpers import read_metadata_from_readme
        from backend.internals.settings import Settings
        from datetime import datetime
        
        LOGGER.info("Starting README.txt update process...")
        
        stats = {
            "readme_files_found": 0,
            "readme_files_updated": 0,
            "errors": 0
        }
        
        # Get root folders from settings
        settings = Settings().get_settings()
        root_folders = settings.root_folders
        
        if not root_folders:
            return jsonify({
                "success": False,
                "message": "No root folders configured",
                "stats": stats
            }), 400
        
        # Find all README.txt files
        readme_files = []
        for root_folder in root_folders:
            root_path = Path(root_folder['path'])
            if root_path.exists():
                for readme_path in root_path.rglob('README.txt'):
                    readme_files.append(readme_path)
        
        stats["readme_files_found"] = len(readme_files)
        LOGGER.info(f"Found {len(readme_files)} README.txt files")
        
        if not readme_files:
            return jsonify({
                "success": True,
                "message": "No README.txt files found",
                "stats": stats
            })
        
        # Update each README.txt file
        for readme_path in readme_files:
            try:
                series_dir = readme_path.parent
                readme_metadata = read_metadata_from_readme(series_dir)
                
                # Get series data from database
                series_id = readme_metadata.get('series_id')
                if not series_id:
                    series_title = readme_metadata.get('title')
                    if series_title:
                        series_result = execute_query(
                            "SELECT id, title, author, publisher, cover_url, metadata_source, metadata_id, content_type FROM series WHERE title = ? LIMIT 1",
                            (series_title,)
                        )
                        if not series_result:
                            LOGGER.warning(f"Series not found for README: {readme_path}")
                            continue
                        series_data = series_result[0]
                    else:
                        LOGGER.warning(f"No series title in README: {readme_path}")
                        continue
                else:
                    series_result = execute_query(
                        "SELECT id, title, author, publisher, cover_url, metadata_source, metadata_id, content_type FROM series WHERE id = ?",
                        (series_id,)
                    )
                    if not series_result:
                        LOGGER.warning(f"Series not found for ID {series_id}: {readme_path}")
                        continue
                    series_data = series_result[0]
                
                # Build new README content
                lines = []
                
                # Read existing content to preserve Created timestamp
                existing_created = None
                try:
                    with open(readme_path, 'r') as f:
                        for line in f:
                            if line.startswith('Created:'):
                                existing_created = line.split(':', 1)[1].strip()
                                break
                except Exception:
                    pass
                
                # Required fields
                lines.append(f"Series: {series_data.get('title', 'Unknown')}")
                lines.append(f"ID: {series_data.get('id', '')}")
                lines.append(f"Type: {series_data.get('content_type', 'MANGA')}")
                
                # Provider information
                if series_data.get('metadata_source'):
                    lines.append(f"Provider: {series_data['metadata_source']}")
                if series_data.get('metadata_id'):
                    lines.append(f"MetadataID: {series_data['metadata_id']}")
                
                # Optional metadata fields
                if series_data.get('author') and series_data['author'] != 'Unknown':
                    lines.append(f"Author: {series_data['author']}")
                if series_data.get('publisher') and series_data['publisher'] != 'Unknown':
                    lines.append(f"Publisher: {series_data['publisher']}")
                if series_data.get('cover_url'):
                    lines.append(f"CoverURL: {series_data['cover_url']}")
                
                # Preserve existing Created timestamp
                if existing_created:
                    lines.append(f"Created: {existing_created}")
                else:
                    lines.append(f"Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                
                # Add footer
                lines.append("")
                lines.append("This folder is managed by Readloom. Place your e-book files here.")
                
                # Write updated README
                new_content = '\n'.join(lines)
                with open(readme_path, 'w') as f:
                    f.write(new_content)
                
                stats["readme_files_updated"] += 1
                LOGGER.info(f"Updated README.txt: {readme_path}")
            
            except Exception as e:
                LOGGER.error(f"Error updating README.txt {readme_path}: {e}")
                stats["errors"] += 1
        
        LOGGER.info(f"README.txt update complete: {stats}")
        
        return jsonify({
            "success": True,
            "message": f"Updated {stats['readme_files_updated']} README.txt file(s)",
            "stats": stats
        })
    
    except Exception as e:
        LOGGER.error(f"Error in update_all_readme_files: {e}")
        import traceback
        LOGGER.error(traceback.format_exc())
        return jsonify({
            "success": False,
            "error": str(e),
            "message": "Failed to update README.txt files"
        }), 500
