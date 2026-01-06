#!/usr/bin/env python3

import sys
sys.path.append('backend')

def test_updated_translation():
    """Test the updated translation function for Kumo desu ga, Nani ka?"""
    
    print("🔍 Testing Updated Translation Function")
    print("=" * 50)
    
    # Test the updated function
    from backend.features.metadata_service.facade import find_mangadex_equivalent
    
    print("\n📚 Testing Kumo desu ga, Nani ka? translation:")
    
    # Test with the AniList ID we found earlier
    anilist_id = "86952"
    series_title = "So I'm a Spider, So What?"  # English title
    
    mangadex_id = find_mangadex_equivalent(anilist_id, series_title)
    
    if mangadex_id:
        print(f"   ✅ SUCCESS!")
        print(f"   AniList ID: {anilist_id}")
        print(f"   Series Title: {series_title}")
        print(f"   MangaDex ID: {mangadex_id}")
        
        # Test if this ID has covers
        print(f"\n🖼️  Testing MangaDex covers...")
        from backend.features.cover_art_manager import COVER_ART_MANAGER
        
        volume_covers = COVER_ART_MANAGER.get_mangadex_covers_for_series(mangadex_id)
        
        if volume_covers:
            print(f"   ✅ Found {len(volume_covers)} volume covers:")
            for cover in volume_covers:
                print(f"      Volume {cover['volume']}: {cover['filename']}")
            
            print(f"\n🎯 READY FOR TESTING!")
            print(f"   ✅ Translation function works")
            print(f"   ✅ MangaDex covers available")
            print(f"   ✅ Cover download should work")
            print(f"\n📚 When you add 'Kumo desu ga, Nani ka?' from AniList:")
            print(f"   1. Series will be created with volumes from MangaFire")
            print(f"   2. Our system will find the MangaDex equivalent")
            print(f"   3. Available covers will be downloaded")
            print(f"   4. Everything should work perfectly!")
        else:
            print(f"   ❌ No volume covers found")
            print(f"   ⚠️  Series will be created but no covers will be downloaded")
    else:
        print(f"   ❌ Still no MangaDex equivalent found")
        print(f"   ⚠️  Series will be created but no covers will be downloaded")

if __name__ == '__main__':
    test_updated_translation()
