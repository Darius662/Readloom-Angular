#!/usr/bin/env python3

import requests
import json

def debug_mangadex_covers():
    """Debug why we're only getting 1 cover from MangaDex."""
    
    print("🔍 Debugging MangaDex Cover API")
    print("=" * 50)
    
    # Test with Kaijuu No. 8
    manga_dex_id = "71763dfb-8b85-4a74-92df-dfe46478fc5d"
    
    print(f"\n📚 Testing MangaDex ID: {manga_dex_id}")
    
    # Get manga details with all covers
    try:
        response = requests.get(
            f"https://api.mangadex.org/manga/{manga_dex_id}",
            params={"includes[]": "cover_art"},
            timeout=10
        )
        
        print(f"   📊 Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            if 'data' in data and data['data']:
                manga = data['data']
                relationships = manga.get('relationships', [])
                
                print(f"   🔗 Total relationships: {len(relationships)}")
                
                # Count different types
                cover_count = 0
                author_count = 0
                artist_count = 0
                other_count = 0
                
                all_covers = []
                
                for rel in relationships:
                    rel_type = rel.get('type', 'unknown')
                    
                    if rel_type == 'cover_art':
                        cover_count += 1
                        attributes = rel.get('attributes', {})
                        volume = attributes.get('volume')
                        filename = attributes.get('fileName')
                        cover_id = rel.get('id')
                        
                        cover_info = {
                            'id': cover_id,
                            'volume': volume,
                            'filename': filename,
                            'has_volume': volume is not None
                        }
                        
                        all_covers.append(cover_info)
                        
                        print(f"      🖼️  Cover {cover_count}:")
                        print(f"         ID: {cover_id}")
                        print(f"         Volume: {volume}")
                        print(f"         Filename: {filename}")
                        print(f"         Has Volume: {volume is not None}")
                        
                    elif rel_type == 'author':
                        author_count += 1
                    elif rel_type == 'artist':
                        artist_count += 1
                    else:
                        other_count += 1
                
                print(f"\n   📊 Summary:")
                print(f"      🖼️  Covers: {cover_count}")
                print(f"      ✍️  Authors: {author_count}")
                print(f"      🎨  Artists: {artist_count}")
                print(f"      ❓  Others: {other_count}")
                
                # Filter covers with volume info
                volume_covers = [c for c in all_covers if c['has_volume']]
                print(f"\n   📚 Volume covers: {len(volume_covers)}")
                
                for cover in volume_covers:
                    print(f"      Volume {cover['volume']}: {cover['filename']}")
                
                # Try to get more covers using the cover endpoint directly
                print(f"\n🔍 Trying direct cover endpoint...")
                for cover in volume_covers:
                    cover_id = cover['id']
                    
                    try:
                        cover_response = requests.get(f"https://api.mangadex.org/cover/{cover_id}", timeout=10)
                        if cover_response.status_code == 200:
                            cover_data = cover_response.json()
                            if 'data' in cover_data and cover_data['data']:
                                attributes = cover_data['data']['attributes']
                                print(f"      ✅ Cover {cover_id}: {attributes.get('fileName')}")
                        else:
                            print(f"      ❌ Cover {cover_id}: {cover_response.status_code}")
                    except Exception as e:
                        print(f"      ❌ Cover {cover_id}: {e}")
                
                # Test if we can get covers for the main series (without volume)
                main_covers = [c for c in all_covers if not c['has_volume']]
                if main_covers:
                    print(f"\n📖 Main series covers: {len(main_covers)}")
                    for cover in main_covers:
                        print(f"      {cover['filename']}")
                
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
    
    # Also test with a different approach - search for the manga and get covers
    print(f"\n" + "="*50)
    print(f"🔍 Testing search approach...")
    
    try:
        search_response = requests.get(
            "https://api.mangadex.org/manga",
            params={
                "title": "Kaijuu No. 8",
                "includes[]": "cover_art",
                "limit": 10
            },
            timeout=10
        )
        
        if search_response.status_code == 200:
            search_data = search_response.json()
            
            if 'data' in search_data and search_data['data']:
                print(f"   📚 Found {len(search_data['data'])} results")
                
                for i, manga in enumerate(search_data['data']):
                    manga_id = manga['id']
                    title = manga.get('attributes', {}).get('title', {})
                    title_text = title.get('en', title.get('ja', 'Unknown'))
                    
                    print(f"\n   📚 Result {i+1}: {title_text}")
                    print(f"      ID: {manga_id}")
                    
                    # Get covers for this manga
                    covers_response = requests.get(
                        f"https://api.mangadex.org/manga/{manga_id}",
                        params={"includes[]": "cover_art"},
                        timeout=10
                    )
                    
                    if covers_response.status_code == 200:
                        covers_data = covers_response.json()
                        if 'data' in covers_data and covers_data['data']:
                            relationships = covers_data['data'].get('relationships', [])
                            cover_count = sum(1 for rel in relationships if rel.get('type') == 'cover_art')
                            volume_count = sum(1 for rel in relationships 
                                              if rel.get('type') == 'cover_art' and rel.get('attributes', {}).get('volume'))
                            
                            print(f"      🖼️  Total covers: {cover_count}")
                            print(f"      📚 Volume covers: {volume_count}")
                            
                            if volume_count > 1:
                                print(f"      🎯 This might be the correct manga!")
                                
                                # Show volume covers
                                for rel in relationships:
                                    if rel.get('type') == 'cover_art':
                                        attributes = rel.get('attributes', {})
                                        volume = attributes.get('volume')
                                        if volume:
                                            print(f"         Volume {volume}: {attributes.get('fileName')}")
        else:
            print(f"   ❌ Search failed: {search_response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Search failed: {e}")

if __name__ == '__main__':
    debug_mangadex_covers()
