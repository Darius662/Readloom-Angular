#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Fix AniList metadata_id inconsistencies in the database.
Standardizes all AniList metadata_id values to use numeric AniList IDs.
"""

import sys
import os

# Add the backend directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from backend.base.logging import LOGGER
from backend.internals.db import execute_query


def fix_anilist_metadata_ids():
    """Fix AniList metadata_id inconsistencies by standardizing to numeric IDs."""
    try:
        LOGGER.info("Starting AniList metadata_id fix...")
        
        # Get all AniList series with UUID metadata_id
        uuid_series = execute_query("""
            SELECT id, title, metadata_id 
            FROM series 
            WHERE metadata_source = 'AniList' 
            AND metadata_id LIKE '%-%'
        """)
        
        LOGGER.info(f"Found {len(uuid_series)} series with UUID metadata_id")
        
        fixed_count = 0
        for series in uuid_series:
            series_id = series['id']
            title = series['title']
            uuid_metadata_id = series['metadata_id']
            
            LOGGER.info(f"Processing: {title} (ID: {series_id}, UUID: {uuid_metadata_id})")
            
            # Try to find matching want_to_read_cache entry by title
            matching_wtr = execute_query("""
                SELECT metadata_id 
                FROM want_to_read_cache 
                WHERE metadata_source = 'AniList' AND title = ?
                LIMIT 1
            """, (title,))
            
            if matching_wtr:
                numeric_id = matching_wtr[0]['metadata_id']
                LOGGER.info(f"  Found matching want_to_read_cache entry with numeric ID: {numeric_id}")
                
                # Update the series table with the numeric ID
                execute_query("""
                    UPDATE series 
                    SET metadata_id = ? 
                    WHERE id = ?
                """, (numeric_id, series_id), commit=True)
                
                LOGGER.info(f"  Updated series {series_id} metadata_id to {numeric_id}")
                fixed_count += 1
            else:
                LOGGER.warning(f"  No matching want_to_read_cache entry found for: {title}")
        
        LOGGER.info(f"Successfully fixed {fixed_count} AniList metadata_id inconsistencies")
        
        # Verify the fix
        LOGGER.info("Verifying the fix...")
        remaining_uuids = execute_query("""
            SELECT COUNT(*) as count 
            FROM series 
            WHERE metadata_source = 'AniList' 
            AND metadata_id LIKE '%-%'
        """)
        
        LOGGER.info(f"Remaining UUID metadata_ids: {remaining_uuids[0]['count']}")
        
        # Show sample of fixed data
        sample_series = execute_query("""
            SELECT id, title, metadata_id 
            FROM series 
            WHERE metadata_source = 'AniList' 
            AND title = 'Geomsulmyeongga Mangnaeadeul'
        """)
        
        if sample_series:
            for series in sample_series:
                LOGGER.info(f"Fixed: {series['title']} -> metadata_id: {series['metadata_id']}")
        
        return fixed_count
        
    except Exception as e:
        LOGGER.error(f"Error fixing AniList metadata_ids: {e}")
        import traceback
        LOGGER.error(traceback.format_exc())
        return 0


def main():
    """Main function to fix AniList metadata IDs."""
    LOGGER.info("Starting AniList metadata_id standardization...")
    
    fixed_count = fix_anilist_metadata_ids()
    
    if fixed_count > 0:
        LOGGER.info(f"Successfully standardized {fixed_count} AniList metadata_id values")
    else:
        LOGGER.info("No AniList metadata_id inconsistencies found or fixed")
    
    LOGGER.info("AniList metadata_id standardization completed!")


if __name__ == "__main__":
    main()
