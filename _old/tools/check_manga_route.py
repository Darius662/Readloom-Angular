#!/usr/bin/env python3
from backend.internals.server import SERVER

app = SERVER.create_app()

routes = [r for r in app.url_map.iter_rules() if r.rule == '/manga']
print(f'Found {len(routes)} routes for /manga\n')

for r in routes:
    func = app.view_functions.get(r.endpoint)
    print(f'Route: {r.rule}')
    print(f'  Endpoint: {r.endpoint}')
    print(f'  Function: {func.__name__ if func else "NOT FOUND"}')
    print(f'  Module: {func.__module__ if func else "N/A"}')
    print()
