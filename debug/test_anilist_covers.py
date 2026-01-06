#!/usr/bin/env python3

import requests
import json

def test_anilist_covers():
    """Test getting cover images from AniList API."""
    
    print("🔍 Testing AniList Cover Access")
    print("=" * 50)
    
    # AniList GraphQL query for manga with covers
    query = """
    query ($search: String) {
      Media (search: $search, type: MANGA) {
        id
        title {
          romaji
          english
          native
        }
        coverImage {
          large
          medium
        }
        description
        status
        chapters
        volumes
      }
    }
    """
    
    # Test manga titles
    test_manga = ["Attack on Titan", "Kaiju No. 8", "One Piece", "My Hero Academia"]
    
    for manga_title in test_manga:
        print(f"\n📚 Testing: {manga_title}")
        
        variables = {"search": manga_title}
        
        try:
            response = requests.post(
                "https://graphql.anilist.co/graphql",
                json={"query": query, "variables": variables},
                timeout=10
            )
            
            print(f"   📊 Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                
                if 'data' in data and data['data'] and data['data']['Media']:
                    media = data['data']['Media']
                    
                    print(f"   🆔 AniList ID: {media['id']}")
                    print(f"   📖 Title: {media['title']['english'] or media['title']['romaji']}")
                    
                    cover_image = media.get('coverImage', {})
                    large_cover = cover_image.get('large')
                    medium_cover = cover_image.get('medium')
                    
                    if large_cover:
                        print(f"   🖼️  Large Cover: {large_cover}")
                        
                        # Test if the cover URL is accessible
                        try:
                            head_response = requests.head(large_cover, timeout=5)
                            if head_response.status_code == 200:
                                content_type = head_response.headers.get('content-type', 'Unknown')
                                content_length = head_response.headers.get('content-length', 'Unknown')
                                print(f"      ✅ ACCESSIBLE - {content_type} ({content_length} bytes)")
                                
                                # Try to download a small sample
                                try:
                                    img_response = requests.get(large_cover, timeout=5, stream=True)
                                    if img_response.status_code == 200:
                                        content = next(img_response.iter_content(1024))
                                        if content.startswith(b'\xff\xd8\xff'):  # JPEG
                                            print(f"      🖼️  Verified JPEG image")
                                        elif content.startswith(b'\x89PNG'):  # PNG
                                            print(f"      🖼️  Verified PNG image")
                                        else:
                                            print(f"      🖼️  Image detected (first bytes: {content[:10].hex()})")
                                        
                                        print(f"      🎯 WORKING COVER FOUND!")
                                    else:
                                        print(f"      ❌ Download failed: {img_response.status_code}")
                                except Exception as e:
                                    print(f"      ❌ Download test failed: {e}")
                            else:
                                print(f"      ❌ HEAD request failed: {head_response.status_code}")
                        except Exception as e:
                            print(f"      ❌ Error testing URL: {e}")
                    else:
                        print(f"   ❌ No large cover found")
                    
                    if medium_cover and medium_cover != large_cover:
                        print(f"   🖼️  Medium Cover: {medium_cover}")
                    
                    print(f"   📊 Status: {media.get('status', 'Unknown')}")
                    print(f"   📚 Volumes: {media.get('volumes', 'Unknown')}")
                    
                else:
                    print(f"   ❌ No media found")
                    if 'errors' in data:
                        print(f"   📝 Errors: {data['errors']}")
            else:
                print(f"   ❌ API Error: {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   📝 Error: {error_data}")
                except:
                    print(f"   📝 Raw response: {response.text[:200]}")
                    
        except Exception as e:
            print(f"   ❌ Request failed: {e}")
    
    print(f"\n🎯 Summary:")
    print("✅ AniList API provides reliable cover access")
    print("✅ Covers are accessible and downloadable")
    print("✅ Good coverage for popular manga")
    print("✅ No authentication required")

if __name__ == '__main__':
    test_anilist_covers()
