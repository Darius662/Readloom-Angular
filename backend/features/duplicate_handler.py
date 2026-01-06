#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Duplicate series handler.
Detects and removes duplicate series entries using metadata_source and metadata_id.
"""

from typing import Dict, List, Any
from backend.base.logging import LOGGER
from backend.internals.db import execute_query


def find_duplicate_series() -> Dict[str, List[Dict[str, Any]]]:
    """Find duplicate series entries by metadata_source and metadata_id.
    
    Returns:
        Dict with metadata_source+metadata_id as key and list of duplicate series as value.
    """
    try:
        # Find groups with multiple series having the same metadata_source and metadata_id
        duplicates = execute_query("""
            SELECT metadata_source, metadata_id, COUNT(*) as count
            FROM series
            WHERE metadata_source IS NOT NULL AND metadata_id IS NOT NULL
            GROUP BY metadata_source, metadata_id
            HAVING count > 1
        """)
        
        result = {}
        for dup in duplicates:
            key = f"{dup['metadata_source']}:{dup['metadata_id']}"
            series_list = execute_query("""
                SELECT id, title, in_library, want_to_read, created_at
                FROM series
                WHERE metadata_source = ? AND metadata_id = ?
                ORDER BY created_at ASC
            """, (dup['metadata_source'], dup['metadata_id']))
            
            result[key] = series_list
        
        return result
    except Exception as e:
        LOGGER.error(f"Error finding duplicate series: {e}")
        return {}


def merge_duplicates(keep_id: int, remove_ids: List[int]) -> bool:
    """Merge duplicate series by keeping one and removing others.
    
    Args:
        keep_id: The series ID to keep
        remove_ids: List of series IDs to remove
        
    Returns:
        bool: True if merge was successful, False otherwise
    """
    try:
        # Get the series to keep
        keep_series = execute_query("SELECT * FROM series WHERE id = ?", (keep_id,))
        if not keep_series:
            LOGGER.error(f"Series {keep_id} not found")
            return False
        
        # For each series to remove
        for remove_id in remove_ids:
            # Get the series to remove
            remove_series = execute_query("SELECT * FROM series WHERE id = ?", (remove_id,))
            if not remove_series:
                LOGGER.warning(f"Series {remove_id} not found, skipping")
                continue
            
            remove_data = remove_series[0]
            
            # Merge flags: if either has in_library=1, keep it as 1
            if remove_data.get('in_library') == 1:
                execute_query(
                    "UPDATE series SET in_library = 1 WHERE id = ?",
                    (keep_id,),
                    commit=True
                )
            
            # Merge flags: if either has want_to_read=1, keep it as 1
            if remove_data.get('want_to_read') == 1:
                execute_query(
                    "UPDATE series SET want_to_read = 1 WHERE id = ?",
                    (keep_id,),
                    commit=True
                )
            
            # Move all collection relationships from remove_id to keep_id
            try:
                # Get all collections for the series to remove
                collections = execute_query(
                    "SELECT collection_id FROM series_collections WHERE series_id = ?",
                    (remove_id,)
                )
                
                for coll in collections:
                    coll_id = coll['collection_id']
                    # Check if keep_id is already in this collection
                    existing = execute_query(
                        "SELECT id FROM series_collections WHERE series_id = ? AND collection_id = ?",
                        (keep_id, coll_id)
                    )
                    
                    if not existing:
                        # Add keep_id to this collection
                        execute_query(
                            "INSERT INTO series_collections (series_id, collection_id) VALUES (?, ?)",
                            (keep_id, coll_id),
                            commit=True
                        )
                        LOGGER.info(f"Moved series {keep_id} to collection {coll_id}")
                
                # Remove all collection relationships for remove_id
                execute_query(
                    "DELETE FROM series_collections WHERE series_id = ?",
                    (remove_id,),
                    commit=True
                )
            except Exception as e:
                LOGGER.warning(f"Error moving collection relationships: {e}")
            
            # Delete the duplicate series
            execute_query(
                "DELETE FROM series WHERE id = ?",
                (remove_id,),
                commit=True
            )
            LOGGER.info(f"Deleted duplicate series {remove_id}")
        
        return True
    except Exception as e:
        LOGGER.error(f"Error merging duplicates: {e}")
        import traceback
        LOGGER.error(traceback.format_exc())
        return False


def remove_all_duplicates() -> Dict[str, Any]:
    """Remove all duplicate series, keeping the oldest one in each group.
    
    Returns:
        Dict with statistics about the operation.
    """
    try:
        duplicates = find_duplicate_series()
        
        stats = {
            'total_groups': len(duplicates),
            'total_removed': 0,
            'errors': []
        }
        
        for key, series_list in duplicates.items():
            if len(series_list) <= 1:
                continue
            
            # Keep the first (oldest) series
            keep_id = series_list[0]['id']
            remove_ids = [s['id'] for s in series_list[1:]]
            
            try:
                if merge_duplicates(keep_id, remove_ids):
                    stats['total_removed'] += len(remove_ids)
                    LOGGER.info(f"Removed {len(remove_ids)} duplicates for {key}, keeping {keep_id}")
                else:
                    stats['errors'].append(f"Failed to merge duplicates for {key}")
            except Exception as e:
                stats['errors'].append(f"Error processing {key}: {str(e)}")
                LOGGER.error(f"Error processing duplicates for {key}: {e}")
        
        LOGGER.info(f"Duplicate removal complete: {stats['total_removed']} series removed from {stats['total_groups']} groups")
        return stats
    except Exception as e:
        LOGGER.error(f"Error removing duplicates: {e}")
        return {
            'total_groups': 0,
            'total_removed': 0,
            'errors': [str(e)]
        }
