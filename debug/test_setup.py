#!/usr/bin/env python3

import sys
sys.path.append('backend')

from backend.internals.db import execute_query

def setup_test_series():
    """Set up a test series with Code Geass to demonstrate cover system."""
    
    # Insert Code Geass series with custom path
    execute_query("""
        INSERT INTO series (
            title, content_type, metadata_source, metadata_id, 
            author, publisher, status, description, custom_path,
            in_library, created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
    """, (
        "Code Geass: Hangyaku no Lelouch",
        "MANGA", 
        "AniList",
        "31528",
        "Goro Taniguchi",
        "Bandai Visual",
        "completed",
        "The Holy Empire of Britannia has conquered Japan and renamed it Area 11. A young Britannian named Lelouch Lamperouge gains the power of Geass and leads a rebellion against the empire.",
        "C:\\Users\\dariu\\Desktop\\Readloom-TEST\\Manga\\Code Geass_ Hangyaku no Lelouch",
        1
    ), commit=True)
    
    # Get the series ID
    result = execute_query("SELECT last_insert_rowid() as id")
    series_id = result[0]['id']
    
    print(f"Created test series with ID: {series_id}")
    
    # Add a test volume
    execute_query("""
        INSERT INTO volumes (
            series_id, volume_number, title, release_date, 
            cover_url, created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
    """, (
        series_id,
        "1",
        "Volume 1",
        "2006-10-26",
        "https://uploads.mangadex.org/covers/31528/cover_filename.jpg"
    ), commit=True)
    
    # Get the volume ID
    result = execute_query("SELECT last_insert_rowid() as id")
    volume_id = result[0]['id']
    
    print(f"Created test volume with ID: {volume_id}")
    
    # Show the data
    print("\nSeries data:")
    series = execute_query("SELECT * FROM series WHERE id = ?", (series_id,))
    for s in series:
        print(f"  Title: {s['title']}")
        print(f"  Custom Path: {s['custom_path']}")
        print(f"  Metadata ID: {s['metadata_id']}")
    
    print("\nVolume data:")
    volumes = execute_query("SELECT * FROM volumes WHERE series_id = ?", (series_id,))
    for v in volumes:
        print(f"  Volume: {v['volume_number']}")
        print(f"  Cover URL: {v['cover_url']}")
        print(f"  Cover Path: {v['cover_path']}")

if __name__ == '__main__':
    setup_test_series()
