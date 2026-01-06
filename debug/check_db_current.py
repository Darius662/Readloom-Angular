#!/usr/bin/env python3
import sqlite3
from pathlib import Path

db_path = Path('backend/data') / 'readloom.db'
conn = sqlite3.connect(str(db_path))
cursor = conn.cursor()

# Check tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [t[0] for t in cursor.fetchall()]
print('Tables in database:', tables)

# Check if volumes and chapters tables exist and have data
if 'volumes' in tables:
    cursor.execute('SELECT COUNT(*) FROM volumes')
    vol_count = cursor.fetchone()[0]
    print(f'Volumes count: {vol_count}')
    
    cursor.execute('SELECT id, series_id, volume_number, title FROM volumes LIMIT 5')
    volumes = cursor.fetchall()
    print('Sample volumes:', volumes)

if 'chapters' in tables:
    cursor.execute('SELECT COUNT(*) FROM chapters')
    chap_count = cursor.fetchone()[0]
    print(f'Chapters count: {chap_count}')
    
    cursor.execute('SELECT id, series_id, chapter_number, title FROM chapters LIMIT 5')
    chapters = cursor.fetchall()
    print('Sample chapters:', chapters)

# Check series table
if 'series' in tables:
    cursor.execute('SELECT COUNT(*) FROM series')
    series_count = cursor.fetchone()[0]
    print(f'Series count: {series_count}')
    
    cursor.execute('SELECT id, name, type, content_type FROM series LIMIT 5')
    series = cursor.fetchall()
    print('Sample series:', series)

conn.close()
