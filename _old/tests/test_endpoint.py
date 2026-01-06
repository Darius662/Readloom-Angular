#!/usr/bin/env python3
"""Test if the AI providers endpoint is registered."""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from frontend.api import api_bp

print("Checking if AI providers endpoints are registered...")
print()

# Get all routes
routes = []
for rule in api_bp.url_map.iter_rules() if hasattr(api_bp, 'url_map') else []:
    routes.append(str(rule))

# Check in app context
from flask import Flask
app = Flask(__name__)
app.register_blueprint(api_bp)

print("Registered routes in api_bp:")
print("-" * 60)

found_ai_providers = False
for rule in app.url_map.iter_rules():
    if 'ai-providers' in str(rule):
        print(f"✓ {rule}")
        found_ai_providers = True

if not found_ai_providers:
    print("✗ No AI providers routes found!")
    print()
    print("All routes:")
    for rule in sorted(app.url_map.iter_rules(), key=lambda r: str(r)):
        print(f"  {rule}")
else:
    print()
    print("✓ AI providers endpoints are registered!")
