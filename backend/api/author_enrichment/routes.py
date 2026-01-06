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


@author_enrichment_api_bp.route('/authors/<int:author_id>/popular-books', methods=['GET'])
def get_popular_books(author_id: int):
    """
    Get popular books for an author from OpenLibrary.
    
    Args:
        author_id: Author ID to fetch popular books for
    
    Returns:
        Response: List of popular books with covers and metadata
    """
    try:
        LOGGER.info(f"Fetching popular books for author {author_id}...")
        
        # Get author from database
        author = execute_query("SELECT id, name FROM authors WHERE id = ?", (author_id,))
        
        if not author:
            return jsonify({"error": "Author not found"}), 404
        
        author_name = author[0]['name']
        
        # Try to get popular books from OpenLibrary
        try:
            from backend.features.author_openlibrary_fetcher import get_author_popular_books
            popular_books = get_author_popular_books(author_id, author_name)
            
            if popular_books:
                LOGGER.info(f"Found {len(popular_books)} popular books for {author_name}")
                return jsonify({
                    "success": True,
                    "books": popular_books,
                    "count": len(popular_books)
                })
            else:
                LOGGER.info(f"No popular books found for {author_name}")
                return jsonify({
                    "success": True,
                    "books": [],
                    "count": 0
                })
                
        except Exception as e:
            LOGGER.error(f"Error fetching popular books from OpenLibrary: {e}")
            return jsonify({
                "success": False,
                "error": f"Failed to fetch popular books: {str(e)}",
                "books": [],
                "count": 0
            }), 500
    
    except Exception as e:
        LOGGER.error(f"Error in get_popular_books for author {author_id}: {e}")
        return jsonify({
            "success": False,
            "error": str(e),
            "books": [],
            "count": 0
        }), 500


@author_enrichment_api_bp.route('/authors/<int:author_id>/books', methods=['GET'])
def get_author_books(author_id: int):
    """
    Get books in library for a specific author.
    
    Args:
        author_id: Author ID to fetch books for
    
    Returns:
        Response: List of books in library by this author
    """
    try:
        LOGGER.info(f"Fetching library books for author {author_id}...")
        
        # Get books from library for this author
        books = execute_query("""
            SELECT s.id, s.name as title, s.cover_url, s.description
            FROM series s
            JOIN author_books ab ON s.id = ab.series_id
            WHERE ab.author_id = ?
            ORDER BY s.name
        """, (author_id,))
        
        if books:
            LOGGER.info(f"Found {len(books)} library books for author {author_id}")
            return jsonify({
                "success": True,
                "books": books,
                "count": len(books)
            })
        else:
            LOGGER.info(f"No library books found for author {author_id}")
            return jsonify({
                "success": True,
                "books": [],
                "count": 0
            })
    
    except Exception as e:
        LOGGER.error(f"Error fetching library books for author {author_id}: {e}")
        return jsonify({
            "success": False,
            "error": str(e),
            "books": [],
            "count": 0
        }), 500


@author_enrichment_api_bp.route('/authors/<int:author_id>/released-count', methods=['GET'])
def get_released_books_count(author_id: int):
    """
    Get total released books count for an author (from OpenLibrary).
    
    Args:
        author_id: Author ID to fetch count for
    
    Returns:
        Response: Total count of released books
    """
    try:
        LOGGER.info(f"Fetching released books count for author {author_id}...")
        
        # Get author from database
        author = execute_query("SELECT id, name FROM authors WHERE id = ?", (author_id,))
        
        if not author:
            return jsonify({"error": "Author not found"}), 404
        
        author_name = author[0]['name']
        
        # Try to get work count from OpenLibrary
        try:
            from backend.features.author_openlibrary_fetcher import get_author_work_count
            work_count = get_author_work_count(author_id, author_name)
            
            if work_count is not None:
                LOGGER.info(f"Found {work_count} total works for {author_name}")
                return jsonify({
                    "success": True,
                    "count": work_count
                })
            else:
                LOGGER.info(f"No work count found for {author_name}")
                return jsonify({
                    "success": True,
                    "count": 0
                })
                
        except Exception as e:
            LOGGER.error(f"Error fetching work count from OpenLibrary: {e}")
            return jsonify({
                "success": False,
                "error": f"Failed to fetch work count: {str(e)}",
                "count": 0
            }), 500
    
    except Exception as e:
        LOGGER.error(f"Error getting released books count for author {author_id}: {e}")
        return jsonify({
            "success": False,
            "error": str(e),
            "count": 0
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
