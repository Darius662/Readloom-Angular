#!/usr/bin/env python3
from backend.internals.server import SERVER

app = SERVER.create_app()

print("All registered routes:")
print("-" * 80)

for rule in sorted(app.url_map.iter_rules(), key=lambda r: r.rule):
    if 'manga' in rule.rule.lower() or rule.endpoint == 'ui.manga_routes.manga_home':
        print(f"Route: {rule.rule}")
        print(f"  Endpoint: {rule.endpoint}")
        print(f"  Methods: {rule.methods}")
        print()

print("\nLooking for /manga specifically:")
for rule in app.url_map.iter_rules():
    if rule.rule == '/manga':
        print(f"Found /manga route:")
        print(f"  Endpoint: {rule.endpoint}")
        print(f"  Methods: {rule.methods}")
        print(f"  Function: {app.view_functions.get(rule.endpoint)}")
