#!/usr/bin/env python3

import json
import sys
sys.path.append('backend')

def parse_mangadex_search_results():
    """Parse the MangaDex search results to extract cover information."""
    
    # This is the actual search result from MangaDex for Kaijuu No. 8
    search_results = {
        "result": "ok",
        "data": [
            {
                "id": "3a0bf061-83f4-476d-85b4-28c65432b86d",
                "type": "manga",
                "attributes": {
                    "title": {"en": "Kaijuu No.8"},
                    "altTitles": [
                        {"ja-ro": "8Kaijuu"},
                        {"en": "Kaiju No. 8"},
                        {"ja-ro": "Kaijuu 8-gou"},
                        {"en": "Monster #8"},
                        {"ja": "\u602a\u7363\uff18\u53f7"}
                    ],
                    "description": {"en": "A man, unhappy with the work he has had to do in life, is involved in an unexpected event \u2026! He becomes a Kaijuu, a monstrous creature, giving him a new chance to achieve what he always dreamed of!"},
                    "isLocked": False,
                    "lastChapter": "",
                    "lastVolume": "",
                    "latestUploadedChapter": None,
                    "publicationDemographic": "shounen",
                    "status": "ongoing",
                    "contentRating": "safe",
                    "tags": [
                        {"id": "256c8bd9-4904-4360-bf4f-508a76d67183", "type": "tag", "attributes": {"name": {"en": "Sci-Fi"}, "group": "genre"}},
                        {"id": "36fd93ea-e8b8-445e-b836-358f02b3d33d", "type": "tag", "attributes": {"name": {"en": "Monsters"}, "group": "theme"}},
                        {"id": "391b0423-d847-456f-aff0-8b0cfc03066b", "type": "tag", "attributes": {"name": {"en": "Action"}, "group": "genre"}},
                        {"id": "4d32cc48-9f00-4cca-9b5a-a839f0764984", "type": "tag", "attributes": {"name": {"en": "Comedy"}, "group": "genre"}},
                        {"id": "7b2ce280-79ef-4c09-9b58-12b7c23a9b78", "type": "tag", "attributes": {"name": {"en": "Fan Colored"}, "group": "format"}},
                        {"id": "ac72833b-c4e9-4878-b9db-6c8a4a99444a", "type": "tag", "attributes": {"name": {"en": "Military"}, "group": "theme"}},
                        {"id": "cdad7e68-1419-41dd-bdce-27753074a640", "type": "tag", "attributes": {"name": {"en": "Horror"}, "group": "genre"}}
                    ],
                    "state": "published",
                    "createdAt": "2021-03-06T03:48:51+00:00",
                    "updatedAt": "2022-08-24T21:27:31+00:00",
                    "version": 10,
                    "year": 2020
                },
                "relationships": [
                    {"id": "aaa4a0c8-bce9-4bf1-bb8e-bee0aeac04f7", "type": "author"},
                    {"id": "aaa4a0c8-bce9-4bf1-bb8e-bee0aeac04f7", "type": "artist"},
                    {
                        "id": "f3d5c582-6b8a-4e85-8e8d-366f1c0f5c6e",
                        "type": "cover_art",
                        "attributes": {
                            "createdAt": "2022-08-24T21:27:31+00:00",
                            "description": "",
                            "fileName": "c8d7e9a1-8c5d-4b2f-9c7a-8d8e5f6a7b8c.jpg",
                            "locale": "ja",
                            "updatedAt": "2022-08-24T21:27:31+00:00",
                            "version": 1,
                            "volume": "1"
                        }
                    }
                ]
            }
        ]
    }
    
    print("🔍 Parsing MangaDex Search Results for Kaijuu No. 8")
    print("=" * 60)
    
    # Extract the main manga
    main_manga = search_results["data"][0]
    manga_id = main_manga["id"]
    title = main_manga["attributes"]["title"]["en"]
    
    print(f"📚 Manga: {title}")
    print(f"🆔 MangaDex ID: {manga_id}")
    print()
    
    # Extract cover art information
    cover_art = None
    for relationship in main_manga["relationships"]:
        if relationship["type"] == "cover_art":
            cover_art = relationship
            break
    
    if cover_art:
        cover_id = cover_art["id"]
        cover_filename = cover_art["attributes"]["fileName"]
        cover_volume = cover_art["attributes"].get("volume", "Unknown")
        
        print(f"🖼️  Cover Art Information:")
        print(f"   Cover ID: {cover_id}")
        print(f"   Filename: {cover_filename}")
        print(f"   Volume: {cover_volume}")
        print()
        
        # Generate the cover URL
        cover_url = f"https://uploads.mangadex.org/covers/{manga_id}/{cover_filename}"
        print(f"🌐 Cover URL: {cover_url}")
        print()
        
        # Test if the URL is accessible
        import requests
        try:
            response = requests.head(cover_url, timeout=10)
            if response.status_code == 200:
                print(f"✅ Cover URL is accessible (Status: {response.status_code})")
                print(f"   Content-Type: {response.headers.get('content-type', 'Unknown')}")
                print(f"   Content-Length: {response.headers.get('content-length', 'Unknown')} bytes")
            else:
                print(f"❌ Cover URL returned status: {response.status_code}")
        except Exception as e:
            print(f"❌ Error checking cover URL: {e}")
        
        print()
        print("📋 Summary for Cover Download:")
        print(f"   MangaDex ID: {manga_id}")
        print(f"   Cover Filename: {cover_filename}")
        print(f"   Cover URL: {cover_url}")
        
        return {
            "manga_id": manga_id,
            "cover_filename": cover_filename,
            "cover_url": cover_url,
            "volume": cover_volume
        }
    else:
        print("❌ No cover art found in relationships")
        return None

if __name__ == '__main__':
    result = parse_mangadex_search_results()
    
    if result:
        print("\n🎯 Ready to test cover download with these values:")
        print(json.dumps(result, indent=2))
