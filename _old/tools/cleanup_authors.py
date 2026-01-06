#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script to clean up orphaned authors from the database.
Run this to remove authors with no associated books/manga.
"""

import sys
import json
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Initialize the database connection
from backend.internals.db import init_db, get_db_path
from backend.features.author_cleanup import cleanup_orphaned_authors

def main():
    """Run the author cleanup."""
    print("=" * 60)
    print("Readloom Author Cleanup Utility")
    print("=" * 60)
    print()
    
    # Initialize database
    db_path = get_db_path()
    print(f"Database path: {db_path}")
    print()
    
    # Run cleanup
    print("Running author cleanup...")
    print("-" * 60)
    
    result = cleanup_orphaned_authors()
    
    print()
    print("Cleanup Results:")
    print("-" * 60)
    print(json.dumps(result, indent=2))
    print()
    
    if result.get("authors_removed", 0) > 0:
        print(f"✅ Successfully removed {result['authors_removed']} orphaned author(s)")
    else:
        print("✅ No orphaned authors found - database is clean!")
    
    print()
    print("=" * 60)

if __name__ == "__main__":
    main()
