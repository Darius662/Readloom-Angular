#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Books UI routes.
Handles book-related pages and views.
"""

from flask import Blueprint, render_template, abort
from backend.base.logging import LOGGER
from backend.internals.db import execute_query
from backend.features.content_service_factory import ContentType, get_content_service
from frontend.middleware import setup_required

# Create routes blueprint
books_routes = Blueprint('books_routes', __name__)


def get_book_collections():
    """Get book collections (excluding default collections)."""
    try:
        collections = execute_query("""
            SELECT c.*, COUNT(sc.series_id) as book_count
            FROM collections c
            LEFT JOIN series_collections sc ON c.id = sc.collection_id
            LEFT JOIN series s ON sc.series_id = s.id AND UPPER(s.content_type) IN ('BOOK', 'NOVEL')
            WHERE UPPER(c.content_type) IN ('BOOK', 'NOVEL')
            AND (c.is_default = 0 OR c.is_default IS NULL)
            GROUP BY c.id
            ORDER BY c.name
        """)
        return collections
    except Exception as e:
        LOGGER.error(f"Error getting book collections: {e}")
        return []


def get_popular_authors(limit=5):
    """Get popular authors."""
    try:
        authors = execute_query("""
            SELECT a.*, COUNT(ab.series_id) as book_count
            FROM authors a
            LEFT JOIN author_books ab ON a.id = ab.author_id
            GROUP BY a.id
            ORDER BY book_count DESC
            LIMIT ?
        """, (limit,))
        return authors
    except Exception as e:
        LOGGER.error(f"Error getting popular authors: {e}")
        return []


def get_recent_books(limit=None):
    """Get recent books. If limit is None, returns all books."""
    try:
        if limit:
            query = """
                SELECT s.*
                FROM series s
                WHERE UPPER(s.content_type) IN ('BOOK', 'NOVEL')
                ORDER BY s.created_at DESC
                LIMIT ?
            """
            books = execute_query(query, (limit,))
        else:
            query = """
                SELECT s.*
                FROM series s
                WHERE UPPER(s.content_type) IN ('BOOK', 'NOVEL')
                ORDER BY s.created_at DESC
            """
            books = execute_query(query)
        return books
    except Exception as e:
        LOGGER.error(f"Error getting recent books: {e}")
        return []


@books_routes.route('/books')
@setup_required
def books_home():
    """Books home page."""
    book_collections = get_book_collections()
    popular_authors = get_popular_authors(5)
    recent_books = get_recent_books()  # Get all books
    
    return render_template(
        'books/home.html',
        book_collections=book_collections,
        popular_authors=popular_authors,
        recent_books=recent_books
    )


@books_routes.route('/books/search')
@setup_required
def books_search():
    """Book search page."""
    return render_template('books/search.html')


@books_routes.route('/books/authors')
def authors_view():
    """Authors list page."""
    authors = execute_query("""
        SELECT a.*, COUNT(ba.book_id) as book_count
        FROM authors a
        LEFT JOIN book_authors ba ON a.id = ba.author_id
        GROUP BY a.id
        ORDER BY a.name
    """)
    
    return render_template('books/authors.html', authors=authors)


@books_routes.route('/books/authors/<int:author_id>')
def author_view(author_id):
    """Author detail page."""
    book_service = get_content_service(ContentType.BOOK)
    author = book_service.get_author_details(author_id)
    
    if "error" in author:
        abort(404)
    
    books = book_service.get_books_by_author(author_id)
    
    return render_template('books/author.html', author=author, books=books)


@books_routes.route('/books/<int:book_id>')
@setup_required
def book_view(book_id):
    """Book detail page."""
    book = execute_query("SELECT * FROM series WHERE id = ? AND content_type = 'BOOK'", (book_id,))
    
    if not book:
        abort(404)
    
    book = book[0]
    
    # Convert subjects to genres for frontend compatibility
    from backend.base.logging import LOGGER
    LOGGER.debug(f"Book {book_id} subjects field: {book.get('subjects')}")
    if book.get('subjects'):
        subjects_list = [s.strip() for s in book['subjects'].split(',')] if isinstance(book['subjects'], str) else book['subjects']
        book['genres'] = subjects_list
        LOGGER.debug(f"Converted subjects to genres: {book['genres']}")
    else:
        book['genres'] = []
        LOGGER.debug(f"No subjects found for book {book_id}")
    
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
