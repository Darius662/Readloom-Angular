#!/usr/bin/env python3

import sys
sys.path.append('backend')

import requests
from backend.internals.db import execute_query
from backend.features.cover_art_manager import COVER_ART_MANAGER
from backend.base.logging import LOGGER

def download_mangadex_covers_for_existing_volumes():
    """Download MangaDex covers for all existing volumes in the database."""
    
    print("🔍 Downloading MangaDex Covers for Existing Volumes")
    print("=" * 60)
    
    # Get all series with AniList metadata
    series = execute_query("""
        SELECT id, title, metadata_source, metadata_id, custom_path
        FROM series 
        WHERE metadata_source = 'AniList' AND metadata_id IS NOT NULL
        ORDER BY title
    """)
    
    total_series = len(series)
    processed_series = 0
    total_covers_downloaded = 0
    
    print(f"\n📚 Found {total_series} series to process")
    
    for s in series:
        series_id = s['id']
        series_title = s['title']
        anilist_id = s['metadata_id']
        custom_path = s['custom_path']
        
        processed_series += 1
        print(f"\n📚 [{processed_series}/{total_series}] Processing: {series_title}")
        print(f"   Series ID: {series_id}")
        print(f"   AniList ID: {anilist_id}")
        print(f"   Custom Path: {custom_path}")
        
        # Find MangaDex equivalent
        mangadex_id = find_mangadex_equivalent(anilist_id, series_title)
        
        if not mangadex_id:
            print(f"   ❌ No MangaDex equivalent found")
            continue
        
        print(f"   ✅ MangaDex ID: {mangadex_id}")
        
        # Update series with MangaDex ID for future reference
        execute_query(
            "UPDATE series SET metadata_id = ? WHERE id = ?",
            (mangadex_id, series_id),
            commit=True
        )
        
        # Get all volumes for this series
        volumes = execute_query(
            "SELECT id, volume_number, cover_url, cover_path FROM volumes WHERE series_id = ? ORDER BY volume_number",
            (series_id,)
        )
        
        if not volumes:
            print(f"   ❌ No volumes found for series {series_id}")
            continue
        
        print(f"   📚 Found {len(volumes)} volumes")
        
        # Get MangaDex covers
        volume_covers = COVER_ART_MANAGER.get_mangadex_covers_for_series(mangadex_id)
        
        if not volume_covers:
            print(f"   ❌ No covers found on MangaDex")
            continue
        
        print(f"   🖼️  Found {len(volume_covers)} covers on MangaDex:")
        for cover in volume_covers:
            print(f"      Volume {cover['volume']}: {cover['filename']}")
        
        # Match and download covers
        matching_results = COVER_ART_MANAGER.match_covers_to_volumes(volume_covers, volumes)
        
        print(f"   📊 Matching Results:")
        print(f"      ✅ Matched: {len(matching_results['matched'])}")
        print(f"      ❌ Unmatched covers: {len(matching_results['unmatched_covers'])}")
        print(f"      ❌ Unmatched volumes: {len(matching_results['unmatched_volumes'])}")
        
        # Download matched covers
        if matching_results['matched']:
            print(f"   🚀 Downloading covers...")
            
            for match in matching_results['matched']:
                volume = match['volume']
                cover = match['cover']
                
                volume_id = volume.get('id')
                volume_number = volume.get('volume_number')
                cover_filename = cover['filename']
                match_type = match['match_type']
                
                print(f"      📦 Volume {volume_number} ↔ Cover {cover['volume']} ({match_type})")
                
                try:
                    cover_path = COVER_ART_MANAGER.save_volume_cover(
                        series_id, volume_id, volume_number, mangadex_id, cover_filename
                    )
                    
                    if cover_path:
                        total_covers_downloaded += 1
                        print(f"         ✅ Downloaded: {cover_path}")
                        
                        # Update volume with cover URL
                        cover_url = f"https://uploads.mangadex.org/covers/{mangadex_id}/{cover_filename}"
                        execute_query(
                            "UPDATE volumes SET cover_url = ?, cover_path = ? WHERE id = ?",
                            (cover_url, cover_path, volume_id),
                            commit=True
                        )
                    else:
                        print(f"         ❌ Download failed")
                        
                except Exception as e:
                    print(f"         ❌ Error: {e}")
        
        # Show unmatched volumes
        if matching_results['unmatched_volumes']:
            print(f"   ⚠️  Unmatched volumes (no covers available):")
            for volume in matching_results['unmatched_volumes']:
                print(f"      Volume {volume['volume_number']}")
    
    print(f"\n🎉 SUMMARY:")
    print(f"   📚 Series processed: {processed_series}/{total_series}")
    print(f"   🖼️  Total covers downloaded: {total_covers_downloaded}")
    print(f"   ✅ Cover download process complete!")

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
            LOGGER.warning(f"Search error for '{term}': {e}")
    
    return None

def test_cover_api():
    """Test if the cover API is working for downloaded covers."""
    
    print("\n🌐 Testing Cover API...")
    
    # Get volumes with cover paths
    volumes_with_covers = execute_query("""
        SELECT v.id, v.volume_number, v.cover_path, s.title as series_title
        FROM volumes v
        JOIN series s ON v.series_id = s.id
        WHERE v.cover_path IS NOT NULL AND v.cover_path != ''
        ORDER BY s.title, v.volume_number
        LIMIT 10
    """)
    
    if not volumes_with_covers:
        print("   ❌ No volumes with covers found")
        return
    
    print(f"   📚 Testing {len(volumes_with_covers)} volumes:")
    
    import requests
    
    for volume in volumes_with_covers:
        volume_id = volume['id']
        volume_number = volume['volume_number']
        series_title = volume['series_title']
        cover_path = volume['cover_path']
        
        try:
            api_url = f"http://localhost:7227/api/cover-art/volume/{volume_id}"
            response = requests.head(api_url, timeout=5)
            
            if response.status_code == 200:
                print(f"      ✅ {series_title} Vol {volume_number}: API working")
            else:
                print(f"      ❌ {series_title} Vol {volume_number}: API returned {response.status_code}")
        except Exception as e:
            print(f"      ❌ {series_title} Vol {volume_number}: API error - {e}")

if __name__ == '__main__':
    download_mangadex_covers_for_existing_volumes()
    test_cover_api()
