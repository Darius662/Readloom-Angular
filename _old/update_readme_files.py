#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Utility script to update existing README.txt files with new metadata fields.
This script will:
1. Find all README.txt files in root folders
2. Read existing metadata
3. Fetch missing metadata from series database
4. Update README.txt with new fields (cover_url, author, publisher, isbn, genres)
"""

import sys
import json
from pathlib import Path
from typing import Dict, Any

# Add the project root to the path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from backend.base.logging import LOGGER
from backend.internals.db import execute_query
from backend.base.helpers import read_metadata_from_readme, get_safe_folder_name
from backend.internals.settings import Settings
from datetime import datetime


def update_readme_file(readme_path: Path, series_data: Dict[str, Any]) -> bool:
    """
    Update a README.txt file with all database metadata fields.
    
    Args:
        readme_path: Path to README.txt file
        series_data: Dictionary with series metadata
        
    Returns:
        bool: True if updated, False otherwise
    """
    try:
        # Read existing README to preserve Created timestamp
        existing_created = None
        try:
            with open(readme_path, 'r') as f:
                for line in f:
                    if line.startswith('Created:'):
                        existing_created = line.split(':', 1)[1].strip()
                        break
        except Exception:
            pass
        
        # Build new README content with all database fields
        lines = []
        
        # Core identification fields
        lines.append(f"Series: {series_data.get('title', 'Unknown')}")
        lines.append(f"ID: {series_data.get('id', '')}")
        lines.append(f"Type: {series_data.get('content_type', 'MANGA')}")
        
        # Metadata provider information
        if series_data.get('metadata_source'):
            lines.append(f"Provider: {series_data['metadata_source']}")
        if series_data.get('metadata_id'):
            lines.append(f"MetadataID: {series_data['metadata_id']}")
        
        # Author and publisher
        if series_data.get('author') and series_data['author'] != 'Unknown':
            lines.append(f"Author: {series_data['author']}")
        if series_data.get('publisher') and series_data['publisher'] != 'Unknown':
            lines.append(f"Publisher: {series_data['publisher']}")
        
        # Cover URL
        if series_data.get('cover_url'):
            lines.append(f"CoverURL: {series_data['cover_url']}")
        
        # ISBN
        if series_data.get('isbn'):
            lines.append(f"ISBN: {series_data['isbn']}")
        
        # Published Date
        if series_data.get('published_date'):
            lines.append(f"PublishedDate: {series_data['published_date']}")
        
        # Subjects/Tags
        if series_data.get('subjects'):
            subjects = series_data['subjects']
            # Convert list to comma-separated string if needed
            subjects_str = ",".join(subjects) if isinstance(subjects, list) else subjects
            lines.append(f"Subjects: {subjects_str}")
        
        # Status
        if series_data.get('status'):
            lines.append(f"Status: {series_data['status']}")
        
        # Description (if available and not too long)
        if series_data.get('description'):
            description = series_data['description']
            # Truncate if too long
            if len(description) > 500:
                description = description[:497] + "..."
            lines.append(f"Description: {description}")
        
        # Custom path (if available)
        if series_data.get('custom_path'):
            lines.append(f"CustomPath: {series_data['custom_path']}")
        
        # Timestamps
        if existing_created:
            lines.append(f"Created: {existing_created}")
        else:
            lines.append(f"Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        if series_data.get('updated_at'):
            lines.append(f"Updated: {series_data['updated_at']}")
        
        # Add footer
        lines.append("")
        lines.append("This folder is managed by Readloom. Place your e-book files here.")
        
        # Write updated README
        new_content = '\n'.join(lines)
        
        with open(readme_path, 'w') as f:
            f.write(new_content)
        
        LOGGER.info(f"Updated README.txt: {readme_path}")
        return True
    
    except Exception as e:
        LOGGER.error(f"Error updating README.txt {readme_path}: {e}")
        return False


def find_and_update_readme_files() -> Dict[str, Any]:
    """
    Find all README.txt files in root folders and update them.
    
    Returns:
        dict: Statistics about the update operation
    """
    stats = {
        "readme_files_found": 0,
        "readme_files_updated": 0,
        "errors": 0
    }
    
    try:
        # Get root folders from settings
        settings = Settings().get_settings()
        root_folders = settings.root_folders
        
        if not root_folders:
            LOGGER.warning("No root folders configured")
            return stats
        
        # Find all README.txt files
        readme_files = []
        for root_folder in root_folders:
            root_path = Path(root_folder['path'])
            if root_path.exists():
                # Find all README.txt files recursively
                for readme_path in root_path.rglob('README.txt'):
                    readme_files.append(readme_path)
        
        stats["readme_files_found"] = len(readme_files)
        LOGGER.info(f"Found {len(readme_files)} README.txt files")
        
        if not readme_files:
            LOGGER.info("No README.txt files found")
            return stats
        
        # Update each README.txt file
        for readme_path in readme_files:
            try:
                # Get series directory
                series_dir = readme_path.parent
                
                # Read existing metadata from README
                readme_metadata = read_metadata_from_readme(series_dir)
                
                # Get series data from database (all fields including new ones)
                series_id = readme_metadata.get('series_id')
                if not series_id:
                    # Try to find series by title
                    series_title = readme_metadata.get('title')
                    if series_title:
                        series_result = execute_query(
                            "SELECT id, title, description, author, publisher, cover_url, status, content_type, metadata_source, metadata_id, custom_path, created_at, updated_at, isbn, published_date, subjects FROM series WHERE title = ? LIMIT 1",
                            (series_title,)
                        )
                        if series_result:
                            series_data = series_result[0]
                        else:
                            LOGGER.warning(f"Series not found for README: {readme_path}")
                            continue
                    else:
                        LOGGER.warning(f"No series title in README: {readme_path}")
                        continue
                else:
                    # Get series by ID (all fields including new ones)
                    series_result = execute_query(
                        "SELECT id, title, description, author, publisher, cover_url, status, content_type, metadata_source, metadata_id, custom_path, created_at, updated_at, isbn, published_date, subjects FROM series WHERE id = ?",
                        (series_id,)
                    )
                    if series_result:
                        series_data = series_result[0]
                    else:
                        LOGGER.warning(f"Series not found for ID {series_id}: {readme_path}")
                        continue
                
                # Update README with series data
                if update_readme_file(readme_path, series_data):
                    stats["readme_files_updated"] += 1
            
            except Exception as e:
                LOGGER.error(f"Error processing README.txt {readme_path}: {e}")
                stats["errors"] += 1
        
        return stats
    
    except Exception as e:
        LOGGER.error(f"Error in find_and_update_readme_files: {e}")
        import traceback
        LOGGER.error(traceback.format_exc())
        stats["errors"] += 1
        return stats


def main():
    """Run the README update utility."""
    print("=" * 70)
    print("Readloom README.txt Update Utility")
    print("=" * 70)
    print()
    print("This utility will update all existing README.txt files with new metadata")
    print("fields including: Author, Publisher, ISBN, Genres, and CoverURL")
    print()
    
    # Ask for confirmation
    response = input("Continue? (yes/no): ").strip().lower()
    if response not in ['yes', 'y']:
        print("Cancelled.")
        return
    
    print()
    print("Updating README.txt files...")
    print("-" * 70)
    
    stats = find_and_update_readme_files()
    
    print()
    print("Update Results:")
    print("-" * 70)
    print(json.dumps(stats, indent=2))
    print()
    
    if stats["readme_files_updated"] > 0:
        print(f"✅ Successfully updated {stats['readme_files_updated']} README.txt file(s)")
    else:
        print("✅ No README.txt files needed updating")
    
    if stats["errors"] > 0:
        print(f"⚠️  {stats['errors']} error(s) occurred during update")
    
    print()
    print("=" * 70)


if __name__ == "__main__":
    main()
