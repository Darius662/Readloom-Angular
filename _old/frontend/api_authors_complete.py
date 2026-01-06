#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Complete Authors API endpoints for Readloom.
"""

from flask import Blueprint, jsonify, request
from backend.base.logging import LOGGER
from backend.internals.db import execute_query

# Create API blueprint
authors_api_bp = Blueprint('authors_api', __name__, url_prefix='/api/authors')


@authors_api_bp.route('', methods=['GET'])
def get_authors():
    """Get all authors with pagination and search.
    
    Query parameters:
        - search: Search term for author name
        - page: Page number (default: 1)
        - per_page: Items per page (default: 20)
    
    Returns:
        Response: List of authors with pagination info.
    """
    try:
        search = request.args.get('search', '').strip()
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        
        # Calculate offset
        offset = (page - 1) * per_page
        
        # Build query
        if search:
            query = """
                SELECT a.id, a.name, a.biography, a.birth_date, a.created_at,
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
                SELECT a.id, a.name, a.biography, a.birth_date, a.created_at,
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
        
        # Get authors
        authors = execute_query(query, params)
        
        # Get total count
        count_result = execute_query(count_query, count_params)
        total = count_result[0]['count'] if count_result else 0
        
        return jsonify({
            "authors": authors,
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": total,
                "pages": (total + per_page - 1) // per_page
            }
        })
    
    except Exception as e:
        LOGGER.error(f"Error getting authors: {e}")
        return jsonify({"error": str(e)}), 500


@authors_api_bp.route('/<int:author_id>', methods=['GET'])
def get_author(author_id):
    """Get author details with their books.
    
    Args:
        author_id: Author ID
    
    Returns:
        Response: Author details and books.
    """
    try:
        # Get author
        author_query = "SELECT * FROM authors WHERE id = ?"
        author = execute_query(author_query, (author_id,))
        
        if not author:
            return jsonify({"error": "Author not found"}), 404
        
        # Get author's books
        books_query = """
            SELECT s.id, s.title, s.content_type, COUNT(DISTINCT v.id) as volumes
            FROM series s
            JOIN author_books ab ON s.id = ab.series_id
            LEFT JOIN volumes v ON s.id = v.series_id
            WHERE ab.author_id = ?
            GROUP BY s.id
            ORDER BY s.title ASC
        """
        books = execute_query(books_query, (author_id,))
        
        return jsonify({
            "author": author[0],
            "books": books,
            "book_count": len(books)
        })
    
    except Exception as e:
        LOGGER.error(f"Error getting author {author_id}: {e}")
        return jsonify({"error": str(e)}), 500


@authors_api_bp.route('/<int:author_id>/books', methods=['GET'])
def get_author_books(author_id):
    """Get all books by an author.
    
    Args:
        author_id: Author ID
    
    Returns:
        Response: List of books by the author.
    """
    try:
        # Verify author exists
        author = execute_query("SELECT id FROM authors WHERE id = ?", (author_id,))
        if not author:
            return jsonify({"error": "Author not found"}), 404
        
        # Get books
        books_query = """
            SELECT s.id, s.title, s.content_type, s.description,
                   COUNT(DISTINCT v.id) as volumes,
                   COUNT(DISTINCT c.id) as chapters
            FROM series s
            JOIN author_books ab ON s.id = ab.series_id
            LEFT JOIN volumes v ON s.id = v.series_id
            LEFT JOIN chapters c ON s.id = c.series_id
            WHERE ab.author_id = ?
            GROUP BY s.id
            ORDER BY s.title ASC
        """
        books = execute_query(books_query, (author_id,))
        
        return jsonify({
            "author_id": author_id,
            "books": books,
            "count": len(books)
        })
    
    except Exception as e:
        LOGGER.error(f"Error getting author {author_id} books: {e}")
        return jsonify({"error": str(e)}), 500


@authors_api_bp.route('/<int:author_id>', methods=['PUT'])
def update_author(author_id):
    """Update author information.
    
    Args:
        author_id: Author ID
    
    Request body:
        {
            "name": "Author Name",
            "biography": "Biography text",
            "birth_date": "YYYY-MM-DD",
            "death_date": "YYYY-MM-DD"
        }
    
    Returns:
        Response: Updated author.
    """
    try:
        data = request.json or {}
        
        # Verify author exists
        author = execute_query("SELECT id FROM authors WHERE id = ?", (author_id,))
        if not author:
            return jsonify({"error": "Author not found"}), 404
        
        # Update author
        update_fields = []
        params = []
        
        if 'name' in data:
            update_fields.append("name = ?")
            params.append(data['name'])
        
        if 'biography' in data:
            update_fields.append("biography = ?")
            params.append(data['biography'])
        
        if 'birth_date' in data:
            update_fields.append("birth_date = ?")
            params.append(data['birth_date'])
        
        if 'death_date' in data:
            update_fields.append("death_date = ?")
            params.append(data['death_date'])
        
        if not update_fields:
            return jsonify({"error": "No fields to update"}), 400
        
        update_fields.append("updated_at = CURRENT_TIMESTAMP")
        params.append(author_id)
        
        query = f"UPDATE authors SET {', '.join(update_fields)} WHERE id = ?"
        execute_query(query, params)
        
        # Get updated author
        updated = execute_query("SELECT * FROM authors WHERE id = ?", (author_id,))
        
        return jsonify({
            "message": "Author updated successfully",
            "author": updated[0]
        })
    
    except Exception as e:
        LOGGER.error(f"Error updating author {author_id}: {e}")
        return jsonify({"error": str(e)}), 500


@authors_api_bp.route('/<int:author_id>', methods=['DELETE'])
def delete_author(author_id):
    """Delete an author.
    
    Args:
        author_id: Author ID
    
    Returns:
        Response: Success message.
    """
    try:
        # Verify author exists
        author = execute_query("SELECT id FROM authors WHERE id = ?", (author_id,))
        if not author:
            return jsonify({"error": "Author not found"}), 404
        
        # Delete author_books associations
        execute_query("DELETE FROM author_books WHERE author_id = ?", (author_id,))
        
        # Delete author
        execute_query("DELETE FROM authors WHERE id = ?", (author_id,))
        
        return jsonify({"message": "Author deleted successfully"})
    
    except Exception as e:
        LOGGER.error(f"Error deleting author {author_id}: {e}")
        return jsonify({"error": str(e)}), 500


@authors_api_bp.route('/search', methods=['GET'])
def search_authors():
    """Search authors by name.
    
    Query parameters:
        - q: Search query
    
    Returns:
        Response: List of matching authors.
    """
    try:
        query = request.args.get('q', '').strip()
        
        if not query or len(query) < 2:
            return jsonify({"error": "Search query must be at least 2 characters"}), 400
        
        authors = execute_query("""
            SELECT id, name, biography, birth_date
            FROM authors
            WHERE name LIKE ?
            ORDER BY name ASC
            LIMIT 20
        """, (f'%{query}%',))
        
        return jsonify({
            "query": query,
            "results": authors,
            "count": len(authors)
        })
    
    except Exception as e:
        LOGGER.error(f"Error searching authors: {e}")
        return jsonify({"error": str(e)}), 500


@authors_api_bp.route('/sync', methods=['POST'])
def sync_all_authors_endpoint():
    """Manually sync all authors from series.
    
    Returns:
        Response: Sync statistics.
    """
    try:
        from backend.features.authors_sync import sync_all_authors
        
        stats = sync_all_authors()
        
        return jsonify({
            "message": "Author sync completed",
            "stats": stats
        })
    
    except Exception as e:
        LOGGER.error(f"Error syncing authors: {e}")
        return jsonify({"error": str(e)}), 500
