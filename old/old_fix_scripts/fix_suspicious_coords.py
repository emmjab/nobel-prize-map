#!/usr/bin/env python3
"""
Re-geocode entries with suspicious (0,0) coordinates
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
            print(f"    Nominatim failed, trying Wikipedia...")
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
    print("Re-geocoding Suspicious Entries (0,0 coordinates)")
    print("=" * 80)

    # Load suspicious entries
    suspicious_file = 'pipeline/data/suspicious_entries.json'
    print(f"\nLoading suspicious entries from: {suspicious_file}")
    with open(suspicious_file, 'r', encoding='utf-8') as f:
        suspicious = json.load(f)

    print(f"Found {len(suspicious)} entries with suspicious coordinates")

    # Load current data
    data_file = 'pipeline/data/05_with_manual_overrides.json'
    if not os.path.exists(data_file):
        data_file = 'pipeline/data/04_fixed_geocoding.json'

    print(f"Loading data from: {data_file}")
    with open(data_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Process each suspicious entry
    updated = 0
    failed = 0
    total = len(suspicious)

    print(f"\n{'=' * 80}")
    print("Processing entries...")
    print(f"{'=' * 80}\n")

    for i, entry in enumerate(suspicious, 1):
        laureate_id = entry['laureate_id']
        name = entry['name']
        work_location = entry['work_location']
        category = entry['category']

        # Find the laureate in the data
        laureate = None
        for cat, laureates in data.items():
            for l in laureates:
                if l.get('laureate_id') == laureate_id:
                    laureate = l
                    break
            if laureate:
                break

        if not laureate:
            print(f"[{i}/{total}] ⚠️  {name} ({laureate_id}) - not found in data")
            failed += 1
            continue

        print(f"[{i}/{total}] {name} ({category} {entry['prize_year']})")
        print(f"  Location: {work_location}")
        print(f"  Geocoding...")

        coords = geocode_location(work_location)

        if coords:
            laureate['work_lat'] = coords[0]
            laureate['work_lon'] = coords[1]
            print(f"  ✅ Geocoded to: ({coords[0]:.4f}, {coords[1]:.4f})")
            updated += 1
        else:
            print(f"  ❌ Failed to geocode")
            failed += 1

        # Save progress every 10 entries
        if i % 10 == 0:
            print(f"\n--- Saving progress: {updated} updated, {failed} failed ---\n")
            with open(data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

    # Save final data
    print(f"\nSaving final data to: {data_file}")
    with open(data_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"\n{'=' * 80}")
    print(f"Summary:")
    print(f"  Total processed: {total}")
    print(f"  Successfully geocoded: {updated}")
    print(f"  Failed: {failed}")
    print(f"  Success rate: {updated/total*100:.1f}%")
    print(f"  Saved to: {data_file}")
    print(f"{'=' * 80}")

if __name__ == '__main__':
    main()
