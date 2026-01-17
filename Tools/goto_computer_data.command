#!/bin/bash
# Open the computer (Mac) VR Dots data folder in Finder
# Double-click this file to open the data folder

DATA_FOLDER="/Users/genestoner1/Library/Application Support/ThatsRandom/VRDotsDataFiles"

echo "=== VR Dots Computer Data Folder ==="
echo "$DATA_FOLDER"
echo ""

if [ -d "$DATA_FOLDER" ]; then
    echo "Opening folder in Finder..."
    open "$DATA_FOLDER"

    echo ""
    echo "Recent session files:"
    ls -lt "$DATA_FOLDER"/*.tsv 2>/dev/null | head -10
else
    echo "ERROR: Data folder not found!"
    echo "Creating folder..."
    mkdir -p "$DATA_FOLDER"
    open "$DATA_FOLDER"
fi

echo ""
read -p "Press Enter to close this window..."
