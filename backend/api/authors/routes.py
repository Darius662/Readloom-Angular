#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
API endpoints for author-related operations.
"""

from flask import Blueprint, jsonify, request

from backend.base.logging import LOGGER
from backend.features.book_service import BookService
from backend.internals.db import execute_query


# Create API blueprint
authors_api_bp = Blueprint('api_authors', __name__, url_prefix='/api/authors')


@authors_api_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    LOGGER.info("Health check called")
    return jsonify({"status": "ok"})


@authors_api_bp.route('/test', methods=['GET'])
def test_endpoint():
    """Test endpoint."""
    LOGGER.info("Test endpoint called")
    return jsonify({"test": "ok"})


@authors_api_bp.route('/', methods=['GET'])
def get_all_authors():
    """Get all authors with pagination, search, and enriched data.
    
    Query parameters:
        - search: Search term for author name
        - page: Page number (default: 1)
        - per_page: Items per page (default: 12)
    
    Returns:
        Response: The authors with enriched data and pagination info.
    """
    try:
        LOGGER.info("get_all_authors API called")
        
        search = request.args.get('search', '').strip()
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 12))
        
        # Calculate offset
        offset = (page - 1) * per_page
        
        # Build query - simplified to avoid JOIN issues
        # Note: photo_url column may not exist in all database versions
        if search:
            query = """
                SELECT 
                    a.id, 
                    a.name, 
                    a.biography, 
                    a.birth_date,
                    a.created_at,
                    COUNT(DISTINCT ab.series_id) as book_count
                FROM authors a
                LEFT JOIN author_books ab ON a.id = ab.author_id
                WHERE a.name LIKE ?
                GROUP BY a.id
                ORDER BY a.name ASC
                LIMIT ? OFFSET ?
            """
            params = (f'%{search}%', per_page, offset)
            
            count_query = "SELECT COUNT(*) as count FROM authors WHERE name LIKE ?"
            count_params = (f'%{search}%',)
        else:
            query = """
                SELECT 
                    a.id, 
                    a.name, 
                    a.biography, 
                    a.birth_date,
                    a.created_at,
                    COUNT(DISTINCT ab.series_id) as book_count
                FROM authors a
                LEFT JOIN author_books ab ON a.id = ab.author_id
                GROUP BY a.id
                ORDER BY a.name ASC
                LIMIT ? OFFSET ?
            """
            params = (per_page, offset)
            
            count_query = "SELECT COUNT(*) as count FROM authors"
            count_params = ()
        
        LOGGER.info(f"Executing query with params: {params}")
        
        # Get authors with statistics
        authors = execute_query(query, params)
        LOGGER.info(f"Query returned {len(authors) if authors else 0} authors")
        
        # Set default released_books_count to 0 for all authors
        # OpenLibrary data is fetched asynchronously on the frontend to avoid blocking
        for author in authors:
            author['released_books_count'] = 0
        
        # Get total count
        count_result = execute_query(count_query, count_params)
        total = count_result[0]['count'] if count_result else 0
        
        LOGGER.info(f"Total authors in database: {total}")
        LOGGER.info(f"Returning {len(authors) if authors else 0} authors")
        
        response = jsonify({
            "success": True,
            "authors": authors if authors else [],
            "total": total,
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": total,
                "pages": (total + per_page - 1) // per_page if total > 0 else 0
            }
        })
        # Add no-cache headers to prevent browser caching issues
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response
        
    except Exception as e:
        LOGGER.error(f"Error getting all authors: {e}")
        import traceback
        LOGGER.error(traceback.format_exc())
        return jsonify({
            "success": False,
            "error": str(e),
            "message": "Failed to load authors. Check server logs for details."
        }), 500


@authors_api_bp.route('/<int:author_id>', methods=['GET'])
def get_author_details(author_id):
    """Get author details including books from library and OpenLibrary stats.
    
    Args:
        author_id: The author ID.
        
    Returns:
        Response: The author details with books and OpenLibrary stats.
    """
    try:
        book_service = BookService()
        author = book_service.get_author_details(author_id)
        
        if "error" in author:
            return jsonify({
                "success": False,
                "error": author["error"]
            }), 404
        
        # Get books by this author from the library
        books = book_service.get_books_by_author(author_id)
        
        # Set defaults for OpenLibrary data (fetched asynchronously on frontend)
        released_books_count = 0
        provider_books = []
        metadata_provider = None
        
        # Get metadata provider from the author's books in the library (fast database query only)
        try:
            if books:
                # Get the metadata source from the first book by this author
                first_book_provider = execute_query("""
                    SELECT DISTINCT s.metadata_source 
                    FROM series s
                    JOIN author_books ab ON s.id = ab.series_id
                    WHERE ab.author_id = ?
                    LIMIT 1
                """, (author_id,))
                
                if first_book_provider:
                    metadata_provider = first_book_provider[0].get('metadata_source')
                    LOGGER.info(f"Found metadata provider for author {author_id}: {metadata_provider}")
                else:
                    LOGGER.info(f"No metadata provider found for author {author_id}")
        except Exception as e:
            LOGGER.error(f"Could not determine metadata provider for author {author_id}: {e}")
        
        # Note: OpenLibrary data (released_books_count and provider_books) will be fetched 
        # asynchronously on the frontend to avoid blocking the initial response
        
        return jsonify({
            "success": True,
            "author": author,
            "books": books,
            "released_books_count": released_books_count,
            "metadata_provider": metadata_provider,
            "provider_books": provider_books
        })
    except Exception as e:
        LOGGER.error(f"Error getting author details: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@authors_api_bp.route('/<int:author_id>/books', methods=['GET'])
def get_books_by_author(author_id):
    """Get books by author.
    
    Args:
        author_id: The author ID.
        
    Returns:
        Response: The books by the author.
    """
    try:
        book_service = BookService()
        books = book_service.get_books_by_author(author_id)
        
        return jsonify({
            "success": True,
            "books": books
        })
    except Exception as e:
        LOGGER.error(f"Error getting books by author: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@authors_api_bp.route('/', methods=['POST'])
def create_author():
    """Create a new author.
    
    Returns:
        Response: The created author.
    """
    try:
        data = request.json
        
        if not data or "name" not in data:
            return jsonify({
                "success": False,
                "error": "Name is required"
            }), 400
        
        name = data["name"]
        description = data.get("description", "")
        
        # Insert the author
        from backend.internals.db import execute_query
        execute_query(
            "INSERT INTO authors (name, description) VALUES (?, ?)",
            (name, description),
            commit=True
        )
        
        # Get the new author ID
        author_id = execute_query("SELECT last_insert_rowid() as id")[0]["id"]
        
        # Get the author details
        book_service = BookService()
        author = book_service.get_author_details(author_id)
        
        return jsonify({
            "success": True,
            "author": author
        }), 201
    except Exception as e:
        LOGGER.error(f"Error creating author: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@authors_api_bp.route('/<int:author_id>', methods=['PUT'])
def update_author(author_id):
    """Update an author.
    
    Args:
        author_id: The author ID.
        
    Returns:
        Response: The updated author.
    """
    try:
        data = request.json
        
        if not data:
            return jsonify({
                "success": False,
                "error": "No data provided"
            }), 400
        
        # Check if the author exists
        from backend.internals.db import execute_query
        author = execute_query("SELECT * FROM authors WHERE id = ?", (author_id,))
        
        if not author:
            return jsonify({
                "success": False,
                "error": "Author not found"
            }), 404
        
        # Update the author
        updates = []
        params = []
        
        if "name" in data:
            updates.append("name = ?")
            params.append(data["name"])
        
        if "description" in data:
            updates.append("description = ?")
            params.append(data["description"])
        
        if not updates:
            return jsonify({
                "success": False,
                "error": "No fields to update"
            }), 400
        
        # Add updated_at timestamp
        updates.append("updated_at = CURRENT_TIMESTAMP")
        
        # Add author_id to params
        params.append(author_id)
        
        # Execute the update
        execute_query(
            f"UPDATE authors SET {', '.join(updates)} WHERE id = ?",
            params,
            commit=True
        )
        
        # Get the updated author details
        book_service = BookService()
        updated_author = book_service.get_author_details(author_id)
        
        return jsonify({
            "success": True,
            "author": updated_author
        })
    except Exception as e:
        LOGGER.error(f"Error updating author: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@authors_api_bp.route('/<int:author_id>', methods=['DELETE'])
def delete_author(author_id):
    """Delete an author.
    
    Args:
        author_id: The author ID.
        
    Returns:
        Response: Success message.
    """
    try:
        # Check if the author exists
        from backend.internals.db import execute_query
        author = execute_query("SELECT * FROM authors WHERE id = ?", (author_id,))
        
        if not author:
            return jsonify({
                "success": False,
                "error": "Author not found"
            }), 404
        
        # Check if the author has books
        books = execute_query(
            "SELECT COUNT(*) as count FROM book_authors WHERE author_id = ?",
            (author_id,)
        )
        
        if books and books[0]["count"] > 0:
            return jsonify({
                "success": False,
                "error": f"Cannot delete author with {books[0]['count']} books"
            }), 400
        
        # Delete the author
        execute_query(
            "DELETE FROM authors WHERE id = ?",
            (author_id,),
            commit=True
        )
        
        return jsonify({
            "success": True,
            "message": "Author deleted successfully"
        })
    except Exception as e:
        LOGGER.error(f"Error deleting author: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500
