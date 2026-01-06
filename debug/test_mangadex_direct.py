#!/usr/bin/env python3

import requests

def test_mangadex_direct_access():
    """Test different approaches to access MangaDex covers."""
    
    # Test URLs
    test_urls = [
        "https://uploads.mangadex.org/covers/a2c1d849-af05-4bbc-b2a7-866ebb10331f/da0341d8-5526-452c-8bd3-dc8e3cd89f99.jpg",
        "https://uploads.mangadex.org/covers/3a0bf061-83f4-476d-85b4-28c65432b86d/c8d7e9a1-8c5d-4b2f-9c7a-8d8e5f6a7b8c.jpg"
    ]
    
    # Test different header combinations
    header_sets = [
        # Basic headers
        {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
        },
        # With referer
        {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
            'Referer': 'https://mangadex.org/',
        },
        # MangaDex specific
        {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
            'Referer': 'https://mangadex.org/',
            'Accept-Language': 'en-US,en;q=0.9',
        },
        # Simple
        {
            'User-Agent': 'Readloom/1.0',
            'Accept': 'image/*',
        }
    ]
    
    print("🔍 Testing MangaDex Cover Access")
    print("=" * 50)
    
    for i, url in enumerate(test_urls, 1):
        manga_name = "One Piece" if "a2c1d849" in url else "Kaijuu No. 8"
        print(f"\n📚 Testing {manga_name} (URL {i}):")
        print(f"   URL: {url}")
        
        for j, headers in enumerate(header_sets, 1):
            header_name = f"Headers {j}"
            if 'Referer' in headers:
                header_name += " (with Referer)"
            
            print(f"   🧪 {header_name}:")
            
            try:
                response = requests.head(url, headers=headers, timeout=10)
                status = response.status_code
                
                if status == 200:
                    content_type = response.headers.get('content-type', 'Unknown')
                    content_length = response.headers.get('content-length', 'Unknown')
                    print(f"      ✅ SUCCESS - Status: {status}, Type: {content_type}, Size: {content_length}")
                    
                    # If successful, try to actually download it
                    try:
                        response = requests.get(url, headers=headers, timeout=10, stream=True)
                        if response.status_code == 200:
                            # Read first few bytes to verify it's an image
                            content = response.content[:100]
                            if content.startswith(b'\xff\xd8\xff'):  # JPEG
                                print(f"      🖼️  Verified JPEG image")
                            elif content.startswith(b'\x89PNG'):  # PNG
                                print(f"      🖼️  Verified PNG image")
                            else:
                                print(f"      🖼️  Image format detected (first bytes: {content[:10].hex()})")
                    except Exception as e:
                        print(f"      ⚠️  Download test failed: {e}")
                else:
                    print(f"      ❌ FAILED - Status: {status}")
                    
            except Exception as e:
                print(f"      ❌ ERROR - {e}")
    
    print("\n🎯 Summary:")
    print("If none of the above work, MangaDex may require:")
    print("1. API authentication")
    print("2. Different CDN endpoints")
    print("3. Rate limiting")
    print("4. Geographic restrictions")

if __name__ == '__main__':
    test_mangadex_direct_access()
