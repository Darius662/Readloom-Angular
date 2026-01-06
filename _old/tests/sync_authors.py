#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Sync authors from series table to authors table.

This script extracts author names from the series table and creates
corresponding entries in the authors table, then links them via author_books.
"""

import sqlite3
from pathlib import Path

def sync_authors():
    """Sync authors from series to authors table."""
    db_path = Path('data/db/readloom.db')
    
    if not db_path.exists():
        print(f"✗ Database not found at {db_path}")
        return False
    
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    try:
        # Get all unique authors from series table
        cursor.execute("""
            SELECT DISTINCT author FROM series 
            WHERE author IS NOT NULL AND author != ''
            ORDER BY author ASC
        """)
        
        series_authors = [row['author'] for row in cursor.fetchall()]
        print(f"Found {len(series_authors)} unique authors in series table:")
        for author in series_authors:
            print(f"  - {author}")
        
        print("\nSyncing authors...")
        
        # For each author, create entry in authors table if not exists
        for author_name in series_authors:
            # Check if author already exists
            cursor.execute("SELECT id FROM authors WHERE name = ?", (author_name,))
            existing = cursor.fetchone()
            
            if existing:
                author_id = existing['id']
                print(f"  ✓ Author '{author_name}' already exists (ID: {author_id})")
            else:
                # Create new author
                cursor.execute("""
                    INSERT INTO authors (name, created_at, updated_at)
                    VALUES (?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                """, (author_name,))
                author_id = cursor.lastrowid
                print(f"  ✓ Created author '{author_name}' (ID: {author_id})")
            
            # Now link this author to all series with this author name
            cursor.execute("""
                SELECT id FROM series WHERE author = ?
            """, (author_name,))
            
            series_ids = [row['id'] for row in cursor.fetchall()]
            
            for series_id in series_ids:
                # Check if link already exists
                cursor.execute("""
                    SELECT id FROM author_books 
                    WHERE author_id = ? AND series_id = ?
                """, (author_id, series_id))
                
                if not cursor.fetchone():
                    # Create link
                    cursor.execute("""
                        INSERT INTO author_books (author_id, series_id)
                        VALUES (?, ?)
                    """, (author_id, series_id))
                    print(f"    → Linked to series ID {series_id}")
        
        conn.commit()
        print("\n✓ Author sync completed successfully!")
        
        # Show final stats
        cursor.execute("SELECT COUNT(*) as count FROM authors")
        author_count = cursor.fetchone()['count']
        cursor.execute("SELECT COUNT(*) as count FROM author_books")
        links_count = cursor.fetchone()['count']
        
        print(f"\nFinal stats:")
        print(f"  Authors: {author_count}")
        print(f"  Author_books links: {links_count}")
        
        return True
    
    except Exception as e:
        print(f"✗ Error syncing authors: {e}")
        conn.rollback()
        return False
    
    finally:
        conn.close()

if __name__ == "__main__":
    success = sync_authors()
    exit(0 if success else 1)
