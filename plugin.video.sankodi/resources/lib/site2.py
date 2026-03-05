import requests
from bs4 import BeautifulSoup

def list_categories(base_url):
    """
    Scrape categories from site2.
    """
    # Different scraping logic for site2
    response = requests.get(base_url + '/categories')
    soup = BeautifulSoup(response.content, 'html.parser')
    categories = []
    # Example parsing
    for link in soup.find_all('a', href=lambda href: href and 'category' in href):
        cat_id = link['href'].split('/')[-1]
        cat_name = link.text.strip()
        categories.append({'id': cat_id, 'name': cat_name})
    return categories

def list_videos(base_url, category_id):
    """
    Scrape videos from site2.
    """
    url = '{}/category/{}/videos'.format(base_url, category_id)
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    videos = []
    for item in soup.find_all('div', class_='video-item'):
        vid_id = item['data-id']
        title = item.find('h3').text
        thumb = item.find('img')['src']
        plot = item.find('p').text
        videos.append({'id': vid_id, 'title': title, 'thumb': thumb, 'plot': plot})
    return videos

def get_video_url(base_url, video_id):
    """
    Get video URL from site2.
    """
    url = '{}/play/{}'.format(base_url, video_id)
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    video_src = soup.find('source')['src']
    return video_src