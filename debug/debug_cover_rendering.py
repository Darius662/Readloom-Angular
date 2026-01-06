#!/usr/bin/env python3

import sys
sys.path.append('backend')

import requests

def debug_cover_rendering():
    """Debug what the frontend is actually getting and what URLs it should generate."""
    
    print("🔍 Debugging Cover Rendering")
    print("=" * 50)
    
    series_id = 6
    
    # Get volumes like frontend does
    try:
        response = requests.get(f"http://localhost:7227/api/series/{series_id}/volumes", timeout=10)
        
        if response.status_code == 200:
            volumes = response.json()
            print(f"✅ Got {len(volumes)} volumes")
            
            print(f"\n🎯 Testing Frontend Logic for First 3 Volumes:")
            
            for i, volume in enumerate(volumes[:3]):
                volume_id = volume.get('id')
                volume_number = volume.get('volume_number')
                cover_path = volume.get('cover_path')
                cover_url = volume.get('cover_url')
                
                print(f"\n📖 Volume {volume_number} (ID: {volume_id}):")
                print(f"   cover_path: {cover_path}")
                print(f"   cover_url: {cover_url}")
                
                # Simulate the exact frontend logic from series.service.ts
                frontend_url = None
                if cover_path:
                    frontend_url = f"http://localhost:7227/api/cover-art/volume/{volume_id}"
                    print(f"   🧠 Logic: cover_path exists -> {frontend_url}")
                elif cover_url:
                    if cover_url.startswith('http'):
                        frontend_url = cover_url
                    else:
                        frontend_url = f"http://localhost:7227{cover_url}"
                    print(f"   🧠 Logic: fallback to cover_url -> {frontend_url}")
                else:
                    print(f"   🧠 Logic: no cover -> would show default")
                
                # Test the actual URL
                if frontend_url:
                    try:
                        img_response = requests.get(frontend_url, timeout=5)
                        if img_response.status_code == 200:
                            content_type = img_response.headers.get('content-type', '')
                            if 'image/' in content_type:
                                print(f"   ✅ URL works! Content-Type: {content_type}")
                            else:
                                print(f"   ⚠️  URL works but not image: {content_type}")
                        else:
                            print(f"   ❌ URL failed: {img_response.status_code}")
                    except Exception as e:
                        print(f"   ❌ URL error: {e}")
            
            # Test if the issue is with the getVolumeCoverUrl method
            print(f"\n🔧 What getVolumeCoverUrl should return:")
            for i, volume in enumerate(volumes[:3]):
                volume_id = volume.get('id')
                cover_path = volume.get('cover_path')
                cover_url = volume.get('cover_url')
                
                # This is the exact logic from series.service.ts
                result = None
                if cover_path:
                    result = f"/api/cover-art/volume/{volume_id}"
                elif cover_url:
                    result = cover_url
                
                print(f"   Volume {volume.get('volume_number')}: {result}")
                
        else:
            print(f"❌ Failed to get volumes: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == '__main__':
    debug_cover_rendering()
