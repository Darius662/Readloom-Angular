#!/usr/bin/env python3
from backend.internals.db import execute_query

# Check recent series
series = execute_query('SELECT id, title, content_type FROM series ORDER BY id DESC LIMIT 10')
print('Recent series:')
for s in series:
    print(f'  {s["id"]}. {s["title"]} ({s["content_type"]})')

# Check ebook files
files = execute_query('SELECT id, series_id, file_name FROM ebook_files ORDER BY id DESC LIMIT 10')
print(f'\nRecent ebook files ({len(files)} total):')
for f in files:
    print(f'  {f["id"]}. Series {f["series_id"]}: {f["file_name"]}')

# Check volumes
volumes = execute_query('SELECT id, series_id, volume_number FROM volumes ORDER BY id DESC LIMIT 10')
print(f'\nRecent volumes ({len(volumes)} total):')
for v in volumes:
    print(f'  {v["id"]}. Series {v["series_id"]}: Volume {v["volume_number"]}')
