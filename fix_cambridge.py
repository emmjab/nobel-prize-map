"""
Fix specific geocoding errors like Cambridge, MA showing UK coordinates
"""

import json
import time
import requests

def geocode_location(location_string):
    """Geocode a location using Nominatim API"""
    url = "https://nominatim.openstreetmap.org/search"
    params = {
        'q': location_string,
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
                return (float(data[0]['lat']), float(data[0]['lon']))
    except Exception as e:
        print(f"Error geocoding '{location_string}': {e}")

    return None

def fix_incorrect_coordinates():
    """Fix locations that have incorrect coordinates"""

    # Load the current data
    with open('nobel_data_complete.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    # List of locations we know are wrong and need fixing
    fixes_needed = {
        'Cambridge, MA, USA': None,
        'Cambridge, England': None,
        'Cambridge, United Kingdom': None,
    }

    print("Geocoding corrected locations...")
    for location in fixes_needed.keys():
        print(f"  Geocoding: {location}...", end=' ')
        coords = geocode_location(location)
        if coords:
            fixes_needed[location] = coords
            print(f"✓ {coords}")
        else:
            print("✗ Not found")
        time.sleep(1.5)

    # Now find all entries that need updating
    updated_count = 0

    for category, laureates in data.items():
        for laureate in laureates:
            birth_loc = laureate.get('birth_location', '')
            work_loc = laureate.get('work_location', '')

            # Fix birth coordinates
            if birth_loc in fixes_needed and fixes_needed[birth_loc]:
                old_coords = (laureate['birth_lat'], laureate['birth_lon'])
                new_coords = fixes_needed[birth_loc]
                laureate['birth_lat'], laureate['birth_lon'] = new_coords
                print(f"  Fixed {laureate['name']} birth: {old_coords} -> {new_coords}")
                updated_count += 1

            # Fix work coordinates
            if work_loc in fixes_needed and fixes_needed[work_loc]:
                old_coords = (laureate['work_lat'], laureate['work_lon'])
                new_coords = fixes_needed[work_loc]
                laureate['work_lat'], laureate['work_lon'] = new_coords
                print(f"  Fixed {laureate['name']} work: {old_coords} -> {new_coords}")
                updated_count += 1

    # Save updated data
    with open('nobel_data_complete.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"\nUpdated {updated_count} coordinate pairs")

if __name__ == '__main__':
    print("=" * 60)
    print("Fix Incorrect Geocoding")
    print("=" * 60)
    fix_incorrect_coordinates()
    print("=" * 60)
