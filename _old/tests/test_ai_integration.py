#!/usr/bin/env python3
"""Test AI integration directly without Flask."""

import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

def test_ai_providers():
    """Test AI providers directly."""
    print("=" * 70)
    print("AI PROVIDERS INTEGRATION TEST")
    print("=" * 70)
    print()
    
    # Test 1: Import AI providers
    print("Test 1: Importing AI providers...")
    try:
        from backend.features.ai_providers import (
            get_ai_provider_manager,
            initialize_ai_providers
        )
        print("✓ Successfully imported AI providers")
    except Exception as e:
        print(f"✗ Failed to import: {e}")
        return False
    
    print()
    
    # Test 2: Initialize AI providers
    print("Test 2: Initializing AI providers...")
    try:
        manager = initialize_ai_providers()
        print("✓ AI providers initialized")
    except Exception as e:
        print(f"✗ Failed to initialize: {e}")
        return False
    
    print()
    
    # Test 3: Check registered providers
    print("Test 3: Checking registered providers...")
    try:
        manager = get_ai_provider_manager()
        providers = manager.get_all_providers()
        print(f"✓ Found {len(providers)} providers:")
        for provider in providers:
            status = "Available" if provider.is_available() else "Not Available"
            print(f"  - {provider.name}: {status}")
    except Exception as e:
        print(f"✗ Failed to check providers: {e}")
        return False
    
    print()
    
    # Test 4: Check for API key
    print("Test 4: Checking for Groq API key...")
    groq_key = os.getenv("GROQ_API_KEY")
    if groq_key:
        masked_key = groq_key[:10] + "..." + groq_key[-5:]
        print(f"✓ GROQ_API_KEY is set: {masked_key}")
    else:
        print("✗ GROQ_API_KEY is not set")
        print("  To set it, run: export GROQ_API_KEY=gsk_your_key_here")
    
    print()
    
    # Test 5: Try to get Groq provider
    print("Test 5: Getting Groq provider...")
    try:
        manager = get_ai_provider_manager()
        groq = manager.get_provider("groq")
        if groq:
            print(f"✓ Groq provider found")
            print(f"  - Available: {groq.is_available()}")
            print(f"  - Enabled: {groq.enabled}")
        else:
            print("✗ Groq provider not found")
    except Exception as e:
        print(f"✗ Failed to get Groq provider: {e}")
        return False
    
    print()
    
    # Test 6: Try to extract metadata (if API key is set)
    print("Test 6: Testing metadata extraction...")
    try:
        manager = get_ai_provider_manager()
        groq = manager.get_provider("groq")
        
        if not groq:
            print("✗ Groq provider not available")
            return False
        
        if not groq.is_available():
            print("✗ Groq provider is not available (API key not set)")
            print("  Set GROQ_API_KEY environment variable and try again")
            return False
        
        print("  Attempting to extract metadata for 'Attack on Titan'...")
        metadata = groq.extract_manga_metadata("Attack on Titan", known_chapters=139)
        
        if metadata:
            print(f"✓ Metadata extraction successful!")
            print(f"  - Title: {metadata.title}")
            print(f"  - Volumes: {metadata.volumes}")
            print(f"  - Chapters: {metadata.chapters}")
            print(f"  - Status: {metadata.status}")
            print(f"  - Confidence: {metadata.confidence}")
            print(f"  - Source: {metadata.source}")
        else:
            print("✗ Metadata extraction returned None")
            return False
    
    except Exception as e:
        print(f"✗ Metadata extraction failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print()
    print("=" * 70)
    print("ALL TESTS PASSED! ✓")
    print("=" * 70)
    return True

if __name__ == "__main__":
    success = test_ai_providers()
    sys.exit(0 if success else 1)
