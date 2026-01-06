#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
AI Providers package for metadata enrichment.

This package provides multiple AI providers for extracting accurate manga metadata
including volumes, chapters, and release dates.
"""

from .base import AIProvider, AIProviderManager, MangaMetadata
from .groq_provider import GroqProvider
from .gemini_provider import GeminiProvider
from .deepseek_provider import DeepSeekProvider
from .ollama_provider import OllamaProvider
from .manager import get_ai_provider_manager, initialize_ai_providers
from .config import AIProviderConfig, setup_ai_providers_from_config
from .integration import (
    extract_metadata_with_ai,
    get_volumes_and_chapters_from_ai,
    enhance_metadata_with_ai,
    add_ai_to_mangainfo_provider,
)

__all__ = [
    # Base classes
    "AIProvider",
    "AIProviderManager",
    "MangaMetadata",
    # Providers
    "GroqProvider",
    "GeminiProvider",
    "DeepSeekProvider",
    "OllamaProvider",
    # Manager
    "get_ai_provider_manager",
    "initialize_ai_providers",
    # Configuration
    "AIProviderConfig",
    "setup_ai_providers_from_config",
    # Integration
    "extract_metadata_with_ai",
    "get_volumes_and_chapters_from_ai",
    "enhance_metadata_with_ai",
    "add_ai_to_mangainfo_provider",
]
