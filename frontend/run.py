#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Frontend startup script - Run from frontend folder.
Starts the Angular development server.
Usage: python run.py
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    """Start the Angular development server."""
    try:
        print("Starting Readloom Frontend (Angular)...")
        
        # Check if node_modules exists
        frontend_dir = Path(__file__).parent
        node_modules = frontend_dir / "node_modules"
        
        if not node_modules.exists():
            print("\n⚠ node_modules not found. Installing dependencies...")
            result = subprocess.run(
                ["npm", "install"],
                cwd=str(frontend_dir),
                capture_output=False
            )
            if result.returncode != 0:
                print("Error installing dependencies")
                return 1
        
        print("\n✓ Starting Angular development server...")
        print("  Frontend will be available at http://localhost:4200")
        print("  Press Ctrl+C to stop\n")
        
        # Start the Angular dev server
        result = subprocess.run(
            ["npm", "start"],
            cwd=str(frontend_dir),
            capture_output=False
        )
        
        return result.returncode
        
    except FileNotFoundError:
        print("Error: npm not found. Please install Node.js and npm.")
        return 1
    except Exception as e:
        print(f"Error starting frontend: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
