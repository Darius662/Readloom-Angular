#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Fetch author biographies from Groq AI for all authors.
"""

import sys
import sqlite3
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Use the correct database path directly
DB_PATH = Path(__file__).parent.parent / 'data' / 'db' / 'readloom.db'


def main():
    """Fetch and update author biographies."""
    import os
    
    # Check if Groq API key is set
    api_key = os.environ.get('GROQ_API_KEY')
    
    if not api_key:
        print("⚠️  GROQ_API_KEY not set")
        print()
        print("To enable author biographies, set your Groq API key:")
        print("  export GROQ_API_KEY=your_groq_api_key_here")
        print()
        print("Get your free key from: https://console.groq.com")
        return
    
    try:
        from groq import Groq
    except ImportError:
        print("❌ Groq library not installed")
        print("Install with: pip install groq")
        return
    
    print("Fetching author biographies from Groq AI...")
    print()
    
    # Connect to database
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Get all authors without biographies
    cursor.execute('SELECT id, name FROM authors WHERE biography IS NULL OR biography = ""')
    authors = cursor.fetchall()
    
    if not authors:
        print("✓ All authors already have biographies")
        conn.close()
        return
    
    print(f"Found {len(authors)} authors without biographies")
    print()
    
    stats = {
        "authors_checked": len(authors),
        "biographies_added": 0,
        "errors": 0
    }
    
    client = Groq(api_key=api_key)
    
    for author in authors:
        author_id = author['id']
        author_name = author['name']
        
        print(f"Fetching biography for: {author_name}")
        
        try:
            import json
            
            prompt = f'''Write a brief biography (2-3 sentences) for the author "{author_name}". 
Focus on their notable works, writing style, and literary significance.
Be factual and concise.

Return ONLY the biography text, no other text or formatting.'''
            
            message = client.chat.completions.create(
                model='llama-3.3-70b-versatile',
                max_tokens=200,
                messages=[
                    {'role': 'user', 'content': prompt}
                ]
            )
            
            biography = message.choices[0].message.content.strip()
            
            if not biography:
                raise Exception("No biography returned")
            
            # Update database
            cursor.execute('UPDATE authors SET biography = ? WHERE id = ?', (biography, author_id))
            conn.commit()
            
            stats["biographies_added"] += 1
            print(f"  ✓ Added biography")
            print(f"    {biography[:100]}...")
        except Exception as e:
            print(f"  ✗ Error: {e}")
            stats["errors"] += 1
        
        print()
    
    conn.close()
    
    print(f"✓ Author biography fetch completed!")
    print()
    print(f"  Authors checked: {stats['authors_checked']}")
    print(f"  Biographies added: {stats['biographies_added']}")
    print(f"  Errors: {stats['errors']}")
    print()
    
    if stats['biographies_added'] > 0:
        print("✓ Author biographies have been updated!")
        print("  Refresh the Authors page to see the new biographies.")
    else:
        print("No new biographies were added.")


if __name__ == "__main__":
    main()
