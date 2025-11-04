"""
Fix historical city names by extracting modern names from parentheses
Example: "Breslau (now Wroclaw), Germany (now Poland)" -> "Wroclaw, Poland"
"""

import json
import time
import requests
import re

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

def extract_modern_name(location):
    """Extract modern city/country names from historical location strings"""

    # Pattern: "OldCity (now NewCity), OldCountry (now NewCountry)"
    # Extract: "NewCity, NewCountry"

    # Find all "now X" patterns
    now_patterns = re.findall(r'now ([^),]+)', location)

    if len(now_patterns) >= 2:
        # City and country
        return f"{now_patterns[0]}, {now_patterns[1]}"
    elif len(now_patterns) == 1:
        # Just city, keep original country
        parts = location.split(',')
        if len(parts) >= 2:
            country_part = parts[-1].strip()
            # Remove "(now X)" from country if present
            country_part = re.sub(r'\s*\(now [^)]+\)', '', country_part)
            return f"{now_patterns[0]}, {country_part}"

    return None

def fix_historical_locations():
    """Fix locations with historical names"""

    # Load the current data
    with open('nobel_data_complete.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Find all locations with (0,0) coordinates
    locations_to_fix = {}

    for category, laureates in data.items():
        for laureate in laureates:
            birth_loc = laureate.get('birth_location', '')
            work_loc = laureate.get('work_location', '')

            # Check birth location
            if birth_loc and laureate['birth_lat'] == 0 and laureate['birth_lon'] == 0:
                if birth_loc not in locations_to_fix:
                    modern_name = extract_modern_name(birth_loc)
                    if modern_name:
                        locations_to_fix[birth_loc] = {'modern': modern_name, 'coords': None}

            # Check work location
            if work_loc and laureate['work_lat'] == 0 and laureate['work_lon'] == 0:
                if work_loc not in locations_to_fix:
                    modern_name = extract_modern_name(work_loc)
                    if modern_name:
                        locations_to_fix[work_loc] = {'modern': modern_name, 'coords': None}

    print(f"Found {len(locations_to_fix)} historical locations to geocode")

    # Geocode the modern names
    count = 0
    for original, info in locations_to_fix.items():
        count += 1
        modern = info['modern']
        print(f"[{count}/{len(locations_to_fix)}] {original}")
        print(f"  -> {modern}...", end=' ')

        coords = geocode_location(modern)
        if coords:
            info['coords'] = coords
            print(f"✓ {coords}")
        else:
            print("✗ Not found")

        time.sleep(1.5)

    # Update the dataset
    updated_count = 0

    for category, laureates in data.items():
        for laureate in laureates:
            birth_loc = laureate.get('birth_location', '')
            work_loc = laureate.get('work_location', '')

            # Update birth coordinates
            if birth_loc in locations_to_fix and locations_to_fix[birth_loc]['coords']:
                coords = locations_to_fix[birth_loc]['coords']
                laureate['birth_lat'], laureate['birth_lon'] = coords
                updated_count += 1

            # Update work coordinates
            if work_loc in locations_to_fix and locations_to_fix[work_loc]['coords']:
                coords = locations_to_fix[work_loc]['coords']
                laureate['work_lat'], laureate['work_lon'] = coords
                updated_count += 1

    # Save updated data
    with open('nobel_data_complete.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"\nUpdated {updated_count} coordinate pairs")

    # Show remaining zeros
    zero_count = 0
    for category, laureates in data.items():
        for laureate in laureates:
            if (laureate['birth_lat'] == 0 and laureate['birth_lon'] == 0) or \
               (laureate['work_lat'] == 0 and laureate['work_lon'] == 0):
                zero_count += 1

    print(f"Remaining entries with (0,0) coordinates: {zero_count}")

if __name__ == '__main__':
    print("=" * 60)
    print("Fix Historical Location Names")
    print("=" * 60)
    fix_historical_locations()
    print("=" * 60)
