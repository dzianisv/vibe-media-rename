#!/usr/bin/env python3
"""
Command-line interface for vibe_media_rename.
"""

import argparse
import sys
from pathlib import Path
from typing import List

from .core import MediaRenamer


def main():
    """Main entry point for the vibe_media_rename command."""
    parser = argparse.ArgumentParser(
        prog="vibe_media_rename",
        description="Rename media files based on location metadata with smart heuristics",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  vibe_media_rename /path/to/photos/*.jpg
  vibe_media_rename --dry-run /Volumes/Dzianis-2/LifeHistory/2025/*
  vibe_media_rename photo1.jpg video1.mp4 photo2.heic

The tool will:
1. Extract GPS coordinates and creation dates from media files
2. For files without GPS data, use nearby files with similar timestamps
3. Convert coordinates to readable place names using geocoding
4. Rename files as: Place_City_State_Country_CreationTime_OriginalName.ext

Supported formats:
  Photos: JPG, PNG, HEIC, TIFF
  Videos: MP4, MOV, AVI, MKV, M4V, 3GP
        """
    )
    
    parser.add_argument(
        'files',
        nargs='+',
        help='Media files to process (supports wildcards)'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be renamed without actually renaming files'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='%(prog)s 1.0.1'
    )
    
    # Parse arguments
    try:
        args = parser.parse_args()
    except SystemExit:
        return
    
    # Convert string paths to Path objects and validate
    filepaths: List[Path] = []
    for file_arg in args.files:
        filepath = Path(file_arg)
        if filepath.exists():
            filepaths.append(filepath)
        else:
            print(f"Warning: File not found: {file_arg}")
    
    if not filepaths:
        print("Error: No valid files found to process.")
        sys.exit(1)
    
    # Show summary
    print(f"Vibe Media Rename v1.0.1")
    print(f"Mode: {'DRY RUN' if args.dry_run else 'RENAME FILES'}")
    print(f"Files found: {len(filepaths)}")
    
    if args.dry_run:
        print("\nNote: This is a dry run. No files will be actually renamed.")
    else:
        print("\nWarning: Files will be permanently renamed!")
        
    print("-" * 50)
    
    # Create renamer instance and process files
    try:
        renamer = MediaRenamer(dry_run=args.dry_run)
        renamer.process_files(filepaths)
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()