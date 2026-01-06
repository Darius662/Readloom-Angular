#!/usr/bin/env python3

import sys
sys.path.append('backend')

from backend.internals.db import execute_query

# Update a volume with a MangaDex cover URL
execute_query('UPDATE volumes SET cover_url = ? WHERE id = 1', 
               ('https://uploads.mangadex.org/covers/5e6fc7ba-5af9-4f74-b439-9c487b6f635b/68182cd6-582e-47b3-87c2-233daa79475e.jpg',), 
               commit=True)
print('Updated volume 1 with cover URL')

# Check the update
volumes = execute_query('SELECT id, volume_number, cover_url, cover_path FROM volumes WHERE id = 1')
for v in volumes:
    print(f'Volume {v["volume_number"]}: Cover URL = {v["cover_url"]}, Cover Path = {v["cover_path"]}')
