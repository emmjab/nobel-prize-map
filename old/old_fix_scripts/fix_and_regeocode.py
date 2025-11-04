"""
Fix character encoding issues and re-geocode failed locations
"""
import csv
import time
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError

# Mapping of broken location names to corrected ones
LOCATION_FIXES = {
    'Bellme, France': 'Bellême, France',
    'Hmeenkyr, Finland': 'Hämeenkyrö, Finland',
    'Liding, Sweden': 'Lidingö, Sweden',
    'Reykjavk, Iceland': 'Reykjavík, Iceland',
    'Krakw, Poland': 'Kraków, Poland',
    'Sdermanland, Sweden': 'Södermanland, Sweden',
    'Lambarn, Gabon': 'Lambaréné, Gabon',
    'Wroc_aw, Poland': 'Wrocław, Poland',
    'San Jos, Costa Rica': 'San José, Costa Rica',
    'Brussels, Belgiium': 'Brussels, Belgium',
    'Bogot, Colombia': 'Bogotá, Colombia',
    'Baden-Wrttemberg, Germany': 'Baden-Württemberg, Germany',
    'Gaomi in Shandong Province, China': 'Gaomi, Shandong, China',
    'Chimel, Guatemala': 'Chimel, Quiché, Guatemala',
    'Wailacama, East Timor': 'Wailacama, East Timor',
    'Langford Grove, Maldon, Essex, United Kingdom': 'Maldon, Essex, United Kingdom',
    'Gaffken, Prussia': 'Gaffken, East Prussia',
}

def geocode_location(geolocator, location_text):
    """
    Geocode a location string and return (lat, lon)
    Returns (None, None) if geocoding fails
    """
    if not location_text or location_text.strip() == '':
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
    print("Fixing Character Encoding and Re-geocoding Failed Locations")
    print("=" * 70)

    # Initialize geocoder
    geolocator = Nominatim(user_agent="nobel_prize_map_geocoder")

    # Read the CSV
    input_file = 'laureates_data_to_fill_filledcoords.csv'

    rows = []
    with open(input_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        rows = list(reader)

    print(f"\nLoaded {len(rows)} laureates")

    # Find and fix problematic locations
    fixed_count = 0
    geocoded_count = 0
    failed_count = 0

    for i, row in enumerate(rows):
        updated = False

        # Check birth location
        if row['birth_location'] and not row['birth_lat']:
            original = row['birth_location']
            if original in LOCATION_FIXES:
                row['birth_location'] = LOCATION_FIXES[original]
                print(f"\n[{i+1}/{len(rows)}] {row['name']}")
                print(f"  Fixed birth: {original} → {row['birth_location']}")
                fixed_count += 1

                # Try geocoding
                lat, lon = geocode_location(geolocator, row['birth_location'])
                if lat is not None:
                    row['birth_lat'] = lat
                    row['birth_lon'] = lon
                    geocoded_count += 1
                else:
                    failed_count += 1
                updated = True
            else:
                # Try geocoding with original name (might work now)
                print(f"\n[{i+1}/{len(rows)}] {row['name']}")
                print(f"  Retrying birth: {original}")
                lat, lon = geocode_location(geolocator, original)
                if lat is not None:
                    row['birth_lat'] = lat
                    row['birth_lon'] = lon
                    geocoded_count += 1
                else:
                    failed_count += 1
                updated = True

        # Check work location
        if row['work_location'] and not row['work_lat']:
            original = row['work_location']
            if original in LOCATION_FIXES:
                if not updated:
                    print(f"\n[{i+1}/{len(rows)}] {row['name']}")
                row['work_location'] = LOCATION_FIXES[original]
                print(f"  Fixed work: {original} → {row['work_location']}")
                fixed_count += 1

                # Try geocoding
                lat, lon = geocode_location(geolocator, row['work_location'])
                if lat is not None:
                    row['work_lat'] = lat
                    row['work_lon'] = lon
                    geocoded_count += 1
                else:
                    failed_count += 1
            else:
                # Try geocoding with original name (might work now)
                if not updated:
                    print(f"\n[{i+1}/{len(rows)}] {row['name']}")
                print(f"  Retrying work: {original}")
                lat, lon = geocode_location(geolocator, original)
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
    print(f"Location names fixed: {fixed_count}")
    print(f"Successfully geocoded: {geocoded_count}")
    print(f"Still failed: {failed_count}")
    print(f"\nUpdated file: {input_file}")
    print("=" * 70)

if __name__ == '__main__':
    main()
