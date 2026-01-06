#!/usr/bin/env python3

import sys
sys.path.append('backend')

import requests
from backend.internals.db import execute_query
from backend.features.cover_art_manager import COVER_ART_MANAGER

def implement_complete_volume_cover_system():
    """Implement the complete volume cover system for all series."""
    
    print("🔍 Implementing Complete Volume Cover System")
    print("=" * 50)
    
    # Get all series with AniList metadata
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
        print(f"   Series ID: {series_id}")
        print(f"   AniList ID: {anilist_id}")
        
        # Find MangaDex equivalent
        mangadex_id = find_mangadex_equivalent(anilist_id, series_title)
        
        if not mangadex_id:
            print(f"   ❌ No MangaDex equivalent found")
            continue
        
        print(f"   ✅ MangaDex ID: {mangadex_id}")
        
        # Update series with MangaDex ID
        execute_query(
            "UPDATE series SET metadata_id = ? WHERE id = ?",
            (mangadex_id, series_id),
            commit=True
        )
        
        # Process volumes and covers
        process_series_volumes_and_covers(series_id, mangadex_id, series_title)

def process_series_volumes_and_covers(series_id, mangadex_id, series_title):
    """Process volumes and covers for a specific series."""
    
    # Get current volumes
    current_volumes = execute_query(
        "SELECT id, volume_number FROM volumes WHERE series_id = ? ORDER BY volume_number",
        (series_id,)
    )
    
    current_vol_numbers = {v['volume_number'] for v in current_volumes}
    print(f"   📚 Current volumes: {sorted(current_vol_numbers)}")
    
    # Get MangaDex volumes from chapters
    mangadex_volumes = get_mangadex_volumes_from_chapters(mangadex_id)
    
    if mangadex_volumes:
        print(f"   📚 MangaDex volumes from chapters: {sorted(mangadex_volumes)}")
    else:
        print(f"   ⚠️  No volume data from chapters")
    
    # Get MangaDex volumes from manga metadata
    metadata_volumes = get_mangadex_volumes_from_metadata(mangadex_id)
    
    if metadata_volumes:
        print(f"   📚 MangaDex volumes from metadata: {sorted(metadata_volumes)}")
    else:
        print(f"   ⚠️  No volume data from metadata")
    
    # Combine all volume sources
    all_mangadex_volumes = mangadex_volumes.union(metadata_volumes)
    
    if not all_mangadex_volumes:
        print(f"   ❌ No MangaDex volume data found")
        return
    
    print(f"   📚 Combined MangaDex volumes: {sorted(all_mangadex_volumes)}")
    
    # Add missing volumes
    missing_volumes = all_mangadex_volumes - current_vol_numbers
    
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
                    None
                ), commit=True)
                
                print(f"      ✅ Added Volume {vol_num}")
                
            except Exception as e:
                print(f"      ❌ Failed to add Volume {vol_num}: {e}")
    
    # Get all volumes now
    all_volumes = execute_query(
        "SELECT id, volume_number FROM volumes WHERE series_id = ? ORDER BY volume_number",
        (series_id,)
    )
    
    # Get MangaDex covers
    volume_covers = COVER_ART_MANAGER.get_mangadex_covers_for_series(mangadex_id)
    
    if volume_covers:
        print(f"   🖼️  Found {len(volume_covers)} covers")
        
        # Match and download covers
        matching_results = COVER_ART_MANAGER.match_covers_to_volumes(volume_covers, all_volumes)
        batch_results = COVER_ART_MANAGER.batch_download_covers(
            series_id, all_volumes, mangadex_id, {}
        )
        
        print(f"   📊 Cover download results: {batch_results['success_count']} successful, {len(batch_results['failed_volumes'])} failed")
        
        if batch_results['updated_volumes']:
            print(f"   ✅ Downloaded covers for:")
            for updated in batch_results['updated_volumes']:
                print(f"      Volume {updated['volume_number']}: {updated['cover_path']}")
        
        if batch_results['failed_volumes']:
            print(f"   ❌ Failed downloads:")
            for failed in batch_results['failed_volumes']:
                print(f"      Volume {failed['volume_number']}: {failed.get('error', 'Unknown error')}")
    else:
        print(f"   ❌ No covers found")

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

def get_mangadex_volumes_from_chapters(mangadex_id):
    """Get volume numbers from MangaDex chapters."""
    
    try:
        volume_numbers = set()
        offset = 0
        limit = 100
        
        while True:
            response = requests.get(
                "https://api.mangadex.org/chapter",
                params={
                    "limit": limit,
                    "offset": offset,
                    "manga": mangadex_id
                },
                timeout=10
            )
            
            if response.status_code != 200:
                break
            
            data = response.json()
            
            if 'data' not in data or not data['data']:
                break
            
            chapters = data['data']
            
            if not chapters:
                break
            
            # Extract volume numbers
            batch_volumes = set()
            for chapter in chapters:
                attributes = chapter.get('attributes', {})
                volume = attributes.get('volume')
                
                if volume:
                    try:
                        vol_num = int(volume)
                        batch_volumes.add(vol_num)
                    except ValueError:
                        pass
            
            if not batch_volumes:
                break
            
            volume_numbers.update(batch_volumes)
            
            # Check if we got all chapters
            if len(chapters) < limit:
                break
            
            offset += limit
            
            # Safety limit
            if offset > 1000:
                break
        
        return volume_numbers
        
    except Exception as e:
        return set()

def get_mangadex_volumes_from_metadata(mangadex_id):
    """Get volume numbers from MangaDex manga metadata."""
    
    try:
        response = requests.get(
            f"https://api.mangadex.org/manga/{mangadex_id}",
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            
            if 'data' in data and data['data']:
                attributes = data['data'].get('attributes', {})
                last_volume = attributes.get('lastVolume')
                
                if last_volume:
                    try:
                        last_vol_num = int(last_volume)
                        # Create a range from 1 to last_volume
                        return set(range(1, last_vol_num + 1))
                    except ValueError:
                        pass
        
    except Exception as e:
        pass
    
    return set()

if __name__ == '__main__':
    implement_complete_volume_cover_system()
