#!/usr/bin/env python3

import sys
sys.path.append('backend')

import requests

def debug_frontend_cover_logic():
    """Debug the exact frontend cover logic step by step."""
    
    print("🔍 Debugging Frontend Cover Logic")
    print("=" * 50)
    
    series_id = 6  # Kumo desu ga, Nani ka?
    
    # Step 1: Get volumes like frontend does
    print("\n📚 Step 1: Getting volumes from frontend API...")
    try:
        response = requests.get(f"http://localhost:7227/api/series/{series_id}/volumes", timeout=10)
        
        if response.status_code == 200:
            volumes = response.json()
            print(f"✅ Got {len(volumes)} volumes")
            
            # Step 2: Test frontend logic for first few volumes
            print(f"\n🎯 Step 2: Testing frontend cover logic...")
            
            for i, volume in enumerate(volumes[:3]):
                volume_id = volume.get('id')
                volume_number = volume.get('volume_number')
                cover_path = volume.get('cover_path')
                cover_url = volume.get('cover_url')
                
                print(f"\n📖 Volume {volume_number} (ID: {volume_id}):")
                print(f"   cover_path: {cover_path}")
                print(f"   cover_url: {cover_url}")
                
                # Step 3: Simulate frontend getVolumeCoverUrl() logic
                print(f"   🧠 Frontend Logic:")
                
                # This is the exact logic from series.service.ts line 159-173
                if cover_path:
                    frontend_url = f"http://localhost:7227/api/cover-art/volume/{volume_id}"
                    print(f"      ✅ cover_path exists -> using: {frontend_url}")
                    
                    # Step 4: Test the cover API call
                    print(f"      🌐 Testing cover API...")
                    try:
                        cover_response = requests.get(frontend_url, timeout=5)
                        
                        if cover_response.status_code == 200:
                            content_type = cover_response.headers.get('content-type', 'Unknown')
                            content_length = cover_response.headers.get('content-length', 'Unknown')
                            print(f"         ✅ Cover API works!")
                            print(f"         📄 Content-Type: {content_type}")
                            print(f"         📏 Content-Length: {content_length} bytes")
                            
                            # Check if it's actually an image
                            if 'image/' in content_type:
                                print(f"         🖼️  Valid image response!")
                            else:
                                print(f"         ⚠️  Not an image content-type!")
                                
                        else:
                            print(f"         ❌ Cover API failed: {cover_response.status_code}")
                            print(f"         📝 Response: {cover_response.text[:200]}")
                            
                    except Exception as e:
                        print(f"         ❌ Cover API error: {e}")
                        
                elif cover_url:
                    print(f"      ⚠️  No cover_path -> fallback to cover_url: {cover_url}")
                    
                    # Test if cover_url is accessible
                    if cover_url.startswith('http'):
                        try:
                            external_response = requests.get(cover_url, timeout=5)
                            print(f"         🌐 External URL test: {external_response.status_code}")
                        except Exception as e:
                            print(f"         ❌ External URL error: {e}")
                    else:
                        # Local URL - would need to be served by backend
                        local_url = f"http://localhost:7227{cover_url}"
                        try:
                            local_response = requests.get(local_url, timeout=5)
                            print(f"         🌐 Local URL test: {local_response.status_code}")
                        except Exception as e:
                            print(f"         ❌ Local URL error: {e}")
                else:
                    print(f"      ❌ No cover_path or cover_url -> would show default")
            
        else:
            print(f"❌ Failed to get volumes: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == '__main__':
    debug_frontend_cover_logic()
