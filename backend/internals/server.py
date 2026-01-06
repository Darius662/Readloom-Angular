#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from typing import Optional, Union

from flask import Flask
from flask_cors import CORS
from waitress import serve

from backend.base.definitions import Constants, StartType
from backend.base.logging import LOGGER


class Server:
    """Server class for Readloom."""
    
    def __init__(self):
        """Initialize the server."""
        self.app: Optional[Flask] = None
        self.start_type: Optional[StartType] = None
        self.url_base: str = Constants.DEFAULT_URL_BASE
    
    def create_app(self) -> Flask:
        """Create the Flask application.

        Returns:
            Flask: The Flask application.
        """
        if self.app is not None:
            return self.app
        
        # NOTE: static_folder removed to disable old Jinja frontend
        # Angular frontend is served separately and accessed via API endpoints only
        self.app = Flask(__name__)
        
        # Configure the application
        self.app.config["SECRET_KEY"] = os.urandom(24)
        self.app.config["JSON_SORT_KEYS"] = False
        
        # Configure CORS for Angular frontend
        cors_config = {
            "origins": [
                "http://localhost:4200",      # Angular dev server
                "http://127.0.0.1:4200",      # Angular dev server (localhost)
                "http://localhost:7227",      # Readloom production
                "http://127.0.0.1:7227",      # Readloom production (localhost)
            ],
            "methods": ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization", "X-Requested-With"],
            "expose_headers": ["Content-Type", "X-Total-Count"],
            "supports_credentials": True,
            "max_age": 3600
        }
        CORS(self.app, resources={r"/api/*": cors_config})
        
        # Ensure photo_url column exists in authors table
        try:
            from backend.internals.db import execute_query
            # Check if column exists
            columns = execute_query("PRAGMA table_info(authors)")
            column_names = [col['name'] for col in columns] if columns else []
            
            if 'photo_url' not in column_names:
                # Add photo_url column
                execute_query("""
                    ALTER TABLE authors 
                    ADD COLUMN photo_url TEXT
                """, commit=True)
                import logging
                logging.info("Added photo_url column to authors table")
        except Exception as e:
            import logging
            logging.warning(f"Could not add photo_url column: {e}")
        
        # Run migrations
        try:
            from backend.internals.migrations import run_migrations
            run_migrations()
        except Exception as e:
            import logging
            logging.warning(f"Error running migrations (non-critical): {e}")
        
        # Register blueprints from new backend/api structure
        from backend.api.collections.routes import collections_api
        from backend.api.series.routes import api_series_bp
        from backend.api.authors.routes import authors_api_bp
        from backend.api.root_folders.routes import rootfolders_api_bp
        from backend.api.metadata.routes import metadata_api_bp
        from backend.api.ai_providers.routes import ai_providers_api_bp
        from backend.api.notifications.routes import notifications_api_bp
        from backend.api.calendar.routes import calendar_bp
        from backend.api.books.routes import get_books_routes
        
        # Import author enrichment API with error handling
        try:
            from backend.api.author_enrichment.routes import author_enrichment_api_bp
            LOGGER.info("Successfully imported author enrichment API blueprint")
        except ImportError as e:
            LOGGER.warning(f"Failed to import author_enrichment_api_bp: {e}")
            author_enrichment_api_bp = None
        
        # Load remaining API modules from frontend (to be migrated)
        # NOTE: These imports are temporarily disabled as the frontend folder has been reorganized
        # They will be migrated to backend/api structure in future updates
        try:
            from frontend.api_author_metadata import author_metadata_api_bp
        except ImportError:
            LOGGER.warning("api_author_metadata not available - skipping")
            author_metadata_api_bp = None
        
        try:
            from frontend.api_author_search import author_search_api_bp
        except ImportError:
            LOGGER.warning("api_author_search not available - skipping")
            author_search_api_bp = None
        
        try:
            from frontend.api_authors_complete import authors_api_bp as authors_complete_api_bp
        except ImportError:
            LOGGER.warning("api_authors_complete not available - skipping")
            authors_complete_api_bp = None
        
        try:
            from frontend.api_ebooks import ebooks_api_bp
        except ImportError:
            LOGGER.warning("api_ebooks not available - skipping")
            ebooks_api_bp = None
        
        try:
            from frontend.api_folders import folders_api
        except ImportError:
            LOGGER.warning("api_folders not available - skipping")
            folders_api = None
        
        try:
            from frontend.api_folder_browser import folder_browser_api_bp
            LOGGER.info("Successfully imported folder_browser_api_bp")
        except ImportError as e:
            LOGGER.warning(f"api_folder_browser not available - skipping: {e}")
            folder_browser_api_bp = None
        
        # NOTE: Removed the old frontend author_enrichment import to avoid conflicts
        # The new backend author_enrichment is imported above
        
        try:
            from frontend.image_proxy import image_proxy_bp
        except ImportError:
            LOGGER.warning("image_proxy not available - skipping")
            image_proxy_bp = None
        
        # Register API blueprints from backend/api structure
        self.app.register_blueprint(collections_api)
        self.app.register_blueprint(api_series_bp)
        self.app.register_blueprint(authors_api_bp)
        self.app.register_blueprint(rootfolders_api_bp)
        self.app.register_blueprint(metadata_api_bp)
        self.app.register_blueprint(ai_providers_api_bp, url_prefix='/api')
        self.app.register_blueprint(notifications_api_bp)
        self.app.register_blueprint(calendar_bp)
        
        # Register books API blueprint
        books_api_bp = get_books_routes()
        self.app.register_blueprint(books_api_bp)
        LOGGER.info("Registered books API blueprint")
        
        # Register author enrichment API if import succeeded
        if author_enrichment_api_bp:
            self.app.register_blueprint(author_enrichment_api_bp)
            LOGGER.info("Registered author enrichment API blueprint")
        else:
            LOGGER.warning("Author enrichment API blueprint not available")
        
        # Register new MangaDex proxy blueprints
        try:
            from backend.api.mangadex_proxy import mangadex_proxy_api_bp
            self.app.register_blueprint(mangadex_proxy_api_bp, url_prefix='/api')
            LOGGER.info("Registered MangaDex proxy API blueprint")
        except ImportError as e:
            LOGGER.warning(f"Failed to import mangadex_proxy_api_bp: {e}")
        
        try:
            from backend.api.manga_prepopulation import manga_prepopulation_api_bp
            self.app.register_blueprint(manga_prepopulation_api_bp, url_prefix='/api')
            LOGGER.info("Registered manga prepopulation API blueprint")
        except ImportError as e:
            LOGGER.warning(f"Failed to import manga_prepopulation_api_bp: {e}")
        
        # Register cover art API blueprint
        try:
            from backend.api.cover_art import cover_art_api_bp
            self.app.register_blueprint(cover_art_api_bp)
            LOGGER.info("Registered cover art API blueprint")
        except ImportError as e:
            LOGGER.warning(f"Failed to import cover_art_api_bp: {e}")
        
        # Register remaining API blueprints from frontend (to be migrated)
        if author_metadata_api_bp:
            self.app.register_blueprint(author_metadata_api_bp)
        if author_search_api_bp:
            self.app.register_blueprint(author_search_api_bp)
        if authors_complete_api_bp:
            self.app.register_blueprint(authors_complete_api_bp)
        if ebooks_api_bp:
            self.app.register_blueprint(ebooks_api_bp)
        if folders_api:
            self.app.register_blueprint(folders_api)
        if folder_browser_api_bp:
            self.app.register_blueprint(folder_browser_api_bp)
            LOGGER.info("Registered folder browser API blueprint")
        # NOTE: Removed author_enrichment_api_bp registration to avoid duplicates
        # It's already registered above from the new backend location
        if image_proxy_bp:
            self.app.register_blueprint(image_proxy_bp)
        
        LOGGER.info("Old Jinja frontend routes disabled - using Angular frontend only")
        
        return self.app
    
    def set_url_base(self, url_base: str) -> None:
        """Set the URL base for the server.

        Args:
            url_base (str): The URL base.
        """
        self.url_base = url_base
    
    def run(self, host: str, port: int) -> None:
        """Run the server.

        Args:
            host (str): The host to bind to.
            port (int): The port to bind to.
        """
        if self.app is None:
            self.create_app()
        
        LOGGER.info(f"Starting server on {host}:{port} with URL base '{self.url_base}'")
        
        try:
            serve(
                self.app,
                host=host,
                port=port,
                url_scheme="http",
                threads=8
            )
        except Exception as e:
            LOGGER.error(f"Server error: {e}")
            raise


# Create a global server instance
SERVER = Server()


def handle_start_type(start_type: StartType) -> None:
    """Handle the start type.

    Args:
        start_type (StartType): The start type.
    """
    SERVER.start_type = None
    
    if start_type == StartType.STARTUP:
        LOGGER.info("Starting up Readloom")
    elif start_type == StartType.RESTART:
        LOGGER.info("Restarting Readloom")
    elif start_type == StartType.UPDATE:
        LOGGER.info("Updating Readloom")
