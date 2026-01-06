#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Authors API routes.
Defines all author endpoints.
"""

from flask import Blueprint, jsonify, request
from backend.base.logging import LOGGER

from .crud import create_author, read_author, update_author, delete_author, get_all_authors
from .search import search_authors, get_authors_by_book_count, get_popular_authors
from .metadata import get_author_metadata, update_author_metadata
from .enrichment import enrich_author_bio, enrich_author_photo, enrich_author_complete
from .import_service import import_author_from_openlibrary, import_authors_batch

# Create routes blueprint
authors_routes = Blueprint('authors_routes', __name__)


@authors_routes.route('/api/authors', methods=['GET'])
def list_authors():
    """Get all authors with book counts."""
    try:
        from backend.internals.db import execute_query
        
        limit = request.args.get('limit', type=int)
        offset = request.args.get('offset', 0, type=int)
        search = request.args.get('search', '')
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 12, type=int)
        
        # Build query with book counts - only return authors with books (not manga authors)
        query = """
            SELECT a.*, COUNT(DISTINCT ab.series_id) as book_count
            FROM authors a
            LEFT JOIN author_books ab ON a.id = ab.author_id
            LEFT JOIN series s ON ab.series_id = s.id
            WHERE s.content_type IN ('BOOK', 'NOVEL') OR ab.series_id IS NULL
        """
        
        params = []
        if search:
            query += " AND LOWER(a.name) LIKE LOWER(?)"
            params.append(f"%{search}%")
        
        query += " GROUP BY a.id HAVING COUNT(DISTINCT CASE WHEN s.content_type IN ('BOOK', 'NOVEL') THEN ab.series_id END) > 0 ORDER BY a.name ASC"
        
        # Get total count - only count authors with books
        count_query = """
            SELECT COUNT(DISTINCT a.id) as total FROM authors a
            LEFT JOIN author_books ab ON a.id = ab.author_id
            LEFT JOIN series s ON ab.series_id = s.id
            WHERE s.content_type IN ('BOOK', 'NOVEL')
        """
        if search:
            count_query += " AND LOWER(a.name) LIKE LOWER(?)"
        
        count_result = execute_query(count_query, (params[0],) if search else ())
        total = count_result[0]['total'] if count_result else 0
        
        # Apply pagination
        if page and per_page:
            offset = (page - 1) * per_page
            query += f" LIMIT ? OFFSET ?"
            params.extend([per_page, offset])
        elif limit:
            query += f" LIMIT ? OFFSET ?"
            params.extend([limit, offset])
        
        authors = execute_query(query, tuple(params))
        
        # Add default released_books_count (will be fetched asynchronously on frontend)
        for author in authors:
            if 'released_books_count' not in author:
                author['released_books_count'] = 0
        
        # Calculate pagination info
        pages = (total + per_page - 1) // per_page if per_page else 1
        
        return jsonify({
            "success": True,
            "authors": authors or [],
            "pagination": {
                "page": page,
                "pages": pages,
                "per_page": per_page,
                "total": total
            }
        }), 200
    except Exception as e:
        LOGGER.error(f"Error listing authors: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@authors_routes.route('/api/authors', methods=['POST'])
def create_new_author():
    """Create a new author."""
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        author, status = create_author(data)
        return jsonify({"author": author}), status
    except Exception as e:
        LOGGER.error(f"Error creating author: {e}")
        return jsonify({"error": str(e)}), 500


@authors_routes.route('/api/authors/<int:author_id>', methods=['GET'])
def get_author(author_id):
    """Get author details with books."""
    try:
        from backend.internals.db import execute_query
        
        # Get author info
        author, status = read_author(author_id)
        if status != 200:
            return jsonify(author), status
        
        # Get books by this author
        books = execute_query("""
            SELECT s.id, s.title, s.content_type, s.cover_url,
                   COUNT(DISTINCT v.id) as volumes,
                   COUNT(DISTINCT c.id) as chapters
            FROM series s
            JOIN author_books ab ON s.id = ab.series_id
            LEFT JOIN volumes v ON s.id = v.series_id
            LEFT JOIN chapters c ON s.id = c.series_id
            WHERE ab.author_id = ?
            GROUP BY s.id
            ORDER BY s.title ASC
        """, (author_id,))
        
        # Try to fetch released books count from OpenLibrary
        released_books_count = 0
        try:
            author_name = author.get('name', '')
            if author_name:
                from backend.features.metadata_providers.openlibrary.provider import OpenLibraryProvider
                import requests
                
                provider = OpenLibraryProvider()
                # Search for author on OpenLibrary
                search_url = f"{provider.base_url}/search/authors.json"
                response = requests.get(search_url, params={"q": author_name}, timeout=5)
                
                if response.ok:
                    data = response.json()
                    if data.get("docs") and len(data["docs"]) > 0:
                        released_books_count = data["docs"][0].get("work_count", 0)
                        LOGGER.debug(f"Found {released_books_count} books for author {author_name} on OpenLibrary")
        except Exception as e:
            LOGGER.debug(f"Could not fetch released books count from OpenLibrary: {e}")
        
        return jsonify({
            "author": author,
            "books": books or [],
            "book_count": len(books) if books else 0,
            "released_books_count": released_books_count
        }), 200
    except Exception as e:
        LOGGER.error(f"Error getting author: {e}")
        return jsonify({"error": str(e)}), 500


@authors_routes.route('/api/authors/<int:author_id>', methods=['PUT'])
def update_author_endpoint(author_id):
    """Update an author."""
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        author, status = update_author(author_id, data)
        return jsonify(author), status
    except Exception as e:
        LOGGER.error(f"Error updating author: {e}")
        return jsonify({"error": str(e)}), 500


@authors_routes.route('/api/authors/<int:author_id>', methods=['DELETE'])
def delete_author_endpoint(author_id):
    """Delete an author."""
    try:
        result, status = delete_author(author_id)
        return jsonify(result), status
    except Exception as e:
        LOGGER.error(f"Error deleting author: {e}")
        return jsonify({"error": str(e)}), 500


@authors_routes.route('/api/authors/search', methods=['GET'])
def search_authors_endpoint():
    """Search authors."""
    try:
        query = request.args.get('q', '')
        if not query:
            return jsonify({"error": "Search query required"}), 400
        
        authors = search_authors(query)
        return jsonify({"authors": authors}), 200
    except Exception as e:
        LOGGER.error(f"Error searching authors: {e}")
        return jsonify({"error": str(e)}), 500


@authors_routes.route('/api/authors/popular', methods=['GET'])
def get_popular_authors_endpoint():
    """Get popular authors."""
    try:
        limit = request.args.get('limit', 5, type=int)
        authors = get_popular_authors(limit)
        return jsonify({"authors": authors}), 200
    except Exception as e:
        LOGGER.error(f"Error getting popular authors: {e}")
        return jsonify({"error": str(e)}), 500


@authors_routes.route('/api/authors/<int:author_id>/metadata', methods=['GET'])
def get_author_metadata_endpoint(author_id):
    """Get author metadata."""
    try:
        metadata, status = get_author_metadata(author_id)
        return jsonify(metadata), status
    except Exception as e:
        LOGGER.error(f"Error getting author metadata: {e}")
        return jsonify({"error": str(e)}), 500


@authors_routes.route('/api/authors/<int:author_id>/enrich', methods=['POST'])
def enrich_author_endpoint(author_id):
    """Enrich author data."""
    try:
        author, status = enrich_author_complete(author_id)
        return jsonify({"author": author}), status
    except Exception as e:
        LOGGER.error(f"Error enriching author: {e}")
        return jsonify({"error": str(e)}), 500


@authors_routes.route('/api/authors/import', methods=['POST'])
def import_author_endpoint():
    """Import author from external source."""
    try:
        data = request.json
        if not data or "name" not in data:
            return jsonify({"error": "Author name required"}), 400
        
        author, status = import_author_from_openlibrary(data["name"])
        return jsonify({"author": author}), status
    except Exception as e:
        LOGGER.error(f"Error importing author: {e}")
        return jsonify({"error": str(e)}), 500


@authors_routes.route('/api/authors/import/batch', methods=['POST'])
def import_authors_batch_endpoint():
    """Import multiple authors."""
    try:
        data = request.json
        if not data or "names" not in data:
            return jsonify({"error": "Author names required"}), 400
        
        results, status = import_authors_batch(data["names"])
        return jsonify(results), status
    except Exception as e:
        LOGGER.error(f"Error importing authors batch: {e}")
        return jsonify({"error": str(e)}), 500


@authors_routes.route('/api/authors/sync-readme', methods=['POST'])
def sync_author_readme_endpoint():
    """Sync all author README files with database.
    
    Query parameters:
        merge (bool): If true, merge with existing README data instead of overwriting.
    """
    try:
        from backend.features.author_readme_sync import sync_all_author_readmes
        
        merge_with_existing = request.args.get('merge', 'false').lower() == 'true'
        
        stats = sync_all_author_readmes(merge_with_existing=merge_with_existing)
        
        return jsonify({
            "success": True,
            "message": f"Synced {stats['synced']} author README files",
            "stats": stats
        }), 200
    except Exception as e:
        LOGGER.error(f"Error syncing author READMEs: {e}")
        return jsonify({"error": str(e)}), 500
