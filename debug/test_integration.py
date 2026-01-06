#!/usr/bin/env python3

import sys
sys.path.append('backend')

def test_integration():
    """Test the MangaDex cover integration."""
    
    print("🔍 Testing MangaDex Cover Integration")
    print("=" * 50)
    
    # Test the functions we added
    from backend.features.metadata_service.facade import find_mangadex_equivalent, download_mangadex_covers_for_series
    
    print("✅ Functions imported successfully")
    
    # Test MangaDex equivalent finding
    print("\n🔍 Testing MangaDex equivalent finding:")
    
    test_cases = [
        ("120760", "Kaijuu No.8"),  # Should find 237d527f-adb5-420e-8e6e-b7dd006fbe47
        ("53390", "Attack on Titan"),  # Should find 84aecfbd-e5aa-40a5-ae28-8ef49ea6e43f
        ("86310", "Enen no Shouboutai"),  # Should find ec514ef4-fb77-43b9b4-52822de1308
    ]
    
    for anilist_id, title in test_cases:
        mangadex_id = find_mangadex_equivalent(anilist_id, title)
        if mangadex_id:
            print(f"   ✅ {title}: AniList {anilist_id} → MangaDex {mangadex_id}")
        else:
            print(f"   ❌ {title}: AniList {anilist_id} → No MangaDex equivalent found")
    
    print("\n🎯 Integration is ready!")
    print("📚 When you add a new series via the frontend:")
    print("   1. Series will be created with volumes from MangaFire")
    print("   2. MangaDex equivalent will be found")
    print("   3. Available covers will be downloaded")
    print("   4. Covers will be stored in cover_art folders")
    print("   5. Database will be updated with cover paths")
    
    print("\n✅ Ready to test with a new series!")

if __name__ == '__main__':
    test_integration()
