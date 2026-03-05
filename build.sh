#!/bin/bash

# Build script for SanKodi plugin

VERSION="1.0.0"
ADDON_ID="plugin.video.sankodi"
ZIP_NAME="${ADDON_ID}-${VERSION}.zip"

echo "Building $ZIP_NAME..."

# Check if directory exists
if [ ! -d "$ADDON_ID" ]; then
    echo "Error: $ADDON_ID directory not found"
    exit 1
fi

# Create zip
zip -r "$ZIP_NAME" "$ADDON_ID/"

echo "Build complete: $ZIP_NAME"