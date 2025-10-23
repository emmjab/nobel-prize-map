"""
Geocode all cities from the Nobel Prize data using Nominatim (OpenStreetMap)
"""

import json
import time
import requests
from collections import defaultdict

def geocode_location(location_string):
    """
    Geocode a full location string using Nominatim API
    Returns (lat, lon) tuple or None
    """
    if not location_string or location_string in ['', 'None']:
        return None

    # Clean up the location string
    location = location_string.strip()

    # Nominatim API - use full location string for better accuracy
    url = "https://nominatim.openstreetmap.org/search"
    params = {
        'q': location,
        'format': 'json',
        'limit': 1
    }
    headers = {
        'User-Agent': 'NobelPrizeMap/1.0'
    }

    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data:
                lat = float(data[0]['lat'])
                lon = float(data[0]['lon'])
                return (lat, lon)
    except Exception as e:
        print(f"Error geocoding '{location}': {e}")

    return None

def extract_all_locations(data):
    """Extract all unique full location strings from the dataset"""
    locations = set()

    for category, laureates in data.items():
        for laureate in laureates:
            birth_loc = laureate.get('birth_location', '')
            work_loc = laureate.get('work_location', '')

            # Use full location string for better geocoding accuracy
            if birth_loc and birth_loc.strip():
                locations.add(birth_loc.strip())

            if work_loc and work_loc.strip():
                locations.add(work_loc.strip())

    return locations

def geocode_all_missing_locations():
    """Geocode all locations that are missing from the dataset"""

    # Load the current data
    with open('nobel_data_complete.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    print("Extracting all unique locations from dataset...")
    all_locations = extract_all_locations(data)
    print(f"Found {len(all_locations)} unique locations")

    # Load existing coordinates from wiki_scraper
    from wiki_scraper import CITY_COORDS

    # Find locations that need geocoding (check if coordinates are 0,0)
    missing_locations = []
    for location in sorted(all_locations):
        # Extract city for checking against CITY_COORDS
        city = location.split(',')[0].strip().lower() if ',' in location else location.lower()

        # Check if this location needs geocoding
        needs_geocoding = True
        if city in CITY_COORDS:
            # Has coords in CITY_COORDS, check if it's actually used in dataset
            # We'll geocode it anyway if dataset shows (0,0) for this location
            for category, laureates in data.items():
                for laureate in laureates:
                    if (laureate.get('birth_location', '') == location and
                        laureate['birth_lat'] != 0 and laureate['birth_lon'] != 0):
                        needs_geocoding = False
                        break
                    if (laureate.get('work_location', '') == location and
                        laureate['work_lat'] != 0 and laureate['work_lon'] != 0):
                        needs_geocoding = False
                        break
                if not needs_geocoding:
                    break

        if needs_geocoding:
            # Check if any laureate has this location with (0,0) coordinates
            has_zero_coords = False
            for category, laureates in data.items():
                for laureate in laureates:
                    if (laureate.get('birth_location', '') == location and
                        laureate['birth_lat'] == 0 and laureate['birth_lon'] == 0):
                        has_zero_coords = True
                        break
                    if (laureate.get('work_location', '') == location and
                        laureate['work_lat'] == 0 and laureate['work_lon'] == 0):
                        has_zero_coords = True
                        break
                if has_zero_coords:
                    break

            if has_zero_coords:
                missing_locations.append(location)

    print(f"Need to geocode {len(missing_locations)} locations")

    if not missing_locations:
        print("All locations already have coordinates!")
        return {}

    # Geocode missing locations
    geocoded = {}
    total = len(missing_locations)

    for i, location in enumerate(missing_locations, 1):
        print(f"[{i}/{total}] Geocoding: {location}...", end=' ')

        coords = geocode_location(location)
        if coords:
            geocoded[location] = coords
            print(f"✓ {coords}")
        else:
            print("✗ Not found")

        # Be nice to the API - wait between requests
        if i < total:
            time.sleep(1.5)  # Nominatim requires 1 request per second max

    print(f"\nSuccessfully geocoded {len(geocoded)} locations")

    # Save to a file
    with open('geocoded_locations.json', 'w', encoding='utf-8') as f:
        json.dump(geocoded, f, indent=2)

    print(f"Geocoded locations saved to geocoded_locations.json")

    return geocoded

def update_dataset_with_coords(geocoded):
    """Update the Nobel dataset with newly geocoded coordinates"""

    # Load the current data
    with open('nobel_data_complete.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    updated_count = 0

    for category, laureates in data.items():
        for laureate in laureates:
            # Update birth coordinates using full location string
            birth_loc = laureate.get('birth_location', '')
            if birth_loc in geocoded:
                laureate['birth_lat'], laureate['birth_lon'] = geocoded[birth_loc]
                updated_count += 1

            # Update work coordinates using full location string
            work_loc = laureate.get('work_location', '')
            if work_loc in geocoded:
                laureate['work_lat'], laureate['work_lon'] = geocoded[work_loc]
                updated_count += 1

    # Save updated data
    with open('nobel_data_complete.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"Updated {updated_count} coordinate pairs in the dataset")

if __name__ == '__main__':
    print("=" * 60)
    print("Nobel Prize Location Geocoder (v2)")
    print("=" * 60)

    geocoded = geocode_all_missing_locations()

    if geocoded:
        print("\nUpdating dataset with new coordinates...")
        update_dataset_with_coords(geocoded)
        print("\n✓ Dataset updated successfully!")

    print("=" * 60)
