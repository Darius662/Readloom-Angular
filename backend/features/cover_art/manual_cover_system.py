#!/usr/bin/env python3

import sys
sys.path.append('backend')

import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from backend.internals.db import execute_query
from backend.base.logging import LOGGER
from backend.features.cover_art_manager import COVER_ART_MANAGER

class ManualCoverSystem:
    """System to detect and link manually added covers to volumes."""
    
    def __init__(self):
        self.logger = LOGGER
        self.cover_patterns = [
            # Volume patterns
            r'vol\.?\s*(\d+)',
            r'volume\s*(\d+)',
            r'v(\d+)',
            # Chapter patterns (for single volume manga)
            r'ch\.?\s*(\d+)',
            r'chapter\s*(\d+)',
            # Number only patterns
            r'^(\d+)',
            r'(\d+)\.(jpg|jpeg|png|webp)',
        ]
    
    def scan_all_series_for_manual_covers(self) -> Dict[str, any]:
        """Scan all series for manually added covers and link them to volumes."""
        
        results = {
            'series_processed': 0,
            'covers_found': 0,
            'covers_linked': 0,
            'series_details': []
        }
        
        # Get all series with custom paths
        series = execute_query("""
            SELECT id, title, custom_path, metadata_source 
            FROM series 
            WHERE custom_path IS NOT NULL AND custom_path != ''
            ORDER BY title
        """)
        
        self.logger.info(f"Scanning {len(series)} series for manual covers...")
        
        for s in series:
            series_id = s['id']
            series_title = s['title']
            custom_path = s['custom_path']
            
            self.logger.info(f"Scanning series: {series_title}")
            
            series_result = self.scan_series_covers(series_id, series_title, custom_path)
            
            results['series_processed'] += 1
            results['covers_found'] += series_result['covers_found']
            results['covers_linked'] += series_result['covers_linked']
            results['series_details'].append(series_result)
        
        self.logger.info(f"Manual cover scan complete: {results['covers_linked']}/{results['covers_found']} covers linked")
        
        return results
    
    def scan_series_covers(self, series_id: int, series_title: str, custom_path: str) -> Dict[str, any]:
        """Scan a specific series for manually added covers."""
        
        result = {
            'series_id': series_id,
            'series_title': series_title,
            'covers_found': 0,
            'covers_linked': 0,
            'cover_details': []
        }
        
        try:
            series_path = Path(custom_path)
            if not series_path.exists():
                self.logger.warning(f"Series path does not exist: {series_path}")
                return result
            
            # Look for cover_art folder
            cover_art_folder = series_path / 'cover_art'
            if not cover_art_folder.exists():
                self.logger.info(f"No cover_art folder for: {series_title}")
                return result
            
            # Get all image files in cover_art folder
            image_extensions = {'.jpg', '.jpeg', '.png', '.webp', '.bmp', '.gif'}
            cover_files = []
            
            for ext in image_extensions:
                cover_files.extend(cover_art_folder.glob(f'*{ext}'))
                cover_files.extend(cover_art_folder.glob(f'*{ext.upper()}'))
            
            if not cover_files:
                self.logger.info(f"No cover files found in: {cover_art_folder}")
                return result
            
            self.logger.info(f"Found {len(cover_files)} cover files for: {series_title}")
            result['covers_found'] = len(cover_files)
            
            # Get volumes for this series
            volumes = execute_query(
                "SELECT id, volume_number, cover_path FROM volumes WHERE series_id = ? ORDER BY volume_number",
                (series_id,)
            )
            
            if not volumes:
                self.logger.warning(f"No volumes found for series: {series_title}")
                return result
            
            # Create volume mapping
            volume_map = {}
            for vol in volumes:
                vol_num = self._extract_volume_number(vol['volume_number'])
                if vol_num is not None:
                    volume_map[vol_num] = vol
            
            # Process each cover file
            for cover_file in cover_files:
                cover_result = self.process_cover_file(
                    cover_file, series_id, series_title, volume_map
                )
                
                if cover_result['linked']:
                    result['covers_linked'] += 1
                
                result['cover_details'].append(cover_result)
            
        except Exception as e:
            self.logger.error(f"Error scanning series {series_title}: {e}")
        
        return result
    
    def process_cover_file(self, cover_file: Path, series_id: int, series_title: str, 
                          volume_map: Dict[int, Dict]) -> Dict[str, any]:
        """Process a single cover file and try to link it to a volume."""
        
        result = {
            'filename': cover_file.name,
            'volume_number': None,
            'linked': False,
            'method': None,
            'error': None
        }
        
        try:
            # Extract volume number from filename
            volume_number = self._extract_volume_from_filename(cover_file.name)
            
            if volume_number is None:
                result['error'] = "Could not extract volume number from filename"
                self.logger.warning(f"Could not extract volume from: {cover_file.name}")
                return result
            
            result['volume_number'] = volume_number
            
            # Find matching volume
            if volume_number in volume_map:
                volume = volume_map[volume_number]
                volume_id = volume['id']
                volume_db_number = volume['volume_number']
                
                # Check if volume already has a cover
                if volume['cover_path']:
                    result['error'] = f"Volume {volume_db_number} already has a cover"
                    self.logger.info(f"Volume {volume_db_number} already has cover: {volume['cover_path']}")
                    return result
                
                # Link the cover to the volume
                success = self._link_cover_to_volume(
                    series_id, volume_id, volume_db_number, cover_file
                )
                
                if success:
                    result['linked'] = True
                    result['method'] = 'auto_match'
                    self.logger.info(f"Linked cover {cover_file.name} to volume {volume_db_number}")
                else:
                    result['error'] = "Failed to link cover to volume"
            else:
                result['error'] = f"No volume found for number {volume_number}"
                self.logger.warning(f"No volume found for number {volume_number} in {series_title}")
        
        except Exception as e:
            result['error'] = str(e)
            self.logger.error(f"Error processing cover file {cover_file.name}: {e}")
        
        return result
    
    def _extract_volume_from_filename(self, filename: str) -> Optional[int]:
        """Extract volume number from filename using various patterns."""
        
        filename_lower = filename.lower()
        
        for pattern in self.cover_patterns:
            match = re.search(pattern, filename_lower)
            if match:
                try:
                    return int(match.group(1))
                except ValueError:
                    continue
        
        return None
    
    def _extract_volume_number(self, volume_str: str) -> Optional[int]:
        """Extract numeric volume number from database volume string."""
        
        try:
            # Handle decimal volumes like "0.1", "1.5"
            if '.' in volume_str:
                return float(volume_str)
            # Handle integer volumes
            return int(volume_str)
        except ValueError:
            # Try to extract numbers from string
            numbers = re.findall(r'\d+', volume_str)
            if numbers:
                return int(numbers[0])
        except Exception:
            pass
        
        return None
    
    def _link_cover_to_volume(self, series_id: int, volume_id: int, volume_number: str, 
                            cover_file: Path) -> bool:
        """Link a cover file to a volume in the database."""
        
        try:
            # Get series custom path for URL generation
            series_result = execute_query(
                "SELECT custom_path FROM series WHERE id = ?", (series_id,)
            )
            
            if not series_result:
                self.logger.error(f"Could not find series {series_id}")
                return False
            
            custom_path = series_result[0]['custom_path']
            
            # Generate cover URL (relative to web root)
            series_path = Path(custom_path)
            relative_path = cover_file.relative_to(series_path.parent.parent)  # Go up two levels to get relative to web root
            cover_url = f"/{str(relative_path).replace('\\', '/')}"
            
            # Update database
            execute_query("""
                UPDATE volumes 
                SET cover_path = ?, cover_url = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (str(cover_file), cover_url, volume_id), commit=True)
            
            self.logger.info(f"Updated volume {volume_id} with cover: {cover_file}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error linking cover to volume {volume_id}: {e}")
            return False
    
    def get_unlinked_covers_report(self) -> Dict[str, any]:
        """Get a report of covers that couldn't be linked."""
        
        report = {
            'total_unlinked': 0,
            'series_with_issues': [],
            'suggestions': []
        }
        
        # Get all series with cover_art folders
        series = execute_query("""
            SELECT id, title, custom_path 
            FROM series 
            WHERE custom_path IS NOT NULL AND custom_path != ''
        """)
        
        for s in series:
            series_id = s['id']
            series_title = s['title']
            custom_path = s['custom_path']
            
            series_path = Path(custom_path)
            cover_art_folder = series_path / 'cover_art'
            
            if not cover_art_folder.exists():
                continue
            
            # Get all cover files
            image_extensions = {'.jpg', '.jpeg', '.png', '.webp', '.bmp', '.gif'}
            cover_files = []
            
            for ext in image_extensions:
                cover_files.extend(cover_art_folder.glob(f'*{ext}'))
                cover_files.extend(cover_art_folder.glob(f'*{ext.upper()}'))
            
            # Get volumes with covers
            volumes_with_covers = execute_query(
                "SELECT COUNT(*) as count FROM volumes WHERE series_id = ? AND cover_path IS NOT NULL",
                (series_id,)
            )
            
            unlinked_count = len(cover_files) - volumes_with_covers[0]['count']
            
            if unlinked_count > 0:
                report['total_unlinked'] += unlinked_count
                report['series_with_issues'].append({
                    'series_title': series_title,
                    'unlinked_count': unlinked_count,
                    'total_covers': len(cover_files),
                    'linked_covers': volumes_with_covers[0]['count']
                })
        
        return report

def main():
    """Main function to run the manual cover system."""
    
    print("🔍 Manual Cover Detection and Linking System")
    print("=" * 60)
    
    system = ManualCoverSystem()
    
    # Scan all series for manual covers
    print("\n📚 Scanning all series for manual covers...")
    results = system.scan_all_series_for_manual_covers()
    
    print(f"\n📊 Results:")
    print(f"   Series processed: {results['series_processed']}")
    print(f"   Covers found: {results['covers_found']}")
    print(f"   Covers linked: {results['covers_linked']}")
    
    # Show details for each series
    for series_detail in results['series_details']:
        if series_detail['covers_found'] > 0:
            print(f"\n📖 {series_detail['series_title']}:")
            print(f"   Covers found: {series_detail['covers_found']}")
            print(f"   Covers linked: {series_detail['covers_linked']}")
            
            for cover_detail in series_detail['cover_details']:
                status = "✅" if cover_detail['linked'] else "❌"
                print(f"   {status} {cover_detail['filename']}")
                if cover_detail['volume_number']:
                    print(f"      Volume: {cover_detail['volume_number']}")
                if cover_detail['error']:
                    print(f"      Error: {cover_detail['error']}")
    
    # Show unlinked covers report
    print(f"\n🔍 Unlinked Covers Report:")
    unlinked_report = system.get_unlinked_covers_report()
    
    if unlinked_report['total_unlinked'] > 0:
        print(f"   Total unlinked covers: {unlinked_report['total_unlinked']}")
        
        for issue in unlinked_report['series_with_issues']:
            print(f"   📖 {issue['series_title']}: {issue['unlinked_count']} unlinked")
    else:
        print(f"   ✅ All covers are linked!")
    
    print(f"\n🎯 Manual cover system complete!")
    print(f"   Covers should now be available in the frontend.")

if __name__ == '__main__':
    main()
