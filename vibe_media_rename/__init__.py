"""
Vibe Media Rename - A tool to rename media files based on location metadata.

This package provides functionality to:
- Extract GPS coordinates and creation dates from photos and videos
- Apply smart heuristics for files without location data
- Convert coordinates to readable place names
- Rename files with location and timestamp information
"""

__version__ = "1.0.1"
__author__ = "Vibe Tools"
__email__ = "tools@vibe.dev"

from .core import MediaRenamer, FileMetadata

__all__ = ["MediaRenamer", "FileMetadata"]