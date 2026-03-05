#!/usr/bin/env python3
from bs4 import BeautifulSoup

with open('/Users/san/DEV/sankodi/tamilgun_page.html', 'r', encoding='utf-8') as f:
    soup = BeautifulSoup(f, 'html.parser')

print("=" * 80)
print("ANALYZING TAMILGUN HTML STRUCTURE")
print("=" * 80)

# Find items
all_items = soup.find_all(['div'], class_=lambda x: x and 'item' in x)

print(f"\n[FOUND] {len(all_items)} video item containers")

if len(all_items) == 0:
    print("\n✗ No 'item' divs found. Checking other possibilities...")
    # Check for videos in iframes or custom player
    iframes = soup.find_all('iframe')
    videos = soup.find_all('video')
    print(f"  - Found {len(iframes)} iframes")
    print(f"  - Found {len(videos)} video tags")
else:
    print("\n✓ Found items! Analyzing first 3 examples:")
    print("-" * 80)
    for idx, item in enumerate(all_items[:3], 1):
        link = item.find('a', href=True)
        title_elem = item.find(['h3', 'h2', 'span'])
        if not title_elem:
            title_elem = item.find('a')
        img = item.find('img')
        
        print(f"\n[Item {idx}]")
        if link:
            print(f"  Link: {link.get('href')[:70]}")
        if title_elem:
            print(f"  Title: {title_elem.get_text(strip=True)[:60]}")
        if img:
            print(f"  Thumb: {img.get('src', 'N/A')[:70]}")
            print(f"  Alt: {img.get('alt', 'N/A')[:50]}")

print("\n" + "=" * 80)
print("RECOMMENDATIONS:")
print("=" * 80)

if len(all_items) > 0:
    print("\nYour selectors need to be updated to:")
    print("  MOVIE_CONTAINER_SELECTOR = 'div[class*=\"item\"]'")
    print("\nOr more specific:")
    print("  MOVIE_CONTAINER_SELECTOR = 'div.image-item, div.item'")
else:
    print("\nThe page might be loading content via JavaScript.")
    print("In that case, you may need to use Selenium instead of BeautifulSoup.")
    print("Or check if the site requires specific headers.")

