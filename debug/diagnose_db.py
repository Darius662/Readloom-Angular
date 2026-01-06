#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Diagnostic script to check database schema and constraints.
"""

import sqlite3
from pathlib import Path

# Connect to the database
db_path = Path("data") / "readloom.db"
if not db_path.exists():
    print(f"Database not found at {db_path}")
    exit(1)

conn = sqlite3.connect(str(db_path))
cursor = conn.cursor()

print("=" * 80)
print("DATABASE DIAGNOSTIC REPORT")
print("=" * 80)

# Check collections table structure
print("\n1. Collections Table Structure:")
print("-" * 80)
cursor.execute("PRAGMA table_info(collections)")
for row in cursor.fetchall():
    print(f"  {row}")

# Check all indexes on collections table
print("\n2. Indexes on Collections Table:")
print("-" * 80)
cursor.execute("SELECT name, sql FROM sqlite_master WHERE type='index' AND tbl_name='collections'")
indexes = cursor.fetchall()
if indexes:
    for name, sql in indexes:
        print(f"  Index: {name}")
        print(f"  SQL: {sql}")
else:
    print("  No indexes found")

# Check all triggers on collections table
print("\n3. Triggers on Collections Table:")
print("-" * 80)
cursor.execute("SELECT name, sql FROM sqlite_master WHERE type='trigger' AND tbl_name='collections'")
triggers = cursor.fetchall()
if triggers:
    for name, sql in triggers:
        print(f"  Trigger: {name}")
        print(f"  SQL: {sql}")
else:
    print("  No triggers found")

# Check current collections data
print("\n4. Current Collections Data:")
print("-" * 80)
cursor.execute("SELECT id, name, content_type, is_default FROM collections")
collections = cursor.fetchall()
if collections:
    for row in collections:
        print(f"  ID: {row[0]}, Name: {row[1]}, Type: {row[2]}, Default: {row[3]}")
else:
    print("  No collections found")

# Check for constraint violations
print("\n5. Constraint Analysis:")
print("-" * 80)
cursor.execute("""
    SELECT content_type, COUNT(*) as default_count 
    FROM collections 
    WHERE is_default = 1 
    GROUP BY content_type 
    HAVING COUNT(*) > 1
""")
violations = cursor.fetchall()
if violations:
    print("  WARNING: Multiple defaults found for same content_type:")
    for content_type, count in violations:
        print(f"    {content_type}: {count} defaults")
else:
    print("  OK: No constraint violations found")

conn.close()
print("\n" + "=" * 80)
