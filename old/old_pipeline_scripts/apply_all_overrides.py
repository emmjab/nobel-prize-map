#!/usr/bin/env python3
"""
Apply ALL manual overrides from manual_overrides.json to nobel_data_complete.json
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

def main():
    print("=" * 80)
    print("Applying ALL Manual Overrides to nobel_data_complete.json")
    print("=" * 80)

    # Load manual overrides
    with open('manual_overrides.json', 'r', encoding='utf-8') as f:
        overrides = json.load(f)

    # Count actual overrides (skip metadata)
    override_count = sum(1 for k in overrides.keys() if not k.startswith('_'))
    print(f"\nFound {override_count} manual overrides to apply")

    # Load current data
    data_file = 'nobel_data_complete.json'
    print(f"Loading data from: {data_file}")
    with open(data_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Process each override
    updated = 0
    failed = 0
    skipped = 0

    for laureate_id, override in overrides.items():
        # Skip metadata entries
        if laureate_id.startswith('_'):
            continue

        work_location = override.get('work_location')
        if not work_location:
            print(f"\n⚠️  {laureate_id} has no work_location - skipping")
            skipped += 1
            continue

        # Find the laureate in the data
        laureate = None
        for category, laureates in data.items():
            for l in laureates:
                if l.get('laureate_id') == laureate_id:
                    laureate = l
                    break
            if laureate:
                break

        if not laureate:
            print(f"\n⚠️  {laureate_id} not found in data - skipping")
            skipped += 1
            continue

        print(f"\n{laureate['name']} ({laureate_id})")
        print(f"  Work location: {work_location}")
        print(f"  Geocoding...")

        coords = geocode_location(work_location)

        if coords:
            laureate['work_location'] = work_location
            laureate['work_lat'] = coords[0]
            laureate['work_lon'] = coords[1]
            laureate['data_source'] = 'manual'
            laureate['needs_enrichment'] = False
            if 'note' in override:
                laureate['manual_note'] = override['note']
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
    print(f"  Skipped: {skipped}")
    print(f"  Total: {override_count}")
    print(f"  Saved to: {output_file}")
    print(f"{'=' * 80}")

if __name__ == '__main__':
    main()
