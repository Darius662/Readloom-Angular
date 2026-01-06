#!/usr/bin/env python3

import sys
sys.path.append('backend')

from backend.base.helpers import create_series_folder_structure
from pathlib import Path

def test_manga_import():
    """Test creating a manga series using the same function that gets called when adding to collection."""
    
    # Test the create_series_folder_structure function
    series_id = 999  # Use a test ID
    series_title = "Test Manga Import"
    content_type = "MANGA"
    
    print(f"Testing manga import for: {series_title}")
    
    try:
        # This is the function that gets called when you add a manga to collection
        series_folder = create_series_folder_structure(
            series_id=series_id,
            series_title=series_title,
            content_type=content_type
        )
        
        print(f"✅ Series folder created: {series_folder}")
        
        # Check if README.txt was created
        readme_file = series_folder / "README.txt"
        if readme_file.exists():
            print(f"✅ README.txt created: {readme_file}")
        else:
            print(f"❌ README.txt not created: {readme_file}")
        
        # Check if cover_art folder was created
        cover_art_folder = series_folder / "cover_art"
        if cover_art_folder.exists():
            print(f"✅ Cover art folder created: {cover_art_folder}")
            print(f"   Folder contents: {list(cover_art_folder.iterdir()) if cover_art_folder.exists() else 'Empty'}")
        else:
            print(f"❌ Cover art folder not created: {cover_art_folder}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_manga_import()
