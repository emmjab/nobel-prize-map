"""
Script to fetch all Nobel Prize laureates from the official Nobel Prize API
and save to a JSON file with location data.
"""

import requests
import json
import time
from wiki_scraper import CITY_COORDS, get_coords

def fetch_all_laureates():
    """Fetch all Nobel Prize laureates from the API"""
    print("Fetching prize data from Nobel Prize API...")

    # Fetch all prizes
    response = requests.get("https://api.nobelprize.org/v1/prize.json")
    prizes_data = response.json()

    print(f"Found {len(prizes_data['prizes'])} prizes")

    # Get unique laureate IDs
    laureate_ids = set()
    for prize in prizes_data['prizes']:
        if 'laureates' in prize:
            for laureate in prize['laureates']:
                laureate_ids.add(laureate['id'])

    print(f"Found {len(laureate_ids)} unique laureates")
    print("Fetching detailed information for each laureate...")

    all_laureates = {}
    count = 0

    for laureate_id in sorted(laureate_ids, key=int):
        count += 1
        if count % 50 == 0:
            print(f"  Processed {count}/{len(laureate_ids)} laureates...")
            time.sleep(0.5)  # Be nice to the API

        try:
            response = requests.get(f"https://api.nobelprize.org/v1/laureate.json?id={laureate_id}")
            data = response.json()

            if 'laureates' in data and len(data['laureates']) > 0:
                all_laureates[laureate_id] = data['laureates'][0]
        except Exception as e:
            print(f"  Error fetching laureate {laureate_id}: {e}")

    print(f"Successfully fetched {len(all_laureates)} laureates")
    return all_laureates

def process_laureates_by_category(all_laureates):
    """Process laureates and organize by category with location data"""

    category_data = {
        'physics': [],
        'chemistry': [],
        'medicine': [],
        'literature': [],
        'peace': [],
        'economics': []
    }

    # Map API category names to our names
    category_map = {
        'physics': 'physics',
        'chemistry': 'chemistry',
        'medicine': 'medicine',
        'literature': 'literature',
        'peace': 'peace',
        'economics': 'economics'
    }

    print("\nProcessing laureates by category...")

    for laureate_id, laureate in all_laureates.items():
        if 'prizes' not in laureate:
            continue

        for prize in laureate['prizes']:
            category = prize.get('category')
            if category not in category_map:
                continue

            cat_key = category_map[category]
            year = int(prize['year'])

            # Get birth location
            birth_city = laureate.get('bornCity', '')
            birth_country = laureate.get('bornCountry', '')
            birth_location = f"{birth_city}, {birth_country}" if birth_city else birth_country

            # Get birth coordinates
            birth_coords = get_coords(birth_city if birth_city else birth_country)
            if not birth_coords:
                birth_coords = (0, 0)  # Default if not found

            # Get work location from affiliations
            work_city = ''
            work_country = ''
            if 'affiliations' in prize and len(prize['affiliations']) > 0:
                aff = prize['affiliations'][0]
                # Handle both dict and list formats
                if isinstance(aff, dict):
                    work_city = aff.get('city', '')
                    work_country = aff.get('country', '')

            work_location = f"{work_city}, {work_country}" if work_city else work_country
            if not work_location or work_location == ', ':
                work_location = birth_location  # Use birth location if no work location

            # Get work coordinates
            work_coords = get_coords(work_city if work_city else work_country)
            if not work_coords:
                work_coords = birth_coords  # Use birth coords if work coords not found

            # Build laureate entry
            firstname = laureate.get('firstname', '')
            surname = laureate.get('surname', '')
            name = f"{firstname} {surname}".strip()

            # For organizations (no surname)
            if not surname:
                name = firstname

            entry = {
                'laureate_id': f"{cat_key}_{year}_{laureate_id}",
                'name': name,
                'birth_location': birth_location,
                'birth_lat': birth_coords[0],
                'birth_lon': birth_coords[1],
                'work_location': work_location,
                'work_lat': work_coords[0],
                'work_lon': work_coords[1],
                'work_years': f"{year-5}-{year}",  # Estimate work years
                'prize_year': year,
                'achievement': prize.get('motivation', '').strip('"'),
                'shared_with': []  # Will be filled in next step
            }

            category_data[cat_key].append(entry)

    # Fill in shared_with information
    print("Linking co-laureates...")
    for category in category_data:
        # Group by year to find co-laureates
        year_groups = {}
        for entry in category_data[category]:
            year = entry['prize_year']
            if year not in year_groups:
                year_groups[year] = []
            year_groups[year].append(entry)

        # For each year with multiple laureates, link them
        for year, laureates in year_groups.items():
            if len(laureates) > 1:
                for laureate in laureates:
                    co_laureates = [l['laureate_id'] for l in laureates if l['laureate_id'] != laureate['laureate_id']]
                    laureate['shared_with'] = co_laureates

    return category_data

def main():
    """Main function to fetch and process all Nobel Prize data"""
    print("=" * 60)
    print("Nobel Prize Data Fetcher")
    print("=" * 60)

    # Fetch all laureates
    all_laureates = fetch_all_laureates()

    # Process into category structure
    category_data = process_laureates_by_category(all_laureates)

    # Print statistics
    print("\n" + "=" * 60)
    print("Statistics:")
    print("=" * 60)
    for category, laureates in category_data.items():
        print(f"{category.capitalize():15} {len(laureates):4} laureates")
    total = sum(len(laureates) for laureates in category_data.values())
    print(f"{'Total':15} {total:4} laureates")

    # Save to file
    output_file = 'nobel_data_complete.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(category_data, f, indent=2, ensure_ascii=False)

    print(f"\nData saved to {output_file}")
    print("=" * 60)

if __name__ == '__main__':
    main()
