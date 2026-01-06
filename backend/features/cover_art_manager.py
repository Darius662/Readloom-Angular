#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import requests
import time
from pathlib import Path
from typing import Optional, Dict, Any, List
from urllib.parse import urljoin, urlparse

from backend.base.custom_exceptions import FileOperationError
from backend.base.helpers import ensure_dir_exists, get_data_dir
from backend.base.logging import LOGGER
from backend.internals.db import execute_query


class CoverArtManager:
    """Manages volume cover art storage and retrieval with MangaDex integration."""
    
    def __init__(self):
        # Don't initialize a global cover art directory anymore
        # We'll use series-specific folders
        LOGGER.info("Cover art manager initialized (using series-specific folders)")
    
    def get_series_folder_path(self, series_id: int) -> Optional[Path]:
        """Get the manga folder path for a series.
        
        Args:
            series_id: The ID of the series
            
        Returns:
            Path: The series folder path, or None if not found
        """
        try:
            # Get series custom path from database
            series_info = execute_query(
                "SELECT title, custom_path FROM series WHERE id = ?", 
                (series_id,)
            )
            
            if not series_info:
                LOGGER.error(f"Series {series_id} not found in database")
                return None
            
            series = series_info[0]
            
            # If custom path exists and is valid, use it
            if series.get('custom_path'):
                custom_path = Path(series['custom_path'])
                if custom_path.exists() and custom_path.is_dir():
                    LOGGER.debug(f"Using custom path for series {series_id}: {custom_path}")
                    return custom_path
                else:
                    LOGGER.warning(f"Custom path exists but is not a directory: {custom_path}")
            
            # If no custom path, we can't determine the manga folder
            # This would require root folder configuration which is more complex
            LOGGER.warning(f"No valid custom path found for series {series_id}")
            return None
            
        except Exception as e:
            LOGGER.error(f"Error getting series folder path for series {series_id}: {e}")
            return None
    
    def get_volume_cover_path(self, series_id: int, volume_number: str) -> Optional[Path]:
        """Generate the local path for a volume cover image in the manga folder.
        
        Args:
            series_id: The ID of the series
            volume_number: The volume number (e.g., "1", "2", "3")
            
        Returns:
            Path: The local path where the cover should be stored, or None if series folder not found
        """
        # Get the series folder path
        series_folder = self.get_series_folder_path(series_id)
        if not series_folder:
            return None
        
        # Create cover_art subdirectory in the series folder
        cover_art_dir = series_folder / "cover_art"
        ensure_dir_exists(cover_art_dir)
        
        # Generate filename: Volume{number}.png
        filename = f"Volume{volume_number}.png"
        return cover_art_dir / filename
    
    def get_series_cover_dir(self, series_id: int) -> Optional[Path]:
        """Get the cover directory for a specific series.
        
        Args:
            series_id: The ID of the series
            
        Returns:
            Path: The directory path for series covers, or None if series folder not found
        """
        series_folder = self.get_series_folder_path(series_id)
        if not series_folder:
            return None
            
        cover_art_dir = series_folder / "cover_art"
        ensure_dir_exists(cover_art_dir)
        return cover_art_dir
    
    def download_mangadex_cover(self, manga_dex_id: str, cover_filename: str, 
                               local_path: Path, max_retries: int = 3) -> bool:
        """Download a cover image from MangaDex.
        
        Args:
            manga_dex_id: The MangaDex manga ID
            cover_filename: The cover filename from MangaDex
            local_path: Local path to save the cover
            max_retries: Maximum number of download attempts
            
        Returns:
            bool: True if download was successful, False otherwise
        """
        # Try multiple CDN endpoints
        cdn_endpoints = [
            f"https://uploads.mangadex.org/covers/{manga_dex_id}/{cover_filename}",
            f"https://mangadex.org/covers/{manga_dex_id}/{cover_filename}",
        ]
        
        for cdn_url in cdn_endpoints:
            LOGGER.info(f"Trying CDN: {cdn_url}")
            
            for attempt in range(max_retries):
                try:
                    # Download with proper headers and timeout
                    headers = {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                        'Accept': 'image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
                        'Accept-Language': 'en-US,en;q=0.9',
                        'Referer': 'https://mangadex.org/',
                        'Sec-Fetch-Dest': 'image',
                        'Sec-Fetch-Mode': 'no-cors',
                        'Sec-Fetch-Site': 'cross-site',
                    }
                    
                    response = requests.get(cdn_url, headers=headers, timeout=30, stream=True)
                    response.raise_for_status()
                    
                    # Verify content type is an image
                    content_type = response.headers.get('content-type', '').lower()
                    if not content_type.startswith('image/'):
                        LOGGER.warning(f"Unexpected content type for cover: {content_type}")
                        continue
                    
                    # Save the image
                    with open(local_path, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            if chunk:
                                f.write(chunk)
                    
                    # Verify file was created and has content
                    if local_path.exists() and local_path.stat().st_size > 0:
                        LOGGER.info(f"Successfully downloaded cover to: {local_path}")
                        return True
                    else:
                        LOGGER.warning(f"Downloaded file is empty or missing: {local_path}")
                        
                except requests.exceptions.RequestException as e:
                    LOGGER.warning(f"Download attempt {attempt + 1} failed: {e}")
                    if attempt < max_retries - 1:
                        time.sleep(2 ** attempt)  # Exponential backoff
                except Exception as e:
                    LOGGER.error(f"Unexpected error downloading cover: {e}")
                    break
            
            LOGGER.warning(f"Failed to download cover from {cdn_url} after {max_retries} attempts")
        
        # Try alternative approach: Use MangaDex API to get cover data
        LOGGER.info(f"Trying MangaDex API for cover data...")
        try:
            cover_id = cover_filename.split('.')[0]  # Extract ID from filename
            api_url = f"https://api.mangadex.org/cover/{cover_id}"
            
            response = requests.get(api_url, timeout=10)
            if response.status_code == 200:
                cover_data = response.json()
                if 'data' in cover_data and cover_data['data']:
                    attributes = cover_data['data']['attributes']
                    actual_filename = attributes.get('fileName')
                    
                    if actual_filename and actual_filename != cover_filename:
                        # Try with the actual filename from API
                        for cdn_url in cdn_endpoints:
                            api_cdn_url = cdn_url.replace(cover_filename, actual_filename)
                            LOGGER.info(f"Trying API filename: {api_cdn_url}")
                            
                            try:
                                response = requests.get(api_cdn_url, headers=headers, timeout=30, stream=True)
                                if response.status_code == 200:
                                    with open(local_path, 'wb') as f:
                                        for chunk in response.iter_content(8192):
                                            if chunk:
                                                f.write(chunk)
                                    
                                    if local_path.exists() and local_path.stat().st_size > 0:
                                        LOGGER.info(f"Successfully downloaded cover via API: {local_path}")
                                        return True
                            except Exception as e:
                                LOGGER.warning(f"API download failed: {e}")
        except Exception as e:
            LOGGER.warning(f"API approach failed: {e}")
        
        LOGGER.error(f"Failed to download cover after all attempts: {manga_dex_id}/{cover_filename}")
        return False
    
    def save_volume_cover(self, series_id: int, volume_id: int, volume_number: str, 
                       manga_dex_id: str, cover_filename: str) -> Optional[str]:
        """Download and save a volume cover image.
        
        Args:
            series_id: The ID of the series
            volume_id: The ID of the volume in the database
            volume_number: The volume number (e.g., "1", "2", "3")
            manga_dex_id: The MangaDex manga ID
            cover_filename: The cover filename from MangaDex
            
        Returns:
            str: Relative path to the saved cover, or None if failed
        """
        try:
            # Generate local path
            local_path = self.get_volume_cover_path(series_id, volume_number)
            
            if not local_path:
                LOGGER.error(f"Cannot determine cover path: series folder not found for series {series_id}")
                return None
            
            # Download from MangaDex if we have the info
            if manga_dex_id and cover_filename:
                success = self.download_mangadex_cover(manga_dex_id, cover_filename, local_path)
                if not success:
                    return None
            else:
                LOGGER.warning(f"No MangaDex info provided for volume {volume_id}")
                return None
            
            # Store the full path in database since covers are in manga folders, not project data
            cover_path = str(local_path)
            
            # Update database with cover path
            execute_query(
                "UPDATE volumes SET cover_path = ? WHERE id = ?",
                (cover_path, volume_id),
                commit=True
            )
            
            LOGGER.info(f"Saved cover for volume {volume_id}: {cover_path}")
            return cover_path
            
        except Exception as e:
            LOGGER.error(f"Error saving volume cover: {e}")
            return None
    
    def get_mangadex_covers_for_series(self, manga_dex_id: str) -> List[Dict[str, Any]]:
        """Get all volume covers for a MangaDex series.
        
        Args:
            manga_dex_id: The MangaDex manga ID
            
        Returns:
            List of dictionaries with cover information
        """
        try:
            response = requests.get(
                f"https://api.mangadex.org/manga/{manga_dex_id}",
                params={"includes[]": "cover_art"},
                timeout=10
            )
            
            if response.status_code != 200:
                LOGGER.error(f"Failed to get MangaDex manga data: {response.status_code}")
                return []
            
            data = response.json()
            if 'data' not in data or not data['data']:
                LOGGER.error(f"No manga data found for {manga_dex_id}")
                return []
            
            manga = data['data']
            relationships = manga.get('relationships', [])
            
            volume_covers = []
            for rel in relationships:
                if rel.get('type') == 'cover_art':
                    attributes = rel.get('attributes', {})
                    volume = attributes.get('volume')
                    filename = attributes.get('fileName')
                    cover_id = rel.get('id')
                    
                    # Skip if no volume info (main series cover)
                    if not volume:
                        continue
                    
                    # Extract volume number and handle various formats
                    volume_num = self._extract_volume_number(volume)
                    if volume_num is None:
                        LOGGER.warning(f"Could not extract volume number from: {volume}")
                        continue
                    
                    volume_covers.append({
                        'volume': volume_num,
                        'volume_original': volume,  # Keep original for debugging
                        'filename': filename,
                        'cover_id': cover_id,
                        'manga_dex_id': manga_dex_id
                    })
            
            # Sort by volume number
            volume_covers.sort(key=lambda x: x['volume'])
            
            LOGGER.info(f"Found {len(volume_covers)} volume covers for MangaDex {manga_dex_id}")
            return volume_covers
            
        except Exception as e:
            LOGGER.error(f"Error getting MangaDex covers: {e}")
            return []
    
    def _extract_volume_number(self, volume_str: str) -> Optional[int]:
        """Extract volume number from various MangaDex volume formats."""
        if not volume_str:
            return None
        
        try:
            # Handle decimal volumes like "0.1", "1.5"
            if '.' in volume_str:
                return float(volume_str)
            # Handle integer volumes
            return int(volume_str)
        except ValueError:
            # Try to extract numbers from string
            import re
            numbers = re.findall(r'\d+', volume_str)
            if numbers:
                return int(numbers[0])
        except Exception:
            return None
    
    def match_covers_to_volumes(self, volume_covers: List[Dict[str, Any]], 
                             volumes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Match MangaDex covers to database volumes.
        
        Args:
            volume_covers: List of MangaDex cover information
            volumes: List of database volume information
            
        Returns:
            Dictionary with matching results
        """
        results = {
            'matched': [],
            'unmatched_covers': [],
            'unmatched_volumes': []
        }
        
        # Create a mapping of volume numbers to database volumes
        volume_map = {}
        for volume in volumes:
            vol_num = self._extract_volume_number(volume.get('volume_number', ''))
            if vol_num is not None:
                volume_map[vol_num] = volume
        
        # Match covers to volumes
        for cover in volume_covers:
            cover_volume = cover['volume']
            
            # Try exact match first
            if cover_volume in volume_map:
                volume = volume_map[cover_volume]
                results['matched'].append({
                    'cover': cover,
                    'volume': volume,
                    'match_type': 'exact'
                })
            else:
                # Try fuzzy matching for close numbers
                closest_volume = None
                closest_diff = float('inf')
                
                for vol_num, volume in volume_map.items():
                    diff = abs(vol_num - cover_volume)
                    if diff < closest_diff and diff <= 1:  # Allow 1 volume difference
                        closest_diff = diff
                        closest_volume = volume
                
                if closest_volume:
                    results['matched'].append({
                        'cover': cover,
                        'volume': closest_volume,
                        'match_type': 'fuzzy',
                        'difference': closest_diff
                    })
                else:
                    results['unmatched_covers'].append(cover)
        
        # Find unmatched volumes
        matched_volume_nums = {match['cover']['volume'] for match in results['matched']}
        for volume in volumes:
            vol_num = self._extract_volume_number(volume.get('volume_number', ''))
            if vol_num is not None and vol_num not in matched_volume_nums:
                results['unmatched_volumes'].append(volume)
        
        LOGGER.info(f"Cover matching results: {len(results['matched'])} matched, "
                   f"{len(results['unmatched_covers'])} unmatched covers, "
                   f"{len(results['unmatched_volumes'])} unmatched volumes")
        
        return results
    
    def batch_download_covers(self, series_id: int, volumes: List[Dict[str, Any]], 
                            manga_dex_id: str, cover_data: Dict[str, str]) -> Dict[str, Any]:
        """Download covers for multiple volumes in batch with smart matching.
        
        Args:
            series_id: The ID of the series
            volumes: List of volume dictionaries with id and volume_number
            manga_dex_id: The MangaDex manga ID
            cover_data: Dictionary mapping volume numbers to cover filenames
            
        Returns:
            Dict[str, Any]: Results with success count, failures, and updated volumes
        """
        results = {
            'success_count': 0,
            'failed_volumes': [],
            'updated_volumes': []
        }
        
        LOGGER.info(f"Starting batch cover download for {len(volumes)} volumes")
        
        # First, get all available covers from MangaDex
        volume_covers = self.get_mangadex_covers_for_series(manga_dex_id)
        
        if not volume_covers:
            LOGGER.warning(f"No volume covers found for MangaDex {manga_dex_id}")
            results['failed_volumes'] = volumes.copy()
            return results
        
        # Match covers to database volumes
        matching_results = self.match_covers_to_volumes(volume_covers, volumes)
        
        # Download matched covers
        for match in matching_results['matched']:
            volume = match['volume']
            cover = match['cover']
            
            volume_id = volume.get('id')
            volume_number = volume.get('volume_number')
            cover_filename = cover['filename']
            
            try:
                cover_path = self.save_volume_cover(
                    series_id, volume_id, volume_number, manga_dex_id, cover_filename
                )
                
                if cover_path:
                    results['success_count'] += 1
                    results['updated_volumes'].append({
                        'volume_id': volume_id,
                        'volume_number': volume_number,
                        'cover_path': cover_path,
                        'match_type': match['match_type']
                    })
                else:
                    results['failed_volumes'].append({
                        'volume_id': volume_id,
                        'volume_number': volume_number,
                        'error': 'Download failed'
                    })
            except Exception as e:
                results['failed_volumes'].append({
                    'volume_id': volume_id,
                    'volume_number': volume_number,
                    'error': str(e)
                })
        
        # Log unmatched items
        if matching_results['unmatched_covers']:
            LOGGER.warning(f"Unmatched covers: {len(matching_results['unmatched_covers'])}")
        
        if matching_results['unmatched_volumes']:
            LOGGER.warning(f"Unmatched volumes: {len(matching_results['unmatched_volumes'])}")
        
        LOGGER.info(f"Batch cover download complete: {results['success_count']} successful, "
                   f"{len(results['failed_volumes'])} failed")
        
        return results
    
    def get_cover_url(self, volume: Dict[str, Any]) -> Optional[str]:
        """Get the appropriate cover URL for a volume, prioritizing local covers.
        
        Args:
            volume: Volume dictionary from database
            
        Returns:
            Optional[str]: URL to the cover image, or None if no cover available
        """
        # First try local cover path (now stored as full path)
        cover_path = volume.get('cover_path')
        if cover_path:
            # Check if it's a full path or relative path
            path_obj = Path(cover_path)
            if not path_obj.is_absolute():
                # If it's relative, assume it's relative to data directory (old format)
                full_path = get_data_dir() / cover_path
            else:
                # It's already an absolute path (new format)
                full_path = path_obj
                
            if full_path.exists():
                # Return as file:// URL for frontend
                return f"file://{full_path}"
            else:
                LOGGER.warning(f"Local cover file not found: {full_path}")
        
        # Fallback to cover_url (MangaDex URL)
        cover_url = volume.get('cover_url')
        if cover_url:
            return cover_url
        
        # No cover available
        return None
    
    def delete_volume_cover(self, volume_id: int) -> bool:
        """Delete a volume's local cover file and update database.
        
        Args:
            volume_id: The ID of the volume
            
        Returns:
            bool: True if deletion was successful, False otherwise
        """
        try:
            # Get volume info to find cover path
            volumes = execute_query(
                "SELECT series_id, cover_path FROM volumes WHERE id = ?",
                (volume_id,)
            )
            
            if not volumes:
                LOGGER.warning(f"Volume {volume_id} not found")
                return False
            
            volume = volumes[0]
            cover_path = volume.get('cover_path')
            
            # Delete local file if it exists
            if cover_path:
                # Check if it's a full path or relative path
                path_obj = Path(cover_path)
                if not path_obj.is_absolute():
                    # If it's relative, assume it's relative to data directory (old format)
                    full_path = get_data_dir() / cover_path
                else:
                    # It's already an absolute path (new format)
                    full_path = path_obj
                    
                if full_path.exists():
                    try:
                        full_path.unlink()
                        LOGGER.info(f"Deleted cover file: {full_path}")
                    except Exception as e:
                        LOGGER.warning(f"Could not delete cover file {full_path}: {e}")
            
            # Update database to remove cover path
            execute_query(
                "UPDATE volumes SET cover_path = NULL WHERE id = ?",
                (volume_id,),
                commit=True
            )
            
            LOGGER.info(f"Removed cover path for volume {volume_id}")
            return True
            
        except Exception as e:
            LOGGER.error(f"Error deleting volume cover: {e}")
            return False
    
    def cleanup_unused_covers(self, series_id: int) -> int:
        """Clean up cover files that are no longer referenced in the database.
        
        Args:
            series_id: The ID of the series
            
        Returns:
            int: Number of files cleaned up
        """
        try:
            series_dir = self.get_series_cover_dir(series_id)
            if not series_dir.exists():
                return 0
            
            # Get all referenced cover paths for this series
            referenced_paths = execute_query(
                "SELECT cover_path FROM volumes WHERE series_id = ? AND cover_path IS NOT NULL",
                (series_id,)
            )
            referenced_files = {Path(row['cover_path']).name for row in referenced_paths}
            
            cleaned_count = 0
            for cover_file in series_dir.glob("*.png"):
                if cover_file.name not in referenced_files:
                    try:
                        cover_file.unlink()
                        cleaned_count += 1
                        LOGGER.info(f"Cleaned up unused cover: {cover_file}")
                    except Exception as e:
                        LOGGER.warning(f"Could not delete unused cover {cover_file}: {e}")
            
            LOGGER.info(f"Cleaned up {cleaned_count} unused cover files for series {series_id}")
            return cleaned_count
            
        except Exception as e:
            LOGGER.error(f"Error cleaning up unused covers: {e}")
            return 0


# Global instance
COVER_ART_MANAGER = CoverArtManager()
