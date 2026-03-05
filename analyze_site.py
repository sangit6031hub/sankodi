#!/usr/bin/env python3
"""
TamilGun Website Structure Analyzer
This script helps identify the correct selectors and video sources
"""

import requests
from bs4 import BeautifulSoup
import json

def analyze_tamilgun():
    """Analyze TamilGun website structure"""
    
    url = "https://tamilgun.now/movies/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    print("=" * 80)
    print("TAMILGUN WEBSITE STRUCTURE ANALYZER")
    print("=" * 80)
    
    try:
        print(f"\n[1/5] Fetching {url}...")
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        print(f"✓ Status: {response.status_code}")
        
        soup = BeautifulSoup(response.content, 'html.parser')
        print(f"✓ HTML parsed successfully")
        
        # Get page title
        title = soup.find('title')
        print(f"\n[2/5] PAGE INFORMATION:")
        print(f"  Title: {title.get_text() if title else 'N/A'}")
        print(f"  Content length: {len(response.content)} bytes")
        
        # Save raw HTML for inspection
        with open('tamilgun_page.html', 'w', encoding='utf-8') as f:
            f.write(response.content.decode('utf-8', errors='ignore'))
        print(f"  ✓ Saved raw HTML to: tamilgun_page.html")
        
        # Analyze structure
        print(f"\n[3/5] MOVIE CONTAINERS SEARCH:")
        
        # Look for common patterns
        common_selectors = {
            'div.movie': soup.select('div.movie'),
            'div.post': soup.select('div.post'),
            'div.item': soup.select('div.item'),
            'article.post': soup.select('article.post'),
            'div[data-id]': soup.find_all('div', attrs={'data-id': True}),
            '.box-title': soup.select('.box-title'),
            '.ml-item': soup.select('.ml-item'),
        }
        
        for selector, elements in common_selectors.items():
            if elements:
                print(f"  ✓ Found {len(elements)} elements matching '{selector}'")
        
        # Sample first movie container
        print(f"\n[4/5] SAMPLE MOVIE DATA:")
        
        # Try different approaches to find movie containers
        first_movie = None
        for selector in ['div.movie', 'div.post', 'article.post', '.ml-item']:
            first_movie = soup.select_one(selector)
            if first_movie:
                print(f"\n  Using selector: {selector}")
                print(f"  Full HTML (first 500 chars):\n{str(first_movie)[:500]}...")
                break
        
        # Extract sample links and images
        print(f"\n[5/5] LINKS AND IMAGES:")
        
        all_links = soup.find_all('a', href=True, limit=15)
        print(f"  Sample Links:")
        for i, link in enumerate(all_links[:5]):
            print(f"    {i+1}. {link.get_text(strip=True)[:40]}")
            print(f"       → {link['href']}")
        
        all_images = soup.find_all('img', limit=10)
        print(f"\n  Sample Images:")
        for i, img in enumerate(all_images[:3]):
            print(f"    {i+1}. src: {img.get('src', 'N/A')[:60]}")
            print(f"       alt: {img.get('alt', 'N/A')[:40]}")
        
        print("\n" + "=" * 80)
        print("NEXT STEPS:")
        print("=" * 80)
        print("""
1. Open 'tamilgun_page.html' in a browser to visually inspect the structure
2. Right-click a movie entry → Inspect Element to get exact classes/ids
3. Note the CSS selectors used for:
   - Movie containers
   - Movie titles
   - Thumbnail images
   - Movie links
4. Then click a movie and inspect the video page to find:
   - Where video files are hosted
   - HTML5 <video> source URLs
   - iFrame player URLs
   - Video CDN URLs in JavaScript
5. Update resources/lib/tamilgun.py with correct selectors
        """)
        
    except requests.exceptions.RequestException as e:
        print(f"\n✗ Network Error: {e}")
        print("""
        Possible solutions:
        - The URL might be wrong or site is down
        - Site may block automated requests
        - Try using a VPN or proxy
        - Check if the domain has changed
        """)
    except Exception as e:
        print(f"\n✗ Error: {e}")

if __name__ == '__main__':
    analyze_tamilgun()
