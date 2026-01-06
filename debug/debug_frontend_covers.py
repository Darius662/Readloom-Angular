#!/usr/bin/env python3

import sys
sys.path.append('backend')

from backend.internals.db import execute_query

def debug_frontend_covers():
    """Debug why covers aren't showing in the frontend."""
    
    print("🔍 Debugging Frontend Cover Display Issue")
    print("=" * 50)
    
    # Check Kumo desu ga, Nani ka? specifically
    print(f"\n📚 Checking Kumo desu ga, Nani ka? volumes...")
    
    series = execute_query("SELECT id, title FROM series WHERE title LIKE '%Kumo%'")
    
    if not series:
        print("❌ Series not found")
        return
    
    series_id = series[0]['id']
    series_title = series[0]['title']
    
    print(f"✅ Found series: {series_title} (ID: {series_id})")
    
    # Get all volumes for this series
    volumes = execute_query("""
        SELECT id, volume_number, title, cover_path, cover_url, created_at, updated_at
        FROM volumes 
        WHERE series_id = ? 
        ORDER BY volume_number
    """, (series_id,))
    
    print(f"\n📊 Volume Analysis:")
    print(f"   Total volumes: {len(volumes)}")
    
    volumes_with_covers = 0
    volumes_without_covers = 0
    
    for vol in volumes:
        vol_id = vol['id']
        vol_num = vol['volume_number']
        cover_path = vol['cover_path']
        cover_url = vol['cover_url']
        updated_at = vol['updated_at']
        
        if cover_path and cover_url:
            volumes_with_covers += 1
            print(f"   ✅ Volume {vol_num}: Has cover")
            print(f"      Path: {cover_path}")
            print(f"      URL: {cover_url}")
            print(f"      Updated: {updated_at}")
            
            # Check if file actually exists
            from pathlib import Path
            cover_file = Path(cover_path)
            if cover_file.exists():
                file_size = cover_file.stat().st_size
                print(f"      File: ✅ Exists ({file_size:,} bytes)")
            else:
                print(f"      File: ❌ Missing!")
        else:
            volumes_without_covers += 1
            print(f"   ❌ Volume {vol_num}: No cover")
            print(f"      Path: {cover_path}")
            print(f"      URL: {cover_url}")
    
    print(f"\n📈 Summary:")
    print(f"   Volumes with covers: {volumes_with_covers}")
    print(f"   Volumes without covers: {volumes_without_covers}")
    
    # Check the cover URL format
    print(f"\n🔍 Cover URL Format Analysis:")
    for vol in volumes[:3]:  # Check first 3
        if vol['cover_url']:
            print(f"   Volume {vol['volume_number']}: {vol['cover_url']}")
            
            # Check if URL starts with /
            if vol['cover_url'].startswith('/'):
                print(f"      ✅ Correct format (starts with /)")
            elif vol['cover_url'].startswith('http'):
                print(f"      ⚠️  External URL (MangaDex)")
            else:
                print(f"      ❌ Incorrect format")
    
    # Test API endpoints that frontend would use
    print(f"\n🌐 Testing Frontend API Endpoints:")
    
    for vol in volumes[:3]:  # Test first 3
        vol_id = vol['id']
        vol_num = vol['volume_number']
        
        if vol['cover_url']:
            print(f"   Volume {vol_num} API test:")
            
            # Test the cover endpoint
            try:
                import requests
                response = requests.get(f"http://localhost:7227/api/cover-art/volume/{vol_id}", timeout=5)
                
                if response.status_code == 200:
                    print(f"      ✅ API endpoint works")
                    content_type = response.headers.get('content-type', 'Unknown')
                    print(f"      Content-Type: {content_type}")
                else:
                    print(f"      ❌ API endpoint failed: {response.status_code}")
            except Exception as e:
                print(f"      ❌ API test failed: {e}")
    
    # Check if there might be a frontend caching issue
    print(f"\n💡 Possible Frontend Issues:")
    print(f"   1. Browser cache - Try hard refresh (Ctrl+F5)")
    print(f"   2. Frontend not calling cover API")
    print(f"   3. CSS/display issues hiding images")
    print(f"   4. JavaScript errors preventing image loading")
    print(f"   5. API endpoint path mismatch")
    
    # Provide specific recommendations
    print(f"\n🎯 Recommendations:")
    if volumes_with_covers > 0:
        print(f"   ✅ Database and backend are working correctly")
        print(f"   🔧 Issue is likely in the frontend:")
        print(f"      - Check browser console for JavaScript errors")
        print(f"      - Verify frontend is calling /api/cover-art/volume/{vol_id}")
        print(f"      - Check if images have correct src attributes")
        print(f"      - Try clearing browser cache")
    else:
        print(f"   ❌ No covers found in database")
        print(f"   🔧 Run manual cover system again")

if __name__ == '__main__':
    debug_frontend_covers()
