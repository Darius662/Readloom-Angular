#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
API endpoints for manga prepopulation from external sources.
"""

from flask import Blueprint, jsonify, request
from backend.base.logging import LOGGER
from backend.internals.db import execute_query
from backend.features.cover_art_manager import COVER_ART_MANAGER

# Create API blueprint
manga_prepopulation_api_bp = Blueprint('api_manga_prepopulation', __name__)

# Log that the blueprint was created
LOGGER.info("Manga Prepopulation API blueprint created")


@manga_prepopulation_api_bp.route('/manga-prepopulation/volumes', methods=['POST'])
def save_volumes():
    """Save prepopulated volume data.
    
    Request body:
        {
            "series_id": 123,
            "volumes": [
                {
                    "volume_number": 1,
                    "title": "Volume 1",
                    "release_date": "2023-01-01",
                    "cover_url": "https://...",
                    "is_confirmed": false
                }
            ]
        }
    """
    try:
        data = request.json or {}
        series_id = data.get('series_id')
        volumes = data.get('volumes', [])
        
        if not series_id or not volumes:
            return jsonify({"error": "Missing series_id or volumes"}), 400
        
        saved_volumes = []
        for volume_data in volumes:
            # Check if volume already exists
            existing = execute_query(
                "SELECT id FROM volumes WHERE series_id = ? AND volume_number = ?",
                (series_id, volume_data['volume_number'])
            )
            
            if existing:
                # Update existing volume
                execute_query("""
                    UPDATE volumes 
                    SET title = ?, release_date = ?, cover_url = ?, is_confirmed = ?
                    WHERE series_id = ? AND volume_number = ?
                """, (
                    volume_data.get('title'),
                    volume_data.get('release_date'),
                    volume_data.get('cover_url'),
                    volume_data.get('is_confirmed', False),
                    series_id,
                    volume_data['volume_number']
                ), commit=True)
                volume_id = existing[0]['id']
            else:
                # Insert new volume
                execute_query("""
                    INSERT INTO volumes (series_id, volume_number, title, release_date, cover_url, is_confirmed)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    series_id,
                    volume_data['volume_number'],
                    volume_data.get('title'),
                    volume_data.get('release_date'),
                    volume_data.get('cover_url'),
                    volume_data.get('is_confirmed', False)
                ), commit=True)
                
                # Get the inserted ID
                result = execute_query(
                    "SELECT last_insert_rowid() as id",
                    ()
                )
                volume_id = result[0]['id']
            
            saved_volumes.append({
                "id": volume_id,
                "volume_number": volume_data['volume_number'],
                "title": volume_data.get('title'),
                "release_date": volume_data.get('release_date'),
                "cover_url": volume_data.get('cover_url'),
                "is_confirmed": volume_data.get('is_confirmed', False)
            })
        
        LOGGER.info(f"Saved {len(saved_volumes)} volumes for series {series_id}")
        return jsonify({
            "success": True,
            "message": f"Saved {len(saved_volumes)} volumes",
            "volumes": saved_volumes
        }), 200
        
    except Exception as e:
        LOGGER.error(f"Error saving volumes: {e}")
        return jsonify({"error": str(e)}), 500


@manga_prepopulation_api_bp.route('/manga-prepopulation/chapters', methods=['POST'])
def save_chapters():
    """Save prepopulated chapter data.
    
    Request body:
        {
            "series_id": 123,
            "chapters": [
                {
                    "chapter_number": 1,
                    "title": "Chapter 1",
                    "release_date": "2023-01-01",
                    "is_confirmed": false
                }
            ]
        }
    """
    try:
        data = request.json or {}
        series_id = data.get('series_id')
        chapters = data.get('chapters', [])
        
        if not series_id or not chapters:
            return jsonify({"error": "Missing series_id or chapters"}), 400
        
        saved_chapters = []
        for chapter_data in chapters:
            # Check if chapter already exists
            existing = execute_query(
                "SELECT id FROM chapters WHERE series_id = ? AND chapter_number = ?",
                (series_id, chapter_data['chapter_number'])
            )
            
            if existing:
                # Update existing chapter
                execute_query("""
                    UPDATE chapters 
                    SET title = ?, release_date = ?, is_confirmed = ?
                    WHERE series_id = ? AND chapter_number = ?
                """, (
                    chapter_data.get('title'),
                    chapter_data.get('release_date'),
                    chapter_data.get('is_confirmed', False),
                    series_id,
                    chapter_data['chapter_number']
                ), commit=True)
                chapter_id = existing[0]['id']
            else:
                # Insert new chapter
                execute_query("""
                    INSERT INTO chapters (series_id, chapter_number, title, release_date, is_confirmed)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    series_id,
                    chapter_data['chapter_number'],
                    chapter_data.get('title'),
                    chapter_data.get('release_date'),
                    chapter_data.get('is_confirmed', False)
                ), commit=True)
                
                # Get the inserted ID
                result = execute_query(
                    "SELECT last_insert_rowid() as id",
                    ()
                )
                chapter_id = result[0]['id']
            
            saved_chapters.append({
                "id": chapter_id,
                "chapter_number": chapter_data['chapter_number'],
                "title": chapter_data.get('title'),
                "release_date": chapter_data.get('release_date'),
                "is_confirmed": chapter_data.get('is_confirmed', False)
            })
        
        LOGGER.info(f"Saved {len(saved_chapters)} chapters for series {series_id}")
        return jsonify({
            "success": True,
            "message": f"Saved {len(saved_chapters)} chapters",
            "chapters": saved_chapters
        }), 200
        
    except Exception as e:
        LOGGER.error(f"Error saving chapters: {e}")
        return jsonify({"error": str(e)}), 500


@manga_prepopulation_api_bp.route('/manga-prepopulation/batch', methods=['POST'])
def save_batch_data():
    """Save both volumes and chapters in one batch operation with cover downloads.
    
    Request body:
        {
            "series_id": 123,
            "volumes": [...],
            "chapters": [...],
            "manga_dex_id": "abc123",
            "cover_data": {"1": "cover1.jpg", "2": "cover2.jpg"}
        }
    """
    try:
        data = request.json or {}
        series_id = data.get('series_id')
        volumes = data.get('volumes', [])
        chapters = data.get('chapters', [])
        manga_dex_id = data.get('manga_dex_id')
        cover_data = data.get('cover_data', {})
        
        if not series_id:
            return jsonify({"error": "Missing series_id"}), 400
        
        results = {}
        saved_volumes = []
        
        # Save volumes first to get their IDs
        if volumes:
            for volume_data in volumes:
                # Check if volume already exists
                existing = execute_query(
                    "SELECT id FROM volumes WHERE series_id = ? AND volume_number = ?",
                    (series_id, volume_data['volume_number'])
                )
                
                if existing:
                    # Update existing volume
                    execute_query("""
                        UPDATE volumes 
                        SET title = ?, release_date = ?, cover_url = ?
                        WHERE series_id = ? AND volume_number = ?
                    """, (
                        volume_data.get('title'),
                        volume_data.get('release_date'),
                        volume_data.get('cover_url'),
                        series_id,
                        volume_data['volume_number']
                    ), commit=True)
                    volume_id = existing[0]['id']
                else:
                    # Insert new volume
                    execute_query("""
                        INSERT INTO volumes (series_id, volume_number, title, release_date, cover_url)
                        VALUES (?, ?, ?, ?, ?)
                    """, (
                        series_id,
                        volume_data['volume_number'],
                        volume_data.get('title'),
                        volume_data.get('release_date'),
                        volume_data.get('cover_url')
                    ), commit=True)
                    
                    # Get the inserted ID
                    result = execute_query(
                        "SELECT last_insert_rowid() as id",
                        ()
                    )
                    volume_id = result[0]['id']
                
                saved_volumes.append({
                    "id": volume_id,
                    "volume_number": volume_data['volume_number'],
                    "title": volume_data.get('title'),
                    "release_date": volume_data.get('release_date'),
                    "cover_url": volume_data.get('cover_url')
                })
        
        # Download covers if we have MangaDex info
        cover_download_results = None
        if manga_dex_id and cover_data and saved_volumes:
            LOGGER.info(f"Starting cover download for {len(saved_volumes)} volumes")
            cover_download_results = COVER_ART_MANAGER.batch_download_covers(
                series_id, saved_volumes, manga_dex_id, cover_data
            )
            
            # Update volume data with cover paths
            for updated_volume in cover_download_results.get('updated_volumes', []):
                for volume in saved_volumes:
                    if volume['id'] == updated_volume['volume_id']:
                        volume['cover_path'] = updated_volume['cover_path']
                        break
        
        # Save chapters
        saved_chapters = []
        if chapters:
            for chapter_data in chapters:
                # Check if chapter already exists
                existing = execute_query(
                    "SELECT id FROM chapters WHERE series_id = ? AND chapter_number = ?",
                    (series_id, chapter_data['chapter_number'])
                )
                
                if existing:
                    # Update existing chapter
                    execute_query("""
                        UPDATE chapters 
                        SET title = ?, release_date = ?
                        WHERE series_id = ? AND chapter_number = ?
                    """, (
                        chapter_data.get('title'),
                        chapter_data.get('release_date'),
                        series_id,
                        chapter_data['chapter_number']
                    ), commit=True)
                    chapter_id = existing[0]['id']
                else:
                    # Insert new chapter
                    execute_query("""
                        INSERT INTO chapters (series_id, chapter_number, title, release_date)
                        VALUES (?, ?, ?, ?)
                    """, (
                        series_id,
                        chapter_data['chapter_number'],
                        chapter_data.get('title'),
                        chapter_data.get('release_date')
                    ), commit=True)
                    
                    # Get the inserted ID
                    result = execute_query(
                        "SELECT last_insert_rowid() as id",
                        ()
                    )
                    chapter_id = result[0]['id']
                
                saved_chapters.append({
                    "id": chapter_id,
                    "chapter_number": chapter_data['chapter_number'],
                    "title": chapter_data.get('title'),
                    "release_date": chapter_data.get('release_date')
                })
        
        # Log results
        LOGGER.info(f"Batch save completed for series {series_id}: "
                   f"{len(saved_volumes)} volumes, {len(saved_chapters)} chapters")
        
        if cover_download_results:
            LOGGER.info(f"Cover download results: {cover_download_results['success_count']} successful, "
                       f"{len(cover_download_results['failed_volumes'])} failed")
        
        return jsonify({
            "success": True,
            "message": f"Batch save completed for series {series_id}",
            "volumes": saved_volumes,
            "chapters": saved_chapters,
            "cover_download_results": cover_download_results
        }), 200
        
    except Exception as e:
        LOGGER.error(f"Error in batch save: {e}")
        return jsonify({"error": str(e)}), 500


@manga_prepopulation_api_bp.route('/manga-prepopulation/volume/<int:volume_id>/cover', methods=['PUT'])
def update_volume_cover(volume_id):
    """Update or replace a volume's cover image.
    
    Request body:
        {
            "cover_url": "https://new-cover-url.com/image.jpg"
        }
    """
    try:
        data = request.json or {}
        cover_url = data.get('cover_url')
        
        if not cover_url:
            return jsonify({"error": "Missing cover_url"}), 400
        
        # Get volume info
        volumes = execute_query(
            "SELECT series_id, volume_number FROM volumes WHERE id = ?",
            (volume_id,)
        )
        
        if not volumes:
            return jsonify({"error": "Volume not found"}), 404
        
        volume = volumes[0]
        series_id = volume['series_id']
        volume_number = volume['volume_number']
        
        # Delete existing local cover if it exists
        COVER_ART_MANAGER.delete_volume_cover(volume_id)
        
        # Update database with new cover URL
        execute_query(
            "UPDATE volumes SET cover_url = ?, cover_path = NULL WHERE id = ?",
            (cover_url, volume_id),
            commit=True
        )
        
        LOGGER.info(f"Updated cover for volume {volume_id}: {cover_url}")
        return jsonify({
            "success": True,
            "message": "Volume cover updated successfully",
            "cover_url": cover_url
        }), 200
        
    except Exception as e:
        LOGGER.error(f"Error updating volume cover: {e}")
        return jsonify({"error": str(e)}), 500


@manga_prepopulation_api_bp.route('/manga-prepopulation/volume/<int:volume_id>/cover', methods=['DELETE'])
def delete_volume_cover(volume_id):
    """Delete a volume's cover image (both local file and database reference)."""
    try:
        # Delete local cover file and update database
        success = COVER_ART_MANAGER.delete_volume_cover(volume_id)
        
        if success:
            return jsonify({
                "success": True,
                "message": "Volume cover deleted successfully"
            }), 200
        else:
            return jsonify({"error": "Volume not found or cover deletion failed"}), 404
        
    except Exception as e:
        LOGGER.error(f"Error deleting volume cover: {e}")
        return jsonify({"error": str(e)}), 500
