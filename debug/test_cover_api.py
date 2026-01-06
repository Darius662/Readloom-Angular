#!/usr/bin/env python3

import sys
sys.path.append('backend')

import requests
from backend.internals.db import execute_query

def test_cover_api():
    """Test if covers are accessible via the API."""
    
    print("🔍 Testing Cover API Access")
    print("=" * 40)
    
    # Test if backend is running
    try:
        response = requests.get("http://localhost:7227/api/health", timeout=5)
        if response.status_code == 200:
            print("✅ Backend is running!")
        else:
            print(f"⚠️  Backend responded with: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("❌ Backend is not running!")
        print("   Start the backend with: cd backend && python run.py")
        return
    except Exception as e:
        print(f"❌ Error checking backend: {e}")
        return
    
    # Get some volumes with covers to test
    print(f"\n📚 Testing cover endpoints...")
    
    volumes_with_covers = execute_query("""
        SELECT v.id, v.volume_number, v.cover_url, v.cover_path, s.title
        FROM volumes v
        JOIN series s ON v.series_id = s.id
        WHERE v.cover_path IS NOT NULL AND v.cover_path != ''
        ORDER BY s.title, v.volume_number
        LIMIT 10
    """)
    
    if not volumes_with_covers:
        print("❌ No volumes with covers found in database")
        return
    
    print(f"   Found {len(volumes_with_covers)} volumes with covers")
    
    # Test each cover endpoint
    for vol in volumes_with_covers:
        volume_id = vol['id']
        volume_number = vol['volume_number']
        series_title = vol['title']
        cover_url = vol['cover_url']
        cover_path = vol['cover_path']
        
        print(f"\n🖼️  Testing {series_title} Volume {volume_number}:")
        print(f"   Cover URL: {cover_url}")
        print(f"   Cover Path: {cover_path}")
        
        # Test the cover API endpoint
        try:
            api_response = requests.get(
                f"http://localhost:7227/api/cover-art/volume/{volume_id}",
                timeout=10
            )
            
            if api_response.status_code == 200:
                print(f"   ✅ API endpoint working!")
                content_type = api_response.headers.get('content-type', 'Unknown')
                content_length = api_response.headers.get('content-length', 'Unknown')
                print(f"      Content-Type: {content_type}")
                print(f"      Content-Length: {content_length} bytes")
            else:
                print(f"   ❌ API endpoint failed: {api_response.status_code}")
                try:
                    error_data = api_response.json()
                    print(f"      Error: {error_data}")
                except:
                    print(f"      Response: {api_response.text[:200]}")
                    
        except Exception as e:
            print(f"   ❌ API test failed: {e}")
    
    print(f"\n🎯 Cover API testing complete!")
    print(f"   If all tests pass, covers should appear in the frontend.")

if __name__ == '__main__':
    test_cover_api()
