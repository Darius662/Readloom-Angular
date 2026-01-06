#!/usr/bin/env python3

import requests

def test_mangadex_chapters():
    """Test different approaches to get MangaDex chapter data."""
    
    print("🔍 Testing MangaDex Chapter API")
    print("=" * 50)
    
    manga_dex_id = "237d527f-adb5-420e-8e6e-b7dd006fbe47"  # Kaijuu No. 8
    
    # Test different chapter endpoints
    endpoints = [
        f"https://api.mangadex.org/manga/{manga_dex_id}/chapter",
        f"https://api.mangadex.org/chapter",
        f"https://api.mangadex.org/feed",
    ]
    
    for endpoint in endpoints:
        print(f"\n📡 Testing: {endpoint}")
        
        # Try different parameter combinations
        param_sets = [
            {"limit": 100},
            {"limit": 100, "manga": manga_dex_id},
            {"limit": 100, "translatedLanguage[]": "en"},
            {"limit": 100, "manga": manga_dex_id, "translatedLanguage[]": "en"},
        ]
        
        for i, params in enumerate(param_sets, 1):
            print(f"   🧪 Params {i}: {params}")
            
            try:
                response = requests.get(endpoint, params=params, timeout=10)
                print(f"      📊 Status: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if 'data' in data and data['data']:
                        chapters = data['data']
                        print(f"      ✅ Found {len(chapters)} chapters")
                        
                        # Extract volume numbers
                        volume_numbers = set()
                        for chapter in chapters:
                            attributes = chapter.get('attributes', {})
                            volume = attributes.get('volume')
                            if volume:
                                try:
                                    vol_num = int(volume)
                                    volume_numbers.add(vol_num)
                                except ValueError:
                                    pass
                        
                        if volume_numbers:
                            print(f"      📚 Volumes: {sorted(volume_numbers)}")
                        else:
                            print(f"      ❌ No volume numbers found")
                        
                        # Show first chapter structure
                        if chapters:
                            first_chapter = chapters[0]
                            attributes = first_chapter.get('attributes', {})
                            print(f"      📖 First chapter: {list(attributes.keys())}")
                        
                        break  # Found working endpoint
                    else:
                        print(f"      ❌ No data found")
                else:
                    try:
                        error_data = response.json()
                        print(f"      ❌ Error: {error_data}")
                    except:
                        print(f"      ❌ Raw: {response.text[:200]}")
                        
            except Exception as e:
                print(f"      ❌ Request failed: {e}")
    
    # Also try the feed endpoint which might work better
    print(f"\n🔍 Testing feed endpoint...")
    try:
        feed_url = f"https://api.mangadex.org/feed"
        feed_params = {
            "manga[]": manga_dex_id,
            "limit": 100,
            "translatedLanguage[]": "en"
        }
        
        response = requests.get(feed_url, params=feed_params, timeout=10)
        print(f"   📊 Feed Status: {response.status_code}")
        
        if response.status_code == 200:
            feed_data = response.json()
            
            if 'data' in feed_data and feed_data['data']:
                chapters = feed_data['data']
                print(f"   ✅ Feed found {len(chapters)} chapters")
                
                # Extract volume numbers
                volume_numbers = set()
                for chapter in chapters:
                    attributes = chapter.get('attributes', {})
                    volume = attributes.get('volume')
                    if volume:
                        try:
                            vol_num = int(volume)
                            volume_numbers.add(vol_num)
                        except ValueError:
                            pass
                
                if volume_numbers:
                    print(f"   📚 Feed volumes: {sorted(volume_numbers)}")
                else:
                    print(f"   ❌ No volume numbers in feed")
            else:
                print(f"   ❌ No feed data")
        else:
            print(f"   ❌ Feed failed: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Feed error: {e}")
    
    # Let's also check if we can get volume info directly from the manga endpoint
    print(f"\n🔍 Testing manga endpoint with more data...")
    try:
        manga_url = f"https://api.mangadex.org/manga/{manga_dex_id}"
        manga_params = {
            "includes[]": ["cover_art", "chapter", "author", "artist"]
        }
        
        response = requests.get(manga_url, params=manga_params, timeout=10)
        print(f"   📊 Manga Status: {response.status_code}")
        
        if response.status_code == 200:
            manga_data = response.json()
            
            if 'data' in manga_data and manga_data['data']:
                manga = manga_data['data']
                attributes = manga.get('attributes', {})
                
                print(f"   📚 Manga attributes: {list(attributes.keys())}")
                print(f"   📚 Last volume: {attributes.get('lastVolume')}")
                print(f"   📚 Last chapter: {attributes.get('lastChapter')}")
                print(f"   📚 Total chapters: {attributes.get('totalChapters')}")
                
                # Check relationships for chapter info
                relationships = manga.get('relationships', [])
                chapter_count = sum(1 for rel in relationships if rel.get('type') == 'chapter')
                print(f"   📚 Chapter relationships: {chapter_count}")
                
                if chapter_count > 0:
                    print(f"   ✅ Found chapter relationships!")
                    
                    # Extract volume info from chapters
                    volume_numbers = set()
                    for rel in relationships:
                        if rel.get('type') == 'chapter':
                            attributes = rel.get('attributes', {})
                            volume = attributes.get('volume')
                            if volume:
                                try:
                                    vol_num = int(volume)
                                    volume_numbers.add(vol_num)
                                except ValueError:
                                    pass
                    
                    if volume_numbers:
                        print(f"   📚 Volumes from relationships: {sorted(volume_numbers)}")
                    else:
                        print(f"   ❌ No volume numbers in chapter relationships")
                else:
                    print(f"   ❌ No chapter relationships found")
            else:
                print(f"   ❌ No manga data")
        else:
            print(f"   ❌ Manga endpoint failed: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Manga endpoint error: {e}")

if __name__ == '__main__':
    test_mangadex_chapters()
