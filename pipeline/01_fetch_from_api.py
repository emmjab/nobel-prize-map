"""
Stage 1: Fetch Nobel Prize data from API
Tracks which laureates have affiliation data from API vs need enrichment
"""
import requests
import json
import time
import sys
import os

# Add parent directory to path to import wiki_scraper
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from wiki_scraper import get_coords

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
    """
    Process laureates and organize by category with location data
    IMPORTANT: Tracks whether affiliation data came from API or is missing
    """

    category_data = {
        'physics': [],
        'chemistry': [],
        'medicine': [],
        'literature': [],
        'peace': [],
        'economics': []
    }

    category_map = {
        'physics': 'physics',
        'chemistry': 'chemistry',
        'medicine': 'medicine',
        'literature': 'literature',
        'peace': 'peace',
        'economics': 'economics'
    }

    print("\nProcessing laureates by category...")

    stats = {
        'total': 0,
        'has_affiliation': 0,
        'needs_enrichment': 0
    }

    for laureate_id, laureate in all_laureates.items():
        if 'prizes' not in laureate:
            continue

        for prize in laureate['prizes']:
            category = prize.get('category')
            if category not in category_map:
                continue

            cat_key = category_map[category]
            year = int(prize['year'])
            stats['total'] += 1

            # Get birth location
            birth_city = laureate.get('bornCity', '')
            birth_country = laureate.get('bornCountry', '')
            birth_location = f"{birth_city}, {birth_country}" if birth_city else birth_country

            # Get birth coordinates
            birth_coords = get_coords(birth_city if birth_city else birth_country)
            if not birth_coords:
                birth_coords = (0, 0)  # Default if not found

            # Check if API has affiliation data
            has_affiliation_data = False
            work_city = ''
            work_country = ''

            if 'affiliations' in prize and len(prize['affiliations']) > 0:
                aff = prize['affiliations'][0]
                if isinstance(aff, dict):
                    work_city = aff.get('city', '')
                    work_country = aff.get('country', '')
                    if work_city or work_country:
                        has_affiliation_data = True

            # Determine work location and whether we need enrichment
            if has_affiliation_data:
                work_location = f"{work_city}, {work_country}" if work_city else work_country
                work_coords = get_coords(work_city if work_city else work_country)
                if not work_coords:
                    # Don't copy birth coords - use (0,0) to flag for re-geocoding
                    # This prevents silent data corruption where location text is correct but coords are wrong
                    work_coords = (0, 0)
                needs_enrichment = False
                data_source = 'api'
                stats['has_affiliation'] += 1
            else:
                # No affiliation data from API - use birth location as placeholder
                work_location = birth_location
                work_coords = birth_coords
                needs_enrichment = True
                data_source = 'birth_fallback'
                stats['needs_enrichment'] += 1

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
                'work_years': f"{year-5}-{year}",
                'prize_year': year,
                'achievement': prize.get('motivation', '').strip('"'),
                'shared_with': [],
                # Metadata about data source
                'data_source': data_source,  # 'api', 'birth_fallback', 'nobelprize_org', 'wikipedia', 'manual'
                'needs_enrichment': needs_enrichment,
                'enrichment_attempts': []  # Track what we tried
            }

            category_data[cat_key].append(entry)

    # Fill in shared_with information
    print("Linking co-laureates...")
    for category in category_data:
        year_groups = {}
        for entry in category_data[category]:
            year = entry['prize_year']
            if year not in year_groups:
                year_groups[year] = []
            year_groups[year].append(entry)

        for year, laureates in year_groups.items():
            if len(laureates) > 1:
                for laureate in laureates:
                    co_laureates = [l['laureate_id'] for l in laureates if l['laureate_id'] != laureate['laureate_id']]
                    laureate['shared_with'] = co_laureates

    # Print statistics
    print("\n" + "=" * 60)
    print("Data Source Statistics:")
    print("=" * 60)
    print(f"Total laureates: {stats['total']}")
    print(f"Has affiliation from API: {stats['has_affiliation']} ({stats['has_affiliation']/stats['total']*100:.1f}%)")
    print(f"Needs enrichment: {stats['needs_enrichment']} ({stats['needs_enrichment']/stats['total']*100:.1f}%)")
    print("=" * 60)

    return category_data

def main():
    """Main function to fetch and process all Nobel Prize data"""
    print("=" * 60)
    print("Stage 1: Fetch Nobel Prize Data from API")
    print("=" * 60)

    # Fetch all laureates
    all_laureates = fetch_all_laureates()

    # Process into category structure
    category_data = process_laureates_by_category(all_laureates)

    # Print category statistics
    print("\nCategory Statistics:")
    print("=" * 60)
    for category, laureates in category_data.items():
        needs_enrich = sum(1 for l in laureates if l['needs_enrichment'])
        print(f"{category.capitalize():15} {len(laureates):4} laureates ({needs_enrich} need enrichment)")
    total = sum(len(laureates) for laureates in category_data.values())
    total_needs_enrich = sum(sum(1 for l in laureates if l['needs_enrichment']) for laureates in category_data.values())
    print(f"{'Total':15} {total:4} laureates ({total_needs_enrich} need enrichment)")
    print("=" * 60)

    # Save to file
    output_file = 'pipeline/data/01_raw_from_api.json'
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(category_data, f, indent=2, ensure_ascii=False)

    print(f"\nData saved to {output_file}")
    print("=" * 60)

if __name__ == '__main__':
    main()
