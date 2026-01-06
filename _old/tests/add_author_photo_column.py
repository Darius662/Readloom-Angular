#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Migration script to add photo_url column to authors table.
"""

import sqlite3
from pathlib import Path

def add_photo_url_column():
    """Add photo_url column to authors table."""
    db_path = Path('data/db/readloom.db')
    
    if not db_path.exists():
        print(f"✗ Database not found at {db_path}")
        return False
    
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    try:
        # Check if column already exists
        cursor.execute("PRAGMA table_info(authors)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if 'photo_url' in columns:
            print("✓ photo_url column already exists")
            return True
        
        # Add photo_url column
        cursor.execute("""
            ALTER TABLE authors 
            ADD COLUMN photo_url TEXT
        """)
        
        conn.commit()
        print("✓ Added photo_url column to authors table")
        
        # Verify
        cursor.execute("PRAGMA table_info(authors)")
        columns = [row[1] for row in cursor.fetchall()]
        print(f"\nAuthors table columns: {', '.join(columns)}")
        
        return True
    
    except Exception as e:
        print(f"✗ Error adding column: {e}")
        conn.rollback()
        return False
    
    finally:
        conn.close()

if __name__ == "__main__":
    success = add_photo_url_column()
    exit(0 if success else 1)
