import sys
import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon
import urllib.parse as urlparse
import requests
import json
from resources.lib import tamilgun, site2  # Import website modules

# Get the plugin handle
handle = int(sys.argv[1])

# Get addon instance
addon = xbmcaddon.Addon()
addon_id = addon.getAddonInfo('id')
current_version = addon.getAddonInfo('version')

def check_for_updates():
    """
    Check GitHub for latest version and notify if update available.
    """
    try:
        # GitHub API for latest release
        url = 'https://api.github.com/repos/san/sankodi/releases/latest'
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            latest_version = data['tag_name'].lstrip('v')
            if latest_version > current_version:
                # Notify user
                dialog = xbmcgui.Dialog()
                if dialog.yesno('Update Available', 
                               'A new version ({}) is available. Update now?'.format(latest_version)):
                    # Attempt to update
                    update_addon(data['zipball_url'])
                else:
                    xbmc.log('User declined update', xbmc.LOGINFO)
            else:
                xbmc.log('Addon is up to date', xbmc.LOGDEBUG)
        else:
            xbmc.log('Failed to check for updates: {}'.format(response.status_code), xbmc.LOGWARNING)
    except Exception as e:
        xbmc.log('Error checking for updates: {}'.format(str(e)), xbmc.LOGERROR)

def update_addon(zip_url):
    """
    Download and install the new addon version.
    """
    try:
        # Download zip
        response = requests.get(zip_url)
        zip_path = xbmc.translatePath('special://temp/{}.zip'.format(addon_id))
        with open(zip_path, 'wb') as f:
            f.write(response.content)
        
        # Install from zip
        xbmc.executebuiltin('InstallFromZip({})'.format(zip_path))
        xbmcgui.Dialog().ok('Update', 'Addon updated successfully. Please restart Kodi.')
    except Exception as e:
        xbmc.log('Error updating addon: {}'.format(str(e)), xbmc.LOGERROR)
        xbmcgui.Dialog().ok('Update Failed', 'Failed to update addon: {}'.format(str(e)))

def get_url(**kwargs):
    """
    Create a URL for calling the plugin recursively from the given set of keyword arguments.
    """
    return '{}?{}'.format(sys.argv[0], urlparse.urlencode(kwargs))

def list_sites():
    """
    List available websites.
    """
    sites = [
        {'name': 'TamilGun', 'module': tamilgun, 'url_setting': 'tamilgun_url'},
        {'name': 'Site 2', 'module': site2, 'url_setting': 'site2_url'},
        # Add more sites here
    ]
    for site in sites:
        url = get_url(action='list_videos', site=site['url_setting'], page='1')
        li = xbmcgui.ListItem(site['name'])
        li.setArt({'icon': 'DefaultFolder.png'})
        li.setInfo('video', {'title': site['name'], 'plot': 'Browse videos from {}'.format(site['name'])})
        xbmcplugin.addDirectoryItem(handle, url, li, True)
    xbmcplugin.endOfDirectory(handle)

def list_categories(site_setting):
    """
    List categories for a site.
    """
    site_url = addon.getSetting(site_setting)
    if not site_url:
        xbmcgui.Dialog().ok('Error', 'URL for {} not configured'.format(site_setting))
        return

    # Assuming each site module has a list_categories function
    # This is a placeholder; actual implementation depends on site
    categories = []  # site_module.list_categories(site_url)
    for cat in categories:
        url = get_url(action='list_videos', site=site_setting, category=cat['id'])
        li = xbmcgui.ListItem(cat['name'])
        li.setArt({'icon': 'DefaultFolder.png'})
        xbmcplugin.addDirectoryItem(handle, url, li, True)
    xbmcplugin.endOfDirectory(handle)

def list_videos(site_setting, category=None, page='1'):
    """
    List videos from a site with pagination support.
    """
    site_url = addon.getSetting(site_setting)
    if not site_url:
        xbmcgui.Dialog().ok('Error', 'URL for {} not configured'.format(site_setting))
        return

    try:
        # Get videos from the site module
        result = tamilgun.list_videos(site_url, int(page)) if site_setting == 'tamilgun_url' else []
        
        videos = result.get('videos', []) if isinstance(result, dict) else []
        total_pages = result.get('total_pages', 1) if isinstance(result, dict) else 1
        current_page = int(page)
        
        for video in videos:
            url = get_url(action='play', site=site_setting, video_url=video.get('url', ''))
            li = xbmcgui.ListItem(video['title'])
            li.setArt({'thumb': video.get('thumb', 'DefaultVideo.png')})
            li.setInfo('video', {'title': video['title'], 'plot': video.get('plot', '')})
            li.setProperty('IsPlayable', 'true')
            xbmcplugin.addDirectoryItem(handle, url, li, False)
        
        # Add "Next Page" button if there are more pages
        if current_page < total_pages:
            next_page = current_page + 1
            url = get_url(action='list_videos', site=site_setting, page=str(next_page))
            li = xbmcgui.ListItem('>> Next Page ({}/{})'.format(current_page, total_pages))
            li.setArt({'icon': 'DefaultFolder.png'})
            xbmcplugin.addDirectoryItem(handle, url, li, True)
        
        # Add "Previous Page" button if not on first page
        if current_page > 1:
            prev_page = current_page - 1
            url = get_url(action='list_videos', site=site_setting, page=str(prev_page))
            li = xbmcgui.ListItem('<< Previous Page ({}/{})'.format(current_page, total_pages))
            li.setArt({'icon': 'DefaultFolder.png'})
            xbmcplugin.addDirectoryItem(handle, url, li, True)
        
        xbmcplugin.endOfDirectory(handle)
    except Exception as e:
        xbmc.log('Error listing videos: {}'.format(str(e)), xbmc.LOGERROR)
        xbmcgui.Dialog().ok('Error', 'Failed to load videos: {}'.format(str(e)))

def play_video(site_setting, video_url):
    """
    Play a video.
    """
    try:
        # Get the direct video URL from the site module
        if site_setting == 'tamilgun_url':
            if video_url.startswith('http'):
                # video_url is the direct page URL
                stream_url = tamilgun.get_video_url(video_url)
            else:
                stream_url = video_url
        else:
            stream_url = video_url
        
        if not stream_url:
            xbmcgui.Dialog().ok('Error', 'Could not find video source')
            return
        
        play_item = xbmcgui.ListItem(path=stream_url)
        xbmcplugin.setResolvedUrl(handle, True, listitem=play_item)
    except Exception as e:
        xbmc.log('Error playing video: {}'.format(str(e)), xbmc.LOGERROR)
        xbmcgui.Dialog().ok('Error', 'Failed to play video: {}'.format(str(e)))

def router(paramstring):
    """
    Router function that calls other functions depending on the provided paramstring.
    """
    params = dict(urlparse.parse_qsl(paramstring))
    if params:
        if params['action'] == 'list_categories':
            list_categories(params['site'])
        elif params['action'] == 'list_videos':
            page = params.get('page', '1')
            list_videos(params['site'], page=page)
        elif params['action'] == 'play':
            play_video(params['site'], params.get('video_url', ''))
    else:
        check_for_updates()
        list_sites()

if __name__ == '__main__':
    router(sys.argv[2][1:])