"""
Core functionality for media file metadata extraction and renaming.
"""

import json
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, NamedTuple

try:
    from PIL import Image
    from PIL.ExifTags import TAGS, GPSTAGS
except ImportError:
    print("Error: PIL (Pillow) not installed. Run: pip install Pillow")
    sys.exit(1)

try:
    from geopy.geocoders import Nominatim
    from geopy.exc import GeocoderTimedOut, GeocoderServiceError
except ImportError:
    print("Error: geopy not installed. Run: pip install geopy")
    sys.exit(1)

try:
    import exifread
except ImportError:
    print("Error: exifread not installed. Run: pip install exifread")
    sys.exit(1)


class FileMetadata(NamedTuple):
    """Metadata container for media files."""
    filepath: Path
    modification_time: datetime
    creation_date: Optional[datetime]
    latitude: Optional[float]
    longitude: Optional[float]
    location_name: Optional[str] = None


class MediaRenamer:
    """
    Main class for extracting metadata and renaming media files.
    
    Features:
    - Extracts GPS coordinates and creation dates from photos and videos
    - Applies heuristics for files without location data
    - Converts coordinates to place names using geocoding
    - Safely renames files with location and timestamp information
    """
    
    def __init__(self, dry_run: bool = False):
        """
        Initialize the MediaRenamer.
        
        Args:
            dry_run: If True, only show what would be renamed without actual changes
        """
        self.dry_run = dry_run
        self.geocoder = Nominatim(user_agent="vibe_media_rename_tool")
        
    def extract_photo_metadata(self, filepath: Path) -> FileMetadata:
        """Extract metadata from photo files using PIL and exifread."""
        mod_time = datetime.fromtimestamp(filepath.stat().st_mtime)
        creation_date = None
        latitude = None
        longitude = None
        
        try:
            # Try PIL first for basic EXIF
            with Image.open(filepath) as img:
                exif_data = img._getexif()
                
                if exif_data:
                    # Extract creation date
                    for tag_id, value in exif_data.items():
                        tag = TAGS.get(tag_id, tag_id)
                        if tag == "DateTime":
                            try:
                                creation_date = datetime.strptime(value, "%Y:%m:%d %H:%M:%S")
                            except ValueError:
                                pass
                        elif tag == "DateTimeOriginal":
                            try:
                                creation_date = datetime.strptime(value, "%Y:%m:%d %H:%M:%S")
                            except ValueError:
                                pass
                        elif tag == "GPSInfo":
                            gps_data = {}
                            for gps_tag_id, gps_value in value.items():
                                gps_tag = GPSTAGS.get(gps_tag_id, gps_tag_id)
                                gps_data[gps_tag] = gps_value
                            
                            # Extract GPS coordinates
                            if 'GPSLatitude' in gps_data and 'GPSLongitude' in gps_data:
                                latitude = self._convert_gps_to_decimal(
                                    gps_data['GPSLatitude'], 
                                    gps_data.get('GPSLatitudeRef', 'N')
                                )
                                longitude = self._convert_gps_to_decimal(
                                    gps_data['GPSLongitude'], 
                                    gps_data.get('GPSLongitudeRef', 'E')
                                )
            
            # Fallback to exifread for more detailed extraction
            if not creation_date or (latitude is None or longitude is None):
                with open(filepath, 'rb') as f:
                    tags = exifread.process_file(f)
                    
                    # Try different date tags
                    for date_tag in ['EXIF DateTimeOriginal', 'EXIF DateTime', 'Image DateTime']:
                        if date_tag in tags and not creation_date:
                            try:
                                creation_date = datetime.strptime(str(tags[date_tag]), "%Y:%m:%d %H:%M:%S")
                                break
                            except ValueError:
                                pass
                    
                    # GPS extraction with exifread
                    if latitude is None or longitude is None:
                        if 'GPS GPSLatitude' in tags and 'GPS GPSLongitude' in tags:
                            lat_ref = str(tags.get('GPS GPSLatitudeRef', 'N'))
                            lon_ref = str(tags.get('GPS GPSLongitudeRef', 'E'))
                            
                            latitude = self._convert_exifread_gps_to_decimal(
                                tags['GPS GPSLatitude'], lat_ref
                            )
                            longitude = self._convert_exifread_gps_to_decimal(
                                tags['GPS GPSLongitude'], lon_ref
                            )
                            
        except Exception as e:
            print(f"Warning: Could not extract metadata from {filepath}: {e}")
        
        return FileMetadata(
            filepath=filepath,
            modification_time=mod_time,
            creation_date=creation_date,
            latitude=latitude,
            longitude=longitude
        )
    
    def extract_video_metadata(self, filepath: Path) -> FileMetadata:
        """Extract metadata from video files using ffprobe."""
        mod_time = datetime.fromtimestamp(filepath.stat().st_mtime)
        creation_date = None
        latitude = None
        longitude = None
        
        try:
            # Use ffprobe to extract metadata
            cmd = [
                'ffprobe', '-v', 'quiet', '-print_format', 'json',
                '-show_format', '-show_streams', str(filepath)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                metadata = json.loads(result.stdout)
                
                # Check format tags first
                format_tags = metadata.get('format', {}).get('tags', {})
                
                # Try different creation date fields
                for date_field in ['creation_time', 'date', 'DATE']:
                    if date_field in format_tags:
                        try:
                            # Handle different date formats
                            date_str = format_tags[date_field]
                            if 'T' in date_str:
                                # ISO format
                                date_str = date_str.split('T')[0] + ' ' + date_str.split('T')[1].split('.')[0]
                                creation_date = datetime.fromisoformat(date_str.replace('Z', ''))
                            else:
                                creation_date = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
                            break
                        except (ValueError, TypeError):
                            pass
                
                # Look for GPS coordinates in various tag formats
                location_keys = ['location', 'com.apple.quicktime.location.ISO6709']
                for key in location_keys:
                    if key in format_tags:
                        location_str = format_tags[key]
                        coords = self._parse_location_string(location_str)
                        if coords:
                            latitude, longitude = coords
                            break
                
                # Also check stream metadata
                for stream in metadata.get('streams', []):
                    stream_tags = stream.get('tags', {})
                    for key in location_keys:
                        if key in stream_tags and not latitude:
                            location_str = stream_tags[key]
                            coords = self._parse_location_string(location_str)
                            if coords:
                                latitude, longitude = coords
                                break
                                
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, json.JSONDecodeError) as e:
            print(f"Warning: Could not extract video metadata from {filepath}: {e}")
        except FileNotFoundError:
            print("Warning: ffprobe not found. Video metadata extraction will be limited.")
        
        return FileMetadata(
            filepath=filepath,
            modification_time=mod_time,
            creation_date=creation_date,
            latitude=latitude,
            longitude=longitude
        )
    
    def _convert_gps_to_decimal(self, coords, ref):
        """Convert GPS coordinates from degrees/minutes/seconds to decimal."""
        try:
            if isinstance(coords, (list, tuple)) and len(coords) >= 3:
                degrees = float(coords[0])
                minutes = float(coords[1])
                seconds = float(coords[2])
                
                decimal = degrees + minutes/60.0 + seconds/3600.0
                
                if ref in ['S', 'W']:
                    decimal = -decimal
                    
                return decimal
        except (ValueError, TypeError, IndexError):
            pass
        return None
    
    def _convert_exifread_gps_to_decimal(self, coords, ref):
        """Convert exifread GPS coordinates to decimal."""
        try:
            # exifread returns IfdTag objects
            coord_parts = str(coords).replace('[', '').replace(']', '').split(', ')
            
            # Parse degrees, minutes, seconds
            degrees = float(coord_parts[0])
            minutes = float(coord_parts[1]) if len(coord_parts) > 1 else 0
            
            # Seconds might be a fraction
            seconds = 0
            if len(coord_parts) > 2:
                sec_str = coord_parts[2]
                if '/' in sec_str:
                    num, den = sec_str.split('/')
                    seconds = float(num) / float(den)
                else:
                    seconds = float(sec_str)
            
            decimal = degrees + minutes/60.0 + seconds/3600.0
            
            if ref in ['S', 'W']:
                decimal = -decimal
                
            return decimal
        except (ValueError, TypeError, IndexError):
            pass
        return None
    
    def _parse_location_string(self, location_str: str) -> Optional[Tuple[float, float]]:
        """Parse various location string formats to extract coordinates."""
        try:
            # ISO 6709 format: +DDMM.MMMM+DDDMM.MMMM/
            iso_match = re.match(r'([+-]\d+\.?\d*)[+-](\d+\.?\d*)', location_str)
            if iso_match:
                lat = float(iso_match.group(1))
                lon = float(iso_match.group(2))
                return (lat, lon)
            
            # Simple decimal format: "lat,lon"
            simple_match = re.match(r'(-?\d+\.?\d*),\s*(-?\d+\.?\d*)', location_str)
            if simple_match:
                lat = float(simple_match.group(1))
                lon = float(simple_match.group(2))
                return (lat, lon)
                
        except (ValueError, AttributeError):
            pass
        
        return None
    
    def get_location_name(self, latitude: float, longitude: float) -> Optional[str]:
        """Convert coordinates to place name using geocoding."""
        try:
            location = self.geocoder.reverse(f"{latitude}, {longitude}", timeout=10)
            if location and location.raw:
                address = location.raw.get('address', {})
                
                # Extract place components
                place = (address.get('village') or 
                        address.get('hamlet') or 
                        address.get('suburb') or
                        address.get('neighbourhood') or
                        address.get('city_district') or
                        "Unknown")
                
                city = (address.get('city') or 
                       address.get('town') or 
                       address.get('municipality') or
                       "Unknown")
                
                state = (address.get('state') or 
                        address.get('province') or 
                        address.get('region') or
                        "Unknown")
                
                country = address.get('country', "Unknown")
                
                return f"{place}_{city}_{state}_{country}"
                
        except (GeocoderTimedOut, GeocoderServiceError) as e:
            print(f"Warning: Geocoding failed: {e}")
        except Exception as e:
            print(f"Warning: Unexpected geocoding error: {e}")
        
        return None
    
    def apply_location_heuristic(self, files_metadata: List[FileMetadata]) -> List[FileMetadata]:
        """Apply heuristic to assign locations to files without GPS data."""
        # Sort by modification time
        sorted_files = sorted(files_metadata, key=lambda x: x.modification_time)
        
        # Files with location data
        located_files = [f for f in sorted_files if f.latitude is not None and f.longitude is not None]
        
        # Files without location data
        unlocated_files = [f for f in sorted_files if f.latitude is None or f.longitude is None]
        
        result = list(files_metadata)
        
        for unlocated in unlocated_files:
            closest_located = None
            min_time_diff = None
            
            for located in located_files:
                time_diff = abs((unlocated.modification_time - located.modification_time).total_seconds())
                
                if min_time_diff is None or time_diff < min_time_diff:
                    min_time_diff = time_diff
                    closest_located = located
            
            if closest_located and min_time_diff <= 3600:  # Within 1 hour
                # Update the metadata with borrowed coordinates
                idx = result.index(unlocated)
                result[idx] = unlocated._replace(
                    latitude=closest_located.latitude,
                    longitude=closest_located.longitude
                )
                print(f"Applied location heuristic: {unlocated.filepath.name} -> "
                      f"borrowed coordinates from {closest_located.filepath.name}")
        
        return result
    
    def generate_new_filename(self, metadata: FileMetadata) -> str:
        """Generate new filename based on metadata."""
        original_name = metadata.filepath.stem
        extension = metadata.filepath.suffix
        
        # Use creation date if available, otherwise modification time
        date_to_use = metadata.creation_date or metadata.modification_time
        creation_time = date_to_use.strftime("%Y%m%d_%H%M%S")
        
        # Get location name
        if metadata.location_name:
            location_parts = metadata.location_name.split('_')
            # Clean up location parts
            location_parts = [self._clean_filename_part(part) for part in location_parts]
            location_str = '_'.join(location_parts)
        else:
            location_str = "Unknown_Unknown_Unknown_Unknown"
        
        # Clean original name
        clean_original = self._clean_filename_part(original_name)
        
        new_filename = f"{location_str}_{creation_time}_{clean_original}{extension}"
        
        # Ensure filename isn't too long (max 255 chars)
        if len(new_filename) > 255:
            # Truncate original name if needed
            max_original_len = 255 - len(f"{location_str}_{creation_time}_{extension}")
            if max_original_len > 0:
                clean_original = clean_original[:max_original_len]
                new_filename = f"{location_str}_{creation_time}_{clean_original}{extension}"
        
        return new_filename
    
    def _clean_filename_part(self, part: str) -> str:
        """Clean a part of filename to be filesystem-safe."""
        # Replace problematic characters
        cleaned = re.sub(r'[<>:"/\\|?*]', '_', part)
        # Remove multiple underscores
        cleaned = re.sub(r'_+', '_', cleaned)
        # Remove leading/trailing underscores and spaces
        cleaned = cleaned.strip('_').strip()
        return cleaned if cleaned else "Unknown"
    
    def process_files(self, filepaths: List[Path]) -> None:
        """Process all files and rename them."""
        print(f"Processing {len(filepaths)} files...")
        
        # Extract metadata from all files
        files_metadata = []
        
        for filepath in filepaths:
            if not filepath.exists():
                print(f"Warning: File not found: {filepath}")
                continue
                
            print(f"Extracting metadata from: {filepath.name}")
            
            # Determine file type and extract appropriate metadata
            if filepath.suffix.lower() in ['.jpg', '.jpeg', '.png', '.tiff', '.tif', '.heic']:
                metadata = self.extract_photo_metadata(filepath)
            elif filepath.suffix.lower() in ['.mp4', '.mov', '.avi', '.mkv', '.m4v', '.3gp']:
                metadata = self.extract_video_metadata(filepath)
            else:
                print(f"Warning: Unsupported file type: {filepath}")
                continue
                
            files_metadata.append(metadata)
        
        if not files_metadata:
            print("No valid files to process.")
            return
        
        # Apply location heuristic
        print("\nApplying location heuristic for files without GPS data...")
        files_metadata = self.apply_location_heuristic(files_metadata)
        
        # Get location names for files with coordinates
        print("\nResolving coordinates to location names...")
        for i, metadata in enumerate(files_metadata):
            if metadata.latitude is not None and metadata.longitude is not None:
                location_name = self.get_location_name(metadata.latitude, metadata.longitude)
                files_metadata[i] = metadata._replace(location_name=location_name)
        
        # Generate new filenames and rename
        print(f"\n{'DRY RUN: ' if self.dry_run else ''}Renaming files...")
        
        for metadata in files_metadata:
            try:
                new_filename = self.generate_new_filename(metadata)
                new_filepath = metadata.filepath.parent / new_filename
                
                if new_filepath == metadata.filepath:
                    print(f"Skipping {metadata.filepath.name} (no change needed)")
                    continue
                
                if new_filepath.exists():
                    print(f"Warning: Target file already exists: {new_filename}")
                    # Add suffix to make unique
                    counter = 1
                    base_name = new_filepath.stem
                    extension = new_filepath.suffix
                    while new_filepath.exists():
                        new_filename = f"{base_name}_{counter:03d}{extension}"
                        new_filepath = metadata.filepath.parent / new_filename
                        counter += 1
                
                print(f"{'WOULD RENAME' if self.dry_run else 'RENAMING'}: "
                      f"{metadata.filepath.name} -> {new_filename}")
                
                if not self.dry_run:
                    metadata.filepath.rename(new_filepath)
                    
            except Exception as e:
                print(f"Error processing {metadata.filepath.name}: {e}")
        
        print(f"\n{'Dry run' if self.dry_run else 'Processing'} completed!")