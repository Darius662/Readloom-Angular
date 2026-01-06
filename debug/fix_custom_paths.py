#!/usr/bin/env python3

import sys
sys.path.append('backend')

from backend.internals.db import execute_query
from pathlib import Path

def fix_custom_paths():
    """Fix custom paths for series that don't have them."""
    
    print("🔧 Fixing Custom Paths")
    print("=" * 40)
    
    # Define the base manga folder
    manga_base = Path("C:/Users/dariu/Desktop/Readloom-TEST/Manga")
    
    # Get series without custom paths
    series = execute_query("SELECT id, title FROM series WHERE custom_path IS NULL")
    
    print(f"\n📚 Found {len(series)} series without custom paths:")
    
    for s in series:
        series_id = s['id']
        series_title = s['title']
        
        # Try to find the folder
        series_folder = manga_base / series_title
        
        if series_folder.exists():
            # Update the database
            execute_query(
                "UPDATE series SET custom_path = ? WHERE id = ?",
                (str(series_folder), series_id),
                commit=True
            )
            print(f"✅ Updated {series_title} (ID: {series_id}) -> {series_folder}")
        else:
            print(f"❌ Folder not found for {series_title}: {series_folder}")
    
    # Show updated series
    print(f"\n📊 Updated series:")
    updated_series = execute_query("SELECT id, title, custom_path FROM series")
    for s in updated_series:
        print(f"ID: {s['id']}, Title: {s['title']}, Path: {s['custom_path']}")

def remove_duplicate_volumes():
    """Remove duplicate volume entries."""
    
    print(f"\n🧹 Removing Duplicate Volumes")
    print("=" * 40)
    
    # Find duplicate volumes
    duplicates = execute_query("""
        SELECT series_id, volume_number, COUNT(*) as count
        FROM volumes 
        GROUP BY series_id, volume_number 
        HAVING COUNT(*) > 1
    """)
    
    if not duplicates:
        print("✅ No duplicate volumes found")
        return
    
    print(f"📊 Found {len(duplicates)} duplicate volume groups:")
    
    for dup in duplicates:
        series_id = dup['series_id']
        volume_number = dup['volume_number']
        count = dup['count']
        
        print(f"   Series {series_id}, Volume {volume_number}: {count} duplicates")
        
        # Get all volumes for this series/volume
        all_volumes = execute_query("""
            SELECT id, created_at 
            FROM volumes 
            WHERE series_id = ? AND volume_number = ?
            ORDER BY created_at DESC
        """, (series_id, volume_number))
        
        if len(all_volumes) > 1:
            # Keep the newest one, delete the rest
            volumes_to_delete = all_volumes[1:]
            
            for vol in volumes_to_delete:
                volume_id = vol['id']
                execute_query("DELETE FROM volumes WHERE id = ?", (volume_id,), commit=True)
                print(f"      ❌ Deleted volume ID {volume_id}")
            
            print(f"      ✅ Kept newest volume ID {all_volumes[0]['id']}")

if __name__ == '__main__':
    fix_custom_paths()
    remove_duplicate_volumes()
