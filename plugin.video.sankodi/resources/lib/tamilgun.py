import requests
from bs4 import BeautifulSoup
import xbmc
import re

# TamilGun module for browsing and playing movies
# 
# IMPORTANT: The selectors below are educated guesses.
# You MUST update them based on actual TamilGun HTML structure.
# 
# To find correct selectors:
# 1. Open the TamilGun website
# 2. Right-click movie entry → Inspect Element
# 3. Note the CSS classes and HTML structure
# 4. Update the selectors below
#

# ============================================================================
# CONFIGURABLE SELECTORS - UPDATE THESE BASED ON ACTUAL SITE STRUCTURE
# ============================================================================

# CSS selector to find movie containers on the list page
# TamilGun uses: <div class="image-item"> for video containers
MOVIE_CONTAINER_SELECTOR = 'div.image-item'

# Extract title from container
def extract_title(container):
    """Extract title from a TamilGun image-item container."""
    # TamilGun: <h3 class="item-title">TITLE</h3>
    title_elem = container.select_one('h3.item-title')
    return title_elem.get_text(strip=True) if title_elem else 'Unknown'

def extract_url(container):
    """Extract movie page URL from container."""
    # TamilGun: <a href="/video/VIDEO-ID/" class="image-link">
    link = container.find('a', class_='image-link', href=True)
    return link['href'] if link else None

def extract_thumb(container):
    """Extract thumbnail image URL from container."""
    # TamilGun: <img src="..." class="item-image">
    img = container.find('img', class_='item-image')
    return img.get('src', '') if img else ''

# ============================================================================
# MAIN FUNCTIONS
# ============================================================================

def list_videos(base_url, page=1):
    """
    Scrape movies from TamilGun with pagination.
    
    Args:
        base_url: Base URL (e.g., https://tamilgun.now/movies/)
        page: Page number (1, 2, 3, ...)
    
    Returns:
        {
            'videos': [
                {'title': str, 'thumb': str, 'url': str, 'plot': str},
                ...
            ],
            'total_pages': int
        }
    """
    try:
        # Build pagination URL
        # TamilGun appears to load all on homepage, but structure suggests pagination might use:
        # Format: /movies/?paged=2 or similar
        if page == 1:
            url = base_url.rstrip('/')
        else:
            # Try pagination with paged parameter (common in WordPress sites)
            separator = '?' if '?' not in base_url else '&'
            url = f"{base_url.rstrip('/')}{separator}paged={page}"  
        
        xbmc.log(f'[TamilGun] Fetching page {page}: {url}', xbmc.LOGINFO)
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        videos = []
        
        # Find all movie containers
        # CRITICAL: Update this selector based on actual site structure
        xbmc.log('[TamilGun] Searching for movie containers...', xbmc.LOGDEBUG)
        movie_containers = soup.select(MOVIE_CONTAINER_SELECTOR)
        xbmc.log(f'[TamilGun] Found {len(movie_containers)} containers', xbmc.LOGINFO)
        
        for idx, container in enumerate(movie_containers[:20]):
            try:
                title = extract_title(container)
                movie_url = extract_url(container)
                thumb = extract_thumb(container)
                
                # Make URLs absolute
                if movie_url and not movie_url.startswith('http'):
                    movie_url = base_url.rstrip('/') + '/' + movie_url.lstrip('/')
                
                if thumb and not thumb.startswith('http'):
                    thumb = base_url.rstrip('/') + '/' + thumb.lstrip('/')
                
                if title and movie_url:
                    videos.append({
                        'title': title,
                        'thumb': thumb or 'DefaultVideo.png',
                        'url': movie_url,
                        'plot': f'Click to watch {title}'
                    })
                    xbmc.log(f'[TamilGun] {idx+1}. {title[:40]} → {movie_url[:60]}', xbmc.LOGDEBUG)
                else:
                    xbmc.log(f'[TamilGun] Skipped item {idx} (incomplete data)', xbmc.LOGDEBUG)
            
            except Exception as e:
                xbmc.log(f'[TamilGun] Error parsing item {idx}: {str(e)}', xbmc.LOGWARNING)
                continue
        
        # Detect total pages
        total_pages = detect_total_pages(soup, page)
        
        xbmc.log(f'[TamilGun] Page {page}: Found {len(videos)} videos of {total_pages} pages total', xbmc.LOGINFO)
        
        return {
            'videos': videos,
            'total_pages': total_pages
        }
    
    except requests.exceptions.RequestException as e:
        xbmc.log(f'[TamilGun] Network error: {str(e)}', xbmc.LOGERROR)
        return {'videos': [], 'total_pages': 0}
    except Exception as e:
        xbmc.log(f'[TamilGun] Error: {str(e)}', xbmc.LOGERROR)
        return {'videos': [], 'total_pages': 0}


def detect_total_pages(soup, current_page):
    """
    Detect total number of pages from pagination controls.
    
    ADJUST THIS based on actual pagination HTML structure.
    """
    try:
        # Try to find pagination element
        pagination = (
            soup.select_one('.pagination') or
            soup.select_one('.pager') or
            soup.select_one('[class*="pagination"]')
        )
        
        if pagination:
            page_links = pagination.find_all('a')
            if page_links:
                # Try to get the highest page number
                last_link = page_links[-1].get_text(strip=True)
                try:
                    return int(last_link)
                except:
                    pass
        
        # Fallback: assume at least this many pages exist
        return max(current_page + 1, 5)
    
    except:
        return current_page + 1


def get_video_url(movie_page_url):
    """
    Extract the direct video URL from a TamilGun movie page.
    
    The video might be in:
    1. HTML5 <video> tag
    2. iFrame player
    3. JavaScript player config
    4. Direct MP4 link
    """
    try:
        xbmc.log(f'[TamilGun] Fetching video page: {movie_page_url}', xbmc.LOGINFO)
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(movie_page_url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Method 1: HTML5 <video> tag with <source>
        xbmc.log('[TamilGun] Checking for HTML5 video tag...', xbmc.LOGDEBUG)
        video_source = soup.find('source', attrs={'type': lambda x: x and 'video' in x.lower()})
        if video_source:
            video_url = video_source.get('src', '')
            if video_url:
                if not video_url.startswith('http'):
                    video_url = movie_page_url.rsplit('/', 1)[0] + '/' + video_url.lstrip('/')
                xbmc.log(f'[TamilGun] Found video in source tag: {video_url[:60]}...', xbmc.LOGINFO)
                return video_url
        
        # Method 2: iFrame embed
        xbmc.log('[TamilGun] Checking for iFrame...', xbmc.LOGDEBUG)
        iframe = soup.find('iframe')
        if iframe:
            iframe_src = iframe.get('src', '')
            if iframe_src and 'http' in iframe_src:
                xbmc.log(f'[TamilGun] Found iFrame: {iframe_src[:60]}...', xbmc.LOGINFO)
                return iframe_src
        
        # Method 3: JavaScript video configuration
        xbmc.log('[TamilGun] Checking for MP4 URLs in scripts...', xbmc.LOGDEBUG)
        scripts = soup.find_all('script')
        for script in scripts:
            if script.string:
                # Look for MP4 URLs
                urls = re.findall(r'https?://[^\s"\'<>]+\.mp4', script.string)
                if urls:
                    xbmc.log(f'[TamilGun] Found MP4 in script: {urls[0][:60]}...', xbmc.LOGINFO)
                    return urls[0]
                
                # Look for video player data URLs
                urls = re.findall(r'https?://[^\s"\'<>]+\.(m3u8|mkv|avi|mov)', script.string)
                if urls:
                    xbmc.log(f'[TamilGun] Found video URL in script: {urls[0][:60]}...', xbmc.LOGINFO)
                    return urls[0]
        
        # Method 4: Direct links in HTML
        xbmc.log('[TamilGun] Checking for direct video links...', xbmc.LOGDEBUG)
        video_links = soup.find_all('a', href=lambda x: x and any(ext in x.lower() for ext in ['.mp4', '.mkv', '.m3u8']))
        if video_links:
            video_url = video_links[0]['href']
            if not video_url.startswith('http'):
                video_url = movie_page_url.rsplit('/', 1)[0] + '/' + video_url.lstrip('/')
            xbmc.log(f'[TamilGun] Found direct link: {video_url[:60]}...', xbmc.LOGINFO)
            return video_url
        
        xbmc.log('[TamilGun] No video URL found on page', xbmc.LOGWARNING)
        return None
    
    except requests.exceptions.RequestException as e:
        xbmc.log(f'[TamilGun] Network error: {str(e)}', xbmc.LOGERROR)
        return None
    except Exception as e:
        xbmc.log(f'[TamilGun] Error extracting video: {str(e)}', xbmc.LOGERROR)
        return None

    """
    Scrape movies from TamilGun with pagination.
    Returns: {
        'videos': [{'title': str, 'thumb': str, 'url': str, 'plot': str}, ...],
        'total_pages': int
    }
    """
    try:
        # Handle pagination: page 1 is root, page 2+ uses offset
        if page == 1:
            url = base_url
        else:
            # TamilGun uses offset-based pagination
            offset = (page - 1) * 20  # Assuming 20 items per page
            separator = '?' if '?' not in base_url else '&'
            url = f"{base_url.rstrip('/')}{separator}offset={offset}"
        
        xbmc.log(f'TamilGun: Fetching {url}', xbmc.LOGINFO)
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        videos = []
        
        # Find all movie containers - TamilGun uses divs with class 'movie' or similar
        # Adjust selectors based on actual HTML structure
        movie_items = soup.find_all('div', class_=['movie', 'item', 'post'])
        
        if not movie_items:
            # Alternative: try finding links in tables or lists
            movie_items = soup.find_all('a', href=lambda x: x and ('/movies/' in x or '/film/' in x))
        
        for item in movie_items[:20]:  # Limit to 20 per page
            try:
                # Extract title
                title_elem = item.find(['h2', 'h3', 'span', 'a'])
                if title_elem:
                    title = title_elem.get_text(strip=True)
                else:
                    title = item.get_text(strip=True)[:50]
                
                # Extract link
                link_elem = item.find('a') if item.name != 'a' else item
                movie_url = link_elem.get('href', '') if link_elem else ''
                
                # Make absolute URL if relative
                if movie_url and not movie_url.startswith('http'):
                    movie_url = base_url.rstrip('/') + '/' + movie_url.lstrip('/')
                
                # Extract thumbnail
                img_elem = item.find('img')
                thumb = img_elem.get('src', '') if img_elem else ''
                
                # Make absolute URL for thumbnail if relative
                if thumb and not thumb.startswith('http'):
                    thumb = base_url.rstrip('/') + '/' + thumb.lstrip('/')
                
                if title and movie_url:
                    videos.append({
                        'title': title,
                        'thumb': thumb or 'DefaultVideo.png',
                        'url': movie_url,
                        'plot': f'Click to watch {title}'
                    })
            except Exception as e:
                xbmc.log(f'Error parsing item: {str(e)}', xbmc.LOGWARNING)
                continue
        
        # Estimate total pages (typically sites have 100+ movies, 20 per page = 5+ pages)
        pagination_elem = soup.find('div', class_=['pagination', 'pager', 'pages'])
        total_pages = 5  # Default to 5 pages
        
        if pagination_elem:
            page_links = pagination_elem.find_all('a')
            if page_links:
                last_page_text = page_links[-1].get_text(strip=True)
                try:
                    total_pages = int(last_page_text)
                except:
                    total_pages = page + 1  # At least assume next page exists
        
        xbmc.log(f'TamilGun: Found {len(videos)} videos on page {page}', xbmc.LOGINFO)
        
        return {
            'videos': videos,
            'total_pages': total_pages
        }
    
    except requests.exceptions.RequestException as e:
        xbmc.log(f'TamilGun: Network error: {str(e)}', xbmc.LOGERROR)
        return {'videos': [], 'total_pages': 0}
    except Exception as e:
        xbmc.log(f'TamilGun: Error listing videos: {str(e)}', xbmc.LOGERROR)
        return {'videos': [], 'total_pages': 0}


def get_video_url(movie_page_url):
    """
    Extract the direct video URL from a TamilGun movie page.
    """
    try:
        xbmc.log(f'TamilGun: Fetching video from {movie_page_url}', xbmc.LOGINFO)
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(movie_page_url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Try to find video source
        # Look for <video> tag with <source>
        video_source = soup.find('source', attrs={'type': lambda x: x and 'video' in x.lower()})
        if video_source:
            video_url = video_source.get('src', '')
            if video_url:
                if not video_url.startswith('http'):
                    video_url = movie_page_url.rsplit('/', 1)[0] + '/' + video_url.lstrip('/')
                xbmc.log(f'TamilGun: Found video URL: {video_url}', xbmc.LOGINFO)
                return video_url
        
        # Try iframe approach
        iframe = soup.find('iframe', src=lambda x: x and 'http' in x)
        if iframe:
            iframe_src = iframe.get('src', '')
            if iframe_src:
                xbmc.log(f'TamilGun: Found iframe: {iframe_src}', xbmc.LOGINFO)
                # Note: This may require additional parsing to get actual video URL
                return iframe_src
        
        # Try video player scripts
        script_tags = soup.find_all('script')
        for script in script_tags:
            if script.string and ('video' in script.string.lower() or 'http' in script.string):
                # Look for URL patterns in JavaScript
                import re
                urls = re.findall(r'https?://[^\s"\'<>]+\.mp4', script.string)
                if urls:
                    xbmc.log(f'TamilGun: Found video URL in script: {urls[0]}', xbmc.LOGINFO)
                    return urls[0]
        
        # Last resort: look for any mp4 links
        all_links = soup.find_all('a', href=lambda x: x and '.mp4' in x.lower())
        if all_links:
            video_url = all_links[0].get('href', '')
            if not video_url.startswith('http'):
                video_url = movie_page_url.rsplit('/', 1)[0] + '/' + video_url.lstrip('/')
            xbmc.log(f'TamilGun: Found mp4 link: {video_url}', xbmc.LOGINFO)
            return video_url
        
        xbmc.log('TamilGun: No video URL found on page', xbmc.LOGWARNING)
        return None
    
    except requests.exceptions.RequestException as e:
        xbmc.log(f'TamilGun: Network error getting video: {str(e)}', xbmc.LOGERROR)
        return None
    except Exception as e:
        xbmc.log(f'TamilGun: Error extracting video URL: {str(e)}', xbmc.LOGERROR)
        return None
