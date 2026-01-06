#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Utility script to enrich series descriptions using AI.
This script will:
1. Find all series without descriptions
2. Use AI provider to generate descriptions
3. Update series with generated descriptions
"""

import sys
import json
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from backend.base.logging import LOGGER
from backend.internals.db import execute_query
from backend.features.ai_providers import get_ai_provider_manager


def enrich_series_descriptions() -> dict:
    """
    Enrich series descriptions using AI provider.
    
    Returns:
        dict: Statistics about the enrichment operation
    """
    stats = {
        "series_checked": 0,
        "descriptions_added": 0,
        "errors": 0
    }
    
    try:
        # Get AI provider manager
        manager = get_ai_provider_manager()
        provider = manager.get_primary_provider()
        
        if not provider or not provider.is_available():
            LOGGER.warning("No AI provider available for description enrichment")
            return {
                "series_checked": 0,
                "descriptions_added": 0,
                "errors": 1,
                "message": "No AI provider available"
            }
        
        # Find all series without descriptions
        series_list = execute_query("""
            SELECT id, title, author FROM series 
            WHERE description IS NULL OR description = ''
            ORDER BY title ASC
        """)
        
        if not series_list:
            LOGGER.info("All series already have descriptions")
            return stats
        
        stats["series_checked"] = len(series_list)
        LOGGER.info(f"Found {len(series_list)} series without descriptions")
        
        for series in series_list:
            try:
                series_id = series['id']
                title = series['title']
                author = series.get('author', '')
                
                LOGGER.info(f"Generating description for: {title}")
                
                # Create prompt for AI
                prompt = f"""Provide a brief, engaging description (2-3 sentences) for the book:
Title: {title}
Author: {author}

Return ONLY the description, no other text."""
                
                # Get description from AI
                description = provider.chat(prompt)
                
                if description and description.strip():
                    # Update series with description
                    execute_query("""
                        UPDATE series SET description = ? WHERE id = ?
                    """, (description.strip(), series_id), commit=True)
                    
                    stats["descriptions_added"] += 1
                    LOGGER.info(f"Added description for {title}: {description[:50]}...")
                else:
                    LOGGER.warning(f"AI provider returned empty description for {title}")
            
            except Exception as e:
                LOGGER.error(f"Error enriching series {series.get('title', 'Unknown')}: {e}")
                stats["errors"] += 1
        
        return stats
    
    except Exception as e:
        LOGGER.error(f"Error in enrich_series_descriptions: {e}")
        import traceback
        LOGGER.error(traceback.format_exc())
        stats["errors"] += 1
        return stats


def main():
    """Run the description enrichment utility."""
    print("=" * 70)
    print("Readloom Series Description Enrichment Utility")
    print("=" * 70)
    print()
    print("This utility will generate descriptions for series that don't have them")
    print("using the configured AI provider (Groq, Google Generative AI, or OpenAI).")
    print()
    
    # Ask for confirmation
    response = input("Continue? (yes/no): ").strip().lower()
    if response not in ['yes', 'y']:
        print("Cancelled.")
        return
    
    print()
    print("Enriching series descriptions...")
    print("-" * 70)
    
    stats = enrich_series_descriptions()
    
    print()
    print("Enrichment Results:")
    print("-" * 70)
    print(json.dumps(stats, indent=2))
    print()
    
    if stats["descriptions_added"] > 0:
        print(f"✅ Successfully added {stats['descriptions_added']} description(s)")
    else:
        print("✅ No descriptions needed enrichment")
    
    if stats["errors"] > 0:
        print(f"⚠️  {stats['errors']} error(s) occurred during enrichment")
    
    print()
    print("=" * 70)


if __name__ == "__main__":
    main()
