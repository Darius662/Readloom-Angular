#!/usr/bin/env python3

import sys
sys.path.append('backend')

from backend.features.cover_art_manager import COVER_ART_MANAGER

def test_cover_manager():
    """Test the cover art manager with the test series."""
    
    series_id = 1
    volume_number = "1"
    
    print(f"Testing cover art manager for series {series_id}, volume {volume_number}")
    
    # Test getting series folder path
    series_folder = COVER_ART_MANAGER.get_series_folder_path(series_id)
    print(f"Series folder path: {series_folder}")
    
    # Test getting volume cover path
    cover_path = COVER_ART_MANAGER.get_volume_cover_path(series_id, volume_number)
    print(f"Volume cover path: {cover_path}")
    
    # Test getting series cover directory
    cover_dir = COVER_ART_MANAGER.get_series_cover_dir(series_id)
    print(f"Series cover directory: {cover_dir}")
    
    # Check if the cover_art directory was created
    if cover_dir and cover_dir.exists():
        print(f"✅ Cover art directory created successfully: {cover_dir}")
        print(f"   Directory contents: {list(cover_dir.iterdir()) if cover_dir.exists() else 'Empty'}")
    else:
        print(f"❌ Cover art directory not created")

if __name__ == '__main__':
    test_cover_manager()
