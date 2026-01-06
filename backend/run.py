#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Backend startup script - Run from backend folder.
Usage: python run.py
"""

import os
import sys
from pathlib import Path

# Add parent directory to path so we can import from root
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

def main():
    """Start the backend server."""
    try:
        print("Starting Readloom Backend...")
        
        # Create data directory if it doesn't exist (in project root)
        data_dir = Path("../data")
        data_dir.mkdir(parents=True, exist_ok=True)
        
        # Set database location
        from backend.internals.db import set_db_location, setup_db
        set_db_location(str(data_dir))
        setup_db()
        
        # Set up logging
        from backend.base.logging import setup_logging, LOGGER
        setup_logging(str(data_dir / "logs"), "readloom.log")
        LOGGER.info("Starting Readloom Backend")
        
        # Initialize settings
        from backend.internals.settings import Settings
        settings = Settings()
        LOGGER.info("Settings initialized")
        
        # Initialize metadata service
        from backend.features.metadata_service import init_metadata_service
        init_metadata_service()
        
        # Initialize AI providers
        from backend.features.ai_providers import initialize_ai_providers
        initialize_ai_providers()
        
        # Create and run Flask app
        from backend.internals.server import SERVER
        SERVER.create_app()
        
        settings_data = settings.get_settings()
        LOGGER.info(f"Backend initialized successfully")
        print(f"\n✓ Backend running on http://{settings_data.host}:{settings_data.port}")
        print("  API endpoints available at /api/*")
        print("  Press Ctrl+C to stop\n")
        
        SERVER.run(settings_data.host, settings_data.port)
        
        return 0
    except Exception as e:
        print(f"Error starting backend: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
