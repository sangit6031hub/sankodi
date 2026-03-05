import sys
import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon
import urllib.parse as urlparse
import requests
import json
from resources.lib import site1, site2  # Import website modules

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
        {'name': 'Site 1', 'module': site1, 'url_setting': 'site1_url'},
        {'name': 'Site 2', 'module': site2, 'url_setting': 'site2_url'},
        # Add more sites here
    ]
    for site in sites:
        url = get_url(action='list_categories', site=site['url_setting'])
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

def list_videos(site_setting, category):
    """
    List videos in a category.
    """
    site_url = addon.getSetting(site_setting)
    videos = []  # site_module.list_videos(site_url, category)
    for video in videos:
        url = get_url(action='play', site=site_setting, video=video['id'])
        li = xbmcgui.ListItem(video['title'])
        li.setArt({'thumb': video.get('thumb', 'DefaultVideo.png')})
        li.setInfo('video', {'title': video['title'], 'plot': video.get('plot', '')})
        li.setProperty('IsPlayable', 'true')
        xbmcplugin.addDirectoryItem(handle, url, li, False)
    xbmcplugin.endOfDirectory(handle)

def play_video(site_setting, video_id):
    """
    Play a video.
    """
    site_url = addon.getSetting(site_setting)
    video_url = ''  # site_module.get_video_url(site_url, video_id)
    play_item = xbmcgui.ListItem(path=video_url)
    xbmcplugin.setResolvedUrl(handle, True, listitem=play_item)

def router(paramstring):
    """
    Router function that calls other functions depending on the provided paramstring.
    """
    params = dict(urlparse.parse_qsl(paramstring))
    if params:
        if params['action'] == 'list_categories':
            list_categories(params['site'])
        elif params['action'] == 'list_videos':
            list_videos(params['site'], params['category'])
        elif params['action'] == 'play':
            play_video(params['site'], params['video'])
    else:
        check_for_updates()
        list_sites()

if __name__ == '__main__':
    router(sys.argv[2][1:])