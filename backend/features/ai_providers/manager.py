#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
AI Provider Manager - Initializes and manages all AI providers with fallback logic.
"""

from typing import Optional
from backend.base.logging import LOGGER

from .base import AIProviderManager
from .groq_provider import GroqProvider
from .gemini_provider import GeminiProvider
from .deepseek_provider import DeepSeekProvider
from .ollama_provider import OllamaProvider


# Global instance
_manager: Optional[AIProviderManager] = None


def initialize_ai_providers() -> AIProviderManager:
    """Initialize all AI providers with fallback chain.
    
    Priority order:
    1. Groq (fastest, free, generous limits)
    2. Gemini (powerful, free tier)
    3. DeepSeek (reasoning models, free tier)
    4. Ollama (self-hosted, no external dependencies)
    
    Returns:
        Initialized AIProviderManager instance.
    """
    global _manager
    
    # Load saved configuration from file
    from .persistence import AIProviderConfigPersistence
    AIProviderConfigPersistence.apply_to_environment()
    
    manager = AIProviderManager()
    
    LOGGER.info("Initializing AI providers...")
    
    # Register providers in priority order
    # 1. Groq - Fastest and most reliable free option
    groq_provider = GroqProvider()
    manager.register_provider(groq_provider)
    
    # 2. Gemini - Powerful alternative
    gemini_provider = GeminiProvider()
    manager.register_provider(gemini_provider)
    
    # 3. DeepSeek - Good reasoning capabilities
    deepseek_provider = DeepSeekProvider()
    manager.register_provider(deepseek_provider)
    
    # 4. Ollama - Self-hosted option
    ollama_provider = OllamaProvider()
    manager.register_provider(ollama_provider)
    
    _manager = manager
    
    providers_info = manager.to_dict()
    LOGGER.info(f"AI providers initialized: {providers_info['count']} providers available")
    for provider in providers_info['providers']:
        status = "[OK]" if provider['available'] else "[FAIL]"
        LOGGER.info(f"  {status} {provider['name']}")
    
    return manager


def get_ai_provider_manager() -> AIProviderManager:
    """Get the global AI provider manager instance.
    
    Initializes if not already done.
    
    Returns:
        AIProviderManager instance.
    """
    global _manager
    
    if _manager is None:
        _manager = initialize_ai_providers()
    
    return _manager
