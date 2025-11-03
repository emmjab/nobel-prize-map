#!/usr/bin/env python3
"""
Convert work_locations_to_fill.csv to manual_overrides.json
Combines with already researched locations
"""

import json
import csv

def main():
    print("=" * 80)
    print("Converting CSV to manual_overrides.json")
    print("=" * 80)

    # Load the 35 already researched
    print("\nLoading already researched locations...")
    with open('pipeline/data/search_results_work_locations.json', 'r') as f:
        already_done = json.load(f)
    print(f"  Found {len(already_done)} already researched")

    # Read the CSV you filled in
    print("\nReading your CSV file...")
    newly_added = {}

    # Try different encodings
    encodings = ['utf-8', 'utf-8-sig', 'latin-1', 'iso-8859-1', 'cp1252', 'macroman']
    csv_data = None
    used_encoding = None

    for encoding in encodings:
        try:
            with open('work_locations_to_fill.csv', 'r', encoding=encoding) as f:
                reader = csv.DictReader(f)
                rows = list(reader)
                # Test if we can read special characters correctly
                test_text = ''.join([row.get('name', '') + row.get('work_location', '') for row in rows])
                if '\ufffd' in test_text:  # Unicode replacement character means bad encoding
                    continue
                csv_data = rows
                used_encoding = encoding
                print(f"  Successfully read CSV with {encoding} encoding")
                break
        except (UnicodeDecodeError, UnicodeError):
            continue

    if csv_data is None:
        print("  ❌ Error: Could not read CSV with any common encoding")
        print("  Try re-saving your CSV as UTF-8 in Excel/Sheets")
        return

    for row in csv_data:
        # Only add if you filled in the work_location
        if row['work_location'].strip():
            newly_added[row['laureate_id']] = {
                'work_location': row['work_location'].strip(),
                'note': row['notes'].strip() if row['notes'].strip() else f"{row['name']} - {row['category']} {row['year']}"
            }

    print(f"  Found {len(newly_added)} new entries you added")

    # Combine both into manual_overrides.json format
    print("\nCombining all entries...")
    manual_overrides = {
        "_comment": "Manual overrides for Nobel Prize laureate work locations",
        "_instructions": "Work locations will be automatically geocoded to lat/lon by the pipeline"
    }

    # Add the already researched ones
    for laureate_id, data in already_done.items():
        manual_overrides[laureate_id] = {
            'work_location': data['work_location'],
            'note': data['source']
        }

    # Add your new ones
    manual_overrides.update(newly_added)

    # Save to manual_overrides.json with proper Unicode handling
    with open('manual_overrides.json', 'w', encoding='utf-8') as f:
        json.dump(manual_overrides, f, indent=2, ensure_ascii=False)

    # Verify the file was written correctly
    with open('manual_overrides.json', 'r', encoding='utf-8') as f:
        verify = json.load(f)
    print(f"  Verified JSON file can be read back correctly")

    total = len(already_done) + len(newly_added)
    print(f"\n✅ Created manual_overrides.json")
    print(f"   - Already researched: {len(already_done)}")
    print(f"   - Newly added by you: {len(newly_added)}")
    print(f"   - Total: {total}")
    print(f"   - Still need: {271 - total}")

    print("\n" + "=" * 80)
    print("Next steps:")
    print("=" * 80)
    print("1. Run the pipeline: python run_pipeline.py")
    print("2. Stage 5 will automatically geocode all work locations")
    print("3. Check the output for any geocoding failures")
    print("=" * 80)

if __name__ == '__main__':
    main()
