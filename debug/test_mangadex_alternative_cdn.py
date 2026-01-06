#!/usr/bin/env python3

import requests
import json

def test_alternative_mangadex_cdn():
    """Test alternative CDN endpoints for MangaDex covers."""
    
    print("🔍 Testing Alternative MangaDex CDN Endpoints")
    print("=" * 50)
    
    # Cover data from the API
    manga_id = "a2c1d849-af05-4bbc-b2a7-866ebb10331f"
    cover_id = "df8780c5-2c6a-4f11-b762-147195d5e593"
    filename = "da0341d8-5526-452c-8bd3-dc8e3cd89f99.jpg"
    
    # Alternative CDN endpoints to try
    alternative_cdns = [
        f"https://cdn.mangadex.org/covers/{manga_id}/{filename}",
        f"https://mangadex.org/covers/{manga_id}/{filename}",
        f"https://img.mangadex.org/covers/{manga_id}/{filename}",
        f"https://media.mangadex.org/covers/{manga_id}/{filename}",
        f"https://uploads.mangadx.org/covers/{manga_id}/{filename}",
        f"https://mangadex-cdn.com/covers/{manga_id}/{filename}",
    ]
    
    # Test with different user agents that might work
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    ]
    
    for i, cdn_url in enumerate(alternative_cdns, 1):
        print(f"\n🌐 Testing CDN {i}: {cdn_url}")
        
        for j, user_agent in enumerate(user_agents, 1):
            print(f"   🧪 UA {j}:")
            
            headers = {
                'User-Agent': user_agent,
                'Accept': 'image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Referer': 'https://mangadex.org/',
                'Sec-Fetch-Dest': 'image',
                'Sec-Fetch-Mode': 'no-cors',
                'Sec-Fetch-Site': 'cross-site',
            }
            
            try:
                response = requests.head(cdn_url, headers=headers, timeout=10)
                status = response.status_code
                
                if status == 200:
                    content_type = response.headers.get('content-type', 'Unknown')
                    content_length = response.headers.get('content-length', 'Unknown')
                    print(f"      ✅ SUCCESS - {status} - {content_type} ({content_length} bytes)")
                    
                    # If successful, try to download a small part
                    try:
                        response = requests.get(cdn_url, headers=headers, timeout=10, stream=True)
                        if response.status_code == 200:
                            # Read first 1KB to verify
                            content = next(response.iter_content(1024))
                            if content.startswith(b'\xff\xd8\xff'):  # JPEG
                                print(f"      🖼️  Verified JPEG image")
                            elif content.startswith(b'\x89PNG'):  # PNG
                                print(f"      🖼️  Verified PNG image")
                            else:
                                print(f"      🖼️  Image detected (first bytes: {content[:10].hex()})")
                            
                            print(f"      🎯 WORKING CDN FOUND!")
                            return cdn_url, headers
                    except Exception as e:
                        print(f"      ⚠️  Download test failed: {e}")
                else:
                    print(f"      ❌ Status: {status}")
                    
            except Exception as e:
                print(f"      ❌ Error: {e}")
    
    # If no CDN works, try to find what the actual MangaDex website uses
    print(f"\n🔍 Checking MangaDex website for cover URLs...")
    
    try:
        # Get the manga page
        page_url = f"https://mangadex.org/title/{manga_id}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        }
        
        response = requests.get(page_url, headers=headers, timeout=10)
        print(f"   📊 Page Status: {response.status_code}")
        
        if response.status_code == 200:
            # Look for cover URLs in the page
            import re
            content = response.text
            
            # Find image URLs
            img_urls = re.findall(r'https://[^"\']*\.jpg[^"\']*', content, re.IGNORECASE)
            img_urls.extend(re.findall(r'https://[^"\']*\.png[^"\']*', content, re.IGNORECASE))
            
            # Filter for cover-related URLs
            cover_urls = [url for url in img_urls if 'cover' in url.lower() or manga_id in url]
            
            print(f"   🔗 Found {len(cover_urls)} potential cover URLs:")
            for url in set(cover_urls):  # Remove duplicates
                print(f"      🌐 {url}")
                
        else:
            print(f"   ❌ Failed to get page: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Error checking website: {e}")
    
    print(f"\n🎯 Summary:")
    print("If no CDN works, we may need to:")
    print("1. Use a different cover source (AniList, MyAnimeList)")
    print("2. Implement a different approach")
    print("3. Use MangaDex's official CDN with proper authentication")

if __name__ == '__main__':
    result = test_alternative_mangadex_cdn()
    if result:
        cdn_url, headers = result
        print(f"\n🎉 FOUND WORKING SOLUTION!")
        print(f"CDN URL: {cdn_url}")
        print(f"Headers: {headers}")
