#!/bin/bash

# Frontend startup script - Run from frontend folder
# Usage: ./run.sh or bash run.sh

echo "Starting Readloom Frontend (Angular)..."

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Check if node_modules exists
if [ ! -d "$SCRIPT_DIR/node_modules" ]; then
    echo ""
    echo "⚠ node_modules not found. Installing dependencies..."
    cd "$SCRIPT_DIR"
    npm install
    if [ $? -ne 0 ]; then
        echo "Error installing dependencies"
        exit 1
    fi
fi

echo ""
echo "✓ Starting Angular development server..."
echo "  Frontend will be available at http://localhost:4200"
echo "  Press Ctrl+C to stop"
echo ""

# Start the Angular dev server
cd "$SCRIPT_DIR"
npm start

exit $?
