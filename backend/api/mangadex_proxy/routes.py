#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
MangaDex API proxy endpoints to bypass CORS restrictions.
"""

import requests
from flask import Blueprint, jsonify, request
from backend.base.logging import LOGGER

# Create API blueprint
mangadex_proxy_api_bp = Blueprint('api_mangadex_proxy', __name__)

# Log that the blueprint was created
LOGGER.info("MangaDex Proxy API blueprint created")

# MangaDex API base URL
MANGADEX_API = "https://api.mangadex.org"
MANGADEX_COVER_BASE = "https://uploads.mangadex.org/covers"


@mangadex_proxy_api_bp.route('/mangadex/search', methods=['GET'])
def search_manga():
    """Proxy for MangaDex manga search."""
    try:
        title = request.args.get('title', '')
        limit = request.args.get('limit', '5')
        includes = request.args.getlist('includes[]')
        
        if not title:
            return jsonify({"error": "Title parameter is required"}), 400
        
        # Build query parameters
        params = {
            'title': title,
            'limit': limit
        }
        
        # Add includes if provided
        for include in includes:
            params[f'includes[]'] = include
        
        # Make request to MangaDex API
        response = requests.get(f"{MANGADEX_API}/manga", params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        LOGGER.info(f"MangaDex search for '{title}': {len(data.get('data', []))} results")
        
        return jsonify(data), 200
        
    except requests.exceptions.RequestException as e:
        LOGGER.error(f"Error searching MangaDex: {e}")
        return jsonify({"error": f"Failed to search MangaDex: {str(e)}"}), 500
    except Exception as e:
        LOGGER.error(f"Unexpected error in MangaDex search: {e}")
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500


@mangadex_proxy_api_bp.route('/mangadex/chapters/<manga_id>', methods=['GET'])
def get_chapters(manga_id):
    """Proxy for MangaDex chapters."""
    try:
        limit = request.args.get('limit', '500')
        translated_languages = request.args.getlist('translatedLanguage[]')
        
        # Build query parameters
        params = {
            'limit': limit
        }
        
        # Add translated languages if provided
        for lang in translated_languages:
            params[f'translatedLanguage[]'] = lang
        
        # Make request to MangaDex API
        response = requests.get(f"{MANGADEX_API}/manga/{manga_id}/chapter", params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        LOGGER.info(f"MangaDex chapters for {manga_id}: {len(data.get('data', []))} chapters")
        
        return jsonify(data), 200
        
    except requests.exceptions.RequestException as e:
        LOGGER.error(f"Error getting MangaDex chapters: {e}")
        return jsonify({"error": f"Failed to get chapters: {str(e)}"}), 500
    except Exception as e:
        LOGGER.error(f"Unexpected error in MangaDex chapters: {e}")
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500


@mangadex_proxy_api_bp.route('/mangadex/cover/<manga_id>/<filename>')
def get_cover_image(manga_id, filename):
    """Proxy for MangaDex cover images."""
    try:
        # Build cover URL
        cover_url = f"{MANGADEX_COVER_BASE}/{manga_id}/{filename}"
        
        # Make request to MangaDex CDN
        response = requests.get(cover_url, timeout=10)
        response.raise_for_status()
        
        # Return the image data
        from flask import Response
        return Response(response.content, mimetype=response.headers.get('content-type', 'image/jpeg'))
        
    except requests.exceptions.RequestException as e:
        LOGGER.error(f"Error getting MangaDex cover: {e}")
        # Return a default placeholder image
        return jsonify({"error": f"Failed to get cover: {str(e)}"}), 500
    except Exception as e:
        LOGGER.error(f"Unexpected error in MangaDex cover: {e}")
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500


@mangadex_proxy_api_bp.route('/mangadex/health', methods=['GET'])
def health_check():
    """Health check for MangaDex proxy."""
    try:
        # Test basic MangaDex API connectivity
        response = requests.get(f"{MANGADEX_API}/manga?limit=1", timeout=5)
        if response.status_code == 200:
            return jsonify({
                "status": "healthy",
                "mangadex_api": "connected",
                "message": "MangaDex proxy is working correctly"
            }), 200
        else:
            return jsonify({
                "status": "unhealthy",
                "mangadex_api": "disconnected",
                "message": f"MangaDex API returned status {response.status_code}"
            }), 503
            
    except requests.exceptions.RequestException as e:
        return jsonify({
            "status": "unhealthy",
            "mangadex_api": "disconnected",
            "message": f"Failed to connect to MangaDex: {str(e)}"
        }), 503
    except Exception as e:
        return jsonify({
            "status": "unhealthy",
            "mangadex_api": "error",
            "message": f"Unexpected error: {str(e)}"
        }), 500
