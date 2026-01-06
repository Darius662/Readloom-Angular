#!/usr/bin/env python3

import sys
sys.path.append('backend')

from backend.internals.db import execute_query

def check_database_fields():
    """Check what cover fields are actually in the database."""
    
    print("🔍 Checking Database Cover Fields")
    print("=" * 40)
    
    # Check what's actually in the database
    volumes = execute_query('SELECT id, volume_number, cover_url, cover_path FROM volumes WHERE series_id = 6 ORDER BY volume_number LIMIT 3')
    print('Database volumes:')
    for vol in volumes:
        print(f'  Volume {vol["volume_number"]}: cover_url={vol["cover_url"]}, cover_path={vol["cover_path"]}')
    
    # Check if cover_path is populated for volumes with covers
    volumes_with_covers = execute_query('SELECT COUNT(*) as count FROM volumes WHERE series_id = 6 AND cover_path IS NOT NULL AND cover_path != ""')
    print(f'\nVolumes with cover_path: {volumes_with_covers[0]["count"]}')
    
    # Check if cover_url is populated
    volumes_with_url = execute_query('SELECT COUNT(*) as count FROM volumes WHERE series_id = 6 AND cover_url IS NOT NULL AND cover_url != ""')
    print(f'Volumes with cover_url: {volumes_with_url[0]["count"]}')

if __name__ == '__main__':
    check_database_fields()
