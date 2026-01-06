#!/usr/bin/env python3

import sys
sys.path.append('backend')

from backend.features.cover_art_manager import COVER_ART_MANAGER
from backend.internals.db import execute_query

def test_correct_mangadex_id():
    """Test with the correct MangaDex ID for Kaijuu No. 8."""
    
    print("🔍 Testing Correct MangaDex ID")
    print("=" * 50)
    
    # Use the correct MangaDex ID for the main series
    series_id = 4  # Kaijuu 8-gou
    correct_mangadex_id = "237d527f-adb5-420e-8e6e-b7dd006fbe47"  # Main series
    
    print(f"\n📚 Testing Kaijuu No. 8 (Main Series)")
    print(f"   Series ID: {series_id}")
    print(f"   Correct MangaDex ID: {correct_mangadex_id}")
    
    # Get volumes from database
    volumes = execute_query("SELECT id, volume_number FROM volumes WHERE series_id = ? ORDER BY volume_number", (series_id,))
    
    print(f"   📚 Found {len(volumes)} volumes in database")
    
    # Get MangaDex covers for the correct ID
    print(f"\n🖼️  Getting MangaDex covers for main series...")
    volume_covers = COVER_ART_MANAGER.get_mangadex_covers_for_series(correct_mangadex_id)
    
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
    batch_results = COVER_ART_MANAGER.batch_download_covers(
        series_id, volumes, correct_mangadex_id, {}
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
    
    # Update the database with the correct MangaDex ID
    print(f"\n🔧 Updating database with correct MangaDex ID...")
    try:
        execute_query(
            "UPDATE series SET metadata_id = ? WHERE id = ?",
            (correct_mangadex_id, series_id),
            commit=True
        )
        print(f"   ✅ Updated series {series_id} with correct MangaDex ID")
    except Exception as e:
        print(f"   ❌ Failed to update: {e}")

if __name__ == '__main__':
    test_correct_mangadex_id()
