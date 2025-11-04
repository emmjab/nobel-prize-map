#!/usr/bin/env python3
"""
Re-geocode specific entries that failed
"""
import json
import sys
import os
import time
import requests

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from wiki_scraper import get_coords

def geocode_location(location_string):
    """Geocode a location using Nominatim API"""
    if not location_string or location_string.strip() == '':
        return None

    url = "https://nominatim.openstreetmap.org/search"
    params = {
        'q': location_string,
        'format': 'json',
        'limit': 1
    }
    headers = {
        'User-Agent': 'NobelPrizeMap/1.0 (Educational Project)'
    }

    try:
        time.sleep(1)  # Rate limiting
        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        results = response.json()

        if results:
            return (float(results[0]['lat']), float(results[0]['lon']))
        else:
            # Try wiki_scraper as fallback
            coords = get_coords(location_string)
            return coords if coords else None
    except Exception as e:
        print(f"  ⚠️  Geocoding error: {e}")
        # Try wiki_scraper as fallback
        try:
            coords = get_coords(location_string)
            return coords if coords else None
        except:
            return None

# Specific entries to rerun (using correct IDs from manual_overrides.json)
ENTRIES_TO_RERUN = [
    "peace_2009_845",           # Barack Obama
]

def main():
    print("=" * 80)
    print("Re-geocoding Failed Entries")
    print("=" * 80)

    # Load manual overrides
    with open('manual_overrides.json', 'r', encoding='utf-8') as f:
        overrides = json.load(f)

    # Load current data
    data_file = 'nobel_data_complete.json'

    print(f"\nLoading data from: {data_file}")
    with open(data_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Process each entry
    updated = 0
    failed = 0

    for laureate_id in ENTRIES_TO_RERUN:
        if laureate_id not in overrides:
            print(f"\n⚠️  {laureate_id} not found in manual_overrides.json - skipping")
            continue

        override = overrides[laureate_id]
        work_location = override.get('work_location')

        if not work_location:
            print(f"\n⚠️  {laureate_id} has no work_location - skipping")
            continue

        # Find the laureate in the data
        laureate = None
        for category, laureates in data.items():
            for l in laureates:
                if l['laureate_id'] == laureate_id:
                    laureate = l
                    break
            if laureate:
                break

        if not laureate:
            print(f"\n⚠️  {laureate_id} not found in data - skipping")
            continue

        print(f"\n{laureate['name']} ({laureate_id})")
        print(f"  Work location: {work_location}")
        print(f"  Geocoding...")

        coords = geocode_location(work_location)

        if coords:
            laureate['work_location'] = work_location  # Update the work_location text too
            laureate['work_lat'] = coords[0]
            laureate['work_lon'] = coords[1]
            laureate['data_source'] = 'manual'
            laureate['needs_enrichment'] = False
            print(f"  ✅ Updated location to: {work_location}")
            print(f"  ✅ Geocoded to: ({coords[0]}, {coords[1]})")
            updated += 1
        else:
            print(f"  ❌ Failed to geocode")
            failed += 1

    # Save updated data
    output_file = 'nobel_data_complete.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"\n{'=' * 80}")
    print(f"Summary:")
    print(f"  Updated: {updated}")
    print(f"  Failed: {failed}")
    print(f"  Saved to: {output_file}")
    print(f"{'=' * 80}")

if __name__ == '__main__':
    main()
