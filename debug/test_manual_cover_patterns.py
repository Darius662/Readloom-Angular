#!/usr/bin/env python3

import sys
sys.path.append('backend')

def test_cover_patterns():
    """Test the filename patterns that the manual cover system supports."""
    
    print("🔍 Testing Manual Cover Filename Patterns")
    print("=" * 50)
    
    # Import the pattern extraction function
    from manual_cover_system import ManualCoverSystem
    
    system = ManualCoverSystem()
    
    # Test various filename patterns
    test_filenames = [
        # Volume patterns
        "Volume 1.jpg",
        "Volume 2.png",
        "vol 3.jpg",
        "vol.4.png",
        "v5.jpg",
        "v6.png",
        # Chapter patterns
        "Chapter 1.jpg",
        "ch.2.png",
        "ch3.jpg",
        # Number patterns
        "1.jpg",
        "2.png",
        "10.jpg",
        "15.png",
        # Complex patterns
        "My Manga - Volume 1 Cover.jpg",
        "Series_v2_final.png",
        "cover_vol_3.jpg",
        "vol04.png",
        # Edge cases
        "cover.jpg",  # Should fail
        "front.png",  # Should fail
        "volume.jpg",  # Should fail
        "vol.jpg",  # Should fail
    ]
    
    print(f"\n📋 Testing {len(test_filenames)} filename patterns:")
    
    for filename in test_filenames:
        volume_number = system._extract_volume_from_filename(filename)
        
        if volume_number is not None:
            print(f"   ✅ {filename:<30} → Volume {volume_number}")
        else:
            print(f"   ❌ {filename:<30} → No volume detected")
    
    print(f"\n🎯 Supported Patterns:")
    print(f"   📚 Volume patterns:")
    print(f"      - Volume 1, vol 1, vol.1, v1")
    print(f"   📖 Chapter patterns:")
    print(f"      - Chapter 1, ch.1, ch1")
    print(f"   🔢 Number patterns:")
    print(f"      - 1.jpg, 2.png, 10.jpg")
    
    print(f"\n💡 Tips for naming your cover files:")
    print(f"   ✅ Use clear volume numbers: 'Volume 1.jpg', 'vol 2.png'")
    print(f"   ✅ Include volume in filename: 'Series_Volume_1.jpg'")
    print(f"   ✅ Use simple patterns: '1.jpg', '2.png', '3.jpg'")
    print(f"   ❌ Avoid generic names: 'cover.jpg', 'front.png'")
    print(f"   ❌ Don't use special characters that confuse the pattern")

def show_example_structure():
    """Show an example of how to structure your cover files."""
    
    print(f"\n📁 Example Cover Folder Structure:")
    print(f"")
    print(f"📂 My Manga/")
    print(f"   📂 cover_art/")
    print(f"      🖼️  Volume 1.jpg")
    print(f"      🖼️  Volume 2.jpg")
    print(f"      🖼️  Volume 3.jpg")
    print(f"      🖼️  vol 4.png")
    print(f"      🖼️  v5.jpg")
    print(f"      🖼️  6.jpg")
    print(f"      🖼️  7.png")
    print(f"      🖼️  Chapter 8.jpg")
    print(f"      🖼️  ch.9.png")
    print(f"")
    print(f"📂 Another Manga/")
    print(f"   📂 cover_art/")
    print(f"      🖼️  1.jpg")
    print(f"      🖼️  2.jpg")
    print(f"      🖼️  3.jpg")
    print(f"")
    print(f"🎯 How it works:")
    print(f"   1. Place cover files in the 'cover_art' folder")
    print(f"   2. Use volume numbers in filenames")
    print(f"   3. Run the manual cover system")
    print(f"   4. System automatically links covers to volumes")
    print(f"   5. Covers appear in the frontend")

if __name__ == '__main__':
    test_cover_patterns()
    show_example_structure()
