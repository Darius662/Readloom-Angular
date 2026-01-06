#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Kavita integration module.
Handles integration with Kavita e-book server.
"""

import requests
from typing import Dict, Tuple, Optional
from backend.base.logging import LOGGER
from backend.internals.db import execute_query


def get_kavita_settings() -> Optional[Dict]:
    """Get Kavita settings from database.
    
    Returns:
        dict: Kavita settings or None if not configured.
    """
    try:
        result = execute_query(
            "SELECT value FROM settings WHERE key = 'kavita_settings'"
        )
        
        if result:
            import json
            settings_json = result[0]['value']
            return json.loads(settings_json)
        return None
    except Exception as e:
        LOGGER.error(f"Error getting Kavita settings: {e}")
        return None


def save_kavita_settings(url: str, username: str, password: str, enabled: bool = True) -> bool:
    """Save Kavita settings to database.
    
    Args:
        url (str): Kavita server URL
        username (str): Kavita username
        password (str): Kavita password
        enabled (bool): Whether integration is enabled
    
    Returns:
        bool: True if saved successfully
    """
    try:
        import json
        settings = {
            'url': url,
            'username': username,
            'password': password,
            'enabled': enabled
        }
        settings_json = json.dumps(settings)
        
        # Check if settings exist
        existing = execute_query(
            "SELECT id FROM settings WHERE key = 'kavita_settings'"
        )
        
        if existing:
            execute_query(
                "UPDATE settings SET value = ? WHERE key = 'kavita_settings'",
                (settings_json,),
                commit=True
            )
        else:
            execute_query(
                "INSERT INTO settings (key, value) VALUES (?, ?)",
                ('kavita_settings', settings_json),
                commit=True
            )
        
        LOGGER.info("Kavita settings saved successfully")
        return True
    except Exception as e:
        LOGGER.error(f"Error saving Kavita settings: {e}")
        return False


def test_kavita_connection(url: str, username: str, password: str) -> Tuple[bool, str]:
    """Test connection to Kavita server.
    
    Args:
        url (str): Kavita server URL
        username (str): Kavita username
        password (str): Kavita password
    
    Returns:
        tuple: (success: bool, message: str)
    """
    try:
        # Ensure URL doesn't have trailing slash
        url = url.rstrip('/')
        
        # Test connection by attempting to get API info
        response = requests.post(
            f"{url}/api/Account/login",
            json={
                'username': username,
                'password': password
            },
            timeout=10
        )
        
        if response.status_code == 200:
            LOGGER.info(f"Successfully connected to Kavita server at {url}")
            return True, "Connection successful"
        else:
            error_msg = f"Authentication failed: {response.status_code}"
            LOGGER.warning(f"Kavita connection failed: {error_msg}")
            return False, error_msg
    
    except requests.exceptions.ConnectionError:
        error_msg = "Could not connect to Kavita server. Check URL and ensure server is running."
        LOGGER.error(f"Kavita connection error: {error_msg}")
        return False, error_msg
    except requests.exceptions.Timeout:
        error_msg = "Connection to Kavita server timed out"
        LOGGER.error(f"Kavita timeout: {error_msg}")
        return False, error_msg
    except Exception as e:
        error_msg = f"Error testing Kavita connection: {str(e)}"
        LOGGER.error(error_msg)
        return False, error_msg


def get_kavita_libraries(url: str, username: str, password: str) -> Tuple[list, str]:
    """Get list of libraries from Kavita server.
    
    Args:
        url (str): Kavita server URL
        username (str): Kavita username
        password (str): Kavita password
    
    Returns:
        tuple: (libraries: list, error: str or None)
    """
    try:
        url = url.rstrip('/')
        
        # First, authenticate
        auth_response = requests.post(
            f"{url}/api/Account/login",
            json={
                'username': username,
                'password': password
            },
            timeout=10
        )
        
        if auth_response.status_code != 200:
            return [], "Authentication failed"
        
        token = auth_response.json().get('token')
        if not token:
            return [], "No token received from server"
        
        # Get libraries
        headers = {'Authorization': f'Bearer {token}'}
        libraries_response = requests.get(
            f"{url}/api/Library",
            headers=headers,
            timeout=10
        )
        
        if libraries_response.status_code == 200:
            libraries = libraries_response.json()
            LOGGER.info(f"Retrieved {len(libraries)} libraries from Kavita")
            return libraries, None
        else:
            return [], f"Failed to get libraries: {libraries_response.status_code}"
    
    except Exception as e:
        error_msg = f"Error getting Kavita libraries: {str(e)}"
        LOGGER.error(error_msg)
        return [], error_msg


def get_kavita_series(url: str, username: str, password: str, library_id: int) -> Tuple[list, str]:
    """Get series from a specific Kavita library.
    
    Args:
        url (str): Kavita server URL
        username (str): Kavita username
        password (str): Kavita password
        library_id (int): Library ID
    
    Returns:
        tuple: (series: list, error: str or None)
    """
    try:
        url = url.rstrip('/')
        
        # Authenticate
        auth_response = requests.post(
            f"{url}/api/Account/login",
            json={
                'username': username,
                'password': password
            },
            timeout=10
        )
        
        if auth_response.status_code != 200:
            return [], "Authentication failed"
        
        token = auth_response.json().get('token')
        if not token:
            return [], "No token received from server"
        
        # Get series
        headers = {'Authorization': f'Bearer {token}'}
        series_response = requests.get(
            f"{url}/api/Series/library/{library_id}",
            headers=headers,
            timeout=10
        )
        
        if series_response.status_code == 200:
            series = series_response.json()
            LOGGER.info(f"Retrieved {len(series)} series from Kavita library {library_id}")
            return series, None
        else:
            return [], f"Failed to get series: {series_response.status_code}"
    
    except Exception as e:
        error_msg = f"Error getting Kavita series: {str(e)}"
        LOGGER.error(error_msg)
        return [], error_msg
