#!/usr/bin/env python3

import sys
sys.path.append('backend')

from backend.features.cover_art_manager import COVER_ART_MANAGER
from backend.internals.db import execute_query
import requests

def test_attack_on_titan():
    """Test downloading Attack on Titan cover - a very popular manga."""
    
    # Attack on Titan data from the search results
    manga_dex_id = "34446a79-91e8-4e3c-bf41-5f68b66c423d"
    cover_filename = "9b5de6c3-8c5d-4b2f-9c7a-8d8e5f6a7b8c.jpg"
    
    print(f"🔍 Testing Attack on Titan Cover Download")
    print(f"   MangaDex ID: {manga_dex_id}")
    print(f"   Cover Filename: {cover_filename}")
    print()
    
    # First test the cover URL directly
    cover_url = f"https://uploads.mangadex.org/covers/{manga_dex_id}/{cover_filename}"
    print(f"🌐 Testing cover URL: {cover_url}")
    
    try:
        response = requests.head(cover_url, timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            content_type = response.headers.get('content-type', 'Unknown')
            content_length = response.headers.get('content-length', 'Unknown')
            print(f"   Content-Type: {content_type}")
            print(f"   Content-Length: {content_length} bytes")
            print("✅ Cover URL is accessible!")
        else:
            print(f"❌ Cover URL returned status: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Error checking cover URL: {e}")
        return
    
    print()
    
    # Create a test series entry for Attack on Titan
    try:
        # Insert Attack on Titan series
        execute_query("""
            INSERT INTO series (
                title, content_type, metadata_source, metadata_id, 
                author, publisher, status, description,
                in_library, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        """, (
            "Attack on Titan (Test)",
            "MANGA", 
            "MangaDex",
            manga_dex_id,
            "Hajime Isayama",
            "Kodansha",
            "completed",
            "Test series for cover download verification.",
            1
        ), commit=True)
        
        # Get the series ID
        result = execute_query("SELECT last_insert_rowid() as id")
        series_id = result[0]['id']
        
        print(f"✅ Created test series with ID: {series_id}")
        
        # Create a test folder
        test_folder = "C:/Users/dariu/Desktop/Readloom-TEST/Manga/Attack on Titan Test"
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
            "2009-09-09",
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
                
                # Update the volume with the cover URL
                execute_query(
                    "UPDATE volumes SET cover_url = ? WHERE id = ?",
                    (cover_url, volume_id),
                    commit=True
                )
                print(f"✅ Updated volume with cover URL")
                
                # Test if we can serve it via API
                print(f"\n🌐 Testing API cover serving:")
                api_url = f"http://localhost:7227/api/cover-art/volume/{volume_id}"
                try:
                    api_response = requests.head(api_url, timeout=10)
                    print(f"   API Status: {api_response.status_code}")
                    if api_response.status_code == 200:
                        print(f"   ✅ API can serve the cover!")
                    else:
                        print(f"   ❌ API returned: {api_response.status_code}")
                except Exception as e:
                    print(f"   ❌ API test failed: {e}")
                    
            else:
                print(f"   ❌ File not found at path")
        else:
            print(f"\n❌ Cover download failed")
            
    except Exception as e:
        print(f"❌ Error during test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_attack_on_titan()
