#!/usr/bin/env python3
import sqlite3
from pathlib import Path

db_path = Path("data") / "readloom.db"
conn = sqlite3.connect(str(db_path))
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [t[0] for t in cursor.fetchall()]
print("Tables in database:", tables)
conn.close()
