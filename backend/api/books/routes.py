#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
API endpoints for books management and recommendations.
"""

from flask import jsonify, request
from backend.base.logging import LOGGER
from backend.internals.db import execute_query
from functools import wraps
from backend.features.ai_recommendations import get_popular_books_this_week, get_ai_book_recommendations

# Create blueprint
books_routes = None

def get_books_routes():
    """Get or create the books routes blueprint."""
    global books_routes
    if books_routes is None:
        from flask import Blueprint
        books_routes = Blueprint('books', __name__)
    return books_routes


def handle_errors(f):
    """Decorator for consistent error handling."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            LOGGER.error(f"Error in {f.__name__}: {e}")
            return jsonify({"error": str(e)}), 500
    return decorated_function


@get_books_routes().route('/api/books/popular-this-week', methods=['GET'])
@handle_errors
def get_popular_books_this_week_api():
    """
    Get popular books for this week using AI recommendations.
    
    Returns:
        JSON response with popular books data.
    """
    try:
        LOGGER.info("Fetching popular books for this week")
        
        # Get popular books using AI recommendations
        popular_books = get_popular_books_this_week()
        
        return jsonify({
            'success': True,
            'data': popular_books,
            'count': len(popular_books)
        })
        
    except Exception as e:
        LOGGER.error(f"Error getting popular books: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@get_books_routes().route('/api/books/manga/trending-this-week', methods=['GET'])
@handle_errors
def get_trending_manga_this_week_api():
    """Get trending manga for this week."""
    try:
        from backend.features.ai_recommendations import get_popular_manga_this_week
        
        trending_manga = get_popular_manga_this_week()
        
        return jsonify({
            'success': True,
            'data': trending_manga,
            'count': len(trending_manga)
        })
        
    except Exception as e:
        LOGGER.error(f"Error getting trending manga: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@get_books_routes().route('/api/books/<int:book_id>/recommendations/ai', methods=['GET'])
@handle_errors
def get_ai_recommendations(book_id):
    """
    Get AI-powered book recommendations based on book details.
    
    Migrated from the old frontend's recommendation system with existing AI prompts.
    
    Args:
        book_id (int): The book ID (series ID)
        
    Returns:
        JSON response with AI recommendations.
    """
    try:
        LOGGER.info(f"Getting AI recommendations for book {book_id}")
        
        # Get AI recommendations using the migrated system
        recommendations = get_ai_book_recommendations(book_id)
        
        # Convert to expected format
        formatted_recommendations = []
        for rec in recommendations:
            formatted_rec = {
                'id': rec.get('id', 0),
                'name': rec.get('title', 'Unknown Title'),
                'author': rec.get('author', 'Unknown Author'),
                'cover_url': rec.get('cover_url', '/static/img/no-cover.png'),
                'star_rating': rec.get('star_rating', 0),
                'subjects': rec.get('subjects', ''),
                'description': rec.get('description', ''),
                'metadata_source': rec.get('metadata_source', 'AI Generated'),
                'content_type': 'BOOK'
            }
            formatted_recommendations.append(formatted_rec)
        
        LOGGER.info(f"Generated {len(formatted_recommendations)} AI recommendations for book {book_id}")
        
        return jsonify({
            "success": True,
            "data": {
                "book_id": book_id,
                "recommendations": formatted_recommendations,
                "method": "ai" if formatted_recommendations else "none",
                "count": len(formatted_recommendations),
                "cached": False  # TODO: Implement cache detection
            }
        }), 200
        
    except Exception as e:
        LOGGER.error(f"Error getting AI recommendations: {e}")
        return jsonify({
            "success": False,
            "error": f"Failed to get recommendations: {str(e)}"
        }), 500


@get_books_routes().route('/api/books/<int:book_id>/recommendations/category', methods=['GET'])
@handle_errors
def get_category_recommendations(book_id):
    """
    Get book recommendations based on category/genre only.
    
    This will be migrated from the old frontend's recommendation system.
    
    Args:
        book_id (int): The book ID (series ID)
        
    Returns:
        JSON response with category-based recommendations.
    """
    try:
        LOGGER.info(f"Getting category recommendations for book {book_id}")
        
        # Get book details for category analysis
        book_result = execute_query("""
            SELECT id, name as title, author, subjects, star_rating, 
                   user_description, reading_progress, metadata_source
            FROM series 
            WHERE id = ? AND content_type = 'BOOK'
        """, (book_id,))
        
        if not book_result:
            return jsonify({
                "success": False,
                "error": "Book not found"
            }), 404
        
        book = book_result[0]
        
        # Use the category recommendation logic from AI recommendations module
        from backend.features.ai_recommendations import _get_category_recommendations
        recommendations = _get_category_recommendations(book)
        
        # Convert to expected format
        formatted_recommendations = []
        for rec in recommendations:
            formatted_rec = {
                'id': rec.get('id', 0),
                'name': rec.get('title', 'Unknown Title'),
                'author': rec.get('author', 'Unknown Author'),
                'cover_url': rec.get('cover_url', '/static/img/no-cover.png'),
                'star_rating': rec.get('star_rating', 0),
                'subjects': rec.get('subjects', ''),
                'description': rec.get('description', ''),
                'metadata_source': rec.get('metadata_source', 'Database'),
                'content_type': 'BOOK'
            }
            formatted_recommendations.append(formatted_rec)
        
        LOGGER.info(f"Generated {len(formatted_recommendations)} category recommendations for book {book_id}")
        
        return jsonify({
            "success": True,
            "data": {
                "book_id": book_id,
                "recommendations": formatted_recommendations,
                "count": len(formatted_recommendations)
            }
        }), 200
        
    except Exception as e:
        LOGGER.error(f"Error getting category recommendations: {e}")
        return jsonify({
            "success": False,
            "error": f"Failed to get recommendations: {str(e)}"
        }), 500
