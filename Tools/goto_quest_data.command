#!/bin/bash
# Navigate to Quest data folder via ADB
# Double-click this file to open Terminal and connect to Quest

echo "=== Quest VR Dots Data Folder ==="
echo ""

# Check if device is connected
if ! adb devices | grep -q "device$"; then
    echo "ERROR: No Quest device connected!"
    echo "Please connect your Quest via USB and enable developer mode."
    echo ""
    read -p "Press Enter to exit..."
    exit 1
fi

DEVICE=$(adb devices | grep "device$" | cut -f1)
echo "Connected to: $DEVICE"
echo ""

# App data path
APP_PATH="/sdcard/Android/data/com.genestoner.vrdptsrebuildX.test/files"

echo "Listing Quest app data folder:"
echo "$APP_PATH"
echo ""
adb shell "ls -la $APP_PATH 2>/dev/null || echo 'Folder empty or not found'"

echo ""
echo "=== Searching for session files on Quest ==="
adb shell "find /sdcard -name '*.tsv' -o -name '*session*.csv' 2>/dev/null"

echo ""
echo "To pull files, use: adb pull <remote_path> <local_path>"
echo ""
read -p "Press Enter to exit..."
