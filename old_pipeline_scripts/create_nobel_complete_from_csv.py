"""
Create nobel_data_complete.json by merging:
- Metadata from pipeline/data/01_raw_from_api.json (achievement, shared_with, etc.)
- Corrected location names and coordinates from laureates_data_to_fill_filledcoords_final.csv
"""
import json
import csv
import shutil
from datetime import datetime

def backup_json():
    """Create a timestamped backup of the existing JSON file"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = f'nobel_data_complete.backup_{timestamp}.json'
    try:
        shutil.copy('nobel_data_complete.json', backup_file)
        print(f"✓ Created backup: {backup_file}")
        return backup_file
    except FileNotFoundError:
        print("✓ No existing nobel_data_complete.json to backup")
        return None

def load_csv_data(csv_file):
    """Load CSV data into a dictionary keyed by laureate_id"""
    csv_data = {}
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            csv_data[row['laureate_id']] = row
    return csv_data

def main():
    print("=" * 70)
    print("Creating nobel_data_complete.json")
    print("=" * 70)
    print("Sources:")
    print("  - Metadata: pipeline/data/01_raw_from_api.json")
    print("  - Locations: laureates_data_to_fill_filledcoords_final.csv")
    print("=" * 70)

    # Backup existing JSON
    backup_file = backup_json()

    # Load CSV data
    print("\nLoading CSV data...")
    csv_data = load_csv_data('laureates_data_to_fill_filledcoords_final.csv')
    print(f"✓ Loaded {len(csv_data)} laureates from CSV")

    # Load API JSON
    print("\nLoading API data...")
    with open('pipeline/data/01_raw_from_api.json', 'r', encoding='utf-8') as f:
        api_data = json.load(f)

    # Count total laureates in API data
    total_api = sum(len(laureates) for laureates in api_data.values())
    print(f"✓ Loaded {total_api} laureates from API JSON")

    # Update API data with CSV locations
    print("\nMerging location data from CSV...")
    updated_count = 0
    missing_in_csv = 0
    csv_used = set()

    for category, laureates in api_data.items():
        for laureate in laureates:
            laureate_id = laureate['laureate_id']

            if laureate_id in csv_data:
                csv_row = csv_data[laureate_id]
                csv_used.add(laureate_id)

                # Update location names (always use CSV values, even if empty)
                laureate['birth_location'] = csv_row['birth_location']
                laureate['work_location'] = csv_row['work_location']

                # Update coordinates if present in CSV
                if csv_row['birth_lat']:
                    laureate['birth_lat'] = float(csv_row['birth_lat'])
                else:
                    laureate['birth_lat'] = 0

                if csv_row['birth_lon']:
                    laureate['birth_lon'] = float(csv_row['birth_lon'])
                else:
                    laureate['birth_lon'] = 0

                if csv_row['work_lat']:
                    laureate['work_lat'] = float(csv_row['work_lat'])
                else:
                    laureate['work_lat'] = 0

                if csv_row['work_lon']:
                    laureate['work_lon'] = float(csv_row['work_lon'])
                else:
                    laureate['work_lon'] = 0

                updated_count += 1
            else:
                missing_in_csv += 1
                print(f"  ⚠ Warning: {laureate_id} not found in CSV")

    # Check for CSV entries not used
    unused_csv = len(csv_data) - len(csv_used)
    if unused_csv > 0:
        print(f"  ⚠ Warning: {unused_csv} CSV entries not found in API data")

    # Write updated JSON
    print("\nWriting nobel_data_complete.json...")
    with open('nobel_data_complete.json', 'w', encoding='utf-8') as f:
        json.dump(api_data, f, indent=2, ensure_ascii=False)

    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    if backup_file:
        print(f"Backup created: {backup_file}")
    print(f"Updated laureates: {updated_count}")
    print(f"Missing in CSV: {missing_in_csv}")
    print(f"Unused CSV entries: {unused_csv}")
    print(f"\n✓ Created: nobel_data_complete.json")
    print("=" * 70)

if __name__ == '__main__':
    main()
