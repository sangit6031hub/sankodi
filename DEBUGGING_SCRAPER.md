# How to Debug and Fix the TamilGun Scraper

## The Problem

I created the scraper with educated guesses about TamilGun's HTML structure. Without actually analyzing the real website, the selectors won't match and videos won't be found.

## Solution: Analyze the Real Website

### Step 1: Run the Website Analyzer

```bash
cd /Users/san/DEV/sankodi
python3 analyze_site.py
```

This will:
- Fetch the actual TamilGun homepage
- Save the raw HTML to `tamilgun_page.html`
- Show you what movie containers exist
- Display sample links and images

### Step 2: Inspect the HTML Manually

1. Open `tamilgun_page.html` in a web browser
2. Right-click on a movie title/thumbnail and select "Inspect Element"
3. Note the CSS classes and structure, example:
   ```html
   <div class="ml-item">
     <div class="ml-item-img">
       <a href="/movies/movie-123/">
         <img src="/img/poster.jpg" alt="Movie Title">
       </a>
     </div>
     <h3 class="ml-item-title">Movie Title</h3>
   </div>
   ```

### Step 3: Update the Selectors in tamilgun.py

Once you know the actual structure, update the `list_videos()` function:

**BEFORE (generic guesses):**
```python
movie_items = soup.find_all('div', class_=['movie', 'item', 'post'])
```

**AFTER (real selectors):**
```python
# Example based on actual structure discovered
movie_items = soup.select('div.ml-item')  # or whatever you find
for item in movie_items:
    title = item.select_one('.ml-item-title').get_text()
    link = item.select_one('a')['href']
    thumb = item.select_one('img')['src']
```

### Step 4: Find the Video Source

1. Click on a movie in TamilGun
2. Right-click on the video player → Inspect Element
3. Look for ONE of these:
   
   **Option A: HTML5 Video Tag**
   ```html
   <video>
     <source src="https://cdn.example.com/video.mp4" type="video/mp4">
   </video>
   ```
   Extract: `source_tag['src']`

   **Option B: iFrame Player**
   ```html
   <iframe src="https://player.example.com/p123"></iframe>
   ```
   Extract: `iframe['src']`

   **Option C: JavaScript Video Config**
   ```javascript
   var playerConfig = {
     sources: [{src: "https://cdn.example.com/video.mp4"}]
   }
   ```
   Extract with regex: `re.findall(r'https?://[^"\']+\.mp4', script.string)`

4. Update `get_video_url()` function with the correct extraction method

### Step 5: Test the Scraper

```bash
cd /Users/san/DEV/sankodi
python3 << 'EOF'
from resources.lib import tamilgun

# Test list_videos
result = tamilgun.list_videos("https://tamilgun.now/movies/", page=1)
print(f"Found {len(result['videos'])} videos")
if result['videos']:
    print(f"First video: {result['videos'][0]}")

# Test get_video_url
if result['videos']:
    video_url = tamilgun.get_video_url(result['videos'][0]['url'])
    print(f"Video URL: {video_url}")
EOF
```

## Common Issues

### Site blocks requests
**Solution**: Add delays and rotate user-agents
```python
import time
time.sleep(1)  # Add delay between requests
```

### Video URL is on CDN (like JsDelivr, Cloudflare)
**Solution**: The script should handle these automatically since we look for any URL

### Site uses JavaScript to load videos
**Solution**: You may need Selenium instead of BeautifulSoup
```python
# Alternative: Use Selenium for JavaScript-heavy sites
from selenium import webdriver
driver = webdriver.Chrome()
driver.get(url)
# Wait for JavaScript to load
```

### Pagination doesn't use ?offset
**Solution**: Check actual pagination links and adjust:
```html
<a href="/movies/?page=2">Next</a>
<!-- Update pagination logic -->
```

## What Info You Need to Provide Me

Run `python3 analyze_site.py` and share:
1. What containers were found (e.g., "Found X elements matching 'div.ml-item'")
2. The actual HTML of a sample movie entry
3. A movie page URL example
4. Whether the video is in `<video>`, `<iframe>`, or JavaScript

Then I can fix the scraper accurately!

## Quick Test Without Uploading

After analyzing, you can test locally:

```bash
python3 << 'EOF'
from resources.lib import tamilgun

# This will show you what the scraper finds
result = tamilgun.list_videos("https://tamilgun.now/movies/", page=1)
print(result)
EOF
```
