#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Populate trending_manga table from AniList API.
Based on the old frontend's fetch_and_store_trending_manga function.
"""

import sys
import os

# Add the backend directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from backend.base.logging import LOGGER
from backend.internals.db import execute_query
import requests
import traceback


def fetch_and_store_trending_manga(limit=10):
    """Fetch trending manga from AniList and store in database."""
    try:
        query = """
        query {
            Page(page: 1, perPage: %d) {
                media(type: MANGA, sort: TRENDING_DESC) {
                    id
                    title {
                        romaji
                        english
                    }
                    coverImage {
                        large
                    }
                    description
                    popularity
                    trending
                }
            }
        }
        """ % limit
        
        LOGGER.info("Fetching trending manga from AniList...")
        response = requests.post(
            'https://graphql.anilist.co',
            json={'query': query},
            timeout=30
        )
        
        LOGGER.info(f"AniList API response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if 'errors' in data:
                LOGGER.error(f"AniList API error: {data['errors']}")
                return []
            
            if 'data' in data and 'Page' in data['data']:
                trending = []
                for media in data['data']['Page']['media']:
                    anilist_id = media.get('id')
                    title = media.get('title', {}).get('english') or media.get('title', {}).get('romaji', 'Unknown')
                    cover_url = media.get('coverImage', {}).get('large')
                    trending_score = media.get('trending', 0)
                    popularity = media.get('popularity', 0)
                    description = media.get('description', '')
                    
                    # Store in database (insert or update)
                    try:
                        execute_query("""
                        INSERT OR REPLACE INTO trending_manga 
                        (anilist_id, title, cover_url, trending_score, popularity, description, updated_at)
                        VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                        """, (anilist_id, title, cover_url, trending_score, popularity, description), commit=True)
                        LOGGER.info(f"Stored trending manga: {title}")
                    except Exception as db_err:
                        LOGGER.error(f"Error storing trending manga {title}: {db_err}")
                    
                    trending.append({
                        'anilist_id': anilist_id,
                        'title': title,
                        'cover_url': cover_url,
                        'trending_score': trending_score,
                        'popularity': popularity,
                        'description': description
                    })
                
                LOGGER.info(f"Successfully fetched and stored {len(trending)} trending manga")
                return trending
        
        LOGGER.warning(f"AniList API returned status {response.status_code}")
        return []
    except Exception as e:
        LOGGER.error(f"Error fetching trending manga from AniList: {e}")
        LOGGER.error(traceback.format_exc())
        return []


def main():
    """Main function to populate trending manga."""
    LOGGER.info("Starting trending manga population...")
    
    # Fetch and store trending manga
    trending_manga = fetch_and_store_trending_manga(12)
    
    if trending_manga:
        LOGGER.info(f"Successfully populated {len(trending_manga)} trending manga:")
        for i, manga in enumerate(trending_manga, 1):
            LOGGER.info(f"{i}. {manga['title']} (Trending: {manga['trending_score']}, Popularity: {manga['popularity']})")
    else:
        LOGGER.warning("No trending manga were fetched")
    
    # Verify the data was stored
    try:
        stored_count = execute_query("SELECT COUNT(*) as count FROM trending_manga")
        LOGGER.info(f"Total trending manga in database: {stored_count[0]['count']}")
        
        # Show first few entries
        recent = execute_query("SELECT title, trending_score, popularity FROM trending_manga ORDER BY trending_score DESC LIMIT 5")
        LOGGER.info("Top 5 trending manga:")
        for i, manga in enumerate(recent, 1):
            LOGGER.info(f"{i}. {manga['title']} - Trending: {manga['trending_score']}, Popularity: {manga['popularity']}")
    except Exception as e:
        LOGGER.error(f"Error verifying stored data: {e}")
    
    LOGGER.info("Trending manga population completed!")


if __name__ == "__main__":
    main()
