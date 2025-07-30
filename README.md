# Vibe Media Rename

A smart Python tool that renames photos and videos based on their location metadata. For files without location data, it uses intelligent heuristics to assign locations based on nearby files with similar timestamps.

## ✨ Features

- **📍 GPS Extraction**: Extracts GPS coordinates and creation dates from photos (EXIF) and videos (FFprobe)
- **🧠 Smart Heuristics**: Assigns locations to files without GPS data using nearby files with similar timestamps
- **🌍 Geocoding**: Converts GPS coordinates to readable place names using OpenStreetMap
- **🔒 Safe Renaming**: Includes dry-run mode to preview changes before applying them
- **📱 Multiple Formats**: Supports common photo formats (JPG, PNG, HEIC, TIFF) and video formats (MP4, MOV, AVI, MKV)

## 🚀 Installation

### From GitHub (Recommended)

```bash
pip install git+https://github.com/vibe-tools/vibe-media-rename.git
```

### From Source

```bash
git clone https://github.com/vibe-tools/vibe-media-rename.git
cd vibe-media-rename
pip install .
```

### Development Install

```bash
git clone https://github.com/vibe-tools/vibe-media-rename.git
cd vibe-media-rename
pip install -e .
```

## 📋 Requirements

- Python 3.7+
- PIL (Pillow) - for photo metadata
- exifread - for detailed EXIF data
- geopy - for geocoding coordinates to place names
- ffprobe (part of ffmpeg) - for video metadata (optional but recommended)

### Install FFmpeg (for video support)

```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt install ffmpeg

# CentOS/RHEL
sudo yum install ffmpeg
```

## 🎯 Usage

### Command Line

```bash
# Dry run to see what would happen (recommended first step)
vibe_media_rename --dry-run /path/to/your/files/*

# Actually rename the files
vibe_media_rename /path/to/your/files/*

# Process specific file types
vibe_media_rename --dry-run /path/to/photos/*.jpg
vibe_media_rename /path/to/videos/*.mp4

# Process mixed media files
vibe_media_rename photo1.jpg video1.mp4 photo2.heic
```

### Python API

```python
from vibe_media_rename import MediaRenamer
from pathlib import Path

# Create renamer instance
renamer = MediaRenamer(dry_run=True)  # Set to False for actual renaming

# Process files
files = [Path("photo1.jpg"), Path("video1.mp4")]
renamer.process_files(files)
```

## 📝 Output Format

Files are renamed using this pattern:
```
${Place}_${City}_${State}_${Country}_${CreationTime}_${OriginalName}.${Extension}
```

### Example Renames

- `IMG_1234.jpg` → `CentralPark_NewYork_NewYork_UnitedStates_20250115_143022_IMG_1234.jpg`
- `VID_5678.mp4` → `GoldenGateBridge_SanFrancisco_California_UnitedStates_20250116_091500_VID_5678.mp4`

## 🔧 How It Works

1. **Metadata Extraction**: 
   - Photos: Uses PIL and exifread to extract EXIF data including GPS coordinates and creation dates
   - Videos: Uses ffprobe to extract metadata from video containers

2. **Location Heuristic**: 
   - Files without GPS data are matched with the closest file (by timestamp) that has location data
   - Only applies if the time difference is within 1 hour

3. **Geocoding**: 
   - GPS coordinates are converted to place names using OpenStreetMap's Nominatim service
   - Extracts Place, City, State, and Country information

4. **Safe Renaming**: 
   - Cleans filename parts to be filesystem-safe
   - Handles name collisions by adding numeric suffixes
   - Limits filename length to filesystem constraints

## 📚 Supported File Types

### Photos
- JPEG (.jpg, .jpeg)
- PNG (.png)
- TIFF (.tiff, .tif)
- HEIC (.heic) - iPhone photos

### Videos
- MP4 (.mp4)
- QuickTime (.mov)
- AVI (.avi)
- Matroska (.mkv)
- M4V (.m4v)
- 3GP (.3gp)

## 🛠️ Command Line Options

```
positional arguments:
  files          Media files to process (supports wildcards)

optional arguments:
  -h, --help     show this help message and exit
  --dry-run      Show what would be renamed without actually renaming files
  --version      show program's version number and exit
```

## 🔍 Troubleshooting

### Common Issues

1. **"ffprobe not found"**: Install ffmpeg for video support
2. **"No GPS data found"**: This is normal for many files - the heuristic will try to assign locations
3. **Geocoding timeouts**: The tool will retry and continue processing other files
4. **Long filenames**: The tool automatically truncates names that are too long

### Rate Limiting

The geocoding service has rate limits. If you're processing many files, the tool may slow down to respect these limits.

## 🔒 Privacy Note

This tool uses OpenStreetMap's Nominatim service for geocoding, which means GPS coordinates are sent to their servers to get place names. No other data is transmitted, and the service doesn't store queries.

## 📄 License

MIT License - see LICENSE file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 🐛 Issues

Report issues on the [GitHub Issues page](https://github.com/vibe-tools/vibe-media-rename/issues).

## 📈 Changelog

### v1.0.0
- Initial release
- Photo and video metadata extraction
- Smart location heuristics
- Geocoding integration
- Safe file renaming with dry-run support