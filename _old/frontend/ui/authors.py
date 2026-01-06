#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Authors UI routes.
Handles author-related pages and views.
"""

from flask import Blueprint, render_template, abort
from backend.base.logging import LOGGER
from backend.internals.db import execute_query
from frontend.middleware import setup_required

# Create routes blueprint
authors_routes = Blueprint('authors_routes', __name__)


@authors_routes.route('/authors')
@setup_required
def authors_home():
    """Authors home page."""
    return render_template('authors/authors.html')


@authors_routes.route('/authors/<int:author_id>')
@setup_required
def author_detail(author_id):
    """Author detail page."""
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


@authors_routes.route('/authors/<int:author_id>/books')
def author_books(author_id):
    """Author's books page."""
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
