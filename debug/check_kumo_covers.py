#!/usr/bin/env python3

import sys
sys.path.append('backend')

from backend.internals.db import execute_query

def check_kumo_covers():
    """Check if MangaDex covers were downloaded for Kumo desu ga, Nani ka?"""
    
    print("🔍 Checking Kumo desu ga, Nani ka? Covers")
    print("=" * 50)
    
    # Get the series ID for Kumo desu ga, Nani ka?
    series = execute_query('SELECT id, title, metadata_id FROM series WHERE title LIKE "%Spider%"')
    
    if not series:
        # Try other search terms
        series = execute_query('SELECT id, title, metadata_id FROM series WHERE title LIKE "%Kumo%"')
    
    if series:
        series_id = series[0]['id']
        series_title = series[0]['title']
        metadata_id = series[0]['metadata_id']
        
        print(f"✅ Found series: {series_title}")
        print(f"   Series ID: {series_id}")
        print(f"   Metadata ID: {metadata_id}")
        
        # Check volumes with covers
        volumes = execute_query(
            'SELECT id, volume_number, cover_path, cover_url FROM volumes WHERE series_id = ? ORDER BY volume_number', 
            (series_id,)
        )
        
        print(f"\n📚 Volumes ({len(volumes)} total):")
        
        covers_found = 0
        volume_16_cover = None
        
        for vol in volumes:
            vol_id = vol['id']
            vol_num = vol['volume_number']
            cover_path = vol['cover_path']
            cover_url = vol['cover_url']
            
            if cover_path or cover_url:
                covers_found += 1
                print(f"  Volume {vol_num}: ✅ Has cover")
                if cover_path:
                    print(f"    Path: {cover_path}")
                if cover_url:
                    print(f"    URL: {cover_url}")
                
                if vol_num == '16':
                    volume_16_cover = {'path': cover_path, 'url': cover_url}
            else:
                if vol_num == '16':
                    print(f"  Volume {vol_num}: ❌ No cover (expected one here)")
                else:
                    print(f"  Volume {vol_num}: - No cover (normal)")
        
        print(f"\n📊 Summary: {covers_found} volumes have covers")
        
        # Check if cover files actually exist
        if volume_16_cover and volume_16_cover['path']:
            print(f"\n🖼️  Checking Volume 16 cover file...")
            from pathlib import Path
            
            cover_file = Path(volume_16_cover['path'])
            if cover_file.exists():
                file_size = cover_file.stat().st_size
                print(f"   ✅ Cover file exists!")
                print(f"   📁 Path: {cover_file}")
                print(f"   📏 Size: {file_size:,} bytes ({file_size/1024:.1f} KB)")
                
                # Check if it's in the right folder structure
                if 'cover_art' in str(cover_file):
                    print(f"   ✅ Stored in correct cover_art folder")
                else:
                    print(f"   ⚠️  Not in cover_art folder")
            else:
                print(f"   ❌ Cover file does not exist!")
        
        # Check the series folder structure
        print(f"\n📁 Checking series folder structure...")
        execute_query('SELECT custom_path FROM series WHERE id = ?', (series_id,))
        series_path_result = execute_query('SELECT custom_path FROM series WHERE id = ?', (series_id,))
        
        if series_path_result and series_path_result[0]['custom_path']:
            custom_path = series_path_result[0]['custom_path']
            print(f"   📂 Series folder: {custom_path}")
            
            from pathlib import Path
            series_folder = Path(custom_path)
            if series_folder.exists():
                print(f"   ✅ Series folder exists")
                
                cover_art_folder = series_folder / 'cover_art'
                if cover_art_folder.exists():
                    print(f"   ✅ cover_art folder exists")
                    
                    # List files in cover_art folder
                    cover_files = list(cover_art_folder.glob('*'))
                    print(f"   📁 Files in cover_art: {len(cover_files)}")
                    for cover_file in cover_files:
                        print(f"      🖼️  {cover_file.name}")
                else:
                    print(f"   ❌ cover_art folder does not exist")
            else:
                print(f"   ❌ Series folder does not exist")
        else:
            print(f"   ⚠️  No custom_path set for series")
        
        # Final assessment
        print(f"\n🎯 Final Assessment:")
        if covers_found > 0:
            print(f"   ✅ MangaDex cover download system WORKED!")
            print(f"   ✅ {covers_found} covers successfully downloaded")
            print(f"   ✅ Integration successful!")
        else:
            print(f"   ❌ No covers downloaded")
            print(f"   ⚠️  Check the backend logs for cover download attempts")
            print(f"   ⚠️  The MangaDex translation might have failed")
        
    else:
        print("❌ Series not found")
        print("   ⚠️  Try searching for different title variations")

if __name__ == '__main__':
    check_kumo_covers()
