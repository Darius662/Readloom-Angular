#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Series API routes.
Defines all series endpoints.
"""

from flask import Blueprint, jsonify, request
from backend.base.logging import LOGGER
from frontend.middleware import root_folders_required
from backend.internals.db import execute_query
from backend.features.ai_providers.manager import get_ai_provider_manager
from backend.features.metadata_service.facade import search_manga

from .crud import create_series, read_series, update_series, delete_series
from .search import get_series_list, search_series_by_title, filter_by_content_type
from .paths import get_series_folder_path, set_custom_path
from .move import plan_series_move_operation, execute_series_move, validate_move_request
from .scan import scan_series_for_ebooks, validate_scan_request

# Create routes blueprint
series_routes = Blueprint('series_routes', __name__)


@series_routes.route('/api/series/folder-path', methods=['POST'])
def get_folder_path():
    """Get folder path for a series."""
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        required = ["series_id", "title", "content_type"]
        for field in required:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        path = get_series_folder_path(
            data["series_id"],
            data["title"],
            data["content_type"],
            data.get("collection_id"),
            data.get("root_folder_id")
        )
        
        return jsonify({"folder_path": path})
    except Exception as e:
        LOGGER.error(f"Error getting folder path: {e}")
        return jsonify({"error": str(e)}), 500


@series_routes.route('/api/series', methods=['GET'])
def list_series():
    """Get series list."""
    try:
        content_type = request.args.get('content_type')
        limit = request.args.get('limit', type=int)
        sort_by = request.args.get('sort_by', 'title')
        sort_order = request.args.get('sort_order', 'asc')
        
        series = get_series_list(content_type, limit, sort_by, sort_order)
        return jsonify({"series": series})
    except Exception as e:
        LOGGER.error(f"Error listing series: {e}")
        return jsonify({"error": str(e)}), 500


@series_routes.route('/api/series/<int:series_id>', methods=['GET'])
def get_series_detail(series_id):
    """Get series details."""
    try:
        series, status = read_series(series_id)
        return jsonify(series), status
    except Exception as e:
        LOGGER.error(f"Error getting series: {e}")
        return jsonify({"error": str(e)}), 500


@series_routes.route('/api/series', methods=['POST'])
@root_folders_required
def create_new_series():
    """Create a new series."""
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        series, status = create_series(data)
        return jsonify({"series": series}), status
    except Exception as e:
        LOGGER.error(f"Error creating series: {e}")
        return jsonify({"error": str(e)}), 500


@series_routes.route('/api/series/<int:series_id>', methods=['PUT'])
def update_series_detail(series_id):
    """Update a series."""
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        series, status = update_series(series_id, data)
        return jsonify(series), status
    except Exception as e:
        LOGGER.error(f"Error updating series: {e}")
        return jsonify({"error": str(e)}), 500


@series_routes.route('/api/series/<int:series_id>', methods=['DELETE'])
def delete_series_detail(series_id):
    """Delete a series."""
    try:
        result, status = delete_series(series_id)
        return jsonify(result), status
    except Exception as e:
        LOGGER.error(f"Error deleting series: {e}")
        return jsonify({"error": str(e)}), 500


@series_routes.route('/api/series/<int:series_id>/move', methods=['POST'])
def move_series(series_id):
    """Move a series."""
    try:
        data = request.json or {}
        
        # Validate request
        is_valid, error = validate_move_request(
            series_id,
            data.get("collection_id"),
            data.get("root_folder_id")
        )
        if not is_valid:
            return jsonify({"error": error}), 400
        
        result, status = execute_series_move(
            series_id,
            data.get("collection_id"),
            data.get("root_folder_id")
        )
        return jsonify(result), status
    except Exception as e:
        LOGGER.error(f"Error moving series: {e}")
        return jsonify({"error": str(e)}), 500


@series_routes.route('/api/series/<int:series_id>/custom-path', methods=['PUT'])
def set_series_custom_path(series_id):
    """Set custom path for a series."""
    try:
        data = request.json
        if not data or "custom_path" not in data:
            return jsonify({"error": "Custom path is required"}), 400
        
        result, status = set_custom_path(series_id, data["custom_path"])
        return jsonify(result), status
    except Exception as e:
        LOGGER.error(f"Error setting custom path: {e}")
        return jsonify({"error": str(e)}), 500


@series_routes.route('/api/series/<int:series_id>/scan', methods=['POST'])
def scan_series(series_id):
    """Scan a series for e-books."""
    try:
        # Validate request
        is_valid, error = validate_scan_request(series_id)
        if not is_valid:
            return jsonify({"error": error}), 400
        
        result, status = scan_series_for_ebooks(series_id)
        return jsonify(result), status
    except Exception as e:
        LOGGER.error(f"Error scanning series: {e}")
        return jsonify({"error": str(e)}), 500


@series_routes.route('/api/series/sync-readme', methods=['POST'])
def sync_series_readme():
    """Sync all book series README files with database.
    
    Query parameters:
        merge (bool): If true, merge with existing README data instead of overwriting.
    """
    try:
        from backend.features.readme_sync import sync_all_series_readmes
        
        merge_with_existing = request.args.get('merge', 'false').lower() == 'true'
        
        stats = sync_all_series_readmes(content_type='BOOK', merge_with_existing=merge_with_existing)
        
        return jsonify({
            "success": True,
            "message": f"Synced {stats['synced']} book README files",
            "stats": stats
        }), 200
    except Exception as e:
        LOGGER.error(f"Error syncing book READMEs: {e}")
        return jsonify({"error": str(e)}), 500


@series_routes.route('/api/series/sync-readme-manga', methods=['POST'])
def sync_manga_readme():
    """Sync all manga series README files with database.
    
    Query parameters:
        merge (bool): If true, merge with existing README data instead of overwriting.
    """
    try:
        from backend.features.readme_sync import sync_all_series_readmes
        
        merge_with_existing = request.args.get('merge', 'false').lower() == 'true'
        
        stats = sync_all_series_readmes(content_type='MANGA', merge_with_existing=merge_with_existing)
        
        return jsonify({
            "success": True,
            "message": f"Synced {stats['synced']} manga README files",
            "stats": stats
        }), 200
    except Exception as e:
        LOGGER.error(f"Error syncing manga READMEs: {e}")
        return jsonify({"error": str(e)}), 500


@series_routes.route('/api/series/manga/filtered', methods=['GET'])
def get_filtered_manga():
    """Get filtered and sorted manga series.
    
    Query parameters:
        sort_by: 'name' (default) or 'release_date'
        filter_name: Filter by manga name (partial match)
    """
    try:
        from backend.internals.db import execute_query
        
        sort_by = request.args.get('sort_by', 'name').lower()
        filter_name = request.args.get('filter_name', '').strip()
        
        # Build query
        query = """
            SELECT id, title, author, publisher, cover_url, status, published_date, created_at
            FROM series
            WHERE UPPER(content_type) IN ('MANGA', 'MANHWA', 'MANHUA', 'COMIC')
        """
        params = []
        
        # Add name filter if provided
        if filter_name:
            query += " AND LOWER(title) LIKE LOWER(?)"
            params.append(f"%{filter_name}%")
        
        # Add sorting
        if sort_by == 'release_date':
            query += " ORDER BY published_date DESC, title ASC"
        else:  # default to name
            query += " ORDER BY title ASC"
        
        manga = execute_query(query, tuple(params))
        
        return jsonify({
            "success": True,
            "manga": manga if manga else [],
            "count": len(manga) if manga else 0
        }), 200
    except Exception as e:
        LOGGER.error(f"Error getting filtered manga: {e}")
        return jsonify({"error": str(e)}), 500


@series_routes.route('/api/series/books/filtered', methods=['GET'])
def get_filtered_books():
    """Get filtered and sorted books.
    
    Query parameters:
        sort_by: 'author' (default), 'title', or 'release_date'
        filter_author: Filter by author name (partial match)
        filter_name: Filter by book title (partial match)
        filter_year: Filter by release year (YYYY)
    """
    try:
        from backend.internals.db import execute_query
        
        sort_by = request.args.get('sort_by', 'author').lower()
        filter_author = request.args.get('filter_author', '').strip()
        filter_name = request.args.get('filter_name', '').strip()
        filter_year = request.args.get('filter_year', '').strip()
        
        # Build query
        query = """
            SELECT DISTINCT s.id, s.title, s.author, s.publisher, s.cover_url, s.status, s.published_date, s.created_at
            FROM series s
            WHERE UPPER(s.content_type) IN ('BOOK', 'NOVEL')
        """
        params = []
        
        # Add filters
        if filter_author:
            query += " AND LOWER(s.author) LIKE LOWER(?)"
            params.append(f"%{filter_author}%")
        
        if filter_name:
            query += " AND LOWER(s.title) LIKE LOWER(?)"
            params.append(f"%{filter_name}%")
        
        if filter_year:
            query += " AND strftime('%Y', s.published_date) = ?"
            params.append(filter_year)
        
        # Add sorting
        if sort_by == 'title':
            query += " ORDER BY s.title ASC"
        elif sort_by == 'release_date':
            query += " ORDER BY s.published_date DESC, s.title ASC"
        else:  # default to author
            query += " ORDER BY s.author ASC, s.title ASC"
        
        books = execute_query(query, tuple(params))
        
        return jsonify({
            "success": True,
            "books": books if books else [],
            "count": len(books) if books else 0
        }), 200
    except Exception as e:
        LOGGER.error(f"Error getting filtered books: {e}")
        return jsonify({"error": str(e)}), 500


# Book Status Endpoints
@series_routes.route('/api/books/<int:book_id>/status', methods=['PUT'])
def update_book_status(book_id):
    """Update book status (star rating, reading progress, user description).
    
    Args:
        book_id (int): The book ID (series ID with is_book=1)
    
    Returns:
        Response: Success or error response
    """
    try:
        from backend.internals.db import execute_query
        
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        # Extract fields
        star_rating = data.get('star_rating', 0)
        reading_progress = data.get('reading_progress', 0)
        user_description = data.get('user_description', '')
        
        # Validate star rating (0-5)
        if not isinstance(star_rating, (int, float)) or star_rating < 0 or star_rating > 5:
            return jsonify({"error": "Star rating must be between 0 and 5"}), 400
        
        # Validate reading progress (0, 25, 50, 75, 100)
        valid_progress = [0, 25, 50, 75, 100]
        if reading_progress not in valid_progress:
            return jsonify({"error": f"Reading progress must be one of {valid_progress}"}), 400
        
        # Update the series record
        execute_query("""
            UPDATE series 
            SET star_rating = ?, reading_progress = ?, user_description = ?
            WHERE id = ?
        """, (star_rating, reading_progress, user_description, book_id), commit=True)
        
        LOGGER.info(f"Updated book status for book {book_id}: rating={star_rating}, progress={reading_progress}%")
        
        # Sync updated data to README file
        try:
            from backend.features.readme_sync import sync_series_to_readme
            sync_series_to_readme(book_id)
            LOGGER.info(f"Synced book status to README for book {book_id}")
        except Exception as e:
            LOGGER.warning(f"Failed to sync book status to README: {e}")
        
        return jsonify({
            "success": True,
            "message": "Book status updated successfully",
            "data": {
                "book_id": book_id,
                "star_rating": star_rating,
                "reading_progress": reading_progress,
                "user_description": user_description
            }
        }), 200
    
    except Exception as e:
        LOGGER.error(f"Error updating book status: {e}")
        import traceback
        LOGGER.error(traceback.format_exc())
        return jsonify({"error": f"Failed to update book status: {str(e)}"}), 500


@series_routes.route('/api/books/<int:book_id>/status', methods=['GET'])
def get_book_status(book_id):
    """Get book status (star rating, reading progress, user description).
    
    Args:
        book_id (int): The book ID (series ID with is_book=1)
    
    Returns:
        Response: Book status data or error response
    """
    try:
        from backend.internals.db import execute_query
        
        result = execute_query("""
            SELECT id, star_rating, reading_progress, user_description
            FROM series 
            WHERE id = ?
        """, (book_id,))
        
        if not result:
            return jsonify({"error": "Book not found"}), 404
        
        book = result[0]
        
        return jsonify({
            "success": True,
            "data": {
                "book_id": book['id'],
                "star_rating": book['star_rating'] or 0,
                "reading_progress": book['reading_progress'] or 0,
                "user_description": book['user_description'] or ''
            }
        }), 200
    
    except Exception as e:
        LOGGER.error(f"Error getting book status: {e}")
        import traceback
        LOGGER.error(traceback.format_exc())
        return jsonify({"error": f"Failed to get book status: {str(e)}"}), 500


# Book Recommendations Endpoints
@series_routes.route('/api/books/<int:book_id>/recommendations/category', methods=['GET'])
def get_category_recommendations(book_id):
    """Get book recommendations based on category/genre only.
    
    Args:
        book_id (int): The book ID (series ID)
    
    Returns:
        Response: List of recommended books in the same category
    """
    try:
        from backend.internals.db import execute_query
        
        # Get the current book's subjects (genres)
        book_result = execute_query("""
            SELECT id, title, subjects
            FROM series 
            WHERE id = ?
        """, (book_id,))
        
        if not book_result:
            return jsonify({"error": "Book not found"}), 404
        
        book = book_result[0]
        
        # If book has no subjects/genres, return empty recommendations
        if not book['subjects']:
            return jsonify({
                "success": True,
                "data": {
                    "book_id": book_id,
                    "recommendations": []
                }
            }), 200
        
        # Parse subjects/genres (stored as comma-separated string)
        subjects_str = book['subjects']
        if isinstance(subjects_str, str):
            genres = [g.strip() for g in subjects_str.split(',') if g.strip()]
        else:
            genres = []
        
        if not genres:
            return jsonify({
                "success": True,
                "data": {
                    "book_id": book_id,
                    "recommendations": []
                }
            }), 200
        
        # Build query to find books with matching subjects/genres
        # Exclude the current book
        recommendations = []
        
        for genre in genres:
            # Search for books with this subject/genre
            results = execute_query("""
                SELECT id, title, author, cover_url, subjects, star_rating
                FROM series 
                WHERE id != ? AND subjects LIKE ?
                LIMIT 10
            """, (book_id, f'%{genre}%'))
            
            if results:
                recommendations.extend(results)
        
        # Remove duplicates while preserving order
        seen_ids = set()
        unique_recommendations = []
        for rec in recommendations:
            if rec['id'] not in seen_ids:
                seen_ids.add(rec['id'])
                unique_recommendations.append(rec)
        
        # Limit to 10 recommendations
        unique_recommendations = unique_recommendations[:10]
        
        return jsonify({
            "success": True,
            "data": {
                "book_id": book_id,
                "recommendations": unique_recommendations,
                "count": len(unique_recommendations)
            }
        }), 200
    
    except Exception as e:
        LOGGER.error(f"Error getting category recommendations: {e}")
        import traceback
        LOGGER.error(traceback.format_exc())
        return jsonify({"error": f"Failed to get recommendations: {str(e)}"}), 500


@series_routes.route('/api/books/<int:book_id>/recommendations/ai', methods=['GET'])
def get_ai_recommendations(book_id):
    """Get AI-powered book recommendations based on book details.
    
    Uses AI to generate recommendations based on genres/subjects, star ratings, and user notes.
    Caches recommendations and regenerates only when book details change.
    Falls back to category-only recommendations if AI fails.
    
    Args:
        book_id (int): The book ID (series ID)
    
    Returns:
        Response: List of recommended books from metadata providers
    """
    try:
        # Get the current book's details
        book_result = execute_query("""
            SELECT id, title, author, subjects, star_rating, metadata_source, metadata_id, 
                   user_description, reading_progress, updated_at
            FROM series 
            WHERE id = ?
        """, (book_id,))
        
        if not book_result:
            return jsonify({"error": "Book not found"}), 404
        
        book = book_result[0]
        
        # Check if cached recommendations exist and are still valid
        cached_recs = _get_cached_recommendations(book_id, book)
        if cached_recs is not None:
            LOGGER.info(f"Using cached recommendations for book {book_id}")
            return jsonify({
                "success": True,
                "data": {
                    "book_id": book_id,
                    "recommendations": cached_recs['recommendations'],
                    "method": cached_recs['method'],
                    "count": len(cached_recs['recommendations']),
                    "cached": True
                }
            }), 200
        
        recommendations = []
        
        # Try AI-powered recommendations first
        try:
            ai_manager = get_ai_provider_manager()
            if ai_manager.get_all_providers():
                recommendations = _get_ai_book_recommendations(book, ai_manager)
        except Exception as e:
            LOGGER.warning(f"AI recommendations failed, falling back to category-only: {e}")
        
        # If AI recommendations failed or returned empty, fall back to category-only
        if not recommendations:
            LOGGER.info(f"Falling back to category-only recommendations for book {book_id}")
            # Use the existing category-only logic
            if not book['subjects']:
                return jsonify({
                    "success": True,
                    "data": {
                        "book_id": book_id,
                        "recommendations": [],
                        "method": "none"
                    }
                }), 200
            
            # Parse subjects/genres (stored as comma-separated string)
            subjects_str = book['subjects']
            if isinstance(subjects_str, str):
                genres = [g.strip() for g in subjects_str.split(',') if g.strip()]
            else:
                genres = []
            
            if genres:
                # Build query to find books with matching subjects/genres
                rec_list = []
                for genre in genres:
                    results = execute_query("""
                        SELECT id, title, author, cover_url, subjects, star_rating
                        FROM series 
                        WHERE id != ? AND subjects LIKE ?
                        LIMIT 10
                    """, (book_id, f'%{genre}%'))
                    
                    if results:
                        rec_list.extend(results)
                
                # Remove duplicates while preserving order
                seen_ids = set()
                unique_recommendations = []
                for rec in rec_list:
                    if rec['id'] not in seen_ids:
                        seen_ids.add(rec['id'])
                        unique_recommendations.append(rec)
                
                recommendations = unique_recommendations[:10]
                method = "category"
            else:
                method = "none"
        else:
            method = "ai"
        
        # Cache the recommendations
        _cache_recommendations(book_id, recommendations, method, book)
        
        return jsonify({
            "success": True,
            "data": {
                "book_id": book_id,
                "recommendations": recommendations,
                "method": method,
                "count": len(recommendations),
                "cached": False
            }
        }), 200
    
    except Exception as e:
        LOGGER.error(f"Error getting AI recommendations: {e}")
        import traceback
        LOGGER.error(traceback.format_exc())
        return jsonify({"error": f"Failed to get recommendations: {str(e)}"}), 500


def _get_ai_book_recommendations(book, ai_manager):
    """Generate book recommendations using AI.
    
    Args:
        book: Book data dictionary
        ai_manager: AI provider manager instance
    
    Returns:
        List of recommended book dictionaries
    """
    try:
        # Build AI prompt
        title = book.get('title', 'Unknown')
        author = book.get('author', 'Unknown')
        subjects = book.get('subjects', '')
        star_rating = book.get('star_rating', 0)
        user_notes = book.get('user_description', '')
        reading_progress = book.get('reading_progress', 0)
        
        # Parse subjects
        genres_list = []
        if subjects and isinstance(subjects, str):
            genres_list = [g.strip() for g in subjects.split(',') if g.strip()]
        
        genres_str = ', '.join(genres_list) if genres_list else 'Fiction'
        
        # Build prompt with all available information
        prompt = f"""Based on the following book details, recommend 5-8 similar books.
        
Book Title: {title}
Author: {author}
Genres/Subjects: {genres_str}
User Rating: {star_rating}/5
Reading Progress: {reading_progress}%"""
        
        if user_notes:
            prompt += f"\nUser Notes: {user_notes}"
        
        prompt += """

Please provide recommendations in this exact format:
Book Title | Author Name

Only provide the title and author, one per line. No additional text."""
        
        # Get AI response
        provider = ai_manager.get_all_providers()[0] if ai_manager.get_all_providers() else None
        if not provider:
            LOGGER.warning("No AI providers available")
            return []
        
        # Call AI provider using the proper client API
        response_text = ""
        try:
            if provider.name == "Groq" and hasattr(provider, 'client'):
                # Groq uses client.chat.completions.create()
                response = provider.client.chat.completions.create(
                    model=provider.model,
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a book recommendation expert. Provide book recommendations based on the given details."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    temperature=0.7,
                    max_tokens=1000,
                    timeout=30
                )
                response_text = response.choices[0].message.content
            elif provider.name == "Gemini" and hasattr(provider, 'client'):
                # Gemini uses client.generate_content()
                response = provider.client.generate_content(prompt)
                response_text = response.text
            elif provider.name == "DeepSeek" and hasattr(provider, 'client'):
                # DeepSeek uses client.chat.completions.create()
                response = provider.client.chat.completions.create(
                    model=provider.model,
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a book recommendation expert. Provide book recommendations based on the given details."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    temperature=0.7,
                    max_tokens=1000,
                    timeout=30
                )
                response_text = response.choices[0].message.content
            elif provider.name == "Ollama" and hasattr(provider, 'client'):
                # Ollama uses client.generate()
                response = provider.client.generate(model=provider.model, prompt=prompt)
                response_text = response.get('response', '')
            else:
                LOGGER.warning(f"AI provider {provider.name} is not supported for recommendations")
                return []
        except Exception as e:
            LOGGER.error(f"Error calling AI provider {provider.name}: {e}")
            return []
        
        if not response_text:
            LOGGER.warning("AI provider returned empty response")
            return []
        
        # Parse AI response to extract book titles and authors
        recommendations = []
        lines = response_text.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            if not line or '|' not in line:
                continue
            
            parts = [p.strip() for p in line.split('|')]
            if len(parts) >= 2:
                rec_title = parts[0]
                rec_author = parts[1]
                
                # Search for the book in metadata providers
                book_data = _search_and_fetch_book(rec_title, rec_author, book.get('metadata_source'))
                if book_data:
                    recommendations.append(book_data)
        
        LOGGER.info(f"AI generated {len(recommendations)} recommendations")
        return recommendations[:10]  # Limit to 10
    
    except Exception as e:
        LOGGER.error(f"Error in AI recommendation generation: {e}")
        import traceback
        LOGGER.error(traceback.format_exc())
        return []


def _search_and_fetch_book(title, author, preferred_provider=None):
    """Search for a book using metadata providers.
    
    Args:
        title: Book title
        author: Book author
        preferred_provider: Preferred metadata provider (e.g., 'GoogleBooks')
    
    Returns:
        Book data dictionary or None
    """
    try:
        search_query = f"{title} {author}"
        
        # Try preferred provider first if specified
        if preferred_provider:
            try:
                results = search_manga(search_query, provider=preferred_provider, search_type='title')
                if results and 'results' in results and preferred_provider in results['results']:
                    provider_results = results['results'][preferred_provider]
                    if provider_results and isinstance(provider_results, list) and len(provider_results) > 0:
                        book_data = provider_results[0]
                        return _format_book_data(book_data, preferred_provider)
            except Exception as e:
                LOGGER.debug(f"Failed to search preferred provider {preferred_provider}: {e}")
        
        # Fall back to searching all providers
        results = search_manga(search_query, search_type='title')
        if results and 'results' in results:
            for provider_name, provider_results in results['results'].items():
                if provider_results and isinstance(provider_results, list) and len(provider_results) > 0:
                    book_data = provider_results[0]
                    return _format_book_data(book_data, provider_name)
        
        return None
    
    except Exception as e:
        LOGGER.debug(f"Error searching for book '{title}' by '{author}': {e}")
        return None


def _format_book_data(book_data, provider_name):
    """Format book data from metadata provider into recommendation format.
    
    Args:
        book_data: Raw book data from metadata provider
        provider_name: Name of the provider
    
    Returns:
        Formatted book dictionary
    """
    try:
        # Handle different provider response formats
        if isinstance(book_data, dict):
            # Extract author from various formats
            author = book_data.get('author')
            if not author and isinstance(book_data.get('authors'), list) and len(book_data.get('authors', [])) > 0:
                author = book_data.get('authors')[0]
            
            formatted = {
                'id': book_data.get('id') or book_data.get('metadata_id'),
                'title': book_data.get('title') or book_data.get('name'),
                'author': author,
                'cover_url': book_data.get('cover_url') or book_data.get('image_url') or book_data.get('cover'),
                'subjects': book_data.get('subjects') or book_data.get('genres') or '',
                'star_rating': book_data.get('rating') or book_data.get('average_rating') or 0,
                'metadata_source': provider_name,
                'metadata_id': book_data.get('id') or book_data.get('metadata_id'),
                'publisher': book_data.get('publisher'),
                'published_date': book_data.get('published_date') or book_data.get('publication_date') or book_data.get('publish_date'),
                'isbn': book_data.get('isbn') or book_data.get('isbn13') or book_data.get('isbn10'),
                'description': book_data.get('description') or book_data.get('summary')
            }
            
            LOGGER.debug(f"Formatted book data from {provider_name}: {formatted}")
            return formatted
        return None
    except Exception as e:
        LOGGER.debug(f"Error formatting book data: {e}")
        return None


def _get_cached_recommendations(book_id, book):
    """Get cached recommendations if they're still valid.
    
    Recommendations are valid if book details haven't changed.
    
    Args:
        book_id: The book ID
        book: Current book data
    
    Returns:
        Cached recommendations dict or None if invalid/missing
    """
    try:
        # Create a hash of book details to detect changes
        book_hash = _hash_book_details(book)
        
        # Check if cached recommendations exist
        cache_result = execute_query("""
            SELECT recommendations, method, book_hash
            FROM recommendation_cache
            WHERE book_id = ?
        """, (book_id,))
        
        if cache_result:
            cached = cache_result[0]
            # If book details haven't changed, return cached recommendations
            if cached['book_hash'] == book_hash:
                import json
                return {
                    'recommendations': json.loads(cached['recommendations']),
                    'method': cached['method']
                }
        
        return None
    except Exception as e:
        LOGGER.debug(f"Error getting cached recommendations: {e}")
        return None


def _cache_recommendations(book_id, recommendations, method, book):
    """Cache recommendations for a book.
    
    Args:
        book_id: The book ID
        recommendations: List of recommendation dicts
        method: Recommendation method (ai, category, none)
        book: Current book data
    """
    try:
        import json
        from datetime import datetime
        
        book_hash = _hash_book_details(book)
        recs_json = json.dumps(recommendations)
        
        # Create table if it doesn't exist
        execute_query("""
            CREATE TABLE IF NOT EXISTS recommendation_cache (
                book_id INTEGER PRIMARY KEY,
                recommendations TEXT NOT NULL,
                method TEXT NOT NULL,
                book_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """, commit=True)
        
        # Check if cache entry exists
        existing = execute_query("""
            SELECT book_id FROM recommendation_cache WHERE book_id = ?
        """, (book_id,))
        
        if existing:
            # Update existing cache
            execute_query("""
                UPDATE recommendation_cache
                SET recommendations = ?, method = ?, book_hash = ?, updated_at = CURRENT_TIMESTAMP
                WHERE book_id = ?
            """, (recs_json, method, book_hash, book_id), commit=True)
        else:
            # Insert new cache entry
            execute_query("""
                INSERT INTO recommendation_cache (book_id, recommendations, method, book_hash)
                VALUES (?, ?, ?, ?)
            """, (book_id, recs_json, method, book_hash), commit=True)
        
        LOGGER.debug(f"Cached recommendations for book {book_id}")
    except Exception as e:
        LOGGER.debug(f"Error caching recommendations: {e}")


def _hash_book_details(book):
    """Create a hash of book details to detect changes.
    
    Args:
        book: Book data dictionary
    
    Returns:
        Hash string
    """
    import hashlib
    
    # Include fields that affect recommendations
    details = f"{book.get('subjects', '')}{book.get('star_rating', 0)}{book.get('user_description', '')}{book.get('reading_progress', 0)}"
    return hashlib.md5(details.encode()).hexdigest()
