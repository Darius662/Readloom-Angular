#!/usr/bin/env python3

import sys
sys.path.append('backend')

from backend.features.cover_art_manager import COVER_ART_MANAGER
from backend.internals.db import execute_query

def test_one_piece_cover():
    """Test downloading One Piece cover to verify the system works."""
    
    # Use One Piece data from the search results
    manga_dex_id = "a2c1d849-af05-4bbc-b2a7-866ebb10331f"
    cover_filename = "da0341d8-5526-452c-8bd3-dc8e3cd89f99.jpg"
    
    print(f"🔍 Testing One Piece Cover Download")
    print(f"   MangaDex ID: {manga_dex_id}")
    print(f"   Cover Filename: {cover_filename}")
    print()
    
    # Test the cover URL directly
    cover_url = f"https://uploads.mangadex.org/covers/{manga_dex_id}/{cover_filename}"
    print(f"🌐 Testing cover URL: {cover_url}")
    
    import requests
    try:
        response = requests.head(cover_url, timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print(f"   Content-Type: {response.headers.get('content-type', 'Unknown')}")
            print(f"   Content-Length: {response.headers.get('content-length', 'Unknown')} bytes")
            print("✅ Cover URL is accessible!")
        else:
            print(f"❌ Cover URL returned status: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Error checking cover URL: {e}")
        return
    
    print()
    
    # Create a test series entry for One Piece
    try:
        # Insert One Piece series
        execute_query("""
            INSERT INTO series (
                title, content_type, metadata_source, metadata_id, 
                author, publisher, status, description,
                in_library, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        """, (
            "One Piece (Test)",
            "MANGA", 
            "MangaDex",
            manga_dex_id,
            "Eiichiro Oda",
            "Shueisha",
            "ongoing",
            "Test series for cover download verification.",
            1
        ), commit=True)
        
        # Get the series ID
        result = execute_query("SELECT last_insert_rowid() as id")
        series_id = result[0]['id']
        
        print(f"✅ Created test series with ID: {series_id}")
        
        # Create a test folder
        test_folder = "C:/Users/dariu/Desktop/Readloom-TEST/Manga/One Piece Test"
        from pathlib import Path
        Path(test_folder).mkdir(parents=True, exist_ok=True)
        
        # Update the series with the custom path
        execute_query(
            "UPDATE series SET custom_path = ? WHERE id = ?",
            (test_folder, series_id),
            commit=True
        )
        
        print(f"✅ Set custom path: {test_folder}")
        
        # Create a test volume
        execute_query("""
            INSERT INTO volumes (
                series_id, volume_number, title, release_date, 
                cover_url, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        """, (
            series_id,
            "1",
            "Volume 1",
            "1997-07-22",
            cover_url
        ), commit=True)
        
        # Get the volume ID
        result = execute_query("SELECT last_insert_rowid() as id")
        volume_id = result[0]['id']
        
        print(f"✅ Created test volume with ID: {volume_id}")
        
        # Now test the cover download
        print(f"\n🎯 Testing cover download:")
        print(f"   Series ID: {series_id}")
        print(f"   Volume ID: {volume_id}")
        print(f"   Volume Number: 1")
        
        cover_path = COVER_ART_MANAGER.save_volume_cover(
            series_id, volume_id, "1", manga_dex_id, cover_filename
        )
        
        if cover_path:
            print(f"\n✅ Cover downloaded successfully!")
            print(f"   Cover path: {cover_path}")
            
            # Check if the file exists
            cover_file = Path(cover_path)
            if cover_file.exists():
                file_size = cover_file.stat().st_size
                print(f"   File size: {file_size:,} bytes ({file_size/1024:.1f} KB)")
                print(f"✅ Cover system is working perfectly!")
            else:
                print(f"   ❌ File not found at path")
        else:
            print(f"\n❌ Cover download failed")
            
    except Exception as e:
        print(f"❌ Error during test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_one_piece_cover()
