#!/bin/bash

# Media Renamer Tool Installation Script

echo "Installing Media Renamer Tool dependencies..."

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is required but not installed."
    echo "Please install Python 3 first."
    exit 1
fi

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "Error: pip3 is required but not installed."
    echo "Please install pip3 first."
    exit 1
fi

# Install Python dependencies
echo "Installing Python dependencies..."
pip3 install -r requirements.txt

# Check if ffprobe is available (for video metadata)
if ! command -v ffprobe &> /dev/null; then
    echo ""
    echo "Warning: ffprobe not found."
    echo "Video metadata extraction will be limited without ffprobe."
    echo ""
    echo "To install ffprobe:"
    echo "  macOS: brew install ffmpeg"
    echo "  Ubuntu/Debian: sudo apt install ffmpeg"
    echo "  CentOS/RHEL: sudo yum install ffmpeg"
    echo ""
fi

# Make the script executable
chmod +x media_renamer.py

echo "Installation completed!"
echo ""
echo "Usage:"
echo "  python3 media_renamer.py --dry-run /path/to/your/files/*"
echo "  python3 media_renamer.py /path/to/your/files/*.jpg"
echo ""
echo "For your specific case:"
echo "  python3 media_renamer.py --dry-run /Volumes/Dzianis-2/LifeHistory/2025/*"