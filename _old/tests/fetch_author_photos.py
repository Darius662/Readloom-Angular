#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Fetch author photos from OpenLibrary for all authors.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Set database location
from backend.internals.db import set_db_location
set_db_location()

from backend.features.author_photo_fetcher import fetch_and_update_all_author_photos


def main():
    """Fetch and update author photos."""
    print("Fetching author photos from OpenLibrary...")
    print()
    
    stats = fetch_and_update_all_author_photos()
    
    print(f"✓ Author photo fetch completed!")
    print()
    print(f"  Authors checked: {stats['authors_checked']}")
    print(f"  Photos added: {stats['photos_added']}")
    print(f"  Errors: {stats['errors']}")
    print()
    
    if stats['photos_added'] > 0:
        print("✓ Author photos have been updated!")
        print("  Refresh the Authors page to see the new photos.")
    else:
        print("No new photos were added.")


if __name__ == "__main__":
    main()
