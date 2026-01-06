#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Configuration for AI providers.

This module handles loading and managing AI provider configurations from
environment variables and saved JSON configuration.
"""

import os
from typing import Dict, Any, Optional
from backend.base.logging import LOGGER
from backend.features.ai_providers.persistence import AIProviderConfigPersistence


class AIProviderConfig:
    """Configuration manager for AI providers."""

    # Default configuration
    DEFAULTS = {
        "groq": {
            "enabled": True,
            "api_key_env": "GROQ_API_KEY",
            "model": "mixtral-8x7b-32768",
        },
        "gemini": {
            "enabled": True,
            "api_key_env": "GEMINI_API_KEY",
            "model": "gemini-2.5-pro",
        },
        "deepseek": {
            "enabled": True,
            "api_key_env": "DEEPSEEK_API_KEY",
            "model": "deepseek-chat",
        },
        "ollama": {
            "enabled": True,
            "base_url": "http://localhost:11434",
            "model": "llama2",
        },
    }

    @classmethod
    def _ensure_config_loaded(cls) -> None:
        """Ensure saved configuration is applied to environment variables."""
        try:
            AIProviderConfigPersistence.apply_to_environment()
        except Exception as e:
            LOGGER.warning(f"Could not apply saved AI provider configuration: {e}")

    @classmethod
    def get_groq_config(cls) -> Dict[str, Any]:
        """Get Groq provider configuration.
        
        Returns:
            Configuration dictionary.
        """
        cls._ensure_config_loaded()
        config = cls.DEFAULTS["groq"].copy()
        config["api_key"] = os.getenv(config["api_key_env"])
        config["enabled"] = config["api_key"] is not None
        return config

    @classmethod
    def get_gemini_config(cls) -> Dict[str, Any]:
        """Get Gemini provider configuration.
        
        Returns:
            Configuration dictionary.
        """
        cls._ensure_config_loaded()
        config = cls.DEFAULTS["gemini"].copy()
        config["api_key"] = os.getenv(config["api_key_env"])
        config["enabled"] = config["api_key"] is not None
        return config

    @classmethod
    def get_deepseek_config(cls) -> Dict[str, Any]:
        """Get DeepSeek provider configuration.
        
        Returns:
            Configuration dictionary.
        """
        cls._ensure_config_loaded()
        config = cls.DEFAULTS["deepseek"].copy()
        config["api_key"] = os.getenv(config["api_key_env"])
        config["enabled"] = config["api_key"] is not None
        return config

    @classmethod
    def get_ollama_config(cls) -> Dict[str, Any]:
        """Get Ollama provider configuration.
        
        Returns:
            Configuration dictionary.
        """
        cls._ensure_config_loaded()
        config = cls.DEFAULTS["ollama"].copy()
        config["base_url"] = os.getenv("OLLAMA_BASE_URL", config["base_url"])
        config["model"] = os.getenv("OLLAMA_MODEL", config["model"])
        # Ollama is always enabled (it's self-hosted)
        config["enabled"] = True
        return config

    @classmethod
    def get_all_configs(cls) -> Dict[str, Dict[str, Any]]:
        """Get all provider configurations.
        
        Returns:
            Dictionary mapping provider names to configurations.
        """
        cls._ensure_config_loaded()
        return {
            "groq": cls.get_groq_config(),
            "gemini": cls.get_gemini_config(),
            "deepseek": cls.get_deepseek_config(),
            "ollama": cls.get_ollama_config(),
        }

    @classmethod
    def print_configuration(cls) -> None:
        """Print current configuration (for debugging)."""
        LOGGER.info("=" * 60)
        LOGGER.info("AI Provider Configuration")
        LOGGER.info("=" * 60)
        
        configs = cls.get_all_configs()
        
        for provider_name, config in configs.items():
            enabled = config.get("enabled", False)
            status = "[ENABLED]" if enabled else "[DISABLED]"
            LOGGER.info(f"\n{provider_name.upper()}: {status}")
            
            if provider_name == "ollama":
                LOGGER.info(f"  Base URL: {config.get('base_url')}")
                LOGGER.info(f"  Model: {config.get('model')}")
            else:
                api_key_env = config.get("api_key_env")
                has_key = "[YES]" if config.get("api_key") else "[NO]"
                LOGGER.info(f"  API Key ({api_key_env}): {has_key}")
                LOGGER.info(f"  Model: {config.get('model')}")
        
        LOGGER.info("\n" + "=" * 60)
        LOGGER.info("To enable providers, set the following environment variables:")
        LOGGER.info("  GROQ_API_KEY=your_key")
        LOGGER.info("  GEMINI_API_KEY=your_key")
        LOGGER.info("  DEEPSEEK_API_KEY=your_key")
        LOGGER.info("  OLLAMA_BASE_URL=http://localhost:11434 (optional)")
        LOGGER.info("  OLLAMA_MODEL=llama2 (optional)")
        LOGGER.info("=" * 60)


def setup_ai_providers_from_config() -> None:
    """Setup AI providers from configuration.
    
    This function should be called during application initialization.
    """
    AIProviderConfig.print_configuration()
