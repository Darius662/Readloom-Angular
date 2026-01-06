#!/usr/bin/env python3

import sys
sys.path.append('backend')

import requests
from backend.internals.db import execute_query

def test_frontend_api_calls():
    """Test the exact API calls the frontend would make for volume covers."""
    
    print("🔍 Testing Frontend API Calls")
    print("=" * 50)
    
    # Get some volume data like the frontend would
    print("\n📚 Getting volume data for Kumo desu ga, Nani ka?...")
    
    series = execute_query("SELECT id, title FROM series WHERE title LIKE '%Kumo%'")
    
    if not series:
        print("❌ Series not found")
        return
    
    series_id = series[0]['id']
    series_title = series[0]['title']
    
    print(f"✅ Found series: {series_title} (ID: {series_id})")
    
    # Get volumes like the frontend does
    try:
        response = requests.get(f"http://localhost:7227/api/series/{series_id}/volumes", timeout=10)
        
        if response.status_code == 200:
            volumes_data = response.json()
            volumes = volumes_data.get('volumes', [])
            
            print(f"✅ Frontend API returned {len(volumes)} volumes")
            
            # Test the first few volumes
            for i, volume in enumerate(volumes[:5]):
                volume_id = volume.get('id')
                volume_number = volume.get('volume_number')
                cover_path = volume.get('cover_path')
                cover_url = volume.get('cover_url')
                
                print(f"\n📖 Volume {volume_number} (ID: {volume_id}):")
                print(f"   Cover Path: {cover_path}")
                print(f"   Cover URL: {cover_url}")
                
                # Test the cover URL the frontend would generate
                if cover_path:
                    frontend_url = f"http://localhost:7227/api/cover-art/volume/{volume_id}"
                    print(f"   Frontend URL: {frontend_url}")
                    
                    try:
                        cover_response = requests.get(frontend_url, timeout=5)
                        
                        if cover_response.status_code == 200:
                            content_type = cover_response.headers.get('content-type', 'Unknown')
                            content_length = cover_response.headers.get('content-length', 'Unknown')
                            print(f"   ✅ Cover API works!")
                            print(f"      Content-Type: {content_type}")
                            print(f"      Content-Length: {content_length} bytes")
                        else:
                            print(f"   ❌ Cover API failed: {cover_response.status_code}")
                            print(f"      Response: {cover_response.text[:200]}")
                    except Exception as e:
                        print(f"   ❌ Cover API error: {e}")
                else:
                    print(f"   ⚠️  No cover path - would show default cover")
        else:
            print(f"❌ Frontend API failed: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            
    except Exception as e:
        print(f"❌ Frontend API error: {e}")
    
    # Test the series detail endpoint
    print(f"\n🔍 Testing series detail endpoint...")
    try:
        series_response = requests.get(f"http://localhost:7227/api/series/{series_id}", timeout=10)
        
        if series_response.status_code == 200:
            series_data = series_response.json()
            print(f"✅ Series API works!")
            print(f"   Series: {series_data.get('series', {}).get('title')}")
        else:
            print(f"❌ Series API failed: {series_response.status_code}")
    except Exception as e:
        print(f"❌ Series API error: {e}")

if __name__ == '__main__':
    test_frontend_api_calls()
