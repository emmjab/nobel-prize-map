"""
Fix work locations by extracting the city/country from affiliation strings
Instead of geocoding "Stanford University School of Medicine, Stanford, CA, USA"
We extract and geocode just "Stanford, CA, USA"
"""

import json
import requests
import time
import re

def load_data(filepath):
    """Load the Nobel Prize data from JSON file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_data(data, filepath):
    """Save the Nobel Prize data to JSON file"""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

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
        print(f"  ❌ Geocoding error for '{location_string}': {e}")
        return None

def extract_location_from_affiliation(affiliation):
    """
    Extract location (city, state/country) from affiliation string

    Examples:
    - "Max Planck Institute for Meteorology, Hamburg, Germany" → "Hamburg, Germany"
    - "Stanford University School of Medicine, Stanford, CA, USA" → "Stanford, CA, USA"
    - "LIGO/VIRGO Collaboration, ; MIT, Cambridge, MA, USA" → "Cambridge, MA, USA"
    - "University of Washington, Seattle, WA, USA; Howard Hughes..." → "Seattle, WA, USA"

    Strategy: Take everything after the last comma that contains an institution name,
    or take the last 2-3 comma-separated parts
    """
    # Clean up the affiliation
    affiliation = affiliation.strip()

    # Split by semicolon and take the first part (handles multiple affiliations)
    if ';' in affiliation:
        affiliation = affiliation.split(';')[0].strip()

    # Split by comma
    parts = [p.strip() for p in affiliation.split(',')]

    if len(parts) < 2:
        # No comma, can't extract location
        return None

    # Try to find location patterns
    # Usually location is the last 2-3 parts: "City, State/Country" or "City, Country"

    # Check last part - should be a country or USA
    last_part = parts[-1]

    # Common patterns:
    # - "City, Country"
    # - "City, State, Country"
    # - "City, ST, Country"

    if len(parts) >= 2:
        # Try last 2 parts
        location = ', '.join(parts[-2:])
        return location

    return None

def identify_problematic_laureates(data):
    """Find all laureates where work_location == birth_location"""
    problematic = []

    for category, laureates in data.items():
        for laureate in laureates:
            if (laureate['work_location'] == laureate['birth_location'] and
                laureate['work_lat'] == laureate['birth_lat'] and
                laureate['work_lon'] == laureate['birth_lon']):
                problematic.append({
                    'category': category,
                    'laureate': laureate
                })

    return problematic

def fix_work_locations(data_file):
    """Main function to fix work locations"""
    print("Loading data...")
    data = load_data(data_file)

    print("\nIdentifying problematic laureates...")
    problematic = identify_problematic_laureates(data)

    print(f"\nFound {len(problematic)} laureates with work_location == birth_location")

    # For each problematic laureate, check if work_location looks like an affiliation
    # (contains commas and institution keywords)
    fixable = []
    for item in problematic:
        laureate = item['laureate']
        work_loc = laureate['work_location']

        # Check if it contains institution keywords or has multiple comma-separated parts
        if ',' in work_loc and len(work_loc.split(',')) >= 2:
            # Could be an affiliation string that needs location extraction
            fixable.append(item)

    print(f"Found {len(fixable)} laureates with affiliation-like work_location strings")
    print("=" * 80)

    fixed_count = 0
    failed_count = 0

    for i, item in enumerate(fixable, 1):
        category = item['category']
        laureate = item['laureate']
        name = laureate['name']
        year = laureate['prize_year']
        current_work = laureate['work_location']

        print(f"\n[{i}/{len(fixable)}] {name} ({year} {category.title()})")
        print(f"  Current work_location: {current_work}")

        # Extract location from affiliation
        location = extract_location_from_affiliation(current_work)

        if not location:
            print(f"  ❌ Could not extract location")
            failed_count += 1
            continue

        print(f"  ✓ Extracted location: {location}")

        # Geocode the location
        coords = geocode_location(location)

        if coords:
            # Keep the full affiliation as work_location, but update coordinates
            laureate['work_lat'] = coords[0]
            laureate['work_lon'] = coords[1]

            print(f"  ✅ FIXED: Updated coordinates to {coords}")
            fixed_count += 1
        else:
            print(f"  ❌ Could not geocode: {location}")
            failed_count += 1

        # Save progress every 10 laureates
        if (i % 10 == 0):
            print(f"\n--- Saving progress ({fixed_count} fixed so far) ---")
            save_data(data, data_file)

    # Final save
    print("\n" + "=" * 80)
    print("Saving final results...")
    save_data(data, data_file)

    print("\n✅ SUMMARY:")
    print(f"   Fixed: {fixed_count}")
    print(f"   Failed: {failed_count}")
    print(f"   Total processed: {len(fixable)}")

    return fixed_count, failed_count

if __name__ == '__main__':
    data_file = 'nobel_data_complete.json'

    print("=" * 80)
    print("FIX WORK LOCATIONS BY EXTRACTING LOCATION FROM AFFILIATIONS")
    print("=" * 80)
    print(f"\nThis script will:")
    print("1. Find laureates with affiliation-like work_location strings")
    print("2. Extract just the location (city, country) from the string")
    print("3. Geocode the extracted location")
    print("4. Update coordinates while keeping full affiliation text")
    print("\nStarting fix...\n")

    fixed, failed = fix_work_locations(data_file)

    print("\n✅ Done!")
