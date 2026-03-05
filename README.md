# SanKodi Video Plugin

A Kodi plugin for browsing and playing videos from multiple websites. Each website is handled by a separate module, with URLs configurable via addon settings.

## Features

- Browse multiple video websites
- Modular design: each site in its own module
- Configurable site URLs via Kodi settings
- Stream videos directly
- Automatic update checking from GitHub

## Structure

- `plugin.video.sankodi/`: Main addon
  - `addon.xml`: Plugin metadata
  - `default.py`: Main entry point with auto-update
  - `resources/settings.xml`: Configuration for site URLs
  - `resources/lib/`: Website modules
- `repository.sankodi/`: Repository addon for updates
  - `addon.xml`: Repository metadata
  - `addons.xml`: List of available addons
  - `addons.xml.md5`: Checksum for validation
- `.github/workflows/`: GitHub Actions for automated builds
- `build.sh`: Manual build script
- `update_repo.sh`: Script to update repository files

## Automatic Publishing and Updates

### GitHub Actions Setup
The repository includes a GitHub Actions workflow that automatically builds and releases the addon when you push a version tag (e.g., `v1.0.1`).

### Repository Installation
1. Download `repository.sankodi.zip` from the latest release
2. Install it in Kodi: Add-ons → Install from zip file
3. The repository will provide updates for the video addon

### Auto-Update Feature
The addon checks for updates every time it's loaded:
- Queries GitHub API for the latest release
- Compares versions
- Prompts user to update if a newer version is available
- Downloads and installs the update automatically

## Adding a New Website

1. Create a new module in `resources/lib/` (e.g., `site3.py`)
2. Implement the required functions:
   - `list_categories(base_url)`: Return list of dicts with 'id' and 'name'
   - `list_videos(base_url, category_id)`: Return list of dicts with 'id', 'title', 'thumb', 'plot'
   - `get_video_url(base_url, video_id)`: Return the direct video URL
3. Add the site to `settings.xml` (e.g., `<setting id="site3_url" type="text" label="Site 3 URL" default="https://example3.com"/>`)
4. Update `default.py` imports and sites list

## Building the Plugin Zip

### Manual Method
1. Ensure all files are in the `plugin.video.sankodi/` directory
2. Add icon.png and fanart.jpg to `resources/` (create or download placeholders)
3. Zip the entire `plugin.video.sankodi` folder (not the parent directory)
4. Name the zip file as `plugin.video.sankodi-1.0.0.zip` (addonid-version.zip)

### Using the Build Script
Run the provided build script:
```bash
./build.sh
```

### Automated with GitHub Actions
Push a version tag to trigger automatic build and release:
```bash
git tag v1.0.1
git push origin v1.0.1
```

## Installing in Kodi

### Direct Installation
1. Open Kodi
2. Go to Add-ons > Install from zip file
3. Select the zip file you created

### Via Repository (Recommended for Updates)
1. Install the repository addon first
2. The repository will handle addon updates automatically

## Repository Management

When releasing new versions:
1. Update version in `plugin.video.sankodi/addon.xml`
2. Update `repository.sankodi/addons.xml` with new version info
3. Regenerate `addons.xml.md5`
4. Commit and tag the release

## Development Notes

- Uses requests and BeautifulSoup for scraping (ensure dependencies are available)
- Kodi uses Python 3 in modern versions
- Test scraping functions carefully to avoid breaking terms of service
- Handle errors gracefully in the plugin

## License

GPL-3.0