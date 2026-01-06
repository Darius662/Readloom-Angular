#!/usr/bin/env python3

import sys
sys.path.append('backend')

import requests
import json

def debug_volumes_api():
    """Debug the volumes API endpoint to see what it's returning."""
    
    print("🔍 Debugging Volumes API Endpoint")
    print("=" * 50)
    
    series_id = 6  # Kumo desu ga, Nani ka?
    
    try:
        response = requests.get(f"http://localhost:7227/api/series/{series_id}/volumes", timeout=10)
        
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"\nRaw Response Data:")
                print(json.dumps(data, indent=2))
                
                print(f"\nData Type: {type(data)}")
                
                if isinstance(data, list):
                    print(f"Response is a list with {len(data)} items")
                    if data:
                        print(f"First item: {data[0]}")
                elif isinstance(data, dict):
                    print(f"Response is a dict with keys: {list(data.keys())}")
                    if 'volumes' in data:
                        print(f"Volumes key: {data['volumes']}")
                else:
                    print(f"Unexpected data type: {type(data)}")
                    
            except json.JSONDecodeError as e:
                print(f"JSON decode error: {e}")
                print(f"Raw response: {response.text[:500]}")
        else:
            print(f"Error response: {response.text}")
            
    except Exception as e:
        print(f"Request error: {e}")

if __name__ == '__main__':
    debug_volumes_api()
