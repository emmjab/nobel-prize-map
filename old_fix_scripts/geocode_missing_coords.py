"""
Geocode missing coordinates in the CSV file
Uses Nominatim (OpenStreetMap) for free geocoding with rate limiting
"""
import csv
import time
import sys
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError

# Force unbuffered output
sys.stdout.reconfigure(line_buffering=True)

def geocode_location(geolocator, location_text, location_type):
    """
    Geocode a location string and return (lat, lon)
    Returns (None, None) if geocoding fails
    """
    if not location_text or location_text.strip() == '':
        return None, None

    try:
        # Add a small delay to respect rate limits (1 request per second)
        time.sleep(1.1)

        location = geolocator.geocode(location_text, timeout=10)
        if location:
            print(f"  ✓ {location_type}: {location_text} → ({location.latitude}, {location.longitude})")
            return location.latitude, location.longitude
        else:
            print(f"  ✗ {location_type}: {location_text} → Not found")
            return None, None
    except (GeocoderTimedOut, GeocoderServiceError) as e:
        print(f"  ✗ {location_type}: {location_text} → Error: {e}")
        return None, None

def main():
    print("=" * 70)
    print("Geocoding Missing Coordinates")
    print("=" * 70)

    # Initialize geocoder
    geolocator = Nominatim(user_agent="nobel_prize_map_geocoder")

    # Read the CSV
    input_file = 'laureates_data_to_fill_filledtext.csv'
    output_file = 'laureates_data_to_fill_filledcoords.csv'

    rows = []
    with open(input_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        rows = list(reader)

    print(f"\nLoaded {len(rows)} laureates from {input_file}")

    # Count what needs geocoding
    need_birth_coords = sum(1 for r in rows if r['birth_location'] and not r['birth_lat'])
    need_work_coords = sum(1 for r in rows if r['work_location'] and not r['work_lat'])

    print(f"\nNeed to geocode:")
    print(f"  Birth locations: {need_birth_coords}")
    print(f"  Work locations: {need_work_coords}")
    print(f"  Total: {need_birth_coords + need_work_coords}")
    print(f"\nStarting geocoding (this will take a while due to rate limiting)...")
    print("=" * 70)

    # Geocode missing coordinates
    geocoded_count = 0
    failed_count = 0

    for i, row in enumerate(rows, 1):
        laureate_id = row['laureate_id']
        name = row['name']

        updated = False

        # Geocode birth location if needed
        if row['birth_location'] and not row['birth_lat']:
            print(f"\n[{i}/{len(rows)}] {name} ({laureate_id})")
            lat, lon = geocode_location(geolocator, row['birth_location'], "Birth")
            if lat is not None:
                row['birth_lat'] = lat
                row['birth_lon'] = lon
                geocoded_count += 1
                updated = True
            else:
                failed_count += 1

        # Geocode work location if needed
        if row['work_location'] and not row['work_lat']:
            if not updated:  # Print header if not already printed
                print(f"\n[{i}/{len(rows)}] {name} ({laureate_id})")
            lat, lon = geocode_location(geolocator, row['work_location'], "Work")
            if lat is not None:
                row['work_lat'] = lat
                row['work_lon'] = lon
                geocoded_count += 1
                updated = True
            else:
                failed_count += 1

    # Write the updated CSV
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Successfully geocoded: {geocoded_count} locations")
    print(f"Failed to geocode: {failed_count} locations")
    print(f"\nOutput written to: {output_file}")
    print("=" * 70)

if __name__ == '__main__':
    main()
