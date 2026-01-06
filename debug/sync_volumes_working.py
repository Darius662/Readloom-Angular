#!/usr/bin/env python3

import sys
sys.path.append('backend')

import requests
from backend.internals.db import execute_query

def sync_volumes_working():
    """Sync volume data using the working MangaDex chapter API."""
    
    print("🔍 Syncing Volumes with Working API")
    print("=" * 50)
    
    # Get Kaijuu No. 8
    series_id = 4
    manga_dex_id = "237d527f-adb5-420e-8e6e-b7dd006fbe47"
    
    print(f"\n📚 Processing Kaijuu No. 8")
    print(f"   MangaDex ID: {manga_dex_id}")
    
    # Get current volumes in database
    current_volumes = execute_query(
        "SELECT id, volume_number FROM volumes WHERE series_id = ? ORDER BY volume_number",
        (series_id,)
    )
    
    current_vol_numbers = {v['volume_number'] for v in current_volumes}
    print(f"   📚 Current volumes: {sorted(current_vol_numbers)}")
    
    # Get all volumes from MangaDex chapters
    mangadex_volumes = get_all_mangadex_volumes(manga_dex_id)
    
    if not mangadex_volumes:
        print(f"   ❌ No volume data found")
        return
    
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
    
    # Test cover download with the updated volumes
    print(f"\n🚀 Testing cover download with updated volumes...")
    
    # Get all volumes now
    all_volumes = execute_query(
        "SELECT id, volume_number FROM volumes WHERE series_id = ? ORDER BY volume_number",
        (series_id,)
    )
    
    from backend.features.cover_art_manager import COVER_ART_MANAGER
    
    # Get MangaDex covers
    volume_covers = COVER_ART_MANAGER.get_mangadex_covers_for_series(manga_dex_id)
    
    if volume_covers:
        print(f"   🖼️  Found {len(volume_covers)} covers")
        
        # Match and download
        matching_results = COVER_ART_MANAGER.match_covers_to_volumes(volume_covers, all_volumes)
        batch_results = COVER_ART_MANAGER.batch_download_covers(
            series_id, all_volumes, manga_dex_id, {}
        )
        
        print(f"   📊 Results: {batch_results['success_count']} successful, {len(batch_results['failed_volumes'])} failed")
        
        if batch_results['updated_volumes']:
            print(f"   ✅ Downloaded covers for:")
            for updated in batch_results['updated_volumes']:
                print(f"      Volume {updated['volume_number']}: {updated['cover_path']}")
    else:
        print(f"   ❌ No covers found")

def get_all_mangadex_volumes(mangadex_id):
    """Get all volume numbers from MangaDex using the chapter API."""
    
    try:
        volume_numbers = set()
        offset = 0
        limit = 100
        
        while True:
            # Get chapters with offset for pagination
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
                print(f"   ❌ Failed to get chapters: {response.status_code}")
                break
            
            data = response.json()
            
            if 'data' not in data or not data['data']:
                break
            
            chapters = data['data']
            
            if not chapters:
                break
            
            # Extract volume numbers from this batch
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
                # No more volumes found in this batch
                break
            
            volume_numbers.update(batch_volumes)
            print(f"   📚 Batch {offset//limit + 1}: Found volumes {sorted(batch_volumes)}")
            
            # Check if we got all chapters
            total_found = len(chapters)
            if total_found < limit:
                break
            
            offset += limit
            
            # Safety limit
            if offset > 1000:
                print(f"   ⚠️  Reached safety limit, stopping")
                break
        
        return volume_numbers
        
    except Exception as e:
        print(f"   ❌ Error getting MangaDex volumes: {e}")
        return set()

if __name__ == '__main__':
    sync_volumes_working()
