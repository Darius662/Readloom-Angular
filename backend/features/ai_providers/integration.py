#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Integration module for AI providers with existing metadata system.

This module provides utilities to integrate AI providers into the existing
MangaInfoProvider and metadata extraction pipeline.
"""

from typing import Optional, Tuple
from backend.base.logging import LOGGER

from .base import MangaMetadata
from .manager import get_ai_provider_manager


def extract_metadata_with_ai(
    manga_title: str,
    known_chapters: Optional[int] = None,
    use_parallel: bool = False
) -> Optional[MangaMetadata]:
    """Extract manga metadata using AI providers.
    
    This is the main entry point for AI metadata extraction.
    
    Args:
        manga_title: The title of the manga.
        known_chapters: Optional known chapter count for context.
        use_parallel: If True, use parallel extraction for best result.
                     If False, use fallback chain (faster).
    
    Returns:
        MangaMetadata object or None if extraction failed.
    """
    manager = get_ai_provider_manager()
    
    if use_parallel:
        return manager.extract_metadata_parallel(manga_title, known_chapters)
    else:
        return manager.extract_metadata_with_fallback(manga_title, known_chapters)


def get_volumes_and_chapters_from_ai(
    manga_title: str,
    known_chapters: Optional[int] = None
) -> Tuple[int, int, str]:
    """Extract volumes and chapters from AI providers.
    
    This function is designed to integrate with the existing MangaInfoProvider
    as a new scraping source.
    
    Args:
        manga_title: The title of the manga.
        known_chapters: Optional known chapter count for context.
    
    Returns:
        Tuple of (chapters, volumes, source) where source is "ai_provider"
    """
    try:
        metadata = extract_metadata_with_ai(manga_title, known_chapters)
        
        if metadata and metadata.chapters > 0 and metadata.volumes > 0:
            LOGGER.info(f"AI extraction successful for {manga_title}: "
                       f"{metadata.chapters} chapters, {metadata.volumes} volumes "
                       f"(confidence: {metadata.confidence}, source: {metadata.source})")
            return (metadata.chapters, metadata.volumes, f"ai_provider_{metadata.source.lower()}")
        else:
            LOGGER.warning(f"AI extraction failed or returned invalid data for {manga_title}")
            return (0, 0, "ai_provider_failed")
    
    except Exception as e:
        LOGGER.error(f"Error during AI extraction for {manga_title}: {e}")
        return (0, 0, "ai_provider_error")


def should_use_ai_provider(
    manga_title: str,
    existing_chapters: int = 0,
    existing_volumes: int = 0
) -> bool:
    """Determine if AI provider should be used for this manga.
    
    Args:
        manga_title: The title of the manga.
        existing_chapters: Existing chapter count from other sources.
        existing_volumes: Existing volume count from other sources.
    
    Returns:
        True if AI provider should be used, False otherwise.
    """
    # Use AI if we don't have reliable data
    if existing_chapters == 0 or existing_volumes == 0:
        return True
    
    # Use AI for verification if data seems incomplete
    if existing_volumes < 2 and existing_chapters > 50:
        # Likely incomplete volume data
        return True
    
    return False


def enhance_metadata_with_ai(
    manga_title: str,
    existing_chapters: int = 0,
    existing_volumes: int = 0,
    existing_status: str = ""
) -> dict:
    """Enhance existing metadata with AI verification and additional data.
    
    Args:
        manga_title: The title of the manga.
        existing_chapters: Existing chapter count.
        existing_volumes: Existing volume count.
        existing_status: Existing status (ONGOING, COMPLETED, etc.)
    
    Returns:
        Dictionary with enhanced metadata.
    """
    result = {
        "chapters": existing_chapters,
        "volumes": existing_volumes,
        "status": existing_status,
        "ai_verified": False,
        "ai_source": None,
        "confidence": 0.0,
    }
    
    try:
        metadata = extract_metadata_with_ai(manga_title, existing_chapters)
        
        if metadata:
            # Use AI data if it's more complete or has higher confidence
            if metadata.confidence > 0.8:
                result["chapters"] = metadata.chapters
                result["volumes"] = metadata.volumes
                result["status"] = metadata.status
                result["ai_verified"] = True
                result["ai_source"] = metadata.source
                result["confidence"] = metadata.confidence
                
                LOGGER.info(f"Metadata enhanced with AI for {manga_title} "
                           f"(confidence: {metadata.confidence})")
            else:
                LOGGER.debug(f"AI confidence too low for {manga_title} "
                            f"({metadata.confidence}), keeping existing data")
    
    except Exception as e:
        LOGGER.warning(f"Error enhancing metadata with AI for {manga_title}: {e}")
    
    return result


# Integration with MangaInfoProvider
def add_ai_to_mangainfo_provider():
    """Add AI provider as a scraping source to MangaInfoProvider.
    
    This function should be called during application initialization
    to integrate AI providers into the existing metadata system.
    """
    try:
        from backend.features.scrapers.mangainfo.provider import MangaInfoProvider
        
        # Store reference to original _scrape_data method
        original_scrape = MangaInfoProvider._scrape_data
        
        def enhanced_scrape_data(self, manga_title: str) -> Tuple[int, int, str]:
            """Enhanced scrape data with AI fallback."""
            # Try original scraping first
            chapters, volumes, source = original_scrape(self, manga_title)
            
            # If original scraping didn't work well, try AI
            if chapters == 0 or volumes == 0 or source == "fallback":
                LOGGER.info(f"Original scraping incomplete for {manga_title}, trying AI provider")
                ai_chapters, ai_volumes, ai_source = get_volumes_and_chapters_from_ai(
                    manga_title,
                    chapters if chapters > 0 else None
                )
                
                if ai_chapters > 0 and ai_volumes > 0:
                    chapters = ai_chapters
                    volumes = ai_volumes
                    source = ai_source
                    LOGGER.info(f"AI provider provided data for {manga_title}")
            
            return (chapters, volumes, source)
        
        # Monkey-patch the method
        MangaInfoProvider._scrape_data = enhanced_scrape_data
        LOGGER.info("AI provider integrated into MangaInfoProvider")
        
    except Exception as e:
        LOGGER.warning(f"Could not integrate AI provider into MangaInfoProvider: {e}")
