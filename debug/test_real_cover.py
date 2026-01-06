#!/usr/bin/env python3

import sys
sys.path.append('backend')

from backend.features.cover_art_manager import COVER_ART_MANAGER

def test_real_cover_download():
    """Test downloading a real cover from MangaDex."""
    
    series_id = 1
    volume_id = 1
    volume_number = "1"
    
    # Use a different cover from the search results (volume 4 cover)
    manga_dex_id = "590666db-1beb-4830-8732-dc11dfbe0148"
    cover_filename = "ed782109-31e7-4752-b02b-47a04f94f613.jpg"
    
    print(f"Testing real cover download:")
    print(f"  Series ID: {series_id}")
    print(f"  Volume ID: {volume_id}")
    print(f"  Volume Number: {volume_number}")
    print(f"  MangaDex ID: {manga_dex_id}")
    print(f"  Cover Filename: {cover_filename}")
    
    # Test the download
    cover_path = COVER_ART_MANAGER.save_volume_cover(
        series_id, volume_id, volume_number, manga_dex_id, cover_filename
    )
    
    if cover_path:
        print(f"✅ Cover downloaded successfully!")
        print(f"  Cover path: {cover_path}")
        
        # Check if the file exists
        from pathlib import Path
        if Path(cover_path).exists():
            print(f"  File size: {Path(cover_path).stat().st_size} bytes")
        else:
            print(f"  ❌ File not found at path")
    else:
        print(f"❌ Cover download failed")

if __name__ == '__main__':
    test_real_cover_download()
