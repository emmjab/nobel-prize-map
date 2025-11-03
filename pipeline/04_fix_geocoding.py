#!/usr/bin/env python3
"""
Stage 4: Fix Geocoding Errors
Comprehensive geocoding fixes in optimal order
"""
import json
import os
import sys
import time
import requests

# Add parent directory to path
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
        # Try wiki_scraper as fallback
        try:
            coords = get_coords(location_string)
            return coords if coords else None
        except:
            return None

def fix_suspicious_coordinates(data):
    """Fix 1: Re-geocode entries with suspicious (0,0) coordinates"""
    print("\n" + "=" * 80)
    print("FIX 1: Re-geocoding Suspicious (0,0) Coordinates")
    print("=" * 80)

    suspicious = []
    for category, laureates in data.items():
        for l in laureates:
            work_lat = l.get('work_lat', 0)
            work_lon = l.get('work_lon', 0)
            if work_lat == 0 and work_lon == 0:
                suspicious.append(l)

    print(f"\nFound {len(suspicious)} entries with (0,0) coordinates")

    if len(suspicious) == 0:
        print("No suspicious coordinates to fix!")
        return 0

    updated = 0
    failed = 0

    for i, laureate in enumerate(suspicious, 1):
        work_location = laureate.get('work_location', '')
        if not work_location:
            continue

        if i % 20 == 0:
            print(f"  [{i}/{len(suspicious)}] Processed {updated} updated, {failed} failed")

        coords = geocode_location(work_location)
        if coords:
            laureate['work_lat'] = coords[0]
            laureate['work_lon'] = coords[1]
            updated += 1
        else:
            failed += 1

    print(f"\n✓ Fixed {updated} suspicious coordinates ({failed} failed)")
    return updated

def fix_cambridge_confusion(data):
    """Fix 2: Fix Cambridge MA/UK coordinate confusion"""
    print("\n" + "=" * 80)
    print("FIX 2: Fixing Cambridge MA/UK Confusion")
    print("=" * 80)

    # Known correct coordinates
    cambridge_ma = (42.3656347, -71.1040018)
    cambridge_uk = (52.2055314, 0.1186637)

    fixes_needed = {
        'Cambridge, MA, USA': cambridge_ma,
        'Cambridge, MA': cambridge_ma,
        'Cambridge, Massachusetts, USA': cambridge_ma,
        'MIT, Cambridge, MA, USA': cambridge_ma,
        'Harvard, Cambridge, MA, USA': cambridge_ma,
        'Cambridge, England': cambridge_uk,
        'Cambridge, United Kingdom': cambridge_uk,
        'Cambridge, UK': cambridge_uk,
    }

    updated = 0

    for category, laureates in data.items():
        for laureate in laureates:
            work_location = laureate.get('work_location', '')
            for location_text, correct_coords in fixes_needed.items():
                if location_text.lower() in work_location.lower():
                    old_coords = (laureate.get('work_lat'), laureate.get('work_lon'))
                    if old_coords != correct_coords:
                        laureate['work_lat'] = correct_coords[0]
                        laureate['work_lon'] = correct_coords[1]
                        updated += 1

    print(f"\n✓ Fixed {updated} Cambridge coordinate issues")
    return updated

def extract_clean_locations(data):
    """Fix 3: Extract clean location from affiliation strings"""
    print("\n" + "=" * 80)
    print("FIX 3: Extracting Clean Locations from Affiliation Strings")
    print("=" * 80)

    import re

    updated = 0

    for category, laureates in data.items():
        for laureate in laureates:
            work_location = laureate.get('work_location', '')

            # Skip if it's already a clean location
            if not work_location or ',' not in work_location:
                continue

            # Try to extract just the location part (city, country)
            # Remove institution names, keep geography
            original = work_location

            # Patterns to extract location
            # e.g., "University of XYZ, City, Country" -> "City, Country"
            # e.g., "Institute, City, State, Country" -> "City, State, Country"

            parts = [p.strip() for p in work_location.split(',')]

            # Look for geographic indicators (countries, US states)
            geographic_terms = [
                'USA', 'United States', 'UK', 'United Kingdom', 'France', 'Germany',
                'Italy', 'Spain', 'Japan', 'China', 'India', 'Canada', 'Australia',
                'Switzerland', 'Sweden', 'Norway', 'Denmark', 'Netherlands', 'Belgium',
                'Austria', 'Poland', 'Russia', 'Israel', 'Brazil', 'Argentina',
                # US States
                'CA', 'NY', 'MA', 'TX', 'IL', 'PA', 'OH', 'MI', 'NJ', 'VA', 'MD',
                'CT', 'RI', 'NH', 'VT', 'ME', 'DE', 'WV', 'NC', 'SC', 'GA', 'FL',
                'AL', 'MS', 'LA', 'AR', 'TN', 'KY', 'IN', 'WI', 'MN', 'IA', 'MO',
                'ND', 'SD', 'NE', 'KS', 'OK', 'CO', 'WY', 'MT', 'ID', 'WA', 'OR',
                'NV', 'UT', 'AZ', 'NM', 'AK', 'HI'
            ]

            # Find the first geographic term
            geo_index = -1
            for i, part in enumerate(parts):
                if any(geo.lower() in part.lower() for geo in geographic_terms):
                    geo_index = i
                    break

            if geo_index > 0:
                # Extract from city to country
                location_parts = parts[max(0, geo_index - 1):]
                extracted_location = ', '.join(location_parts)

                # Re-geocode with the clean location
                coords = geocode_location(extracted_location)
                if coords:
                    laureate['work_location'] = extracted_location
                    laureate['work_lat'] = coords[0]
                    laureate['work_lon'] = coords[1]
                    updated += 1

    print(f"\n✓ Extracted and re-geocoded {updated} locations")
    return updated

def regeocode_work_locations(data):
    """Fix 4: Re-geocode all work_location strings to ensure coords match text"""
    print("\n" + "=" * 80)
    print("FIX 4: Re-geocoding Work Locations (Final Verification)")
    print("=" * 80)
    print("This ensures all work_location text matches coordinates")

    all_laureates = []
    for category, laureates in data.items():
        for l in laureates:
            if l.get('work_location'):
                all_laureates.append(l)

    print(f"\nFound {len(all_laureates)} laureates with work_location")
    print("Re-geocoding to verify coords match location text...")

    updated = 0
    already_correct = 0
    failed = 0

    for i, laureate in enumerate(all_laureates, 1):
        if i % 50 == 0:
            print(f"  [{i}/{len(all_laureates)}] {updated} updated, {already_correct} verified, {failed} failed")

        work_location = laureate['work_location']
        old_coords = (laureate.get('work_lat'), laureate.get('work_lon'))

        coords = geocode_location(work_location)

        if coords:
            # Check if coords changed significantly (more than 0.01 degrees ~ 1km)
            if old_coords and old_coords != (0, 0):
                lat_diff = abs(coords[0] - old_coords[0])
                lon_diff = abs(coords[1] - old_coords[1])
                if lat_diff < 0.01 and lon_diff < 0.01:
                    already_correct += 1
                    continue

            laureate['work_lat'] = coords[0]
            laureate['work_lon'] = coords[1]
            updated += 1
        else:
            failed += 1

    print(f"\n✓ Updated {updated} coordinates, verified {already_correct}, failed {failed}")
    return updated

def main():
    """Main function to run all geocoding fixes"""
    print("=" * 80)
    print("Stage 4: Fix Geocoding Errors (Comprehensive)")
    print("=" * 80)

    # Load data from previous stage
    input_file = 'pipeline/data/03_enriched_wikipedia.json'
    if not os.path.exists(input_file):
        print(f"\nERROR: Input file not found: {input_file}")
        print("Please run stage 3 first.")
        return

    print(f"\nLoading data from: {input_file}")
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Count total laureates
    total = sum(len(laureates) for laureates in data.values())
    print(f"Loaded {total} laureates")

    # Run all fixes in optimal order
    stats = {}

    stats['fix1_suspicious'] = fix_suspicious_coordinates(data)
    stats['fix2_cambridge'] = fix_cambridge_confusion(data)
    stats['fix3_extract'] = extract_clean_locations(data)
    stats['fix4_regeocode'] = regeocode_work_locations(data)

    # Save fixed data
    output_file = 'pipeline/data/04_fixed_geocoding.json'
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    # Print summary
    print("\n" + "=" * 80)
    print("GEOCODING FIX SUMMARY")
    print("=" * 80)
    print(f"Fix 1 - Suspicious (0,0) coords:     {stats['fix1_suspicious']:4} fixed")
    print(f"Fix 2 - Cambridge confusion:         {stats['fix2_cambridge']:4} fixed")
    print(f"Fix 3 - Extract clean locations:     {stats['fix3_extract']:4} fixed")
    print(f"Fix 4 - Re-geocode verification:     {stats['fix4_regeocode']:4} updated")
    print("=" * 80)
    print(f"Total fixes applied: {sum(stats.values())}")
    print(f"\nData saved to: {output_file}")
    print("=" * 80)

if __name__ == '__main__':
    main()
