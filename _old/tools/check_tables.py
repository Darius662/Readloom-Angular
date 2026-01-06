#!/usr/bin/env python3
from backend.internals.db import execute_query

tables = execute_query("SELECT name FROM sqlite_master WHERE type='table'")
print("Tables in database:")
for t in tables:
    print(f"  - {t['name']}")

# Check if trending_manga table exists
if any(t['name'] == 'trending_manga' for t in tables):
    print("\n✓ trending_manga table EXISTS")
    trending = execute_query("SELECT * FROM trending_manga")
    print(f"  Entries: {len(trending)}")
else:
    print("\n✗ trending_manga table DOES NOT EXIST")
