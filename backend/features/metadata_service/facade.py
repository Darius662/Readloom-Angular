#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Facade for metadata service.
Exposes public API and delegates to cache and provider gateway.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union

from backend.base.logging import LOGGER
from backend.features.metadata_providers.setup import initialize_providers, get_provider_settings, update_provider_settings
from .cache import save_to_cache, get_from_cache, clear_cache
from .provider_gateway import (
    search_with_provider,
    search_with_all_providers,
    get_manga_details_from_provider,
    get_chapter_list_from_provider,
    get_chapter_images_from_provider,
    get_latest_releases_from_provider,
    get_latest_releases_from_all_providers,
)


def download_mangadex_covers_for_series(series_id: int, manga_details: Dict[str, Any], provider: str, manga_id: str) -> None:
    """Download MangaDex covers for a newly imported series.
    
    Args:
        series_id: The ID of the newly imported series
        manga_details: The manga details from the provider
        provider: The provider name (e.g., 'AniList')
        manga_id: The manga ID from the provider
    """
    try:
        # Only download covers for AniList series (since we can translate to MangaDex)
        if provider != 'AniList':
            LOGGER.info(f"Skipping cover download for non-AniList provider: {provider}")
            return
        
        # Find MangaDex equivalent
        mangadex_id = find_mangadex_equivalent(manga_id, manga_details.get('title', ''))
        
        if not mangadex_id:
            LOGGER.warning(f"No MangaDex equivalent found for AniList ID: {manga_id}")
            return
        
        LOGGER.info(f"Found MangaDex equivalent: {mangadex_id}")
        
        # Update series with MangaDex ID for future reference
        from backend.internals.db import execute_query
        execute_query(
            "UPDATE series SET metadata_id = ? WHERE id = ?",
            (mangadex_id, series_id),
            commit=True
        )
        
        # Get all volumes for this series
        volumes = execute_query(
            "SELECT id, volume_number FROM volumes WHERE series_id = ? ORDER BY volume_number",
            (series_id,)
        )
        
        if not volumes:
            LOGGER.info(f"No volumes found for series {series_id}")
            return
        
        LOGGER.info(f"Found {len(volumes)} volumes for series {series_id}")
        
        # Get MangaDex covers
        from backend.features.cover_art_manager import COVER_ART_MANAGER
        volume_covers = COVER_ART_MANAGER.get_mangadex_covers_for_series(mangadex_id)
        
        if not volume_covers:
            LOGGER.info(f"No covers found on MangaDex for {mangadex_id}")
            return
        
        LOGGER.info(f"Found {len(volume_covers)} covers on MangaDex")
        
        # Match and download covers
        matching_results = COVER_ART_MANAGER.match_covers_to_volumes(volume_covers, volumes)
        
        LOGGER.info(f"Cover matching results: {len(matching_results['matched'])} matched, "
                   f"{len(matching_results['unmatched_covers'])} unmatched covers, "
                   f"{len(matching_results['unmatched_volumes'])} unmatched volumes")
        
        # Download matched covers
        covers_downloaded = 0
        for match in matching_results['matched']:
            volume = match['volume']
            cover = match['cover']
            
            volume_id = volume.get('id')
            volume_number = volume.get('volume_number')
            cover_filename = cover['filename']
            match_type = match['match_type']
            
            try:
                cover_path = COVER_ART_MANAGER.save_volume_cover(
                    series_id, volume_id, volume_number, mangadex_id, cover_filename
                )
                
                if cover_path:
                    covers_downloaded += 1
                    LOGGER.info(f"Downloaded cover for Volume {volume_number} ({match_type}): {cover_path}")
                    
                    # Update volume with cover URL
                    cover_url = f"https://uploads.mangadex.org/covers/{mangadex_id}/{cover_filename}"
                    execute_query(
                        "UPDATE volumes SET cover_url = ?, cover_path = ? WHERE id = ?",
                        (cover_url, cover_path, volume_id),
                        commit=True
                    )
                else:
                    LOGGER.warning(f"Failed to download cover for Volume {volume_number}")
                    
            except Exception as e:
                LOGGER.error(f"Error downloading cover for Volume {volume_number}: {e}")
        
        LOGGER.info(f"Successfully downloaded {covers_downloaded} covers for series {series_id}")
        
    except Exception as e:
        LOGGER.error(f"Error in download_mangadex_covers_for_series: {e}")


def find_mangadex_equivalent(anilist_id: str, series_title: str) -> Optional[str]:
    """Find MangaDex equivalent for an AniList series.
    
    Args:
        anilist_id: The AniList ID
        series_title: The series title
        
    Returns:
        The MangaDex ID or None if not found
    """
    try:
        import requests
        
        # Try different search terms
        search_terms = [
            series_title,
            series_title.replace("Kaijuu 8-gou", "Kaiju No. 8"),
            series_title.replace("Shingeki no Kyojin", "進撃の巨人"),
            series_title.replace("Enen no Shouboutai", "炎炎消防隊"),
            series_title.replace("Code Geass: Hangyaku no Lelouch", "Code Geass"),
            # Special case for Kumo desu ga, Nani ka?
            "Murabito desu ga Nani ka?",
            "I'm a Villager, So What?",
            "So I'm a Spider, So What?",
        ]
        
        for term in search_terms:
            try:
                response = requests.get(
                    "https://api.mangadex.org/manga",
                    params={"title": term, "limit": 10, "includes[]": "cover_art"},
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if 'data' in data and data['data']:
                        for manga in data['data']:
                            if manga.get('type') == 'manga':
                                attributes = manga.get('attributes', {})
                                title = attributes.get('title', {})
                                alt_titles = attributes.get('altTitles', [])
                                
                                # Check if this looks like the main series
                                all_titles = [title.get('en', '')] + [t.get('en', '') for t in alt_titles]
                                
                                if any(term.lower() in title.lower() for title in all_titles):
                                    # Skip obvious spinoffs/side stories
                                    manga_title = title.get('en', '')
                                    if any(keyword in manga_title.lower() for keyword in ['relax', 'b-side', 'day off', 'fan colored']):
                                        continue
                                    
                                    return manga['id']
            except Exception as e:
                LOGGER.warning(f"Search error for '{term}': {e}")
        
        return None
        
    except Exception as e:
        LOGGER.error(f"Error finding MangaDex equivalent: {e}")
        return None


def populate_volumes_and_chapters(series_id: int, manga_details: Dict[str, Any], provider: str, metadata_id: Optional[str] = None) -> int:
    """Populate volumes and chapters with release dates for a series.
    
    This function replicates the logic from import_manga_to_collection to ensure
    file system imports get the same volume/chapter data as search imports.
    
    Args:
        series_id: The series ID to populate
        manga_details: The manga details dict from metadata provider
        provider: The provider name (e.g., 'AniList', 'MangaDex')
        metadata_id: The metadata ID to fetch actual chapter data from provider
        
    Returns:
        int: Number of chapters added
    """
    from backend.internals.db import execute_query, get_db_connection
    
    try:
        # Get chapter list - first try from manga_details, then fetch from provider if available
        chapter_list = manga_details.get("chapters", [])
        
        # If no chapters in manga_details and we have metadata_id, fetch actual chapters from provider
        if (not chapter_list or not isinstance(chapter_list, list)) and metadata_id:
            LOGGER.info(f"Fetching actual chapter list from {provider} for metadata_id {metadata_id}")
            try:
                chapter_list_result = get_chapter_list(metadata_id, provider)
                
                # Handle different return types (for backward compatibility)
                if isinstance(chapter_list_result, dict):
                    if "error" in chapter_list_result:
                        LOGGER.warning(f"Error getting chapters from provider: {chapter_list_result.get('error')}")
                        chapter_list = []
                    else:
                        chapter_list = chapter_list_result.get("chapters", [])
                elif isinstance(chapter_list_result, list):
                    chapter_list = chapter_list_result
                else:
                    LOGGER.warning(f"Unexpected chapter list result type: {type(chapter_list_result)}")
                    chapter_list = []
                    
                if chapter_list:
                    LOGGER.info(f"Fetched {len(chapter_list)} actual chapters from {provider}")
            except Exception as e:
                LOGGER.warning(f"Error fetching chapter list from provider: {e}")
                chapter_list = []
        
        # If still no chapters, create placeholder chapters with future dates
        if not chapter_list or not isinstance(chapter_list, list):
            LOGGER.info(f"No actual chapters found, creating placeholder chapters for series {series_id}")
            chapter_list = []
        
        # Insert volumes - ensure we create them even if provider doesn't give them
        volumes = {}
        create_volumes = True
        volume_count = 4  # Default minimum volume count
        
        if "volumes" in manga_details and isinstance(manga_details["volumes"], list) and manga_details["volumes"]:
            LOGGER.info(f"Importing {len(manga_details['volumes'])} volumes from {provider}")
            for volume in manga_details["volumes"]:
                create_volumes = False  # We're creating them from the provider data
                try:
                    conn = get_db_connection()
                    cursor = conn.cursor()
                    cursor.execute(
                        """
                        INSERT INTO volumes (
                            series_id, volume_number, title, description, cover_url, release_date
                        ) VALUES (?, ?, ?, ?, ?, ?)
                        """,
                        (
                            series_id,
                            volume.get("number", "0"),
                            volume.get("title", f"Volume {volume.get('number', '0')}"),
                            volume.get("description", ""),
                            volume.get("cover_url", ""),
                            volume.get("release_date", "") or volume.get("date", "")
                        )
                    )
                    conn.commit()
                    volume_id = cursor.lastrowid
                    
                    if volume_id:
                        volumes[volume.get("number", "0")] = volume_id
                except Exception as e:
                    LOGGER.error(f"Error inserting volume: {e}")
        
        # Create default volumes if none provided by the API
        if create_volumes:
            LOGGER.info(f"Creating {volume_count} default volumes since none provided by {provider}")
            start_date = datetime.now()  # Start from today, not the past
            
            for i in range(1, volume_count + 1):
                volume_date = start_date + timedelta(days=i * 90)
                release_date_str = volume_date.strftime("%Y-%m-%d")
                
                try:
                    conn = get_db_connection()
                    cursor = conn.cursor()
                    cursor.execute(
                        """
                        INSERT INTO volumes (
                            series_id, volume_number, title, description, cover_url, release_date
                        ) VALUES (?, ?, ?, ?, ?, ?)
                        """,
                        (
                            series_id,
                            str(i),
                            f"Volume {i}",
                            "",
                            "",
                            release_date_str
                        )
                    )
                    conn.commit()
                    volume_id = cursor.lastrowid
                    
                    if volume_id:
                        volumes[str(i)] = volume_id
                        LOGGER.info(f"Created default volume {i} with date {release_date_str}")
                except Exception as e:
                    LOGGER.error(f"Error creating default volume {i}: {e}")
        
        # Insert chapters
        chapters_added = 0
        # Ensure chapter_list is actually a list (fix for when it's an int from AniList)
        # AniList returns chapter COUNT as an integer, not actual chapter data
        if not isinstance(chapter_list, list):
            LOGGER.debug(f"chapter_list is not a list (got {type(chapter_list)}: {chapter_list}), creating placeholder chapters")
            # Create placeholder chapters with future dates (same as search import does)
            chapter_list = [
                {"number": "1", "title": "Chapter 1", "date": datetime.now().strftime("%Y-%m-%d")},
                {"number": "2", "title": "Chapter 2", "date": (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")},
                {"number": "3", "title": "Chapter 3", "date": (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d")}
            ]
            LOGGER.info("Created 3 placeholder chapters since provider returned chapter count instead of data")
        
        for chapter in chapter_list:
            # Try to determine volume number from chapter number
            volume_number = "0"
            if "number" in chapter:
                try:
                    chapter_num = float(chapter["number"])
                    volume_number = str(max(1, int(chapter_num / 10)))
                except (ValueError, TypeError):
                    volume_number = "0"
            
            # Get volume ID if available
            volume_id = volumes.get(volume_number, None)
            
            # If no matching volume, try to use volume 1
            if volume_id is None and "1" in volumes:
                volume_id = volumes.get("1", None)
            
            # Get release date - prioritize standardized format
            chapter_date = chapter.get("date", "") or chapter.get("release_date", "")
            
            # Log chapter data for debugging
            LOGGER.info(f"Importing chapter: {chapter.get('number', 'Unknown')} with date {chapter_date}")
            
            # Validate the date format
            if chapter_date:
                try:
                    # Try to parse the date to verify format
                    test_date = datetime.fromisoformat(chapter_date)
                    # It's valid, keep it
                except (ValueError, TypeError):
                    # Invalid format, log warning but continue with the date
                    LOGGER.warning(f"Potentially invalid date format: {chapter_date} for chapter {chapter.get('number', 'Unknown')}")
            
            execute_query(
                """
                INSERT INTO chapters (
                    series_id, volume_id, chapter_number, title, description, release_date, status, read_status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    series_id,
                    volume_id,
                    chapter.get("number", "0") or "0",  # Ensure chapter_number is never null
                    chapter.get("title", f"Chapter {chapter.get('number', '0') or '0'}"),
                    "",
                    chapter_date,  # Use our validated date
                    "ANNOUNCED",
                    "UNREAD"
                )
            )
            
            chapters_added += 1
        
        LOGGER.info(f"Populated {chapters_added} chapters for series {series_id}")
        return chapters_added
        
    except Exception as e:
        LOGGER.error(f"Error populating volumes and chapters for series {series_id}: {e}")
        import traceback
        LOGGER.error(traceback.format_exc())
        return 0


def init_metadata_service() -> None:
    """Initialize the metadata service."""
    try:
        # Initialize metadata providers
        initialize_providers()
        
        # Drop and recreate metadata cache table to ensure proper schema
        from backend.internals.db import execute_query
        execute_query("DROP TABLE IF EXISTS metadata_cache")
        
        # Create metadata cache table with proper schema
        execute_query("""
            CREATE TABLE IF NOT EXISTS metadata_cache (
                id TEXT PRIMARY KEY,
                provider TEXT NOT NULL,
                type TEXT NOT NULL,
                data TEXT NOT NULL,
                timestamp TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """, commit=True)
        
        LOGGER.info("Metadata service initialized")
    except Exception as e:
        LOGGER.error(f"Error initializing metadata service: {e}")


def search_manga(query: str, provider: Optional[str] = None, page: int = 1, search_type: str = "title") -> Dict[str, Any]:
    """Search for manga across all enabled providers or a specific provider.
    
    Args:
        query: The search query.
        provider: The provider name (optional).
        page: The page number.
        search_type: The type of search to perform (title or author).
        
    Returns:
        A dictionary containing search results.
    """
    try:
        if provider:
            # Search with a specific provider
            results = {provider: search_with_provider(query, provider, page, search_type)}
        else:
            # Search with all enabled providers
            results = search_with_all_providers(query, page, search_type)
        
        # Format the response
        response = {
            "query": query,
            "page": page,
            "search_type": search_type,
            "results": results,
            "timestamp": datetime.now().isoformat()
        }
        
        return response
    except Exception as e:
        LOGGER.error(f"Error searching manga: {e}")
        return {"error": str(e)}


def get_manga_details(manga_id: str, provider: str) -> Dict[str, Any]:
    """Get details for a manga.
    
    Args:
        manga_id: The manga ID.
        provider: The provider name.
        
    Returns:
        A dictionary containing manga details.
    """
    try:
        # Check cache first
        cache_key = f"{provider}_{manga_id}"
        cached_data = get_from_cache(cache_key, "manga_details")
        
        if cached_data:
            return cached_data
        
        # Get from provider if not in cache
        details = get_manga_details_from_provider(manga_id, provider)
        
        if details:
            # Add to cache
            save_to_cache(cache_key, "manga_details", details)
        
        return details
    except Exception as e:
        LOGGER.error(f"Error getting manga details: {e}")
        return {"error": str(e)}


def get_chapter_list(manga_id: str, provider: str) -> Union[List[Dict[str, Any]], Dict[str, Any]]:
    """Get the chapter list for a manga.
    
    Args:
        manga_id: The manga ID.
        provider: The provider name.
        
    Returns:
        A list of chapters or a dictionary with error information.
    """
    try:
        # Check if we have a cached version
        cache_key = f"{provider}_{manga_id}_chapters"
        cached = get_from_cache(cache_key, "chapters")
        if cached:
            return cached
        
        # Get chapter list from provider
        chapters = get_chapter_list_from_provider(manga_id, provider)
        
        # Handle different return types
        if isinstance(chapters, dict):
            # Already in the right format
            result = chapters
        elif isinstance(chapters, list):
            # Convert list to dict format
            result = {"chapters": chapters}
        else:
            # Handle unexpected return type
            LOGGER.error(f"Unexpected return type from get_chapter_list: {type(chapters)}")
            result = {"error": f"Unexpected return type: {type(chapters)}", "chapters": []}
        
        # Cache the results
        save_to_cache(cache_key, "chapters", result)
        
        return result
    except Exception as e:
        LOGGER.error(f"Error getting chapter list: {e}")
        return {"error": str(e), "chapters": []}


def get_chapter_images(manga_id: str, chapter_id: str, provider: str) -> Dict[str, Any]:
    """Get the images for a chapter.
    
    Args:
        manga_id: The manga ID.
        chapter_id: The chapter ID.
        provider: The provider name.
        
    Returns:
        A dictionary containing chapter images.
    """
    try:
        # Check cache first
        cache_key = f"{provider}_{manga_id}_{chapter_id}"
        cached_data = get_from_cache(cache_key, "chapter_images")
        
        if cached_data:
            return {"images": cached_data}
        
        # Get from provider if not in cache
        images = get_chapter_images_from_provider(manga_id, chapter_id, provider)
        
        if images:
            # Add to cache
            save_to_cache(cache_key, "chapter_images", images)
        
        return {"images": images}
    except Exception as e:
        LOGGER.error(f"Error getting chapter images: {e}")
        return {"error": str(e)}


def get_latest_releases(provider: Optional[str] = None, page: int = 1) -> Dict[str, Any]:
    """Get the latest manga releases.
    
    Args:
        provider: The provider name (optional).
        page: The page number.
        
    Returns:
        A dictionary containing latest releases.
    """
    try:
        if provider:
            # Get latest releases from a specific provider
            results = {provider: get_latest_releases_from_provider(provider, page)}
        else:
            # Get latest releases from all enabled providers
            results = get_latest_releases_from_all_providers(page)
        
        # Format the response
        response = {
            "page": page,
            "results": results,
            "timestamp": datetime.now().isoformat()
        }
        
        return response
    except Exception as e:
        LOGGER.error(f"Error getting latest releases: {e}")
        return {"error": str(e)}


def get_providers() -> Dict[str, Any]:
    """Get all metadata providers and their settings.
    
    Returns:
        A dictionary containing provider information.
    """
    try:
        providers_response = get_provider_settings()
        
        # get_provider_settings() already returns {"providers": [...]}
        # so we just add the timestamp
        providers_response["timestamp"] = datetime.now().isoformat()
        
        return providers_response
    except Exception as e:
        LOGGER.error(f"Error getting providers: {e}")
        return {"error": str(e)}


def update_provider(name: str, enabled: bool, settings: Dict[str, Any]) -> Dict[str, Any]:
    """Update a metadata provider's settings.
    
    Args:
        name: The provider name.
        enabled: Whether the provider is enabled.
        settings: The provider settings.
        
    Returns:
        A dictionary containing the result.
    """
    try:
        success = update_provider_settings(name, enabled, settings)
        
        if success:
            return {
                "success": True,
                "message": f"Provider {name} updated successfully"
            }
        else:
            return {
                "success": False,
                "message": f"Failed to update provider {name}"
            }
    except Exception as e:
        LOGGER.error(f"Error updating provider: {e}")
        return {
            "success": False,
            "message": str(e)
        }


def add_to_want_to_read_collection(
    manga_id: str,
    provider: str,
    content_type: Optional[str] = None,
) -> Dict[str, Any]:
    """Add a manga to the want-to-read cache (NOT to series table or collections).
    
    Args:
        manga_id: The manga ID.
        provider: The provider name.
        content_type: The content type (MANGA, BOOK, etc.).
        
    Returns:
        A dictionary containing the result.
    """
    try:
        from backend.internals.db import execute_query
        from backend.features.want_to_read_cache import add_to_cache, sync_cache_to_readme_files
        
        # Get manga details
        manga_details = get_manga_details(manga_id, provider)
        
        if "error" in manga_details:
            return manga_details
        
        # Check if the series already exists in the series table
        existing_series = execute_query(
            "SELECT id FROM series WHERE metadata_source = ? AND metadata_id = ?",
            (provider, manga_id)
        )
        
        series_id = None
        if existing_series:
            # If series exists, use its ID
            series_id = existing_series[0]["id"]
            LOGGER.info(f"Found existing series {series_id}")
        
        # Add to want-to-read cache (regardless of whether series exists)
        try:
            # Use series_id if it exists, otherwise use a placeholder
            cache_series_id = series_id if series_id else 0
            cache_content_type = content_type or "MANGA"
            
            LOGGER.info(f"Adding to cache: provider={provider}, manga_id={manga_id}, content_type={cache_content_type}")
            
            result = add_to_cache(
                cache_series_id,
                manga_details.get("title", "Unknown"),
                manga_details.get("author", "Unknown"),
                manga_details.get("cover_url", ""),
                provider,
                manga_id,
                cache_content_type
            )
            
            if result:
                # Sync cache to README files based on content type
                sync_cache_to_readme_files(cache_content_type)
                LOGGER.info(f"Successfully added to want-to-read cache (series_id={cache_series_id}, content_type={cache_content_type})")
            else:
                LOGGER.warning(f"Failed to add to cache but continuing")
        except Exception as e:
            LOGGER.error(f"Error updating want-to-read cache: {e}", exc_info=True)
        
        return {
            "success": True,
            "message": "Added to 'Want to read' list",
            "series_id": series_id
        }
    except Exception as e:
        LOGGER.error(f"Error adding to want to read: {e}")
        return {
            "success": False,
            "message": str(e)
        }


def import_manga_to_collection(
    manga_id: str,
    provider: str,
    collection_id: Optional[int] = None,
    content_type: Optional[str] = None,
    root_folder_id: Optional[int] = None,
) -> Dict[str, Any]:
    """Import a manga from an external source to the collection.
    
    Args:
        manga_id: The manga ID.
        provider: The provider name.
        
    Returns:
        A dictionary containing the result.
    """
    # Import LOGGER at the top of the function to ensure it's available in all code paths
    from backend.base.logging import LOGGER
    
    try:
        # Get manga details
        manga_details = get_manga_details(manga_id, provider)
        
        if "error" in manga_details:
            return manga_details
        
        # Check if the series already exists
        from backend.internals.db import execute_query, get_db_connection
        existing_series = execute_query(
            "SELECT id FROM series WHERE metadata_source = ? AND metadata_id = ?",
            (provider, manga_id)
        )
        
        if existing_series:
            return {
                "success": False,
                "message": "Series already exists in the collection",
                "series_id": existing_series[0]["id"]
            }
        
        # Determine inferred content type using metadata heuristics
        def infer_from_metadata(details: Dict[str, Any]) -> Optional[str]:
            try:
                text_bins: List[str] = []
                # Common fields across providers
                for key in [
                    "categories", "subjects", "tags", "genres", "topic",
                    "topic_list", "genre_list"
                ]:
                    val = details.get(key)
                    if isinstance(val, list):
                        text_bins.extend([str(v) for v in val])
                    elif isinstance(val, str):
                        text_bins.append(val)
                # Title/description hints
                for key in ["title", "description"]:
                    v = details.get(key)
                    if isinstance(v, str):
                        text_bins.append(v)

                blob = " ".join(text_bins).lower()
                if any(tok in blob for tok in ["manga", "manhwa", "manhua", "shonen", "seinen", "shojo", "shoujo"]):
                    return "MANGA"
                if any(tok in blob for tok in ["graphic novel", "comics", "comic", "bd "]):
                    return "COMIC"
                return None
            except Exception:
                return None

        if content_type:
            inferred_type = (content_type or "MANGA").upper()
        else:
            heur = infer_from_metadata(manga_details) if isinstance(manga_details, dict) else None
            if heur:
                inferred_type = heur
            else:
                # Provider-based fallback
                provider_upper = (provider or "").upper()
                if provider_upper in {"GOOGLEBOOKS", "OPENLIBRARY", "ISBNDB", "WORLDCAT"}:
                    inferred_type = "BOOK"
                else:
                    inferred_type = "MANGA"

        # Insert the series
        try:
            # Get a direct connection to execute the insert and get the last row ID
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Prepare genres/subjects as comma-separated string
            genres = manga_details.get("genres", [])
            subjects_str = ",".join(genres) if isinstance(genres, list) else genres
            
            cursor.execute(
                """
                INSERT INTO series (
                    title, description, author, publisher, cover_url, status, content_type, metadata_source, metadata_id,
                    isbn, published_date, subjects
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    manga_details.get("title", "Unknown"),
                    manga_details.get("description", ""),
                    manga_details.get("author", "Unknown"),
                    manga_details.get("publisher", "Unknown"),
                    manga_details.get("cover_url", ""),
                    manga_details.get("status", "ONGOING"),
                    manga_details.get("content_type", inferred_type),
                    provider,
                    manga_id,
                    manga_details.get("isbn", ""),
                    manga_details.get("published_date", ""),
                    subjects_str
                )
            )
            conn.commit()
            
            # Get the ID of the last inserted row
            series_id = cursor.lastrowid
            
            if not series_id:
                return {
                    "success": False,
                    "message": "Failed to insert series into database"
                }
            
            # Automatically sync author if provided
            author_id = None
            try:
                author_name = manga_details.get("author", "").strip()
                if author_name and author_name != "Unknown":
                    LOGGER.info(f"Attempting to sync author '{author_name}' for series {series_id}")
                    from backend.features.authors_sync import sync_author_for_series
                    result = sync_author_for_series(series_id, author_name)
                    LOGGER.info(f"sync_author_for_series returned: {result}")
                    
                    # Get the author ID for returning in response
                    author_result = execute_query(
                        "SELECT id FROM authors WHERE name = ?",
                        (author_name,)
                    )
                    if author_result:
                        author_id = author_result[0]['id']
                        LOGGER.info(f"Found author ID {author_id} for '{author_name}'")
                    else:
                        LOGGER.warning(f"Could not find author ID for '{author_name}' after sync")
                else:
                    LOGGER.debug(f"Skipping author sync: author_name='{author_name}'")
            except Exception as e:
                LOGGER.error(f"Failed to sync author for series {series_id}: {e}")
                import traceback
                LOGGER.error(traceback.format_exc())
        
        except Exception as e:
            LOGGER.error(f"Error inserting series: {e}")
            return {
                "success": False,
                "message": f"Database error: {str(e)}"
            }
        
        # Get chapter list
        from datetime import timedelta
        chapter_list_result = get_chapter_list(manga_id, provider)
        
        # Handle different return types (for backward compatibility)
        if isinstance(chapter_list_result, dict):
            if "error" in chapter_list_result:
                LOGGER.warning(f"Error getting chapters from provider: {chapter_list_result.get('error')}")
                # Create at least 3 placeholder chapters
                chapter_list = [
                    {"number": "1", "title": "Chapter 1", "date": datetime.now().strftime("%Y-%m-%d")},
                    {"number": "2", "title": "Chapter 2", "date": (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")},
                    {"number": "3", "title": "Chapter 3", "date": (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d")}
                ]
                LOGGER.info("Created 3 placeholder chapters since provider failed")
            else:
                chapter_list = chapter_list_result.get("chapters", [])
        elif isinstance(chapter_list_result, list):
            chapter_list = chapter_list_result
        else:
            # If it's neither a dict nor a list, create placeholder chapters
            LOGGER.warning(f"Unexpected chapter list result type: {type(chapter_list_result)}")
            chapter_list = [
                {"number": "1", "title": "Chapter 1", "date": datetime.now().strftime("%Y-%m-%d")},
                {"number": "2", "title": "Chapter 2", "date": (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")},
                {"number": "3", "title": "Chapter 3", "date": (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d")}
            ]
            LOGGER.info("Created 3 placeholder chapters due to unexpected result type")
        
        # Insert volumes - ensure we create them even if provider doesn't give them
        volumes = {}
        create_volumes = True
        volume_count = 4  # Default minimum volume count
        
        if "volumes" in manga_details and isinstance(manga_details["volumes"], list) and manga_details["volumes"]:
            LOGGER.info(f"Importing {len(manga_details['volumes'])} volumes from {provider}")
            for volume in manga_details["volumes"]:
                create_volumes = False  # We're creating them from the provider data
                try:
                    # Get a direct connection to execute the insert and get the last row ID
                    conn = get_db_connection()
                    cursor = conn.cursor()
                    cursor.execute(
                        """
                        INSERT INTO volumes (
                            series_id, volume_number, title, description, cover_url, release_date
                        ) VALUES (?, ?, ?, ?, ?, ?)
                        """,
                        (
                            series_id,
                            volume.get("number", "0"),
                            volume.get("title", f"Volume {volume.get('number', '0')}"),
                            volume.get("description", ""),
                            volume.get("cover_url", ""),
                            volume.get("release_date", "") or volume.get("date", "")
                        )
                    )
                    conn.commit()
                    
                    # Get the ID of the last inserted row
                    volume_id = cursor.lastrowid
                    
                    if volume_id:
                        volumes[volume.get("number", "0")] = volume_id
                except Exception as e:
                    LOGGER.error(f"Error inserting volume: {e}")
        
        # Create default volumes if none provided by the API
        if create_volumes:
            LOGGER.info(f"Creating {volume_count} default volumes since none provided by {provider}")
            start_date = datetime.now()  # Start from today, not the past
            
            for i in range(1, volume_count + 1):
                volume_date = start_date + timedelta(days=i * 90)
                release_date_str = volume_date.strftime("%Y-%m-%d")
                
                try:
                    conn = get_db_connection()
                    cursor = conn.cursor()
                    cursor.execute(
                        """
                        INSERT INTO volumes (
                            series_id, volume_number, title, description, cover_url, release_date
                        ) VALUES (?, ?, ?, ?, ?, ?)
                        """,
                        (
                            series_id,
                            str(i),
                            f"Volume {i}",
                            "",
                            "",
                            release_date_str
                        )
                    )
                    conn.commit()
                    volume_id = cursor.lastrowid
                    
                    if volume_id:
                        volumes[str(i)] = volume_id
                        LOGGER.info(f"Created default volume {i} with date {release_date_str}")
                except Exception as e:
                    LOGGER.error(f"Error creating default volume {i}: {e}")
        
        # Insert chapters
        chapters_added = 0
        # Ensure chapter_list is actually a list (fix for when it's an int from AniList)
        # AniList returns chapter COUNT as an integer, not actual chapter data
        if not isinstance(chapter_list, list):
            LOGGER.debug(f"chapter_list is not a list (got {type(chapter_list)}: {chapter_list}), skipping chapter creation")
            chapter_list = []
        
        for chapter in chapter_list:
            # Try to determine volume number from chapter number
            volume_number = "0"
            if "number" in chapter:
                try:
                    chapter_num = float(chapter["number"])
                    volume_number = str(max(1, int(chapter_num / 10)))
                except (ValueError, TypeError):
                    volume_number = "0"
            
            # Get volume ID if available
            volume_id = volumes.get(volume_number, None)
            
            # If no matching volume, try to use volume 1
            if volume_id is None and "1" in volumes:
                volume_id = volumes.get("1", None)
            
            # Get release date - prioritize standardized format
            chapter_date = chapter.get("date", "") or chapter.get("release_date", "")
            
            # Log chapter data for debugging
            LOGGER.info(f"Importing chapter: {chapter.get('number', 'Unknown')} with date {chapter_date}")
            
            # Validate the date format
            if chapter_date:
                try:
                    # Try to parse the date to verify format
                    test_date = datetime.fromisoformat(chapter_date)
                    # It's valid, keep it
                except (ValueError, TypeError):
                    # Invalid format, log warning but continue with the date
                    LOGGER.warning(f"Potentially invalid date format: {chapter_date} for chapter {chapter.get('number', 'Unknown')}")
            
            execute_query(
                """
                INSERT INTO chapters (
                    series_id, volume_id, chapter_number, title, description, release_date, status, read_status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    series_id,
                    volume_id,
                    chapter.get("number", "0") or "0",  # Ensure chapter_number is never null
                    chapter.get("title", f"Chapter {chapter.get('number', '0') or '0'}"),
                    "",
                    chapter_date,  # Use our validated date
                    "ANNOUNCED",
                    "UNREAD"
                )
            )
            
            chapters_added += 1
        
        # Link to a collection (selected or default by type)
        try:
            from backend.features.collection import add_series_to_collection, get_default_collection
            target_collection_id = None
            if collection_id:
                try:
                    target_collection_id = int(collection_id)
                except Exception:
                    target_collection_id = None
            if not target_collection_id:
                default_coll = get_default_collection(manga_details.get("content_type", inferred_type))
                if default_coll and default_coll.get("id"):
                    target_collection_id = default_coll["id"]
            if target_collection_id:
                add_series_to_collection(target_collection_id, series_id)
        except Exception as e:
            LOGGER.warning(f"Failed linking series to collection: {e}")

        # Create folder structure for the series
        # Skip folder creation for BOOK content type as it's handled by the enhanced import
        skip_folder_creation = (inferred_type == "BOOK" or content_type == "BOOK")
        
        folder_already_exists = False
        series_path = None
        
        if not skip_folder_creation:
            try:
                from backend.base.helpers import create_series_folder_structure, get_safe_folder_name
                from pathlib import Path
                
                LOGGER.info(f"Creating folder structure for imported series: {manga_details.get('title', 'Unknown')} (ID: {series_id})")
                
                # Get the safe folder name
                safe_title = get_safe_folder_name(manga_details.get('title', 'Unknown'))
                
                # Check if folder already exists in any root folder
                folder_already_exists = False
                existing_folder_path = None
                
                # Get root folders from settings
                from backend.internals.settings import Settings
                settings = Settings().get_settings()
                root_folders = settings.root_folders
                
                if root_folders:
                    for root_folder in root_folders:
                        root_path = Path(root_folder['path'])
                        potential_series_dir = root_path / safe_title
                        LOGGER.info(f"Checking if folder already exists: {potential_series_dir}")
                        
                        if potential_series_dir.exists() and potential_series_dir.is_dir():
                            folder_already_exists = True
                            existing_folder_path = potential_series_dir
                            LOGGER.info(f"Found existing folder: {existing_folder_path}")
                            break
                
                # Create the folder if it doesn't exist
                if not folder_already_exists:
                    series_path = create_series_folder_structure(
                        series_id,
                        manga_details.get('title', 'Unknown'),
                        manga_details.get('content_type', inferred_type),
                        collection_id,
                        root_folder_id
                    )
                    LOGGER.info(f"Folder structure created at: {series_path}")
                else:
                    series_path = existing_folder_path
                    LOGGER.info(f"Using existing folder: {series_path}")
            except Exception as e:
                LOGGER.error(f"Error creating folder structure: {e}")
        else:
            LOGGER.info(f"Skipping folder creation for BOOK content type (handled by enhanced import)")
        
        try:
            # Add the series to the collection
            # No-op: linking performed above with add_series_to_collection
            
            # If the folder already existed, scan it for e-books
            if not skip_folder_creation and folder_already_exists:
                LOGGER.info(f"Scanning existing folder for e-books: {series_path}")
                from backend.features.ebook_files import scan_for_ebooks
                scan_stats = scan_for_ebooks(specific_series_id=series_id)
                LOGGER.info(f"Scan results: {scan_stats}")
        except Exception as e:
            LOGGER.error(f"Error creating folder structure or adding to collection: {e}")
            import traceback
            LOGGER.error(traceback.format_exc())
            # Continue even if folder creation fails
        
        # Get author details if available
        author_data = None
        if author_id:
            try:
                author_result = execute_query(
                    "SELECT id, name, biography, birth_date, photo_url FROM authors WHERE id = ?",
                    (author_id,)
                )
                if author_result:
                    author_data = author_result[0]
            except Exception as e:
                LOGGER.debug(f"Could not fetch author details: {e}")
        
        # Try to read metadata from README.txt if it exists and update series with stored metadata
        try:
            from pathlib import Path
            from backend.base.helpers import read_metadata_from_readme, get_safe_folder_name
            from backend.internals.settings import Settings
            
            safe_title = get_safe_folder_name(manga_details.get('title', 'Unknown'))
            settings = Settings().get_settings()
            root_folders = settings.root_folders
            
            if root_folders:
                for root_folder in root_folders:
                    root_path = Path(root_folder['path'])
                    series_dir = root_path / safe_title
                    
                    if series_dir.exists():
                        readme_metadata = read_metadata_from_readme(series_dir)
                        
                        if readme_metadata and readme_metadata.get('cover_url'):
                            # Update series with cover_url from README
                            execute_query("""
                                UPDATE series SET cover_url = ? WHERE id = ?
                            """, (readme_metadata['cover_url'], series_id), commit=True)
                            LOGGER.info(f"Updated series {series_id} with cover URL from README.txt")
                        
                        break
        except Exception as e:
            LOGGER.debug(f"Could not read metadata from README.txt: {e}")
        
        # If description is empty, try to fetch from AI provider
        current_series = execute_query("SELECT description FROM series WHERE id = ?", (series_id,))
        if current_series and not current_series[0].get('description'):
            try:
                LOGGER.info(f"Series {series_id} has no description, attempting to fetch from AI...")
                from backend.features.ai_providers import get_ai_provider_manager
                
                manager = get_ai_provider_manager()
                provider_instance = manager.get_primary_provider()
                
                if provider_instance and provider_instance.is_available():
                    title = manga_details.get('title', 'Unknown')
                    author = manga_details.get('author', '')
                    
                    prompt = f"""Provide a brief, engaging description (2-3 sentences) for the book:
Title: {title}
Author: {author}

Return ONLY the description, no other text."""
                    
                    description_text = provider_instance.chat(prompt)
                    
                    if description_text and description_text.strip():
                        execute_query("""
                            UPDATE series SET description = ? WHERE id = ?
                        """, (description_text.strip(), series_id), commit=True)
                        LOGGER.info(f"Added AI-generated description for series {series_id}")
            except Exception as e:
                LOGGER.debug(f"Could not fetch description from AI: {e}")
        
        # Update the calendar to include the newly imported series with release dates
        try:
            from backend.features.calendar import update_calendar
            LOGGER.info(f"Updating calendar for newly imported series (ID: {series_id})")
            update_calendar(series_id=series_id)
        except Exception as e:
            LOGGER.error(f"Error updating calendar after import: {e}")
            # Continue anyway - we don't want to fail the import if calendar update fails
        
        # Download MangaDex covers for the newly imported series
        try:
            LOGGER.info(f"Attempting to download MangaDex covers for series {series_id}")
            download_mangadex_covers_for_series(series_id, manga_details, provider, manga_id)
        except Exception as e:
            LOGGER.warning(f"Error downloading MangaDex covers for series {series_id}: {e}")
            # Continue anyway - we don't want to fail the import if cover download fails
        
        return {
            "success": True,
            "message": f"Series added to collection with {chapters_added} chapters",
            "series_id": series_id,
            "author": author_data
        }
    except Exception as e:
        LOGGER.error(f"Error importing manga to collection: {e}")
        return {
            "success": False,
            "message": str(e)
        }
