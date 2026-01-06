#!/usr/bin/env python3

import requests
import json

def test_mangadex_api_covers():
    """Test getting cover data through MangaDex API."""
    
    print("🔍 Testing MangaDex API for Cover Data")
    print("=" * 50)
    
    # Test manga IDs
    test_manga = [
        {"id": "a2c1d849-af05-4bbc-b2a7-866ebb10331f", "name": "One Piece"},
        {"id": "3a0bf061-83f4-476d-85b4-28c65432b86d", "name": "Kaijuu No. 8"}
    ]
    
    MANGADEX_API = "https://api.mangadex.org"
    
    for manga in test_manga:
        manga_id = manga["id"]
        name = manga["name"]
        
        print(f"\n📚 Testing {name}")
        print(f"   Manga ID: {manga_id}")
        
        # Try to get manga details with cover art
        try:
            url = f"{MANGADEX_API}/manga/{manga_id}"
            params = {
                'includes[]': 'cover_art'
            }
            
            response = requests.get(url, params=params, timeout=10)
            print(f"   📡 API Request: {url}")
            print(f"   📊 Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                
                if 'data' in data and data['data']:
                    manga_data = data['data']
                    relationships = manga_data.get('relationships', [])
                    
                    print(f"   🔗 Found {len(relationships)} relationships")
                    
                    # Find cover art relationships
                    cover_arts = [rel for rel in relationships if rel.get('type') == 'cover_art']
                    print(f"   🖼️  Found {len(cover_arts)} cover arts")
                    
                    for i, cover in enumerate(cover_arts, 1):
                        cover_id = cover.get('id')
                        attributes = cover.get('attributes', {})
                        filename = attributes.get('fileName')
                        volume = attributes.get('volume', 'Unknown')
                        locale = attributes.get('locale', 'Unknown')
                        
                        print(f"      Cover {i}:")
                        print(f"        ID: {cover_id}")
                        print(f"        Filename: {filename}")
                        print(f"        Volume: {volume}")
                        print(f"        Locale: {locale}")
                        
                        if filename:
                            # Try different CDN URLs
                            cdn_urls = [
                                f"https://uploads.mangadex.org/covers/{manga_id}/{filename}",
                                f"https://mangadex.org/covers/{manga_id}/{filename}",
                            ]
                            
                            for j, cdn_url in enumerate(cdn_urls, 1):
                                try:
                                    head_response = requests.head(cdn_url, timeout=5)
                                    status = head_response.status_code
                                    
                                    if status == 200:
                                        content_type = head_response.headers.get('content-type', 'Unknown')
                                        content_length = head_response.headers.get('content-length', 'Unknown')
                                        print(f"        ✅ CDN {j} WORKS: {status} - {content_type} ({content_length} bytes)")
                                        
                                        # This URL works!
                                        print(f"        🎯 Working URL: {cdn_url}")
                                        break
                                    else:
                                        print(f"        ❌ CDN {j}: {status}")
                                except Exception as e:
                                    print(f"        ❌ CDN {j} Error: {e}")
                        else:
                            print(f"        ❌ No filename found")
                else:
                    print(f"   ❌ No data in response")
            else:
                print(f"   ❌ API Error: {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   📝 Error: {error_data}")
                except:
                    print(f"   📝 Raw response: {response.text[:200]}")
                    
        except Exception as e:
            print(f"   ❌ Request failed: {e}")

if __name__ == '__main__':
    test_mangadex_api_covers()
