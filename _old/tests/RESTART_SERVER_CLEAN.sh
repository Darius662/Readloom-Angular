#!/bin/bash

# Clean Python cache
echo "Cleaning Python cache..."
find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true
find . -type f -name "*.pyo" -delete 2>/dev/null || true

# Clear Flask cache
echo "Clearing Flask cache..."
rm -rf .flask_cache 2>/dev/null || true
rm -rf .pytest_cache 2>/dev/null || true

echo "Cache cleaned!"
echo ""
echo "Now run: python run_dev.py"
