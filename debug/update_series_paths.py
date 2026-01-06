#!/usr/bin/env python3

import sys
sys.path.append('backend')

from backend.internals.db import execute_query
from pathlib import Path

def update_series_paths():
    """Update series with their correct custom paths."""
    
    # Define the base manga folder
    manga_base = Path("C:/Users/dariu/Desktop/Readloom-TEST/Manga")
    
    # Get all series without custom paths
    series = execute_query("SELECT id, title FROM series WHERE custom_path IS NULL")
    
    print(f"Found {len(series)} series without custom paths:")
    
    for s in series:
        series_id = s['id']
        series_title = s['title']
        
        # Try to find the folder
        series_folder = manga_base / series_title
        
        if series_folder.exists():
            # Update the database
            execute_query(
                "UPDATE series SET custom_path = ? WHERE id = ?",
                (str(series_folder), series_id),
                commit=True
            )
            print(f"✅ Updated {series_title} (ID: {series_id}) -> {series_folder}")
        else:
            print(f"❌ Folder not found for {series_title}: {series_folder}")
    
    # Show updated series
    print("\nUpdated series:")
    updated_series = execute_query("SELECT id, title, custom_path FROM series")
    for s in updated_series:
        print(f"ID: {s['id']}, Title: {s['title']}, Path: {s['custom_path']}")

if __name__ == '__main__':
    update_series_paths()
