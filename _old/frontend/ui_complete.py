#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Complete UI routes for Readloom.
Includes all routes from the original UI blueprint and the content-specific routes.
"""

from flask import Blueprint, render_template, redirect, url_for, request, abort, jsonify

from backend.base.logging import LOGGER
from backend.features.content_service_factory import ContentType, get_content_service
from backend.internals.db import execute_query
from frontend.middleware import setup_required, collections_required


# Create Blueprint for UI routes
ui_bp = Blueprint('ui', __name__)


# Helper functions
def get_user_preference():
    """Get the user's content type preference."""
    # This could be stored in a cookie or user settings
    # For now, default to books
    return request.cookies.get('content_preference', 'book')


def get_book_collections():
    """Get book collections."""
    try:
        collections = execute_query("""
            SELECT c.*, COUNT(sc.series_id) as book_count
            FROM collections c
            LEFT JOIN series_collections sc ON c.id = sc.collection_id
            LEFT JOIN series s ON sc.series_id = s.id AND UPPER(s.content_type) IN ('BOOK', 'NOVEL')
            WHERE UPPER(c.content_type) IN ('BOOK', 'NOVEL')
            GROUP BY c.id
            ORDER BY c.name
        """)
        return collections
    except Exception as e:
        LOGGER.error(f"Error getting book collections: {e}")
        return []


def get_manga_collections():
    """Get manga collections."""
    try:
        collections = execute_query("""
            SELECT c.*, COUNT(sc.series_id) as manga_count
            FROM collections c
            LEFT JOIN series_collections sc ON c.id = sc.collection_id
            LEFT JOIN series s ON sc.series_id = s.id AND UPPER(s.content_type) IN ('MANGA', 'MANHWA', 'MANHUA', 'COMIC')
            WHERE UPPER(c.content_type) IN ('MANGA', 'MANHWA', 'MANHUA', 'COMIC')
            GROUP BY c.id
            ORDER BY c.name
        """)
        return collections
    except Exception as e:
        LOGGER.error(f"Error getting manga collections: {e}")
        return []


def get_popular_authors(limit=10):
    """Get popular authors."""
    try:
        authors = execute_query("""
            SELECT a.*, COUNT(ab.series_id) as book_count
            FROM authors a
            LEFT JOIN author_books ab ON a.id = ab.author_id
            GROUP BY a.id
            ORDER BY book_count DESC, a.name
            LIMIT ?
        """, (limit,))
        return authors
    except Exception as e:
        LOGGER.error(f"Error getting popular authors: {e}")
        return []


def get_recent_books(limit=None):
    """Get recent books. If limit is None, returns all books."""
    try:
        # Use content_type to filter books
        if limit:
            books = execute_query("""
                SELECT s.*
                FROM series s
                WHERE UPPER(s.content_type) IN ('BOOK', 'NOVEL')
                ORDER BY s.created_at DESC
                LIMIT ?
            """, (limit,))
        else:
            books = execute_query("""
                SELECT s.*
                FROM series s
                WHERE UPPER(s.content_type) IN ('BOOK', 'NOVEL')
                ORDER BY s.created_at DESC
            """)
        return books
    except Exception as e:
        LOGGER.error(f"Error getting recent books: {e}")
        return []


def get_recent_series(limit=None):
    """Get recent manga series. If limit is None, returns all manga."""
    try:
        # Use content_type to filter manga
        if limit:
            series = execute_query("""
                SELECT s.*
                FROM series s
                WHERE UPPER(s.content_type) IN ('MANGA', 'MANHWA', 'MANHUA', 'COMIC')
                ORDER BY s.created_at DESC
                LIMIT ?
            """, (limit,))
        else:
            series = execute_query("""
                SELECT s.*
                FROM series s
                WHERE UPPER(s.content_type) IN ('MANGA', 'MANHWA', 'MANHUA', 'COMIC')
                ORDER BY s.created_at DESC
            """)
        return series
    except Exception as e:
        LOGGER.error(f"Error getting recent series: {e}")
        return []


# Setup wizard route
@ui_bp.route('/setup')
@ui_bp.route('/setup-wizard')
def setup_wizard():
    """Setup wizard page."""
    # Check if setup is already complete
    from backend.features.setup_check import is_setup_complete
    if is_setup_complete():
        return redirect(url_for('ui.home'))
    
    # Get root folders for the setup wizard
    from backend.internals.settings import Settings
    settings = Settings().get_settings()
    root_folders = settings.root_folders
    
    return render_template('setup_wizard.html', root_folders=root_folders)


# Settings route
@ui_bp.route('/settings')
def settings():
    """Settings page."""
    return render_template('settings.html')


# Root folders route
@ui_bp.route('/root-folders')
@setup_required
def root_folders():
    """Root folders page."""
    return render_template('root_folders.html')


# Collections route
@ui_bp.route('/collections')
@setup_required
def collections_manager():
    """Collections management page."""
    return render_template('collections_manager.html')


# Collection route
@ui_bp.route('/collection')
@setup_required
def collection():
    """Collection page."""
    return render_template('collection.html')


# Collection view route
@ui_bp.route('/collection/<int:collection_id>')
@setup_required
def collection_view(collection_id):
    """Collection detail page."""
    return render_template('collection_view.html', collection_id=collection_id)


# About route
@ui_bp.route('/about')
def about():
    """About page."""
    return render_template('about.html')


# Calendar route
@ui_bp.route('/calendar')
@setup_required
def calendar():
    """Calendar page."""
    return render_template('calendar.html')


# Series list route
@ui_bp.route('/series')
@setup_required
def series_list():
    """Series list page."""
    # Get root folders from settings
    from backend.internals.settings import Settings
    settings = Settings().get_settings()
    root_folders = settings.root_folders
    
    return render_template('series_list.html', root_folders=root_folders)


# Series detail route (for backward compatibility)
# NOTE: This route is now handled by ui/manga.py and ui/books.py
# Keeping this commented out to avoid route conflicts
# @ui_bp.route('/series/<int:series_id>')
# @setup_required
# def series_detail(series_id: int):
#     """Series detail page.
#     
#     This route is for backward compatibility. It will redirect to the appropriate
#     book or manga detail page based on the series type.
#     """
#     # Check if the series is a book or manga
#     from backend.internals.db import execute_query
#     series = execute_query("SELECT content_type FROM series WHERE id = ?", (series_id,))
#     
#     if not series:
#         abort(404)
#     
#     content_type = series[0]['content_type']
#     
#     if content_type == 'BOOK':
#         return redirect(url_for('ui.book_view', book_id=series_id))
#     else:
#         return redirect(url_for('ui.series_view', series_id=series_id))


# Search route (for backward compatibility)
@ui_bp.route('/search')
@setup_required
def search():
    """Search page.
    
    This route is for backward compatibility. It will redirect to the books search page.
    """
    return redirect(url_for('ui.books_search'))


# Notifications route
@ui_bp.route('/notifications')
@setup_required
def notifications():
    """Notifications page."""
    return render_template('notifications.html')


# Integrations routes
@ui_bp.route('/integrations')
def integrations():
    """Integrations page."""
    return render_template('integrations.html')


@ui_bp.route('/integrations/home-assistant')
def home_assistant():
    """Home Assistant integration page."""
    return render_template('home_assistant.html')


@ui_bp.route('/integrations/homarr')
def homarr():
    """Homarr integration page."""
    return render_template('homarr.html')


@ui_bp.route('/integrations/providers')
def provider_config():
    """Provider configuration page."""
    return render_template('provider_config.html')


@ui_bp.route('/integrations/ai-providers')
def ai_providers_config():
    """AI providers configuration page."""
    return render_template('ai_providers_config.html')


# Favicon route
@ui_bp.route('/favicon.ico')
def favicon():
    """Serve the favicon."""
    from flask import send_from_directory
    return send_from_directory('static/img', 'favicon.ico')


# Authors routes
@ui_bp.route('/authors')
@setup_required
def authors_home():
    """Authors home page."""
    return render_template('authors/authors.html')


@ui_bp.route('/authors/<int:author_id>')
@setup_required
def author_detail(author_id):
    """Author detail page."""
    # Get author details
    author = execute_query("SELECT * FROM authors WHERE id = ?", (author_id,))
    
    if not author:
        abort(404)
    
    # Get author's books
    books = execute_query("""
        SELECT s.id, s.title, s.content_type, 
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
    
    return render_template(
        'authors/author_detail.html',
        author=author[0],
        books=books
    )


@ui_bp.route('/authors/<int:author_id>/books')
def author_books(author_id):
    """Author's books page."""
    # Get author details
    author = execute_query("SELECT * FROM authors WHERE id = ?", (author_id,))
    
    if not author:
        abort(404)
    
    # Get author's books
    books = execute_query("""
        SELECT s.* 
        FROM series s
        JOIN author_books ab ON s.id = ab.series_id
        WHERE ab.author_id = ?
        ORDER BY s.title ASC
    """, (author_id,))
    
    return render_template(
        'authors/author_books.html',
        author=author[0],
        books=books
    )


# Books routes
@ui_bp.route('/books')
@setup_required
def books_home():
    """Books home page."""
    # Get book collections
    book_collections = get_book_collections()
    
    # Get popular authors
    popular_authors = get_popular_authors(5)
    
    # Get recent books
    recent_books = get_recent_books()
    
    return render_template(
        'books/home.html',
        book_collections=book_collections,
        popular_authors=popular_authors,
        recent_books=recent_books
    )


@ui_bp.route('/books/search')
@setup_required
def books_search():
    """Book search page."""
    return render_template('books/search.html')


@ui_bp.route('/books/authors')
def authors_view():
    """Authors list page."""
    # Get all authors
    authors = execute_query("""
        SELECT a.*, COUNT(ba.book_id) as book_count
        FROM authors a
        LEFT JOIN book_authors ba ON a.id = ba.author_id
        GROUP BY a.id
        ORDER BY a.name
    """)
    
    return render_template('books/authors.html', authors=authors)


@ui_bp.route('/books/authors/<int:author_id>')
def author_view(author_id):
    """Author detail page."""
    # Get author details
    book_service = get_content_service(ContentType.BOOK)
    author = book_service.get_author_details(author_id)
    
    if "error" in author:
        abort(404)
    
    # Get books by author
    books = book_service.get_books_by_author(author_id)
    
    return render_template('books/author.html', author=author, books=books)


@ui_bp.route('/books/<int:book_id>')
@setup_required
def book_view(book_id):
    """Book detail page."""
    # Get book details
    book = execute_query("SELECT * FROM series WHERE id = ? AND content_type = 'BOOK'", (book_id,))
    
    if not book:
        abort(404)
    
    book = book[0]
    
    # Get author
    author = execute_query("""
        SELECT a.* FROM authors a
        JOIN author_books ab ON a.id = ab.author_id
        WHERE ab.series_id = ?
    """, (book_id,))
    
    author = author[0] if author else None
    
    # Get collection
    collection = execute_query("""
        SELECT c.* FROM collections c
        JOIN series_collections sc ON c.id = sc.collection_id
        WHERE sc.series_id = ?
    """, (book_id,))
    
    collection = collection[0] if collection else None
    
    # Get e-book files
    from backend.features.ebook_files import get_ebook_files_for_series
    ebook_files = get_ebook_files_for_series(book_id)
    
    # Get all book collections for the edit form
    book_collections = get_book_collections()
    
    return render_template(
        'books/book.html',
        book=book,
        author=author,
        collection=collection,
        ebook_files=ebook_files,
        book_collections=book_collections
    )


# Manga routes
@ui_bp.route('/manga')
@setup_required
def manga_home():
    """Manga home page."""
    # Get manga collections
    manga_collections = get_manga_collections()
    
    # Get recent series (all manga, no limit)
    recent_series = get_recent_series()
    
    return render_template(
        'manga/home.html',
        manga_collections=manga_collections,
        recent_series=recent_series
    )


@ui_bp.route('/manga/search')
@setup_required
def manga_search():
    """Manga search page."""
    return render_template('manga/search.html')


@ui_bp.route('/manga/series/<int:series_id>')
@setup_required
def series_view(series_id):
    """Series detail page."""
    # Get series details
    series = execute_query("SELECT * FROM series WHERE id = ? AND content_type IN ('MANGA', 'MANHWA', 'MANHUA', 'COMIC')", (series_id,))
    
    if not series:
        abort(404)
    
    series = series[0]
    
    # Get volumes
    volumes = execute_query("""
        SELECT v.*, COUNT(c.id) as chapter_count
        FROM volumes v
        LEFT JOIN chapters c ON v.id = c.volume_id
        WHERE v.series_id = ?
        GROUP BY v.id
        ORDER BY CAST(v.volume_number AS INTEGER)
    """, (series_id,))
    
    # Get collection
    collection = execute_query("""
        SELECT c.* FROM collections c
        JOIN series_collections sc ON c.id = sc.collection_id
        WHERE sc.series_id = ?
    """, (series_id,))
    
    collection = collection[0] if collection else None
    
    # Get e-book files
    from backend.features.ebook_files import get_ebook_files_for_series
    ebook_files = get_ebook_files_for_series(series_id)
    
    return render_template(
        'manga/series.html',
        series=series,
        volumes=volumes,
        collection=collection,
        ebook_files=ebook_files
    )


# Home route - renders the dashboard
@ui_bp.route('/')
@setup_required
def home():
    """Dashboard page."""
    # Get root folders from settings
    from backend.internals.settings import Settings
    settings = Settings().get_settings()
    root_folders = settings.root_folders
    
    # Get book collections
    book_collections = get_book_collections()
    
    # Get manga collections
    manga_collections = get_manga_collections()
    
    # Get popular authors
    popular_authors = get_popular_authors(5)
    
    # Get recent books
    recent_books = get_recent_books()
    
    # Get recent manga series
    recent_series = get_recent_series(6)
    
    return render_template(
        'dashboard.html',
        root_folders=root_folders,
        book_collections=book_collections,
        manga_collections=manga_collections,
        popular_authors=popular_authors,
        recent_books=recent_books,
        recent_series=recent_series,
        title="Dashboard"
    )


# Legacy index route for backward compatibility
@ui_bp.route('/index')
@setup_required
def index():
    """Dashboard page (legacy)."""
    return redirect(url_for('ui.home'))


# Library routes
@ui_bp.route('/library')
@setup_required
def library_home():
    """Library home page."""
    try:
        from frontend.ui.library import get_library_items, get_library_stats
        
        # Get all library items
        library_items = get_library_items()
        
        # Get statistics
        stats = get_library_stats()
        
        return render_template(
            'library/home.html',
            library_items=library_items,
            stats=stats
        )
    except Exception as e:
        LOGGER.error(f"Error loading library: {e}")
        return render_template('library/home.html', library_items=[], stats={})


@ui_bp.route('/library/api/items')
@setup_required
def api_library_items():
    """API endpoint to get library items with filters."""
    try:
        from frontend.ui.library import get_library_items
        from flask import jsonify
        
        content_type = request.args.get('content_type')
        ownership_status = request.args.get('ownership_status')
        format_type = request.args.get('format')
        
        items = get_library_items(
            content_type=content_type,
            ownership_status=ownership_status,
            format_type=format_type
        )
        
        return jsonify({
            'success': True,
            'items': items,
            'count': len(items)
        }), 200
    
    except Exception as e:
        LOGGER.error(f"Error fetching library items: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@ui_bp.route('/library/api/stats')
@setup_required
def api_library_stats():
    """API endpoint to get library statistics."""
    try:
        from frontend.ui.library import get_library_stats
        from flask import jsonify
        
        stats = get_library_stats()
        return jsonify({
            'success': True,
            'stats': stats
        }), 200
    
    except Exception as e:
        LOGGER.error(f"Error fetching library stats: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@ui_bp.route('/api/collection/want-to-read', methods=['GET'])
@setup_required
def get_want_to_read_api():
    """Get all want-to-read entries (series with want_to_read=1).
    
    Returns:
        Response: The want-to-read entries.
    """
    try:
        from flask import jsonify
        
        # Query want-to-read cache entries
        items = execute_query("""
            SELECT
                wtc.id,
                wtc.series_id,
                wtc.title,
                wtc.author,
                wtc.cover_url,
                COALESCE(wtc.content_type, 'MANGA') as content_type,
                wtc.metadata_source,
                wtc.metadata_id,
                CASE WHEN s.id IS NOT NULL THEN 1 ELSE 0 END as in_library,
                1 as want_to_read
            FROM want_to_read_cache wtc
            LEFT JOIN series s ON wtc.metadata_source = s.metadata_source AND wtc.metadata_id = s.metadata_id
            ORDER BY wtc.title ASC
        """)
        
        return jsonify({
            "success": True,
            "items": items if items else [],
            "count": len(items) if items else 0
        })
    
    except Exception as e:
        LOGGER.error(f"Error getting want-to-read entries: {e}")
        return jsonify({"error": str(e)}), 500


@ui_bp.route('/api/want-to-read/<int:cache_id>/details', methods=['GET'])
@setup_required
def get_want_to_read_details(cache_id: int):
    """Get details for a want-to-read cache item including metadata from provider.
    
    Args:
        cache_id: The want-to-read cache ID
        
    Returns:
        Response: Item details with metadata
    """
    try:
        # Get item from want-to-read cache
        cache_item = execute_query(
            "SELECT * FROM want_to_read_cache WHERE id = ?",
            (cache_id,)
        )
        
        if not cache_item:
            return jsonify({"error": "Item not found"}), 404
        
        item_data = cache_item[0]
        
        # Check if item already exists in series table
        existing_series = execute_query(
            "SELECT id, content_type FROM series WHERE metadata_source = ? AND metadata_id = ?",
            (item_data['metadata_source'], item_data['metadata_id'])
        )
        
        in_library = False
        series_id = None
        if existing_series:
            in_library = True
            series_id = existing_series[0]['id']
        
        # Try to fetch fresh metadata from provider
        try:
            from backend.features.metadata_service import get_manga_details
            metadata = get_manga_details(item_data['metadata_id'], item_data['metadata_source'])
            
            # Merge with cache data
            if metadata and "error" not in metadata:
                item_data.update(metadata)
        except Exception as e:
            LOGGER.warning(f"Could not fetch fresh metadata: {e}")
        
        return jsonify({
            "success": True,
            "item": item_data,
            "in_library": in_library,
            "series_id": series_id
        })
    
    except Exception as e:
        LOGGER.error(f"Error getting want-to-read details: {e}")
        return jsonify({"error": str(e)}), 500


@ui_bp.route('/api/want-to-read/<int:cache_id>', methods=['DELETE'])
@setup_required
def remove_from_want_to_read(cache_id: int):
    """Remove an item from want-to-read cache.
    
    Args:
        cache_id: The want-to-read cache ID
        
    Returns:
        Response: Success or error message
    """
    try:
        from backend.features.want_to_read_cache import remove_from_cache
        
        result = remove_from_cache(cache_id)
        
        if result:
            return jsonify({
                "success": True,
                "message": "Removed from Want to Read"
            })
        else:
            return jsonify({
                "success": False,
                "message": "Failed to remove from Want to Read"
            }), 400
    except Exception as e:
        LOGGER.error(f"Error removing from want to read: {e}")
        return jsonify({"error": str(e)}), 500


@ui_bp.route('/want-to-read')
@setup_required
def want_to_read():
    """Want to read collection page."""
    return render_template('want_to_read.html')


# Series detail route (backward compatibility)
@ui_bp.route('/series/<int:series_id>')
@setup_required
def series_detail(series_id: int):
    """Series detail page (backward compatibility).
    
    Redirects to the appropriate book or manga detail page based on the series type.
    """
    series = execute_query("SELECT content_type FROM series WHERE id = ?", (series_id,))
    
    if not series:
        abort(404)
    
    content_type = series[0]['content_type']
    
    if content_type == 'BOOK':
        return redirect(url_for('ui.book_view', book_id=series_id))
    else:
        return redirect(url_for('ui.manga_series_view', series_id=series_id))


# Manga series view route
@ui_bp.route('/manga/series/<int:series_id>')
@setup_required
def manga_series_view(series_id):
    """Series detail page."""
    series = execute_query(
        "SELECT * FROM series WHERE id = ? AND content_type IN ('MANGA', 'MANHWA', 'MANHUA', 'COMIC')",
        (series_id,)
    )
    
    if not series:
        abort(404)
    
    series = series[0]
    
    # Get volumes
    volumes = execute_query("""
        SELECT v.*, COUNT(c.id) as chapter_count
        FROM volumes v
        LEFT JOIN chapters c ON v.id = c.volume_id
        WHERE v.series_id = ?
        GROUP BY v.id
        ORDER BY CAST(v.volume_number AS INTEGER)
    """, (series_id,))
    
    # Get collection
    collection = execute_query("""
        SELECT c.* FROM collections c
        JOIN series_collections sc ON c.id = sc.collection_id
        WHERE sc.series_id = ?
    """, (series_id,))
    
    collection = collection[0] if collection else None
    
    # Get e-book files
    from backend.features.ebook_files import get_ebook_files_for_series
    ebook_files = get_ebook_files_for_series(series_id)
    
    return render_template(
        'manga/series.html',
        series=series,
        volumes=volumes,
        collection=collection,
        ebook_files=ebook_files
    )
