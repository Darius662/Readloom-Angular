#!/usr/bin/env python3

import sys
sys.path.append('backend')

def debug_series_creation():
    """Debug what went wrong with the Kumo desu ga, Nani ka? series creation."""
    
    print("🔍 Debugging Series Creation Issues")
    print("=" * 50)
    
    from backend.internals.db import execute_query
    
    # Check the series details
    series = execute_query('SELECT * FROM series WHERE id = 6')
    
    if series:
        s = series[0]
        print(f"📚 Series Details:")
        print(f"   ID: {s['id']}")
        print(f"   Title: {s['title']}")
        print(f"   Content Type: {s['content_type']}")
        print(f"   Metadata Source: {s['metadata_source']}")
        print(f"   Metadata ID: {s['metadata_id']}")
        print(f"   Custom Path: {s['custom_path']}")
        print(f"   Created At: {s['created_at']}")
        
        # The metadata_id should be the MangaDex ID, but it's the side story ID
        print(f"\n⚠️  Issue Found:")
        print(f"   Expected MangaDex ID: 5283351f-a4e3-4699-af58-021864b5e062 (main series)")
        print(f"   Actual Metadata ID: {s['metadata_id']} (side story)")
        
        # Check if we can fix it
        print(f"\n🔧 Attempting to fix...")
        
        # Update with correct MangaDex ID
        correct_mangadex_id = "5283351f-a4e3-4699-af58-021864b5e062"
        execute_query(
            "UPDATE series SET metadata_id = ? WHERE id = ?",
            (correct_mangadex_id, 6),
            commit=True
        )
        print(f"   ✅ Updated series with correct MangaDex ID")
        
        # Create the missing volumes (should be 16, we have 6)
        current_volumes = execute_query("SELECT volume_number FROM volumes WHERE series_id = ?", (6,))
        current_vol_numbers = {v['volume_number'] for v in current_volumes}
        
        print(f"   Current volumes: {sorted(current_vol_numbers)}")
        
        # Add missing volumes 7-16
        missing_volumes = [str(i) for i in range(7, 17) if str(i) not in current_vol_numbers]
        
        if missing_volumes:
            print(f"   Adding missing volumes: {missing_volumes}")
            
            for vol_num in missing_volumes:
                execute_query("""
                    INSERT INTO volumes (
                        series_id, volume_number, title, release_date, 
                        created_at, updated_at
                    ) VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                """, (
                    6,
                    vol_num,
                    f"Volume {vol_num}",
                    None
                ), commit=True)
                print(f"      ✅ Added Volume {vol_num}")
        
        # Set up the custom path
        from pathlib import Path
        manga_base = Path("C:/Users/dariu/Desktop/Readloom-TEST/Manga")
        # Use a safe filename for Windows
        safe_title = "Kumo desu ga Nani ka"
        series_folder = manga_base / safe_title
        
        if not series_folder.exists():
            series_folder.mkdir(parents=True, exist_ok=True)
            print(f"   ✅ Created series folder: {series_folder}")
        
        # Create cover_art folder
        cover_art_folder = series_folder / "cover_art"
        if not cover_art_folder.exists():
            cover_art_folder.mkdir(parents=True, exist_ok=True)
            print(f"   ✅ Created cover_art folder")
        
        # Update series with custom path
        execute_query(
            "UPDATE series SET custom_path = ? WHERE id = ?",
            (str(series_folder), 6),
            commit=True
        )
        print(f"   ✅ Updated series custom path")
        
        # Now try to download covers
        print(f"\n🚀 Attempting to download covers...")
        
        from backend.features.cover_art_manager import COVER_ART_MANAGER
        
        # Get MangaDex covers
        volume_covers = COVER_ART_MANAGER.get_mangadex_covers_for_series(correct_mangadex_id)
        
        if volume_covers:
            print(f"   ✅ Found {len(volume_covers)} covers on MangaDex")
            
            # Get all volumes
            all_volumes = execute_query(
                "SELECT id, volume_number FROM volumes WHERE series_id = ? ORDER BY volume_number",
                (6,)
            )
            
            # Match and download
            matching_results = COVER_ART_MANAGER.match_covers_to_volumes(volume_covers, all_volumes)
            
            print(f"   📊 Matching: {len(matching_results['matched'])} matched")
            
            # Download covers
            covers_downloaded = 0
            for match in matching_results['matched']:
                volume = match['volume']
                cover = match['cover']
                
                try:
                    cover_path = COVER_ART_MANAGER.save_volume_cover(
                        6, volume['id'], volume['volume_number'], correct_mangadex_id, cover['filename']
                    )
                    
                    if cover_path:
                        covers_downloaded += 1
                        print(f"      ✅ Downloaded Volume {volume['volume_number']}: {cover_path}")
                        
                        # Update volume
                        cover_url = f"https://uploads.mangadex.org/covers/{correct_mangadex_id}/{cover['filename']}"
                        execute_query(
                            "UPDATE volumes SET cover_url = ?, cover_path = ? WHERE id = ?",
                            (cover_url, cover_path, volume['id']),
                            commit=True
                        )
                except Exception as e:
                    print(f"      ❌ Failed Volume {volume['volume_number']}: {e}")
            
            print(f"   🎯 Downloaded {covers_downloaded} covers")
        else:
            print(f"   ❌ No covers found on MangaDex")
        
        # Final check
        print(f"\n📊 Final Status:")
        final_volumes = execute_query("SELECT COUNT(*) as count FROM volumes WHERE series_id = ?", (6,))
        covers_with_paths = execute_query("SELECT COUNT(*) as count FROM volumes WHERE series_id = ? AND cover_path IS NOT NULL", (6,))
        
        print(f"   Total volumes: {final_volumes[0]['count']}")
        print(f"   Volumes with covers: {covers_with_paths[0]['count']}")
        
        if covers_with_paths[0]['count'] > 0:
            print(f"   🎉 SUCCESS! The MangaDex cover system is working!")
        else:
            print(f"   ⚠️  Still having issues with cover downloads")

if __name__ == '__main__':
    debug_series_creation()
