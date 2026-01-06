#!/usr/bin/env python3

import sys
sys.path.append('backend')

from backend.features.cover_art_manager import COVER_ART_MANAGER
from backend.internals.db import execute_query

def debug_volume_matching():
    """Debug why volume matching isn't working."""
    
    print("🔍 Debugging Volume Matching")
    print("=" * 50)
    
    series_id = 4  # Kaijuu 8-gou
    manga_dex_id = "237d527f-adb5-420e-8e6e-b7dd006fbe47"
    
    # Get volumes from database
    volumes = execute_query("SELECT id, volume_number FROM volumes WHERE series_id = ? ORDER BY volume_number", (series_id,))
    
    print(f"\n📚 Database volumes:")
    for vol in volumes:
        vol_num = vol['volume_number']
        extracted_num = COVER_ART_MANAGER._extract_volume_number(vol_num)
        print(f"      Volume {vol_num} -> Extracted: {extracted_num}")
    
    # Get MangaDex covers
    volume_covers = COVER_ART_MANAGER.get_mangadex_covers_for_series(manga_dex_id)
    
    print(f"\n🖼️  MangaDex covers:")
    for cover in volume_covers:
        vol_num = cover['volume']
        print(f"      Cover Volume {vol_num} (original: {cover['volume_original']})")
    
    # Test matching manually
    print(f"\n🎯 Manual matching test:")
    
    if volumes and volume_covers:
        # Create volume map
        volume_map = {}
        for volume in volumes:
            vol_num = COVER_ART_MANAGER._extract_volume_number(volume.get('volume_number', ''))
            if vol_num is not None:
                volume_map[vol_num] = volume
        
        print(f"   Volume map: {list(volume_map.keys())}")
        
        # Test each cover
        for cover in volume_covers:
            cover_volume = cover['volume']
            print(f"\n   Testing cover volume {cover_volume}:")
            print(f"      In volume_map: {cover_volume in volume_map}")
            
            if cover_volume in volume_map:
                print(f"      ✅ Exact match found!")
                matched_volume = volume_map[cover_volume]
                print(f"      Matched to: Volume {matched_volume['volume_number']} (ID: {matched_volume['id']})")
            else:
                print(f"      ❌ No exact match")
                
                # Try fuzzy matching
                closest_volume = None
                closest_diff = float('inf')
                
                for vol_num, volume in volume_map.items():
                    diff = abs(vol_num - cover_volume)
                    print(f"      Comparing with {vol_num}: diff = {diff}")
                    
                    if diff < closest_diff and diff <= 1:
                        closest_diff = diff
                        closest_volume = volume
                
                if closest_volume:
                    print(f"      ✅ Fuzzy match: Volume {closest_volume['volume_number']} (diff: {closest_diff})")
                else:
                    print(f"      ❌ No fuzzy match found")
    
    # Let's also check if we can get more covers by looking at the MangaDex chapters
    print(f"\n" + "="*50)
    print(f"🔍 Checking MangaDex chapters for more cover info...")
    
    try:
        import requests
        
        chapters_response = requests.get(
            f"https://api.mangadex.org/manga/{manga_dex_id}/chapter",
            params={"limit": 100},
            timeout=10
        )
        
        if chapters_response.status_code == 200:
            chapters_data = chapters_response.json()
            
            if 'data' in chapters_data and chapters_data['data']:
                chapters = chapters_data['data']
                
                # Extract volume numbers from chapters
                volume_numbers = set()
                for chapter in chapters:
                    attributes = chapter.get('attributes', {})
                    volume = attributes.get('volume')
                    if volume:
                        try:
                            vol_num = int(volume)
                            volume_numbers.add(vol_num)
                        except ValueError:
                            pass
                
                print(f"   📚 Found {len(chapters)} chapters")
                print(f"   📚 Volumes mentioned in chapters: {sorted(volume_numbers)}")
                
                # Compare with database volumes
                db_volumes = {COVER_ART_MANAGER._extract_volume_number(vol.get('volume_number', '')) for vol in volumes}
                db_volumes.discard(None)
                
                print(f"   📚 Database volumes: {sorted(db_volumes)}")
                
                # Find missing volumes
                missing_volumes = volume_numbers - db_volumes
                if missing_volumes:
                    print(f"   ❌ Volumes in chapters but not in database: {sorted(missing_volumes)}")
                
                extra_volumes = db_volumes - volume_numbers
                if extra_volumes:
                    print(f"   ❌ Volumes in database but not in chapters: {sorted(extra_volumes)}")
                
        else:
            print(f"   ❌ Failed to get chapters: {chapters_response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Error checking chapters: {e}")

if __name__ == '__main__':
    debug_volume_matching()
