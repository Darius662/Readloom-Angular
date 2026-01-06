#!/usr/bin/env python3

import sys
sys.path.append('backend')

import requests

def test_kumo_desu_ga():
    """Test if Kumo desu ga, Nani ka? will work with our MangaDex cover system."""
    
    print("🔍 Testing: Kumo desu ga, Nani ka?")
    print("=" * 50)
    
    # First, let's search for it on AniList to get the correct AniList ID
    print("\n📚 Searching AniList for Kumo desu ga, Nani ka?...")
    
    anilist_query = """
    query ($search: String) {
      Media (search: $search, type: MANGA) {
        id
        title {
          romaji
          english
          native
        }
        coverImage {
          large
          medium
        }
        status
        volumes
        chapters
      }
    }
    """
    
    try:
        response = requests.post(
            "https://graphql.anilist.co/graphql",
            json={"query": anilist_query, "variables": {"search": "Kumo desu ga, Nani ka?"}},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if 'data' in data and data['data'] and data['data']['Media']:
                media = data['data']['Media']
                anilist_id = media['id']
                title = media['title']
                
                print(f"   ✅ Found on AniList:")
                print(f"      ID: {anilist_id}")
                print(f"      Title (EN): {title.get('english', 'N/A')}")
                print(f"      Title (ROMAJI): {title.get('romaji', 'N/A')}")
                print(f"      Title (NATIVE): {title.get('native', 'N/A')}")
                print(f"      Status: {media.get('status', 'N/A')}")
                print(f"      Volumes: {media.get('volumes', 'N/A')}")
                print(f"      Chapters: {media.get('chapters', 'N/A')}")
                
                # Test our MangaDex translation
                print(f"\n🔍 Testing MangaDex translation...")
                from backend.features.metadata_service.facade import find_mangadex_equivalent
                
                # Use the English title for better translation
                search_title = title.get('english') or title.get('romaji') or "Kumo desu ga, Nani ka?"
                mangadex_id = find_mangadex_equivalent(str(anilist_id), search_title)
                
                if mangadex_id:
                    print(f"   ✅ MangaDex equivalent found: {mangadex_id}")
                    
                    # Check what covers are available
                    print(f"\n🖼️  Checking MangaDex covers...")
                    from backend.features.cover_art_manager import COVER_ART_MANAGER
                    
                    volume_covers = COVER_ART_MANAGER.get_mangadex_covers_for_series(mangadex_id)
                    
                    if volume_covers:
                        print(f"   ✅ Found {len(volume_covers)} covers on MangaDex:")
                        for cover in volume_covers:
                            print(f"      Volume {cover['volume']}: {cover['filename']}")
                        
                        # Test cover download for one volume
                        print(f"\n🚀 Testing cover download...")
                        test_cover = volume_covers[0]
                        print(f"   Testing Volume {test_cover['volume']} cover...")
                        
                        # Create a test series entry
                        from backend.internals.db import execute_query
                        execute_query("""
                            INSERT INTO series (
                                title, content_type, metadata_source, metadata_id, 
                                author, publisher, status, description,
                                in_library, created_at, updated_at
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                        """, (
                            "Kumo desu ga, Nani ka? (Test)",
                            "MANGA", 
                            "AniList",
                            mangadex_id,
                            "Okina Baba",
                            "Futabasha",
                            media.get('status', 'unknown'),
                            "Test series for cover download verification.",
                            1
                        ), commit=True)
                        
                        # Get the series ID
                        result = execute_query("SELECT last_insert_rowid() as id")
                        series_id = result[0]['id']
                        
                        # Create a test volume
                        execute_query("""
                            INSERT INTO volumes (
                                series_id, volume_number, title, release_date, 
                                created_at, updated_at
                            ) VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                        """, (
                            series_id,
                            str(test_cover['volume']),
                            f"Volume {test_cover['volume']}",
                            None
                        ), commit=True)
                        
                        # Get the volume ID
                        result = execute_query("SELECT last_insert_rowid() as id")
                        volume_id = result[0]['id']
                        
                        # Try to download the cover
                        cover_path = COVER_ART_MANAGER.save_volume_cover(
                            series_id, volume_id, str(test_cover['volume']), mangadex_id, test_cover['filename']
                        )
                        
                        if cover_path:
                            print(f"   ✅ Cover download successful!")
                            print(f"      Path: {cover_path}")
                            
                            # Check file size
                            from pathlib import Path
                            cover_file = Path(cover_path)
                            if cover_file.exists():
                                file_size = cover_file.stat().st_size
                                print(f"      File size: {file_size:,} bytes ({file_size/1024:.1f} KB)")
                            
                            # Clean up test data
                            execute_query("DELETE FROM volumes WHERE id = ?", (volume_id,), commit=True)
                            execute_query("DELETE FROM series WHERE id = ?", (series_id,), commit=True)
                            print(f"   🧹 Cleaned up test data")
                        else:
                            print(f"   ❌ Cover download failed")
                        
                    else:
                        print(f"   ❌ No covers found on MangaDex")
                else:
                    print(f"   ❌ No MangaDex equivalent found")
                    
                    # Let's search MangaDex directly to see what's available
                    print(f"\n🔍 Direct MangaDex search...")
                    try:
                        response = requests.get(
                            "https://api.mangadex.org/manga",
                            params={"title": "Kumo desu ga, Nani ka", "limit": 5, "includes[]": "cover_art"},
                            timeout=10
                        )
                        
                        if response.status_code == 200:
                            data = response.json()
                            if 'data' in data and data['data']:
                                print(f"   📚 Found {len(data['data'])} results on MangaDex:")
                                for i, manga in enumerate(data['data']):
                                    attributes = manga.get('attributes', {})
                                    title = attributes.get('title', {})
                                    print(f"      {i+1}. {title.get('en', title.get('ja', 'Unknown'))}")
                                    print(f"         ID: {manga['id']}")
                                    
                                    # Check covers
                                    relationships = manga.get('relationships', [])
                                    cover_count = sum(1 for rel in relationships if rel.get('type') == 'cover_art')
                                    print(f"         Covers: {cover_count}")
                            else:
                                print(f"   ❌ No results found")
                        else:
                            print(f"   ❌ Search failed: {response.status_code}")
                    except Exception as e:
                        print(f"   ❌ Direct search error: {e}")
            else:
                print(f"   ❌ No results found on AniList")
        else:
            print(f"   ❌ AniList API error: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   📝 Error: {error_data}")
            except:
                print(f"   📝 Raw: {response.text[:200]}")
                
    except Exception as e:
        print(f"   ❌ Error: {e}")

if __name__ == '__main__':
    test_kumo_desu_ga()
