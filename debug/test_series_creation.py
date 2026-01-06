#!/usr/bin/env python3

import sys
sys.path.append('backend')

from backend.internals.db import execute_query
from pathlib import Path

def test_series_creation():
    """Test creating a series and see if cover_art folder is created."""
    
    # Create a test series
    execute_query("""
        INSERT INTO series (
            title, content_type, metadata_source, metadata_id, 
            author, publisher, status, description,
            in_library, created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
    """, (
        "Test Manga Series",
        "MANGA", 
        "AniList",
        "12345",
        "Test Author",
        "Test Publisher",
        "ongoing",
        "This is a test manga series to verify cover_art folder creation.",
        1
    ), commit=True)
    
    # Get the series ID
    result = execute_query("SELECT last_insert_rowid() as id")
    series_id = result[0]['id']
    
    print(f"Created test series with ID: {series_id}")
    
    # Create a test folder for this series
    test_folder = Path("C:/Users/dariu/Desktop/Readloom-TEST/Manga/Test Manga Series")
    test_folder.mkdir(parents=True, exist_ok=True)
    
    # Update the series with the custom path
    execute_query(
        "UPDATE series SET custom_path = ? WHERE id = ?",
        (str(test_folder), series_id),
        commit=True
    )
    
    print(f"Set custom path: {test_folder}")
    
    # Now trigger the README sync (which should also create cover_art folder)
    try:
        from backend.features.readme_sync import sync_series_to_readme
        success = sync_series_to_readme(series_id)
        print(f"README sync result: {success}")
    except Exception as e:
        print(f"README sync error: {e}")
    
    # Check if cover_art folder was created
    cover_art_folder = test_folder / "cover_art"
    if cover_art_folder.exists():
        print(f"✅ Cover art folder created successfully: {cover_art_folder}")
        print(f"   Folder contents: {list(cover_art_folder.iterdir()) if cover_art_folder.exists() else 'Empty'}")
    else:
        print(f"❌ Cover art folder not created: {cover_art_folder}")
    
    # Check if README.txt was created
    readme_file = test_folder / "README.txt"
    if readme_file.exists():
        print(f"✅ README.txt created: {readme_file}")
    else:
        print(f"❌ README.txt not created: {readme_file}")

if __name__ == '__main__':
    test_series_creation()
