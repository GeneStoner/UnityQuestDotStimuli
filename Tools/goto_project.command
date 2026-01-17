#!/bin/bash
# Open the VRDptsRebuild Unity project folder in Finder
# Double-click this file to open the project folder

PROJECT_FOLDER="/Users/genestoner1/UnityProjectsLocal/VRDptsRebuild"

echo "=== VR Dots Unity Project Folder ==="
echo "$PROJECT_FOLDER"
echo ""

if [ -d "$PROJECT_FOLDER" ]; then
    echo "Opening folder in Finder..."
    open "$PROJECT_FOLDER"

    echo ""
    echo "Key folders:"
    echo "  Assets/Scripts/  - C# scripts"
    echo "  Assets/Shaders/  - Shader files"
    echo "  Tools/Analysis/  - Python analysis scripts"
    echo "  quest_logs/      - Legacy Quest logs"
else
    echo "ERROR: Project folder not found!"
fi

echo ""
read -p "Press Enter to close this window..."
