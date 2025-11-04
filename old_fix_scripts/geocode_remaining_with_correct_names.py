"""
Geocode remaining failed locations by matching corrupted names and geocoding with correct names
Leaves the corrupted text as-is in the CSV, only updates coordinates
"""
import csv
import time
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError

# Map corrupted location names to their correct versions for geocoding
GEOCODE_CORRECTIONS = {
    'Bellme, France': 'Bellême, France',
    'Hmeenkyr, Finland': 'Hämeenkyrö, Finland',
    'Liding, Sweden': 'Lidingö, Sweden',
    'Reykjavk, Iceland': 'Reykjavík, Iceland',
    'Sdermanland, Sweden': 'Södermanland, Sweden',
    'Krakw, Poland': 'Kraków, Poland',
    'Lambarn, Gabon': 'Lambaréné, Gabon',
    'San Jos, Costa Rica': 'San José, Costa Rica',
    'Bogot, Colombia': 'Bogotá, Colombia',
    'Baden-Wrttemberg, Germany': 'Baden-Württemberg, Germany',
}

def geocode_location(geolocator, location_text):
    """Geocode a location and return (lat, lon)"""
    if not location_text:
        return None, None

    try:
        time.sleep(1.1)  # Rate limiting
        location = geolocator.geocode(location_text, timeout=10)
        if location:
            print(f"  ✓ {location_text} → ({location.latitude}, {location.longitude})")
            return location.latitude, location.longitude
        else:
            print(f"  ✗ {location_text} → Not found")
            return None, None
    except (GeocoderTimedOut, GeocoderServiceError) as e:
        print(f"  ✗ {location_text} → Error: {e}")
        return None, None

def main():
    print("=" * 70)
    print("Geocoding Remaining Locations with Correct Character Encoding")
    print("=" * 70)

    geolocator = Nominatim(user_agent="nobel_prize_map_geocoder")

    input_file = 'laureates_data_to_fill_filledcoords.csv'

    rows = []
    with open(input_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        rows = list(reader)

    print(f"\nLoaded {len(rows)} laureates")
    print(f"\nLooking for {len(GEOCODE_CORRECTIONS)} corrupted location names to geocode...")
    print("=" * 70)

    geocoded_count = 0
    failed_count = 0

    for i, row in enumerate(rows):
        updated = False

        # Check birth location
        if row['birth_location'] in GEOCODE_CORRECTIONS and not row['birth_lat']:
            correct_name = GEOCODE_CORRECTIONS[row['birth_location']]
            print(f"\n[{i+1}/{len(rows)}] {row['name']}")
            print(f"  Geocoding birth with correct name: {correct_name}")

            lat, lon = geocode_location(geolocator, correct_name)
            if lat is not None:
                row['birth_lat'] = lat
                row['birth_lon'] = lon
                geocoded_count += 1
                updated = True
            else:
                failed_count += 1

        # Check work location
        if row['work_location'] in GEOCODE_CORRECTIONS and not row['work_lat']:
            correct_name = GEOCODE_CORRECTIONS[row['work_location']]
            if not updated:
                print(f"\n[{i+1}/{len(rows)}] {row['name']}")
            print(f"  Geocoding work with correct name: {correct_name}")

            lat, lon = geocode_location(geolocator, correct_name)
            if lat is not None:
                row['work_lat'] = lat
                row['work_lon'] = lon
                geocoded_count += 1
            else:
                failed_count += 1

    # Write the updated CSV
    with open(input_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Successfully geocoded: {geocoded_count} locations")
    print(f"Failed to geocode: {failed_count} locations")
    print(f"\nUpdated file: {input_file}")
    print("=" * 70)

if __name__ == '__main__':
    main()
