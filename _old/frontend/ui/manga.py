#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Manga UI routes.
Handles manga-related pages and views.
"""

from flask import Blueprint, render_template, abort, redirect, url_for
from backend.base.logging import LOGGER
from backend.internals.db import execute_query
from frontend.middleware import setup_required

# Create routes blueprint
manga_routes = Blueprint('manga_routes', __name__)


def get_manga_collections():
    """Get manga collections (excluding default collections)."""
    try:
        collections = execute_query("""
            SELECT c.*, COUNT(sc.series_id) as manga_count
            FROM collections c
            LEFT JOIN series_collections sc ON c.id = sc.collection_id
            LEFT JOIN series s ON sc.series_id = s.id AND UPPER(s.content_type) IN ('MANGA', 'MANHWA', 'MANHUA', 'COMIC')
            WHERE UPPER(c.content_type) IN ('MANGA', 'MANHWA', 'MANHUA', 'COMIC')
            AND (c.is_default = 0 OR c.is_default IS NULL)
            GROUP BY c.id
            ORDER BY c.name
        """)
        return collections
    except Exception as e:
        LOGGER.error(f"Error getting manga collections: {e}")
        return []


def get_recent_series(limit=10):
    """Get recent manga series."""
    try:
        series = execute_query("""
            SELECT s.*
            FROM series s
            WHERE UPPER(s.content_type) IN ('MANGA', 'MANHWA', 'MANHUA', 'COMIC')
            ORDER BY s.created_at DESC
            LIMIT ?
        """, (limit,))
        return series
    except Exception as e:
        LOGGER.error(f"Error getting recent series: {e}")
        return []


def fetch_and_store_trending_manga(limit=10):
    """Fetch trending manga from AniList and store in database."""
    try:
        import requests
        
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
        import traceback
        LOGGER.error(traceback.format_exc())
        return []


def get_trending_manga_from_db(limit=10):
    """Get trending manga from database."""
    try:
        trending = execute_query("""
        SELECT anilist_id, title, cover_url, trending_score, popularity, description
        FROM trending_manga
        ORDER BY trending_score DESC
        LIMIT ?
        """, (limit,))
        return trending
    except Exception as e:
        LOGGER.error(f"Error getting trending manga from database: {e}")
        return []


def get_trending_manga(limit=12):
    """Get trending manga from AniList."""
    try:
        import requests
        
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
                    trending.append({
                        'id': media.get('id'),
                        'title': media.get('title', {}).get('english') or media.get('title', {}).get('romaji', 'Unknown'),
                        'cover_url': media.get('coverImage', {}).get('large'),
                        'description': media.get('description', ''),
                        'popularity': media.get('popularity', 0),
                        'trending': media.get('trending', 0)
                    })
                LOGGER.info(f"Successfully fetched {len(trending)} trending manga")
                return trending
        
        LOGGER.warning(f"AniList API returned status {response.status_code}")
        return []
    except Exception as e:
        LOGGER.error(f"Error fetching trending manga from AniList: {e}")
        import traceback
        LOGGER.error(traceback.format_exc())
        return []


@manga_routes.route('/manga')
def manga_home():
    """Manga home page."""
    return "MANGA_HOME FUNCTION CALLED - THIS IS A TEST"
    
    # Fetch and store trending manga from AniList
    trending_manga = []
    try:
        LOGGER.info("Fetching trending manga from AniList...")
        trending_manga = fetch_and_store_trending_manga(10)
        LOGGER.info(f"Successfully fetched and stored {len(trending_manga) if trending_manga else 0} trending manga")
        LOGGER.info(f"Trending manga data: {trending_manga[:1] if trending_manga else 'EMPTY'}")
    except Exception as e:
        LOGGER.error(f"Failed to fetch trending manga from AniList: {e}")
        import traceback
        LOGGER.error(traceback.format_exc())
        # Fall back to database
        try:
            LOGGER.info("Falling back to database for trending manga...")
            trending_manga = get_trending_manga_from_db(10)
            LOGGER.info(f"Got {len(trending_manga)} trending manga from database")
        except Exception as db_err:
            LOGGER.error(f"Failed to get trending manga from database: {db_err}")
            import traceback
            LOGGER.error(traceback.format_exc())
            trending_manga = []
    
    LOGGER.info(f"Rendering template with {len(trending_manga)} trending manga")
    
    return render_template(
        'manga/home.html',
        manga_collections=manga_collections,
        recent_series=recent_series,
        trending_manga=trending_manga
    )


@manga_routes.route('/manga/search')
@setup_required
def manga_search():
    """Manga search page."""
    import sys
    print(">>> MANGA_SEARCH CALLED <<<", file=sys.stderr, flush=True)
    return render_template('manga/search.html')


@manga_routes.route('/manga/series/<int:series_id>')
@setup_required
def series_view(series_id):
    """Series detail page."""
    series = execute_query(
        "SELECT * FROM series WHERE id = ? AND content_type IN ('MANGA', 'MANHWA', 'MANHUA', 'COMIC')",
        (series_id,)
    )
    
    if not series:
        abort(404)
    
    series = series[0]
    
    # Get volumes
    volumes = execute_query("""
        SELECT v.*, COUNT(c.id) as chapter_count
        FROM volumes v
        LEFT JOIN chapters c ON v.id = c.volume_id
        WHERE v.series_id = ?
        GROUP BY v.id
        ORDER BY CAST(v.volume_number AS INTEGER)
    """, (series_id,))
    
    # Get collection
    collection = execute_query("""
        SELECT c.* FROM collections c
        JOIN series_collections sc ON c.id = sc.collection_id
        WHERE sc.series_id = ?
    """, (series_id,))
    
    collection = collection[0] if collection else None
    
    # Get e-book files
    from backend.features.ebook_files import get_ebook_files_for_series
    ebook_files = get_ebook_files_for_series(series_id)
    
    return render_template(
        'manga/series.html',
        series=series,
        volumes=volumes,
        collection=collection,
        ebook_files=ebook_files
    )


@manga_routes.route('/series/<int:series_id>')
@setup_required
def series_detail(series_id: int):
    """Series detail page (backward compatibility).
    
    Redirects to the appropriate book or manga detail page based on the series type.
    """
    series = execute_query("SELECT content_type FROM series WHERE id = ?", (series_id,))
    
    if not series:
        abort(404)
    
    content_type = series[0]['content_type']
    
    if content_type == 'BOOK':
        return redirect(url_for('ui.book_view', book_id=series_id))
    else:
        return redirect(url_for('manga_routes.series_view', series_id=series_id))
