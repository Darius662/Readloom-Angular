#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Base classes for AI providers.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
import logging

from backend.base.logging import LOGGER


@dataclass
class MangaMetadata:
    """Structured manga metadata from AI."""
    title: str
    volumes: int
    chapters: int
    status: str  # ONGOING, COMPLETED, HIATUS, etc.
    release_dates: Dict[int, str]  # volume_number -> release_date
    next_release_date: Optional[str] = None
    confidence: float = 0.8  # 0.0-1.0 confidence score
    source: str = "unknown"
    raw_response: Optional[str] = None


class AIProvider(ABC):
    """Base class for AI providers."""

    def __init__(self, name: str, enabled: bool = True, api_key: Optional[str] = None):
        """Initialize the AI provider.
        
        Args:
            name: The name of the provider.
            enabled: Whether the provider is enabled.
            api_key: Optional API key for the provider.
        """
        self.name = name
        self.enabled = enabled
        self.api_key = api_key
        self.logger = LOGGER

    @abstractmethod
    def extract_manga_metadata(self, manga_title: str, known_chapters: Optional[int] = None) -> Optional[MangaMetadata]:
        """Extract manga metadata using AI.
        
        Args:
            manga_title: The title of the manga.
            known_chapters: Optional known chapter count for context.
            
        Returns:
            MangaMetadata object or None if extraction failed.
        """
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if the provider is available and properly configured.
        
        Returns:
            True if provider is ready to use, False otherwise.
        """
        pass

    def to_dict(self) -> Dict[str, Any]:
        """Convert provider to dictionary.
        
        Returns:
            Dictionary representation of the provider.
        """
        return {
            "name": self.name,
            "enabled": self.enabled,
            "available": self.is_available(),
        }


class AIProviderManager:
    """Manager for AI providers with fallback logic."""

    def __init__(self):
        """Initialize the AI provider manager."""
        self.providers: List[AIProvider] = []
        self.logger = LOGGER

    def register_provider(self, provider: AIProvider) -> None:
        """Register an AI provider.
        
        Args:
            provider: The provider to register.
        """
        if provider.is_available():
            self.providers.append(provider)
            self.logger.info(f"Registered AI provider: {provider.name}")
        else:
            self.logger.warning(f"AI provider {provider.name} is not available (missing config)")

    def get_provider(self, name: str) -> Optional[AIProvider]:
        """Get a provider by name.
        
        Args:
            name: The name of the provider.
            
        Returns:
            The provider or None if not found.
        """
        for provider in self.providers:
            if provider.name.lower() == name.lower():
                return provider
        return None

    def get_all_providers(self) -> List[AIProvider]:
        """Get all registered providers.
        
        Returns:
            List of all providers.
        """
        return self.providers

    def extract_metadata_with_fallback(self, manga_title: str, known_chapters: Optional[int] = None) -> Optional[MangaMetadata]:
        """Extract metadata using first available provider with fallback.
        
        Args:
            manga_title: The title of the manga.
            known_chapters: Optional known chapter count for context.
            
        Returns:
            MangaMetadata from first successful provider, or None if all fail.
        """
        if not self.providers:
            self.logger.warning("No AI providers registered")
            return None

        for provider in self.providers:
            try:
                if not provider.enabled:
                    self.logger.debug(f"Skipping disabled provider: {provider.name}")
                    continue

                self.logger.info(f"Attempting to extract metadata using {provider.name}")
                metadata = provider.extract_manga_metadata(manga_title, known_chapters)
                
                if metadata:
                    self.logger.info(f"Successfully extracted metadata using {provider.name}")
                    return metadata
                else:
                    self.logger.debug(f"{provider.name} returned no metadata")
                    
            except Exception as e:
                self.logger.warning(f"Error with {provider.name}: {e}")
                continue

        self.logger.warning(f"All AI providers failed to extract metadata for {manga_title}")
        return None

    def extract_metadata_parallel(self, manga_title: str, known_chapters: Optional[int] = None) -> Optional[MangaMetadata]:
        """Extract metadata using all providers and return best result.
        
        Args:
            manga_title: The title of the manga.
            known_chapters: Optional known chapter count for context.
            
        Returns:
            MangaMetadata with highest confidence score.
        """
        from concurrent.futures import ThreadPoolExecutor, as_completed

        if not self.providers:
            self.logger.warning("No AI providers registered")
            return None

        results = []

        with ThreadPoolExecutor(max_workers=len(self.providers)) as executor:
            futures = {}
            for provider in self.providers:
                if provider.enabled:
                    future = executor.submit(
                        provider.extract_manga_metadata,
                        manga_title,
                        known_chapters
                    )
                    futures[future] = provider.name

            for future in as_completed(futures):
                provider_name = futures[future]
                try:
                    metadata = future.result(timeout=30)
                    if metadata:
                        results.append(metadata)
                        self.logger.info(f"{provider_name} returned metadata with confidence {metadata.confidence}")
                except Exception as e:
                    self.logger.warning(f"Error with {provider_name}: {e}")

        if not results:
            self.logger.warning(f"All AI providers failed to extract metadata for {manga_title}")
            return None

        # Return result with highest confidence
        best_result = max(results, key=lambda x: x.confidence)
        self.logger.info(f"Selected best result from {best_result.source} with confidence {best_result.confidence}")
        return best_result

    def to_dict(self) -> Dict[str, Any]:
        """Convert manager to dictionary.
        
        Returns:
            Dictionary representation of all providers.
        """
        return {
            "providers": [provider.to_dict() for provider in self.providers],
            "count": len(self.providers),
        }
