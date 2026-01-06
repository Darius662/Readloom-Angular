#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Author biography fetcher - fetches author biographies from Groq AI.
"""

import json
from backend.base.logging import LOGGER
from backend.internals.db import execute_query


def fetch_author_biography_from_groq(author_name: str) -> str:
    """
    Fetch author biography from Groq AI.
    
    Args:
        author_name: Author name
    
    Returns:
        str: Biography text or None
    """
    try:
        from groq import Groq
        import os
        
        # Try to get API key from database settings first, then environment variable
        api_key = None
        try:
            result = execute_query("SELECT value FROM settings WHERE key = 'groq_api_key'")
            if result and result[0]['value']:
                api_key = json.loads(result[0]['value'])
                LOGGER.debug(f"Found Groq API key in database settings")
        except Exception as e:
            LOGGER.debug(f"Could not read Groq API key from settings: {e}")
        
        # Fall back to environment variable
        if not api_key:
            api_key = os.environ.get('GROQ_API_KEY')
            if api_key:
                LOGGER.debug(f"Found Groq API key in environment variable")
        
        if not api_key:
            LOGGER.warning(f"GROQ_API_KEY not set in database settings or environment - cannot fetch biography for {author_name}")
            return None
        
        client = Groq(api_key=api_key)
        
        # Create a prompt to get author biography
        prompt = f"""
        Write a brief biography (2-3 sentences) for the author "{author_name}". 
        Focus on their notable works, writing style, and literary significance.
        Be factual and concise.
        
        Return ONLY the biography text, no other text or formatting.
        """
        
        message = client.chat.completions.create(
            model='llama-3.3-70b-versatile',
            max_tokens=200,
            messages=[
                {'role': 'user', 'content': prompt}
            ]
        )
        
        biography = message.choices[0].message.content.strip()
        
        if biography:
            LOGGER.info(f"Fetched biography for {author_name} from Groq")
            return biography
        
        LOGGER.debug(f"Empty response from Groq for author {author_name}")
        return None
        
    except Exception as e:
        LOGGER.debug(f"Error fetching author biography from Groq: {e}")
        return None


def update_author_biography(author_id: int, author_name: str) -> bool:
    """
    Fetch and update author biography.
    
    Args:
        author_id: Author ID
        author_name: Author name
    
    Returns:
        bool: True if biography was updated
    """
    try:
        LOGGER.info(f"Attempting to fetch biography for author {author_name} (ID: {author_id})")
        
        # Fetch biography
        biography = fetch_author_biography_from_groq(author_name)
        
        if not biography:
            LOGGER.warning(f"Could not fetch biography for author {author_name} - Groq API key may not be configured")
            return False
        
        # Update author with biography
        execute_query("""
            UPDATE authors 
            SET biography = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (biography, author_id), commit=True)
        
        LOGGER.info(f"Successfully updated author {author_name} with biography: {biography[:50]}...")
        return True
    
    except Exception as e:
        LOGGER.error(f"Error updating author biography: {e}")
        import traceback
        LOGGER.error(traceback.format_exc())
        return False


def fetch_and_update_all_author_biographies() -> dict:
    """
    Fetch and update biographies for all authors without biographies.
    
    Returns:
        dict: Statistics about the operation
    """
    try:
        stats = {
            "authors_checked": 0,
            "biographies_added": 0,
            "errors": 0
        }
        
        # Get all authors without biographies
        authors = execute_query("""
            SELECT id, name FROM authors 
            WHERE biography IS NULL OR biography = ''
        """)
        
        if not authors:
            LOGGER.info("All authors already have biographies")
            return stats
        
        stats["authors_checked"] = len(authors)
        
        for author in authors:
            try:
                if update_author_biography(author['id'], author['name']):
                    stats["biographies_added"] += 1
            except Exception as e:
                LOGGER.error(f"Error updating biography for author {author['name']}: {e}")
                stats["errors"] += 1
        
        LOGGER.info(f"Author biography fetch complete: {stats}")
        return stats
    
    except Exception as e:
        LOGGER.error(f"Error in fetch_and_update_all_author_biographies: {e}")
        return {
            "authors_checked": 0,
            "biographies_added": 0,
            "errors": 1
        }
