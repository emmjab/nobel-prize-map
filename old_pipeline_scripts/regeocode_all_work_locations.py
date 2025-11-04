#!/usr/bin/env python3
"""
Re-geocode all work_location strings to ensure coordinates are correct
"""
import json
import time
import requests

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
            return None
    except Exception as e:
        print(f"  ⚠️  Geocoding error: {e}")
        return None

def main():
    print("=" * 80)
    print("Re-geocode All Work Locations")
    print("=" * 80)

    # Load data
    data_file = 'pipeline/data/05_with_manual_overrides.json'
    print(f"\nLoading data from: {data_file}")
    with open(data_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Collect all laureates with work_location
    all_laureates = []
    for category, laureates in data.items():
        for l in laureates:
            if l.get('work_location'):
                all_laureates.append(l)

    print(f"\nFound {len(all_laureates)} laureates with work_location")

    # Fix each entry
    updated = 0
    failed = 0
    skipped = 0

    for i, laureate in enumerate(all_laureates, 1):
        work_location = laureate['work_location']
        old_coords = (laureate.get('work_lat'), laureate.get('work_lon'))

        print(f"\n[{i}/{len(all_laureates)}] {laureate['name']}")
        print(f"  Work location: {work_location}")
        print(f"  Old coords: {old_coords}")
        print(f"  Geocoding...")

        coords = geocode_location(work_location)

        if coords:
            laureate['work_lat'] = coords[0]
            laureate['work_lon'] = coords[1]
            if coords != old_coords:
                print(f"  ✅ Updated to: ({coords[0]:.4f}, {coords[1]:.4f})")
                updated += 1
            else:
                print(f"  ✓ Already correct: ({coords[0]:.4f}, {coords[1]:.4f})")
                skipped += 1
        else:
            print(f"  ❌ Failed to geocode")
            failed += 1

        # Save progress every 20 entries
        if i % 20 == 0:
            print(f"\n--- Saving progress: {updated} updated, {skipped} already correct, {failed} failed ---\n")
            with open(data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

    # Save final data
    print(f"\nSaving final data to: {data_file}")
    with open(data_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"\n{'=' * 80}")
    print(f"Summary:")
    print(f"  Total processed: {len(all_laureates)}")
    print(f"  Updated: {updated}")
    print(f"  Already correct: {skipped}")
    print(f"  Failed: {failed}")
    print(f"  Saved to: {data_file}")
    print(f"{'=' * 80}")

if __name__ == '__main__':
    main()
