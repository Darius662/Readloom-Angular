#!/usr/bin/env python3

import sys
sys.path.append('backend')

from backend.internals.db import execute_query

def check_series():
    # First check table structure
    print('Series table structure:')
    try:
        structure = execute_query('PRAGMA table_info(series)')
        for col in structure:
            print(f'  {col["name"]}: {col["type"]}')
    except Exception as e:
        print(f'Error getting structure: {e}')
    
    print('\nSeries in database:')
    try:
        series = execute_query('SELECT * FROM series')
        for s in series:
            print(f'ID: {s["id"]}, Title: {s.get("title", "N/A")}, Source: {s.get("metadata_source", "N/A")}, ID: {s.get("metadata_id", "N/A")}, Custom Path: {s.get("custom_path", "N/A")}')
    except Exception as e:
        print(f'Error getting series: {e}')
    
    print('\nVolumes in database:')
    try:
        volumes = execute_query('SELECT id, series_id, volume_number, cover_url, cover_path FROM volumes LIMIT 10')
        for v in volumes:
            print(f'Volume ID: {v["id"]}, Series ID: {v["series_id"]}, Number: {v["volume_number"]}, Cover URL: {v.get("cover_url", "None")}, Cover Path: {v.get("cover_path", "None")}')
    except Exception as e:
        print(f'Error getting volumes: {e}')

if __name__ == '__main__':
    check_series()
