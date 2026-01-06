#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional, Union

from backend.base.definitions import Constants
from backend.base.helpers import ensure_dir_exists, get_logs_dir

# Create a logger
LOGGER = logging.getLogger("Readloom")


def setup_logging(log_folder: Optional[str] = None, log_file: Optional[str] = None) -> None:
    """Set up logging for the application.

    Args:
        log_folder (Optional[str], optional): The folder to store logs in.
            Defaults to None.
        log_file (Optional[str], optional): The name of the log file.
            Defaults to None.
    """
    # Set up the logger
    LOGGER.setLevel(logging.INFO)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create console handler with UTF-8 encoding to handle Unicode characters
    import sys
    console_handler = logging.StreamHandler(sys.stdout)
    # Force UTF-8 encoding for console output
    if hasattr(console_handler.stream, 'reconfigure'):
        console_handler.stream.reconfigure(encoding='utf-8', errors='replace')
    console_handler.setFormatter(formatter)
    LOGGER.addHandler(console_handler)
    
    # Determine log file path
    if log_folder:
        log_path = Path(log_folder)
        if not ensure_dir_exists(log_path):
            LOGGER.error(f"Could not create log folder: {log_folder}")
            return
    else:
        log_path = get_logs_dir()
    
    log_filename = log_file or Constants.DEFAULT_LOG_NAME
    log_file_path = log_path / log_filename
    
    # Create file handler with UTF-8 encoding
    try:
        file_handler = RotatingFileHandler(
            log_file_path,
            maxBytes=Constants.DEFAULT_LOG_SIZE * 1024 * 1024,  # Convert MB to bytes
            backupCount=Constants.DEFAULT_LOG_ROTATION,
            encoding='utf-8',  # Force UTF-8 encoding for file handler
            errors='replace'   # Replace unencodable characters
        )
        file_handler.setFormatter(formatter)
        LOGGER.addHandler(file_handler)
        
        LOGGER.info(f"Logging to {log_file_path}")
    except Exception as e:
        LOGGER.error(f"Could not set up file logging: {e}")
