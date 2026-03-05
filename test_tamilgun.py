#!/usr/bin/env python3
"""Test TamilGun scraper"""
import sys
import os

# Mock xbmc before importing tamilgun
class MockXbmc:
    LOGINFO = 0
    LOGDEBUG = 1
    LOGWARNING = 2
    LOGERROR = 3
    
    @staticmethod
    def log(msg, level=0):
        level_names = {0: 'INFO', 1: 'DEBUG', 2: 'WARN', 3: 'ERROR'}
        print(f"[{level_names.get(level, 'UNK')}] {msg}")

sys.modules['xbmc'] = MockXbmc()

# Add plugin path
sys.path.insert(0, '/Users/san/DEV/sankodi/plugin.video.sankodi/resources/lib')

print("\n" + "=" * 80)
print("TESTING TAMILGUN SCRAPER")
print("=" * 80)

try:
    import tamilgun
    print("[INFO] tamilgun module imported successfully\n")
    
    print("[TEST 1] Fetching movies from TamilGun...")
    print("-" * 80)
    
    result = tamilgun.list_videos("https://tamilgun.now/movies/", page=1)
    
    print(f"\n✓ Request completed")
    print(f"  - Videos found: {len(result['videos'])}")
    print(f"  - Total pages detected: {result['total_pages']}")
    
    if result['videos']:
        print(f"\n✓ SUCCESS! Found {len(result['videos'])} videos")
        print("\nFirst 3 videos:")
        for i, video in enumerate(result['videos'][:3], 1):
            print(f"\n  {i}. {video['title'][:60]}")
            print(f"     URL: {video['url'][:70]}")
            print(f"     Thumb: {'Yes' if video['thumb'] != 'DefaultVideo.png' else 'No'}")
    else:
        print(f"\n✗ No videos found")
        print("\nLooks like the HTML selectors need adjustment.")
        print("Run: python3 analyze_site.py")
        print("Then inspect the HTML and update MOVIE_CONTAINER_SELECTOR")
        
except ImportError as e:
    print(f"[ERROR] Import failed: {e}")
except Exception as e:
    print(f"[ERROR] Test failed: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
