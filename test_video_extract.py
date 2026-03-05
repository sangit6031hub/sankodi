#!/usr/bin/env python3

import sys
sys.path.insert(0, '/Users/san/DEV/sankodi/plugin.video.sankodi/resources/lib')

class MockXbmc:
    LOGINFO = 0
    LOGDEBUG = 1
    LOGWARNING = 2
    LOGERROR = 3
    
    @staticmethod
    def log(msg, level=0):
        level_names = {0: 'INFO', 1: 'DEBUG', 2: 'WARN', 3: 'ERROR'}
        if level <= 1:  # Show INFO and DEBUG
            print(f"[{level_names.get(level, 'UNK')}] {msg}")

sys.modules['xbmc'] = MockXbmc()

import tamilgun

print("\n" + "=" * 80)
print("TESTING VIDEO URL EXTRACTION")
print("=" * 80)

test_video_url = "https://tamilgun.now/video/subedaar/"

print(f"\nTesting with: {test_video_url}")
print("-" * 80)

video_stream = tamilgun.get_video_url(test_video_url)

if video_stream:
    print(f"\n✓ SUCCESS! Found video stream URL:")
    print(f"  {video_stream[:100]}...")
else:
    print(f"\n✗ No video URL found in HTML")
    print(f"\nLikely reasons:")
    print(f"  1. Video is in an iFrame (external player)")
    print(f"  2. Video source loaded via JavaScript")
    print(f"  3. Video is region-locked or requires login")

print("\n" + "=" * 80)
