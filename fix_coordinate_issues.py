"""
Fix coordinate issues where:
1. Work coordinates incorrectly match birth coordinates
2. US locations geocoded to wrong countries
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

def fix_coordinate_issues():
    """Fix work coordinates that match birth or are in wrong countries"""

    # Load the current data
    with open('nobel_data_complete.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Track issues
    coord_match_issues = []
    us_location_issues = []

    # Find all issues
    for category, laureates in data.items():
        for laureate in laureates:
            work_loc = laureate['work_location']
            birth_loc = laureate['birth_location']
            work_lat, work_lon = laureate['work_lat'], laureate['work_lon']
            birth_lat, birth_lon = laureate['birth_lat'], laureate['birth_lon']

            # Issue 1: Work coordinates match birth but locations are different
            if (work_lat == birth_lat and work_lon == birth_lon and
                work_loc != birth_loc):
                coord_match_issues.append({
                    'name': laureate['name'],
                    'category': category,
                    'year': laureate['prize_year'],
                    'work_location': work_loc,
                    'birth_location': birth_loc,
                    'laureate': laureate
                })

            # Issue 2: US location with non-US coordinates
            elif ', usa' in work_loc.lower():
                if not (25 <= work_lat <= 50 and -125 <= work_lon <= -65):
                    us_location_issues.append({
                        'name': laureate['name'],
                        'category': category,
                        'year': laureate['prize_year'],
                        'work_location': work_loc,
                        'current_coords': (work_lat, work_lon),
                        'laureate': laureate
                    })

    print(f"\nFound {len(coord_match_issues)} entries with matching coordinates")
    print(f"Found {len(us_location_issues)} US locations with wrong coordinates")
    print(f"Total issues to fix: {len(coord_match_issues) + len(us_location_issues)}\n")

    # Combine all issues
    all_issues = coord_match_issues + us_location_issues

    # Fix each issue
    fixed_count = 0
    failed_count = 0

    for i, issue in enumerate(all_issues, 1):
        laureate = issue['laureate']
        work_location = issue['work_location']

        print(f"[{i}/{len(all_issues)}] {issue['name']} ({issue['year']}, {issue['category']})")
        print(f"  Work location: {work_location}")
        print(f"  Current coords: ({laureate['work_lat']}, {laureate['work_lon']})")
        print(f"  Geocoding...", end=' ')

        # Geocode the work location
        new_coords = geocode_location(work_location)

        if new_coords:
            laureate['work_lat'], laureate['work_lon'] = new_coords
            print(f"✓ Updated to {new_coords}")
            fixed_count += 1
        else:
            print("✗ Failed to geocode")
            failed_count += 1

        # Be nice to the API
        time.sleep(1.5)

    # Save updated data
    print(f"\nSaving changes to nobel_data_complete.json...")
    with open('nobel_data_complete.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print("\n" + "=" * 60)
    print(f"Fixed: {fixed_count}")
    print(f"Failed: {failed_count}")
    print(f"Total processed: {fixed_count + failed_count}")
    print("=" * 60)

if __name__ == '__main__':
    print("=" * 60)
    print("Fix Coordinate Issues")
    print("=" * 60)

    response = input("\nThis will update nobel_data_complete.json. Continue? (y/n): ")
    if response.lower() == 'y':
        fix_coordinate_issues()
    else:
        print("Cancelled.")
