#!/usr/bin/env python3

import sys
sys.path.append('backend')

import requests
import json
from backend.internals.db import execute_query
from backend.features.cover_art_manager import COVER_ART_MANAGER

def test_hybrid_cover_system():
    """Test a hybrid cover system that uses AniList for series covers and MangaDex for volume covers."""
    
    print("🔍 Testing Hybrid Cover System")
    print("=" * 50)
    
    # Get series from database
    series = execute_query("SELECT id, title, metadata_source, metadata_id FROM series WHERE metadata_source = 'AniList'")
    
    for s in series:
        series_id = s['id']
        series_title = s['title']
        anilist_id = s['metadata_id']
        
        print(f"\n📚 Series: {series_title}")
        print(f"   AniList ID: {anilist_id}")
        
        # Step 1: Get series cover from AniList
        anilist_cover = get_anilist_series_cover(anilist_id)
        if anilist_cover:
            print(f"   ✅ AniList Series Cover: {anilist_cover}")
        
        # Step 2: Try to find MangaDex equivalent
        mangadex_id = find_mangadex_equivalent(anilist_id, series_title)
        if mangadex_id:
            print(f"   ✅ MangaDex ID: {mangadex_id}")
            
            # Step 3: Get volume covers from MangaDex
            volume_covers = get_mangadex_volume_covers(mangadex_id)
            if volume_covers:
                print(f"   ✅ Found {len(volume_covers)} volume covers")
                
                # Test downloading first volume cover
                first_volume = volume_covers[0]
                print(f"   🎯 Testing Volume {first_volume['volume']} Cover:")
                print(f"      MangaDex ID: {mangadex_id}")
                print(f"      Cover Filename: {first_volume['filename']}")
                
                # Get volume info from database
                volumes = execute_query("SELECT id, volume_number FROM volumes WHERE series_id = ? ORDER BY volume_number", (series_id,))
                if volumes:
                    volume_id = volumes[0]['id']
                    volume_number = volumes[0]['volume_number']
                    
                    # Try to download using our system (will likely fail due to CDN, but let's test)
                    cover_path = COVER_ART_MANAGER.save_volume_cover(
                        series_id, volume_id, volume_number, mangadex_id, first_volume['filename']
                    )
                    
                    if cover_path:
                        print(f"      ✅ Cover downloaded: {cover_path}")
                    else:
                        print(f"      ❌ Cover download failed (expected due to CDN issues)")
        else:
            print(f"   ❌ Could not find MangaDex equivalent")

def get_anilist_series_cover(anilist_id):
    """Get series cover from AniList."""
    query = """
    query ($id: Int) {
      Media (id: $id, type: MANGA) {
        coverImage {
          large
          medium
        }
      }
    }
    """
    
    try:
        response = requests.post(
            "https://graphql.anilist.co/graphql",
            json={"query": query, "variables": {"id": anilist_id}},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if 'data' in data and data['data'] and data['data']['Media']:
                media = data['data']['Media']
                cover_image = media.get('coverImage', {})
                return cover_image.get('large') or cover_image.get('medium')
    except Exception as e:
        print(f"   ❌ AniList API error: {e}")
    
    return None

def find_mangadex_equivalent(anilist_id, series_title):
    """Find MangaDex equivalent using title search."""
    
    # Try different search terms
    search_terms = [
        series_title,
        # Try to extract Japanese title if possible
        series_title.replace("Attack on Titan", "進撃の巨人"),
        series_title.replace("Kaijuu No. 8", "怪獣8号"),
        series_title.replace("Enen no Shouboutai", "炎炎消防隊"),
    ]
    
    for term in search_terms:
        try:
            response = requests.get(
                f"http://localhost:7227/api/mangadex/search",
                params={"title": term, "limit": 10, "includes[]": "cover_art"},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if 'data' in data and data['data']:
                    for manga in data['data']:
                        # Look for main series (not doujinshi)
                        if manga.get('type') == 'manga':
                            # Check if this looks like the main series
                            attributes = manga.get('attributes', {})
                            title = attributes.get('title', {})
                            alt_titles = attributes.get('altTitles', [])
                            
                            # Check if any title matches our search
                            all_titles = [title.get('en', '')] + [t.get('en', '') for t in alt_titles]
                            
                            if any(term.lower() in title.lower() for title in all_titles):
                                return manga['id']
        except Exception as e:
            print(f"   ❌ Search error for '{term}': {e}")
    
    return None

def get_mangadex_volume_covers(mangadex_id):
    """Get volume covers from MangaDex."""
    
    try:
        response = requests.get(
            f"https://api.mangadex.org/manga/{mangadex_id}",
            params={"includes[]": "cover_art"},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if 'data' in data and data['data']:
                manga = data['data']
                relationships = manga.get('relationships', [])
                
                volume_covers = []
                for rel in relationships:
                    if rel.get('type') == 'cover_art':
                        attributes = rel.get('attributes', {})
                        volume = attributes.get('volume')
                        filename = attributes.get('fileName')
                        
                        if volume and filename:
                            volume_covers.append({
                                'volume': volume,
                                'filename': filename,
                                'cover_id': rel.get('id')
                            })
                
                return volume_covers
    except Exception as e:
        print(f"   ❌ MangaDex API error: {e}")
    
    return []

def suggest_alternative_solution():
    """Suggest alternative solutions given the MangaDex CDN issues."""
    
    print(f"\n🎯 Alternative Solutions:")
    print(f"1. ✅ Use AniList series covers (working)")
    print(f"2. ❌ MangaDex volume covers (blocked by CDN)")
    print(f"3. 💡 Implement fallback system:")
    print(f"   - Primary: AniList series cover")
    print(f"   - Secondary: Manual volume cover upload")
    print(f"   - Tertiary: Generic volume covers")
    print(f"4. 🔧 Create cover upload interface for users")
    print(f"5. 📚 Use other sources (MyAnimeList, Kitsu)")

if __name__ == '__main__':
    test_hybrid_cover_system()
    suggest_alternative_solution()
