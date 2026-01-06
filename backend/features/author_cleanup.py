#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Author cleanup module - removes authors with no books automatically.
"""

from backend.base.logging import LOGGER
from backend.internals.db import execute_query


def cleanup_orphaned_authors() -> dict:
    """
    Remove authors that have no books.
    
    Returns:
        dict: Statistics about cleanup operation.
    """
    try:
        stats = {
            "authors_checked": 0,
            "authors_removed": 0,
            "errors": 0
        }
        
        # Find authors with no books
        orphaned = execute_query("""
            SELECT a.id, a.name
            FROM authors a
            LEFT JOIN author_books ab ON a.id = ab.author_id
            GROUP BY a.id
            HAVING COUNT(ab.id) = 0
        """)
        
        stats["authors_checked"] = len(orphaned) if orphaned else 0
        
        if not orphaned:
            LOGGER.info("No orphaned authors found")
            return stats
        
        # Remove each orphaned author
        for author in orphaned:
            try:
                author_id = author['id']
                author_name = author['name']
                
                # Delete the author
                execute_query("""
                    DELETE FROM authors WHERE id = ?
                """, (author_id,), commit=True)
                
                stats["authors_removed"] += 1
                LOGGER.info(f"Removed orphaned author: {author_name} (ID: {author_id})")
            
            except Exception as e:
                LOGGER.error(f"Error removing author {author['id']}: {e}")
                stats["errors"] += 1
        
        LOGGER.info(f"Author cleanup complete: {stats}")
        return stats
    
    except Exception as e:
        LOGGER.error(f"Error in cleanup_orphaned_authors: {e}")
        return {
            "authors_checked": 0,
            "authors_removed": 0,
            "errors": 1
        }


def cleanup_author_if_orphaned(author_id: int) -> bool:
    """
    Remove author if they have no books.
    
    Args:
        author_id: Author ID
    
    Returns:
        bool: True if author was removed, False if author still has books
    """
    try:
        # Check if author has any books
        books = execute_query("""
            SELECT COUNT(*) as count FROM author_books WHERE author_id = ?
        """, (author_id,))
        
        book_count = books[0]['count'] if books else 0
        
        if book_count > 0:
            LOGGER.debug(f"Author {author_id} still has {book_count} books, not removing")
            return False
        
        # Get author name for logging
        author = execute_query("""
            SELECT name FROM authors WHERE id = ?
        """, (author_id,))
        
        author_name = author[0]['name'] if author else f"ID {author_id}"
        
        # Remove author
        execute_query("""
            DELETE FROM authors WHERE id = ?
        """, (author_id,), commit=True)
        
        LOGGER.info(f"Removed orphaned author: {author_name} (ID: {author_id})")
        return True
    
    except Exception as e:
        LOGGER.error(f"Error cleaning up author {author_id}: {e}")
        return False
