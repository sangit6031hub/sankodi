#!/bin/bash

# Update repository files script

VERSION=$1
if [ -z "$VERSION" ]; then
    echo "Usage: $0 <version>"
    exit 1
fi

# Update addons.xml with new version
sed -i '' "s/version=\"[^\"]*\"/version=\"$VERSION\"/" repository.sankodi/addons.xml

# Regenerate md5
cd repository.sankodi
md5 addons.xml > addons.xml.md5
cd ..

echo "Repository updated to version $VERSION"