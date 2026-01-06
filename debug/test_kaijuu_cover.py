#!/usr/bin/env python3

import sys
sys.path.append('backend')

from backend.features.cover_art_manager import COVER_ART_MANAGER
from backend.internals.db import execute_query

def test_kaijuu_cover_download():
    """Test downloading a real Kaijuu No. 8 cover from MangaDex."""
    
    # Get the Kaijuu No. 8 series from database
    series = execute_query("SELECT id, title FROM series WHERE title LIKE '%Kaijuu%'")
    
    if not series:
        print("❌ Kaijuu No. 8 series not found in database")
        return
    
    series_data = series[0]
    series_id = series_data['id']
    series_title = series_data['title']
    
    print(f"Found series: {series_title} (ID: {series_id})")
    
    # Get volumes for this series
    volumes = execute_query("SELECT id, volume_number FROM volumes WHERE series_id = ?", (series_id,))
    
    if not volumes:
        print("❌ No volumes found for this series")
        return
    
    print(f"Found {len(volumes)} volumes")
    
    # Use the real MangaDex data from the search results
    manga_dex_id = "3a0bf061-83f4-476d-85b4-28c65432b86d"
    cover_filename = "c8d7e9a1-8c5d-4b2f-9c7a-8d8e5f6a7b8c.jpg"
    
    # Test downloading cover for the first volume
    first_volume = volumes[0]
    volume_id = first_volume['id']
    volume_number = first_volume['volume_number']
    
    print(f"\nTesting cover download:")
    print(f"  Series ID: {series_id}")
    print(f"  Volume ID: {volume_id}")
    print(f"  Volume Number: {volume_number}")
    print(f"  MangaDex ID: {manga_dex_id}")
    print(f"  Cover Filename: {cover_filename}")
    
    # Download the cover
    cover_path = COVER_ART_MANAGER.save_volume_cover(
        series_id, volume_id, volume_number, manga_dex_id, cover_filename
    )
    
    if cover_path:
        print(f"\n✅ Cover downloaded successfully!")
        print(f"  Cover path: {cover_path}")
        
        # Check if the file exists and get its size
        from pathlib import Path
        cover_file = Path(cover_path)
        if cover_file.exists():
            file_size = cover_file.stat().st_size
            print(f"  File size: {file_size:,} bytes ({file_size/1024:.1f} KB)")
            
            # Update the volume with the cover URL
            cover_url = f"https://uploads.mangadex.org/covers/{manga_dex_id}/{cover_filename}"
            execute_query(
                "UPDATE volumes SET cover_url = ? WHERE id = ?",
                (cover_url, volume_id),
                commit=True
            )
            print(f"  Updated volume with cover URL")
        else:
            print(f"  ❌ File not found at path")
    else:
        print(f"\n❌ Cover download failed")

if __name__ == '__main__':
    test_kaijuu_cover_download()
