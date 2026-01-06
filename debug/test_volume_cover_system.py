#!/usr/bin/env python3

import sys
sys.path.append('backend')

from backend.features.cover_art_manager import COVER_ART_MANAGER
from backend.internals.db import execute_query

def test_volume_cover_system():
    """Test the new volume cover system with smart matching."""
    
    print("🔍 Testing Volume Cover System")
    print("=" * 50)
    
    # Test with Kaijuu No. 8 (should work)
    series_id = 4  # Kaijuu 8-gou
    manga_dex_id = "71763dfb-8b85-4a74-92df-dfe46478fc5d"
    
    print(f"\n📚 Testing Kaijuu No. 8 (Series ID: {series_id})")
    print(f"   MangaDex ID: {manga_dex_id}")
    
    # Get volumes from database
    volumes = execute_query("SELECT id, volume_number FROM volumes WHERE series_id = ? ORDER BY volume_number", (series_id,))
    
    if not volumes:
        print(f"   ❌ No volumes found for series {series_id}")
        return
    
    print(f"   📚 Found {len(volumes)} volumes in database:")
    for vol in volumes:
        print(f"      Volume {vol['volume_number']} (ID: {vol['id']})")
    
    # Get MangaDex covers
    print(f"\n🖼️  Getting MangaDex covers...")
    volume_covers = COVER_ART_MANAGER.get_mangadex_covers_for_series(manga_dex_id)
    
    if not volume_covers:
        print(f"   ❌ No covers found on MangaDex")
        return
    
    print(f"   ✅ Found {len(volume_covers)} covers on MangaDex:")
    for cover in volume_covers:
        print(f"      Volume {cover['volume']} - {cover['filename']}")
    
    # Match covers to volumes
    print(f"\n🎯 Matching covers to volumes...")
    matching_results = COVER_ART_MANAGER.match_covers_to_volumes(volume_covers, volumes)
    
    print(f"   📊 Matching Results:")
    print(f"      ✅ Matched: {len(matching_results['matched'])}")
    print(f"      ❌ Unmatched covers: {len(matching_results['unmatched_covers'])}")
    print(f"      ❌ Unmatched volumes: {len(matching_results['unmatched_volumes'])}")
    
    # Show matched pairs
    if matching_results['matched']:
        print(f"\n🎯 Matched pairs:")
        for match in matching_results['matched']:
            volume = match['volume']
            cover = match['cover']
            match_type = match['match_type']
            difference = match.get('difference', 0)
            
            print(f"      Volume {volume['volume_number']} ↔ Cover {cover['volume']} ({match_type})")
            if difference:
                print(f"         (Difference: {difference})")
    
    # Test batch download
    print(f"\n🚀 Testing batch download...")
    cover_data = {}  # Empty since we're using smart matching
    
    batch_results = COVER_ART_MANAGER.batch_download_covers(
        series_id, volumes, manga_dex_id, cover_data
    )
    
    print(f"   📊 Batch Download Results:")
    print(f"      ✅ Success: {batch_results['success_count']}")
    print(f"      ❌ Failed: {len(batch_results['failed_volumes'])}")
    
    if batch_results['updated_volumes']:
        print(f"\n✅ Successfully downloaded covers:")
        for updated in batch_results['updated_volumes']:
            print(f"      Volume {updated['volume_number']}: {updated['cover_path']}")
    
    if batch_results['failed_volumes']:
        print(f"\n❌ Failed downloads:")
        for failed in batch_results['failed_volumes']:
            print(f"      Volume {failed['volume_number']}: {failed.get('error', 'Unknown error')}")
    
    # Test with Attack on Titan
    print(f"\n" + "="*50)
    print(f"📚 Testing Attack on Titan (Shingeki no Kyojin)")
    
    series_id = 5  # Shingeki no Kyojin
    manga_dex_id = "84aecfbd-e5aa-40a5-ae28-8ef49ea6e43f"
    
    print(f"   Series ID: {series_id}")
    print(f"   MangaDex ID: {manga_dex_id}")
    
    # Get volumes
    volumes = execute_query("SELECT id, volume_number FROM volumes WHERE series_id = ? ORDER BY volume_number", (series_id,))
    
    if volumes:
        print(f"   📚 Found {len(volumes)} volumes")
        
        # Get covers
        volume_covers = COVER_ART_MANAGER.get_mangadex_covers_for_series(manga_dex_id)
        
        if volume_covers:
            print(f"   🖼️  Found {len(volume_covers)} covers")
            
            # Match and download
            matching_results = COVER_ART_MANAGER.match_covers_to_volumes(volume_covers, volumes)
            batch_results = COVER_ART_MANAGER.batch_download_covers(
                series_id, volumes, manga_dex_id, {}
            )
            
            print(f"   📊 Results: {batch_results['success_count']} successful, {len(batch_results['failed_volumes'])} failed")
        else:
            print(f"   ❌ No covers found")
    else:
        print(f"   ❌ No volumes found")

if __name__ == '__main__':
    test_volume_cover_system()
