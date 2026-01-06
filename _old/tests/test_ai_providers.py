#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test script for AI providers.

This script tests all configured AI providers and shows their capabilities.

Usage:
    python test_ai_providers.py
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from backend.base.logging import setup_logging
from backend.features.ai_providers import (
    get_ai_provider_manager,
    AIProviderConfig,
    extract_metadata_with_ai,
)


def print_header(text: str):
    """Print a formatted header."""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70)


def test_configuration():
    """Test and display current configuration."""
    print_header("AI Provider Configuration")
    AIProviderConfig.print_configuration()


def test_providers():
    """Test all registered providers."""
    print_header("Testing AI Providers")
    
    manager = get_ai_provider_manager()
    
    print(f"\nTotal providers registered: {len(manager.get_all_providers())}")
    print("\nProvider Status:")
    print("-" * 70)
    
    for provider in manager.get_all_providers():
        status = "✓ AVAILABLE" if provider.is_available() else "✗ NOT AVAILABLE"
        print(f"  {provider.name:15} {status}")
    
    if not manager.get_all_providers():
        print("\n⚠️  No AI providers are configured!")
        print("Please set at least one API key:")
        print("  - GROQ_API_KEY")
        print("  - GEMINI_API_KEY")
        print("  - DEEPSEEK_API_KEY")
        print("  - Or start Ollama server")
        return False
    
    return True


def test_metadata_extraction():
    """Test metadata extraction with sample manga."""
    print_header("Testing Metadata Extraction")
    
    test_cases = [
        ("Attack on Titan", 139),
        ("One Piece", 1000),
        ("Demon Slayer", 205),
        ("Jujutsu Kaisen", 271),
    ]
    
    manager = get_ai_provider_manager()
    
    for manga_title, known_chapters in test_cases:
        print(f"\nExtracting metadata for: {manga_title}")
        print(f"  Known chapters: {known_chapters}")
        print("-" * 70)
        
        try:
            # Test with fallback
            metadata = manager.extract_metadata_with_fallback(
                manga_title=manga_title,
                known_chapters=known_chapters
            )
            
            if metadata:
                print(f"  ✓ Success!")
                print(f"    Volumes: {metadata.volumes}")
                print(f"    Chapters: {metadata.chapters}")
                print(f"    Status: {metadata.status}")
                print(f"    Source: {metadata.source}")
                print(f"    Confidence: {metadata.confidence:.1%}")
                if metadata.next_release_date:
                    print(f"    Next Release: {metadata.next_release_date}")
            else:
                print(f"  ✗ Failed - No metadata returned")
        
        except Exception as e:
            print(f"  ✗ Error: {e}")


def test_parallel_extraction():
    """Test parallel extraction from all providers."""
    print_header("Testing Parallel Extraction")
    
    manga_title = "Attack on Titan"
    print(f"\nExtracting from all providers for: {manga_title}")
    print("-" * 70)
    
    manager = get_ai_provider_manager()
    
    try:
        metadata = manager.extract_metadata_parallel(
            manga_title=manga_title,
            known_chapters=139
        )
        
        if metadata:
            print(f"\n✓ Best result selected:")
            print(f"  Source: {metadata.source}")
            print(f"  Volumes: {metadata.volumes}")
            print(f"  Chapters: {metadata.chapters}")
            print(f"  Confidence: {metadata.confidence:.1%}")
        else:
            print(f"\n✗ No results from any provider")
    
    except Exception as e:
        print(f"\n✗ Error: {e}")


def test_integration_function():
    """Test the integration function."""
    print_header("Testing Integration Function")
    
    manga_title = "Demon Slayer"
    print(f"\nUsing extract_metadata_with_ai() for: {manga_title}")
    print("-" * 70)
    
    try:
        metadata = extract_metadata_with_ai(
            manga_title=manga_title,
            known_chapters=205
        )
        
        if metadata:
            print(f"\n✓ Success!")
            print(f"  Volumes: {metadata.volumes}")
            print(f"  Chapters: {metadata.chapters}")
            print(f"  Status: {metadata.status}")
            print(f"  Source: {metadata.source}")
        else:
            print(f"\n✗ Failed - No metadata returned")
    
    except Exception as e:
        print(f"\n✗ Error: {e}")


def main():
    """Run all tests."""
    print("\n" + "=" * 70)
    print("  AI Providers Test Suite")
    print("=" * 70)
    
    # Setup logging
    setup_logging(None, None)
    
    # Test configuration
    test_configuration()
    
    # Test providers
    if not test_providers():
        print("\n⚠️  Skipping extraction tests - no providers available")
        return
    
    # Test metadata extraction
    test_metadata_extraction()
    
    # Test parallel extraction
    test_parallel_extraction()
    
    # Test integration function
    test_integration_function()
    
    # Summary
    print_header("Test Summary")
    print("\n✓ All tests completed!")
    print("\nNext steps:")
    print("  1. Check the results above")
    print("  2. If no providers are available, set API keys:")
    print("     - export GROQ_API_KEY=your_key")
    print("     - export GEMINI_API_KEY=your_key")
    print("     - export DEEPSEEK_API_KEY=your_key")
    print("  3. Or start Ollama: ollama serve")
    print("  4. Re-run this test")
    print("\nDocumentation:")
    print("  - Quick Start: docs/AI_PROVIDERS_QUICKSTART.md")
    print("  - Full Docs: docs/AI_PROVIDERS.md")
    print("\n" + "=" * 70 + "\n")


if __name__ == "__main__":
    main()
