#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Persistence layer for AI provider configuration.

Saves and loads API keys from a config file so they persist across restarts.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional

from backend.base.logging import LOGGER


class AIProviderConfigPersistence:
    """Handles persistence of AI provider configuration."""
    
    CONFIG_DIR = Path("../data")  # Go up one level from backend to data folder
    CONFIG_FILE = CONFIG_DIR / "ai_providers_config.json"
    
    @classmethod
    def ensure_config_dir(cls) -> None:
        """Ensure config directory exists."""
        cls.CONFIG_DIR.mkdir(exist_ok=True)
    
    @classmethod
    def load_config(cls) -> Dict[str, Any]:
        """Load AI provider configuration from file.
        
        Returns:
            Dictionary with provider configurations.
        """
        cls.ensure_config_dir()
        
        if not cls.CONFIG_FILE.exists():
            return {}
        
        try:
            with open(cls.CONFIG_FILE, 'r') as f:
                config = json.load(f)
                LOGGER.info(f"Loaded AI provider config from {cls.CONFIG_FILE}")
                return config
        except Exception as e:
            LOGGER.warning(f"Failed to load AI provider config: {e}")
            return {}
    
    @classmethod
    def save_config(cls, config: Dict[str, Any]) -> bool:
        """Save AI provider configuration to file.
        
        Args:
            config: Configuration dictionary.
            
        Returns:
            True if successful, False otherwise.
        """
        cls.ensure_config_dir()
        
        try:
            with open(cls.CONFIG_FILE, 'w') as f:
                json.dump(config, f, indent=2)
            LOGGER.info(f"Saved AI provider config to {cls.CONFIG_FILE}")
            return True
        except Exception as e:
            LOGGER.error(f"Failed to save AI provider config: {e}")
            return False
    
    @classmethod
    def get_api_key(cls, provider: str) -> Optional[str]:
        """Get API key for a provider.
        
        Args:
            provider: Provider name (groq, gemini, deepseek).
            
        Returns:
            API key or None if not found.
        """
        config = cls.load_config()
        return config.get(f"{provider}_api_key")
    
    @classmethod
    def set_api_key(cls, provider: str, api_key: str) -> bool:
        """Set API key for a provider.
        
        Args:
            provider: Provider name (groq, gemini, deepseek).
            api_key: API key value.
            
        Returns:
            True if successful, False otherwise.
        """
        config = cls.load_config()
        config[f"{provider}_api_key"] = api_key
        return cls.save_config(config)
    
    @classmethod
    def get_ollama_config(cls) -> Dict[str, str]:
        """Get Ollama configuration.
        
        Returns:
            Dictionary with base_url and model.
        """
        config = cls.load_config()
        return {
            "base_url": config.get("ollama_base_url", "http://localhost:11434"),
            "model": config.get("ollama_model", "llama2"),
        }
    
    @classmethod
    def set_ollama_config(cls, base_url: str, model: str) -> bool:
        """Set Ollama configuration.
        
        Args:
            base_url: Ollama server URL.
            model: Model name.
            
        Returns:
            True if successful, False otherwise.
        """
        config = cls.load_config()
        config["ollama_base_url"] = base_url
        config["ollama_model"] = model
        return cls.save_config(config)
    
    @classmethod
    def apply_to_environment(cls) -> None:
        """Apply saved configuration to environment variables."""
        config = cls.load_config()
        
        # Set API keys
        if "groq_api_key" in config:
            os.environ["GROQ_API_KEY"] = config["groq_api_key"]
        if "gemini_api_key" in config:
            os.environ["GEMINI_API_KEY"] = config["gemini_api_key"]
        if "deepseek_api_key" in config:
            os.environ["DEEPSEEK_API_KEY"] = config["deepseek_api_key"]
        
        # Set Ollama config
        if "ollama_base_url" in config:
            os.environ["OLLAMA_BASE_URL"] = config["ollama_base_url"]
        if "ollama_model" in config:
            os.environ["OLLAMA_MODEL"] = config["ollama_model"]
        
        LOGGER.info("Applied saved AI provider configuration to environment")
