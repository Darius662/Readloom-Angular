#!/usr/bin/env python3

import requests

def check_exact_mangadex_match():
    """Check the exact MangaDex match for Kumo Desu ga, Nani ka?"""
    
    print("🔍 Checking Exact MangaDex Match")
    print("=" * 50)
    
    # The exact match from the search results
    mangadex_id = "f4cc68e3-2cbb-4af0-b362-49e4fae6aff5"  # Kumo Desu ga, Nani ka? - Dear Mother
    
    print(f"\n📚 Testing MangaDex ID: {mangadex_id}")
    
    # Get detailed manga info
    try:
        response = requests.get(
            f"https://api.mangadex.org/manga/{mangadex_id}",
            params={"includes[]": "cover_art"},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            
            if 'data' in data and data['data']:
                manga = data['data']
                attributes = manga.get('attributes', {})
                
                print(f"   ✅ Manga Details:")
                print(f"      Title: {attributes.get('title', {})}")
                print(f"      Alt Titles: {attributes.get('altTitles', [])[:3]}...")  # First 3 alt titles
                print(f"      Status: {attributes.get('status')}")
                print(f"      Year: {attributes.get('year')}")
                
                # Check relationships for covers
                relationships = manga.get('relationships', [])
                cover_count = sum(1 for rel in relationships if rel.get('type') == 'cover_art')
                
                print(f"      Total Relationships: {len(relationships)}")
                print(f"      Cover Arts: {cover_count}")
                
                # Show cover details
                volume_covers = []
                for rel in relationships:
                    if rel.get('type') == 'cover_art':
                        cover_attrs = rel.get('attributes', {})
                        volume = cover_attrs.get('volume')
                        filename = cover_attrs.get('fileName')
                        
                        print(f"      🖼️  Cover:")
                        print(f"         Volume: {volume}")
                        print(f"         Filename: {filename}")
                        print(f"         Cover ID: {rel.get('id')}")
                        
                        if volume:  # Only count volume covers
                            volume_covers.append({
                                'volume': volume,
                                'filename': filename,
                                'cover_id': rel.get('id')
                            })
                
                print(f"      Volume Covers: {len(volume_covers)}")
                
                if volume_covers:
                    print(f"      📋 Volume Cover List:")
                    for cover in volume_covers:
                        print(f"         Volume {cover['volume']}: {cover['filename']}")
                    
                    # Test cover download for one volume
                    print(f"\n🚀 Testing cover download...")
                    test_cover = volume_covers[0]
                    
                    cover_url = f"https://uploads.mangadex.org/covers/{mangadex_id}/{test_cover['filename']}"
                    print(f"   Testing cover URL: {cover_url}")
                    
                    try:
                        head_response = requests.head(cover_url, timeout=5)
                        if head_response.status_code == 200:
                            content_type = head_response.headers.get('content-type', 'Unknown')
                            content_length = head_response.headers.get('content-length', 'Unknown')
                            print(f"   ✅ Cover URL accessible!")
                            print(f"      Content-Type: {content_type}")
                            print(f"      Content-Length: {content_length} bytes")
                            
                            # Try to download a small sample
                            try:
                                img_response = requests.get(cover_url, timeout=5, stream=True)
                                if img_response.status_code == 200:
                                    content = next(img_response.iter_content(1024))
                                    if content.startswith(b'\xff\xd8\xff'):  # JPEG
                                        print(f"      🖼️  Verified JPEG image")
                                    elif content.startswith(b'\x89PNG'):  # PNG
                                        print(f"      🖼️  Verified PNG image")
                                    else:
                                        print(f"      🖼️  Image detected (first bytes: {content[:10].hex()})")
                                    
                                    print(f"   ✅ Cover download test successful!")
                                else:
                                    print(f"   ❌ Download failed: {img_response.status_code}")
                            except Exception as e:
                                print(f"   ❌ Download test failed: {e}")
                        else:
                            print(f"   ❌ Cover URL returned: {head_response.status_code}")
                    except Exception as e:
                        print(f"   ❌ Cover URL test failed: {e}")
                else:
                    print(f"   ❌ No volume covers found")
            else:
                print(f"   ❌ No manga data found")
        else:
            print(f"   ❌ API Error: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   📝 Error: {error_data}")
            except:
                print(f"   📝 Raw: {response.text[:200]}")
                
    except Exception as e:
        print(f"   ❌ Request failed: {e}")
    
    # Also check if there's a main series (not the side story)
    print(f"\n🔍 Checking for main series...")
    try:
        response = requests.get(
            "https://api.mangadex.org/manga",
            params={"title": "Kumo desu ga, Nani ka", "limit": 10, "includes[]": "cover_art"},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if 'data' in data and data['data']:
                print(f"   📚 All MangaDex results:")
                for i, manga in enumerate(data['data']):
                    attributes = manga.get('attributes', {})
                    title = attributes.get('title', {})
                    manga_id = manga['id']
                    
                    print(f"      {i+1}. {title.get('en', title.get('ja', 'Unknown'))}")
                    print(f"         ID: {manga_id}")
                    
                    # Check if this is the main series (not side story)
                    manga_title_lower = title.get('en', '').lower()
                    if 'dear mother' not in manga_title_lower and 'side story' not in manga_title_lower:
                        print(f"         🎯 This looks like the main series!")
                        
                        # Get cover count
                        relationships = manga.get('relationships', [])
                        cover_count = sum(1 for rel in relationships if rel.get('type') == 'cover_art')
                        volume_count = sum(1 for rel in relationships 
                                          if rel.get('type') == 'cover_art' and rel.get('attributes', {}).get('volume'))
                        
                        print(f"         Total covers: {cover_count}")
                        print(f"         Volume covers: {volume_count}")
                        
                        if volume_count > 0:
                            print(f"         ✅ This would be a better match for cover downloads!")
                    else:
                        print(f"         ⚠️  This appears to be a side story")
                    
                    print()
    except Exception as e:
        print(f"   ❌ Search error: {e}")

if __name__ == '__main__':
    check_exact_mangadex_match()
