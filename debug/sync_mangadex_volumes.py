#!/usr/bin/env python3

import sys
sys.path.append('backend')

import requests
from backend.internals.db import execute_query
from backend.base.logging import LOGGER

def sync_mangadex_volumes():
    """Sync volume data from MangaDex to the database."""
    
    print("🔍 Syncing MangaDex Volume Data")
    print("=" * 50)
    
    # Get series that need MangaDex volume sync
    series = execute_query("""
        SELECT id, title, metadata_source, metadata_id 
        FROM series 
        WHERE metadata_source = 'AniList' AND metadata_id IS NOT NULL
    """)
    
    for s in series:
        series_id = s['id']
        series_title = s['title']
        anilist_id = s['metadata_id']
        
        print(f"\n📚 Processing: {series_title}")
        print(f"   AniList ID: {anilist_id}")
        
        # Find MangaDex equivalent
        mangadex_id = find_mangadex_equivalent(anilist_id, series_title)
        
        if not mangadex_id:
            print(f"   ❌ No MangaDex equivalent found")
            continue
        
        print(f"   ✅ MangaDex ID: {mangadex_id}")
        
        # Get current volumes in database
        current_volumes = execute_query(
            "SELECT id, volume_number FROM volumes WHERE series_id = ? ORDER BY volume_number",
            (series_id,)
        )
        
        current_vol_numbers = {v['volume_number'] for v in current_volumes}
        print(f"   📚 Current volumes: {sorted(current_vol_numbers)}")
        
        # Get MangaDex chapters to determine actual volumes
        mangadex_volumes = get_mangadex_volumes(mangadex_id)
        
        if not mangadex_volumes:
            print(f"   ❌ No volume data found on MangaDex")
            continue
        
        print(f"   📚 MangaDex volumes: {sorted(mangadex_volumes)}")
        
        # Find missing volumes
        missing_volumes = mangadex_volumes - current_vol_numbers
        extra_volumes = current_vol_numbers - mangadex_volumes
        
        if missing_volumes:
            print(f"   ➕ Adding missing volumes: {sorted(missing_volumes)}")
            
            for vol_num in sorted(missing_volumes):
                try:
                    execute_query("""
                        INSERT INTO volumes (
                            series_id, volume_number, title, release_date, 
                            created_at, updated_at
                        ) VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                    """, (
                        series_id,
                        str(vol_num),
                        f"Volume {vol_num}",
                        None  # We don't have release dates
                    ), commit=True)
                    
                    print(f"      ✅ Added Volume {vol_num}")
                    
                except Exception as e:
                    print(f"      ❌ Failed to add Volume {vol_num}: {e}")
        
        if extra_volumes:
            print(f"   ⚠️  Extra volumes in database: {sorted(extra_volumes)}")
        
        # Update the series with the correct MangaDex ID
        execute_query(
            "UPDATE series SET metadata_id = ? WHERE id = ?",
            (mangadex_id, series_id),
            commit=True
        )
        print(f"   ✅ Updated series with MangaDex ID")

def find_mangadex_equivalent(anilist_id, series_title):
    """Find MangaDex equivalent for an AniList series."""
    
    # Try different search terms
    search_terms = [
        series_title,
        series_title.replace("Kaijuu 8-gou", "Kaiju No. 8"),
        series_title.replace("Shingeki no Kyojin", "進撃の巨人"),
        series_title.replace("Enen no Shouboutai", "炎炎消防隊"),
        series_title.replace("Code Geass: Hangyaku no Lelouch", "Code Geass"),
    ]
    
    for term in search_terms:
        try:
            response = requests.get(
                "https://api.mangadex.org/manga",
                params={"title": term, "limit": 10, "includes[]": "cover_art"},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if 'data' in data and data['data']:
                    for manga in data['data']:
                        if manga.get('type') == 'manga':
                            attributes = manga.get('attributes', {})
                            title = attributes.get('title', {})
                            alt_titles = attributes.get('altTitles', [])
                            
                            # Check if this looks like the main series
                            all_titles = [title.get('en', '')] + [t.get('en', '') for t in alt_titles]
                            
                            if any(term.lower() in title.lower() for title in all_titles):
                                # Skip obvious spinoffs/side stories
                                manga_title = title.get('en', '')
                                if any(keyword in manga_title.lower() for keyword in ['relax', 'b-side', 'day off', 'fan colored']):
                                    continue
                                
                                return manga['id']
        except Exception as e:
            print(f"   ❌ Search error for '{term}': {e}")
    
    return None

def get_mangadex_volumes(mangadex_id):
    """Get all volume numbers from MangaDex chapters."""
    
    try:
        response = requests.get(
            f"https://api.mangadex.org/manga/{mangadex_id}/chapter",
            params={"limit": 500, "translatedLanguage[]": "en"},
            timeout=10
        )
        
        if response.status_code != 200:
            # Try without language filter
            response = requests.get(
                f"https://api.mangadex.org/manga/{mangadex_id}/chapter",
                params={"limit": 500},
                timeout=10
            )
        
        if response.status_code == 200:
            data = response.json()
            
            if 'data' in data and data['data']:
                volume_numbers = set()
                
                for chapter in data['data']:
                    attributes = chapter.get('attributes', {})
                    volume = attributes.get('volume')
                    
                    if volume:
                        try:
                            vol_num = int(volume)
                            volume_numbers.add(vol_num)
                        except ValueError:
                            pass
                
                return volume_numbers
        
    except Exception as e:
        print(f"   ❌ Error getting MangaDex volumes: {e}")
    
    return set()

if __name__ == '__main__':
    sync_mangadex_volumes()
