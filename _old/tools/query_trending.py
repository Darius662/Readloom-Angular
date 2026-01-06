#!/usr/bin/env python3
from backend.internals.db import execute_query

result = execute_query('SELECT * FROM trending_manga')
print(f'Total entries: {len(result)}\n')

for i, r in enumerate(result, 1):
    print(f'{i}. {r["title"]}')
    print(f'   AniList ID: {r["anilist_id"]}')
    print(f'   Trending Score: {r["trending_score"]}')
    print(f'   Popularity: {r["popularity"]}')
    print(f'   Cover URL: {r["cover_url"][:50]}...' if r["cover_url"] else '   Cover URL: None')
    print()
