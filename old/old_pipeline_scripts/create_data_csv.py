"""
Create CSV from JSON data for manual enrichment
Merges in existing manual work_locations_to_fill.csv data
"""
import json
import csv

# Load JSON data
with open('pipeline/data/01_raw_from_api.json', 'r') as f:
    data = json.load(f)

# Load existing manual data
manual_data = {}
try:
    # Try different encodings
    for encoding in ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252']:
        try:
            with open('work_locations_to_fill.csv', 'r', encoding=encoding) as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row['work_location']:  # Only use rows where work_location is filled
                        manual_data[row['laureate_id']] = {
                            'work_location': row['work_location'],
                            'notes': row.get('notes', '')
                        }
            print(f"Loaded {len(manual_data)} manually researched work locations (encoding: {encoding})")
            break
        except UnicodeDecodeError:
            continue
except FileNotFoundError:
    print("No existing work_locations_to_fill.csv found")

# Create CSV
output_file = 'laureates_data_to_fill.csv'
fieldnames = [
    'laureate_id', 'name', 'category', 'year',
    'birth_location', 'birth_lat', 'birth_lon',
    'work_location', 'work_lat', 'work_lon',
    'notes'
]

rows = []
for category, laureates in data.items():
    for entry in laureates:
        # Check if we have manual data for this laureate
        manual_info = manual_data.get(entry['laureate_id'], {})

        # Use manual work_location if available, otherwise use API data
        work_location = manual_info.get('work_location', entry['work_location'])
        notes = manual_info.get('notes', '')

        row = {
            'laureate_id': entry['laureate_id'],
            'name': entry['name'],
            'category': category,
            'year': entry['prize_year'],
            'birth_location': entry['birth_location'],
            'birth_lat': entry['birth_lat'] if entry['birth_lat'] != 0 else '',
            'birth_lon': entry['birth_lon'] if entry['birth_lon'] != 0 else '',
            'work_location': work_location,
            'work_lat': entry['work_lat'] if entry['work_lat'] != 0 else '',
            'work_lon': entry['work_lon'] if entry['work_lon'] != 0 else '',
            'notes': notes
        }
        rows.append(row)

# Sort by category, then year
rows.sort(key=lambda x: (x['category'], x['year']))

with open(output_file, 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)

print(f"Created {output_file} with {len(rows)} laureates")

# Count what needs filling
missing_birth_location = sum(1 for r in rows if not r['birth_location'])
missing_birth_coords = sum(1 for r in rows if r['birth_location'] and not r['birth_lat'])
missing_work_location = sum(1 for r in rows if not r['work_location'])
missing_work_coords = sum(1 for r in rows if r['work_location'] and not r['work_lat'])

print(f"\nData to fill in:")
print(f"  Birth locations: {missing_birth_location}")
print(f"  Birth coords (have location, need geocoding): {missing_birth_coords}")
print(f"  Work locations: {missing_work_location}")
print(f"  Work coords (have location, need geocoding): {missing_work_coords}")
