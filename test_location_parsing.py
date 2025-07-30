#!/usr/bin/env python3

import re
from typing import Optional, Tuple

def _parse_location_string(location_str: str) -> Optional[Tuple[float, float]]:
    """Parse various location string formats to extract coordinates."""
    try:
        # ISO 6709 format: +DDMM.MMMM+DDDMM.MMMM/ or +DD.DDDD-DDD.DDDD/
        iso_match = re.match(r'([+-]\d+\.?\d*)([+-]\d+\.?\d*)', location_str)
        if iso_match:
            lat = float(iso_match.group(1))
            lon = float(iso_match.group(2))
            print(f"ISO match: lat={lat}, lon={lon}")
            return (lat, lon)
        
        # Simple decimal format: "lat,lon"
        simple_match = re.match(r'(-?\d+\.?\d*),\s*(-?\d+\.?\d*)', location_str)
        if simple_match:
            lat = float(simple_match.group(1))
            lon = float(simple_match.group(2))
            print(f"Simple match: lat={lat}, lon={lon}")
            return (lat, lon)
            
    except (ValueError, AttributeError):
        pass
    
    return None

# Test with the actual metadata
test_location = "+37.7290-122.4135/"
print(f"Testing location string: {test_location}")
result = _parse_location_string(test_location)
print(f"Result: {result}")