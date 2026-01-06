#!/usr/bin/env python3

import requests
import json

def test_mangadex_cover_endpoint():
    """Test MangaDex's cover-specific API endpoint."""
    
    print("🔍 Testing MangaDex Cover API Endpoint")
    print("=" * 50)
    
    # One Piece cover ID from the previous test
    cover_id = "df8780c5-2c6a-4f11-b762-147195d5e593"
    
    # Try different cover API endpoints
    endpoints = [
        f"https://api.mangadex.org/cover/{cover_id}",
        f"https://api.mangadex.org/cover/{cover_id}/image",
        f"https://api.mangadex.org/cover/{cover_id}/file",
    ]
    
    for endpoint in endpoints:
        print(f"\n📡 Testing: {endpoint}")
        
        try:
            response = requests.get(endpoint, timeout=10)
            print(f"   📊 Status: {response.status_code}")
            
            if response.status_code == 200:
                content_type = response.headers.get('content-type', 'Unknown')
                print(f"   📄 Content-Type: {content_type}")
                
                if 'image' in content_type.lower():
                    content_length = response.headers.get('content-length', 'Unknown')
                    print(f"   📏 Content-Length: {content_length} bytes")
                    print(f"   ✅ SUCCESS - Got image data!")
                    
                    # Save a small sample to verify
                    with open('test_cover.jpg', 'wb') as f:
                        f.write(response.content)
                    print(f"   💾 Saved sample as test_cover.jpg")
                    break
                else:
                    print(f"   📝 Response: {response.text[:200]}")
            else:
                try:
                    error_data = response.json()
                    print(f"   ❌ Error: {error_data}")
                except:
                    print(f"   ❌ Raw response: {response.text[:200]}")
                    
        except Exception as e:
            print(f"   ❌ Request failed: {e}")
    
    # Also try to get cover through the manga endpoint with different includes
    print(f"\n🔍 Trying manga endpoint with different includes:")
    
    manga_id = "a2c1d849-af05-4bbc-b2a7-866ebb10331f"
    
    try:
        url = f"https://api.mangadex.org/manga/{manga_id}"
        params = {
            'includes[]': ['cover_art', 'author', 'artist']
        }
        
        response = requests.get(url, params=params, timeout=10)
        print(f"   📊 Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            # Look for any URLs in the response
            response_str = json.dumps(data)
            if 'http' in response_str:
                print(f"   🔗 Found URLs in response!")
                
                # Extract all URLs
                import re
                urls = re.findall(r'https?://[^\s"\']+', response_str)
                for url in set(urls):  # Remove duplicates
                    print(f"      🌐 {url}")
            else:
                print(f"   ❌ No URLs found in response")
        else:
            print(f"   ❌ Failed: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Request failed: {e}")

if __name__ == '__main__':
    test_mangadex_cover_endpoint()
