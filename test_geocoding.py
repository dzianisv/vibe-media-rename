#!/usr/bin/env python3

from geopy.geocoders import Nominatim

def test_coordinates():
    geocoder = Nominatim(user_agent="test_geocoding")
    
    # Test the failing coordinates (positive longitude - China)
    print("Testing 37.729000, 122.413500 (positive longitude):")
    try:
        location = geocoder.reverse("37.729000, 122.413500", timeout=10, language='en')
        if location:
            print(f"  Found: {location}")
            print(f"  Address: {location.raw.get('address', {})}")
        else:
            print("  No location found")
    except Exception as e:
        print(f"  Error: {e}")
    
    # Test with corrected coordinates (negative longitude - US)
    print("\nTesting 37.729000, -122.413500 (negative longitude):")
    try:
        location = geocoder.reverse("37.729000, -122.413500", timeout=10, language='en')
        if location:
            print(f"  Found: {location}")
            print(f"  Address: {location.raw.get('address', {})}")
        else:
            print("  No location found")
    except Exception as e:
        print(f"  Error: {e}")

if __name__ == "__main__":
    test_coordinates()