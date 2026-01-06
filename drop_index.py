#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Force drop the problematic UNIQUE index.
"""

import sqlite3
from pathlib import Path

db_path = Path("data") / "readloom.db"
if not db_path.exists():
    print(f"Database not found at {db_path}")
    exit(1)

conn = sqlite3.connect(str(db_path))
cursor = conn.cursor()

try:
    print("Attempting to drop idx_unique_default index...")
    cursor.execute("DROP INDEX IF EXISTS idx_unique_default")
    conn.commit()
    print("✓ Successfully dropped idx_unique_default index")
except Exception as e:
    print(f"✗ Error dropping index: {e}")
    conn.rollback()

# Verify it's gone
cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND name='idx_unique_default'")
result = cursor.fetchone()
if result:
    print("✗ Index still exists!")
else:
    print("✓ Index successfully removed from database")

conn.close()
