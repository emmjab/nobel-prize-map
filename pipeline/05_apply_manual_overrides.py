"""
Stage 5: Apply manual overrides
Applies manually curated fixes from manual_overrides.json
Automatically geocodes work_location to get lat/lon
"""
import json
import os
import sys
import requests
import time

# Add parent directory to path to import wiki_scraper
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
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
        print(f"  ⚠️  Geocoding error for '{location_string}': {e}")
        # Try wiki_scraper as fallback
        try:
            coords = get_coords(location_string)
            return coords if coords else None
        except:
            return None

def load_data(filepath):
    """Load JSON data"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_data(data, filepath):
    """Save JSON data"""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def apply_manual_overrides(data, overrides):
    """Apply manual overrides to the data and geocode locations"""
    applied_count = 0
    failed_geocoding = []

    for category, laureates in data.items():
        for laureate in laureates:
            laureate_id = laureate['laureate_id']

            if laureate_id in overrides:
                override = overrides[laureate_id]

                # Skip metadata entries
                if laureate_id.startswith('_'):
                    continue

                print(f"\nProcessing: {laureate['name']} ({laureate_id})")

                # Apply work location
                if 'work_location' in override:
                    work_location = override['work_location']
                    laureate['work_location'] = work_location
                    print(f"  Work location: {work_location}")

                    # Geocode the location
                    print(f"  Geocoding...")
                    coords = geocode_location(work_location)

                    if coords:
                        laureate['work_lat'] = coords[0]
                        laureate['work_lon'] = coords[1]
                        print(f"  ✅ Geocoded to: ({coords[0]}, {coords[1]})")
                    else:
                        print(f"  ⚠️  Failed to geocode")
                        failed_geocoding.append({
                            'laureate_id': laureate_id,
                            'name': laureate['name'],
                            'work_location': work_location
                        })
                        # Keep existing coordinates as fallback
                else:
                    # Old format with explicit lat/lon
                    if 'work_lat' in override:
                        laureate['work_lat'] = override['work_lat']
                    if 'work_lon' in override:
                        laureate['work_lon'] = override['work_lon']

                # Mark as manually overridden
                laureate['data_source'] = 'manual'
                laureate['needs_enrichment'] = False

                if 'note' in override:
                    laureate['manual_note'] = override['note']

                applied_count += 1

    if failed_geocoding:
        print(f"\n⚠️  Warning: {len(failed_geocoding)} location(s) failed to geocode:")
        for item in failed_geocoding:
            print(f"  - {item['name']}: {item['work_location']}")

    return applied_count

def main():
    """Main function"""
    print("=" * 80)
    print("Stage 5: Apply Manual Overrides")
    print("=" * 80)

    # Load data from previous stage
    input_file = 'pipeline/data/04_fixed_geocoding.json'
    print(f"Loading data from: {input_file}")
    data = load_data(input_file)

    # Load manual overrides
    overrides_file = 'manual_overrides.json'
    if not os.path.exists(overrides_file):
        print(f"\n⚠️  No manual overrides file found: {overrides_file}")
        print("   Creating empty overrides file...")
        save_data({}, overrides_file)
        overrides = {}
    else:
        print(f"Loading manual overrides from: {overrides_file}")
        overrides = load_data(overrides_file)

    print(f"\nFound {len(overrides)} manual override(s)")

    # Apply overrides
    if overrides:
        print("Applying manual overrides...")
        applied_count = apply_manual_overrides(data, overrides)
        print(f"✅ Applied {applied_count} manual override(s)")
    else:
        print("No overrides to apply")

    # Save output
    output_file = 'pipeline/data/05_with_manual_overrides.json'
    save_data(data, output_file)
    print(f"\nData saved to: {output_file}")
    print("=" * 80)

if __name__ == '__main__':
    main()
