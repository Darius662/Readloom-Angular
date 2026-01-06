#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
API endpoints for AI provider management and testing.
"""

from flask import Blueprint, jsonify, request
from backend.base.logging import LOGGER
from backend.features.ai_providers.persistence import AIProviderConfigPersistence

# Create API blueprint
ai_providers_api_bp = Blueprint('api_ai_providers', __name__)

# Log that the blueprint was created
LOGGER.info("AI Providers API blueprint created")


@ai_providers_api_bp.route('/ai-providers/status', methods=['GET'])
def get_ai_providers_status():
    """Get status of all AI providers.
    
    Returns:
        Response: Status of each provider.
    """
    try:
        from backend.features.ai_providers.manager import initialize_ai_providers
        manager = initialize_ai_providers()
        
        providers = {}
        for provider_name in ['groq', 'gemini', 'deepseek', 'ollama']:
            provider = manager.get_provider(provider_name)
            providers[provider_name] = {
                'available': provider.is_available() if provider else False,
                'configured': provider is not None
            }
        
        return jsonify({'providers': providers}), 200
    except Exception as e:
        LOGGER.error(f"Error getting AI providers status: {e}")
        return jsonify({"error": str(e)}), 500


@ai_providers_api_bp.route('/ai-providers/config', methods=['GET'])
def get_ai_provider_config():
    """Get AI provider configuration.
    
    Returns:
        Response: Current configuration.
    """
    try:
        config = AIProviderConfigPersistence.load_config()
        LOGGER.info(f"Retrieved AI provider config: {len(config)} settings")
        return jsonify(config), 200
    except Exception as e:
        LOGGER.error(f"Error getting AI provider config: {e}")
        return jsonify({"error": str(e)}), 500


@ai_providers_api_bp.route('/ai-providers/config', methods=['POST'])
def save_ai_provider_config():
    """Save AI provider configuration.
    
    Request body:
        {
            "provider": "groq",
            "api_key": "...",
            "enabled": true
        }
        
    Returns:
        Response: Save result.
    """
    try:
        data = request.json or {}
        LOGGER.info(f"Save AI config request received: {data}")
        
        provider = data.get('provider', '').lower()
        api_key = data.get('api_key')
        enabled = data.get('enabled', True)
        
        LOGGER.info(f"Provider: {provider}, API key length: {len(api_key) if api_key else 0}, Enabled: {enabled}")
        
        if not provider:
            return jsonify({"error": "Missing provider name"}), 400
        
        # Save to config file
        if provider == 'groq' and api_key:
            LOGGER.info(f"Saving Groq API key...")
            result = AIProviderConfigPersistence.set_api_key('groq', api_key)
            LOGGER.info(f"Groq save result: {result}")
        elif provider == 'gemini' and api_key:
            LOGGER.info(f"Saving Gemini API key...")
            result = AIProviderConfigPersistence.set_api_key('gemini', api_key)
            LOGGER.info(f"Gemini save result: {result}")
        elif provider == 'deepseek' and api_key:
            LOGGER.info(f"Saving DeepSeek API key...")
            result = AIProviderConfigPersistence.set_api_key('deepseek', api_key)
            LOGGER.info(f"DeepSeek save result: {result}")
        elif provider == 'ollama':
            LOGGER.info(f"Saving Ollama config...")
            result = AIProviderConfigPersistence.set_ollama_config(
                data.get('base_url', 'http://localhost:11434'),
                data.get('model', 'llama2')
            )
            LOGGER.info(f"Ollama save result: {result}")
        else:
            LOGGER.warning(f"Unknown provider or missing API key: {provider}")
        
        # Reinitialize AI providers
        try:
            from backend.features.ai_providers.manager import initialize_ai_providers
            initialize_ai_providers()
            LOGGER.info("AI providers reinitialized successfully")
        except Exception as e:
            LOGGER.warning(f"Could not reinitialize AI providers: {e}")
        
        return jsonify({"success": True, "message": f"{provider.capitalize()} configuration saved"}), 200
    except Exception as e:
        LOGGER.error(f"Error saving AI provider config: {e}")
        import traceback
        LOGGER.error(traceback.format_exc())
        return jsonify({"error": str(e)}), 500


@ai_providers_api_bp.route('/ai-providers/test', methods=['POST'])
def test_ai_provider():
    """Test an AI provider.
    
    Request body:
        {
            "provider": "groq"
        }
        
    Returns:
        Response: Test result.
    """
    LOGGER.info("test_ai_provider endpoint called")
    try:
        data = request.json or {}
        provider = data.get('provider', '').lower()
        LOGGER.info(f"Testing provider: {provider}")
        
        if not provider:
            return jsonify({"error": "Missing provider name"}), 400
        
        # Reinitialize AI providers to pick up any new API keys
        from backend.features.ai_providers.manager import initialize_ai_providers
        LOGGER.info(f"Reinitializing AI providers to pick up new configuration...")
        manager = initialize_ai_providers()
        
        # Get the provider directly from the manager's internal list (including unavailable ones)
        provider_obj = None
        for p in manager.providers:
            if p.name.lower() == provider.lower():
                provider_obj = p
                break
        
        # Also check for providers that weren't registered due to missing config
        if not provider_obj:
            # Try to instantiate the provider directly to test it
            if provider == 'groq':
                from backend.features.ai_providers.groq_provider import GroqProvider
                provider_obj = GroqProvider()
            elif provider == 'gemini':
                from backend.features.ai_providers.gemini_provider import GeminiProvider
                provider_obj = GeminiProvider()
            elif provider == 'deepseek':
                from backend.features.ai_providers.deepseek_provider import DeepSeekProvider
                provider_obj = DeepSeekProvider()
            elif provider == 'ollama':
                from backend.features.ai_providers.ollama_provider import OllamaProvider
                provider_obj = OllamaProvider()
        
        if not provider_obj:
            return jsonify({"error": f"Provider {provider} not found"}), 404
        
        if not provider_obj.is_available():
            return jsonify({"error": f"Provider {provider} is not available. Please configure API key or check server status."}), 400
        
        # Try to extract metadata for a test manga
        LOGGER.info(f"Testing {provider} provider with 'Attack on Titan'...")
        metadata = provider_obj.extract_manga_metadata("Attack on Titan", known_chapters=139)
        
        if metadata:
            LOGGER.info(f"✓ {provider} provider test successful!")
            return jsonify({
                "message": f"✓ {provider.capitalize()} provider is working!",
                "metadata": {
                    "title": metadata.title,
                    "volumes": metadata.volumes,
                    "chapters": metadata.chapters,
                    "status": metadata.status,
                    "confidence": metadata.confidence
                }
            })
        else:
            LOGGER.warning(f"{provider} provider returned no metadata")
            return jsonify({"error": f"Provider {provider} returned no metadata"}), 500
    
    except Exception as e:
        LOGGER.error(f"Error testing AI provider: {e}")
        import traceback
        LOGGER.error(traceback.format_exc())
        return jsonify({"error": f"Test failed: {str(e)}"}), 500
