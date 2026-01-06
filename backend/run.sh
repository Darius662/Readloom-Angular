#!/bin/bash

# Backend startup script - Run from backend folder
# Usage: ./run.sh or bash run.sh

echo "Starting Readloom Backend..."

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"

# Add root directory to Python path
export PYTHONPATH="$ROOT_DIR:$PYTHONPATH"

# Change to root directory to ensure relative paths work
cd "$ROOT_DIR"

# Run the Python backend startup script
python3 backend/run.py

exit $?
