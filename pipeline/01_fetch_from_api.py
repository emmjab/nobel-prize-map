"""
Stage 1: Fetch Nobel Prize data from API v2.1
Tracks which laureates have affiliation data from API vs need enrichment
"""
import requests
import json
import time
import sys
import os

def fetch_all_laureates():
    """Fetch all Nobel Prize laureates from the API v2.1 with pagination"""
    print("Fetching laureate data from Nobel Prize API v2.1...")

    all_laureates = []
    offset = 0
    limit = 25  # API default page size

    while True:
        url = f"https://api.nobelprize.org/2.1/laureates?offset={offset}&limit={limit}"

        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()

            laureates = data.get('laureates', [])
            if not laureates:
                break

            all_laureates.extend(laureates)

            print(f"  Fetched {len(all_laureates)} laureates so far...")

            # Check if there are more pages
            meta = data.get('meta', {})
            total = meta.get('count', 0)
            if len(all_laureates) >= total or len(laureates) < limit:
                break

            offset += limit
            time.sleep(0.5)  # Be nice to the API

        except Exception as e:
            print(f"  Error fetching laureates at offset {offset}: {e}")
            break

    print(f"Successfully fetched {len(all_laureates)} laureates")
    return all_laureates

def process_laureates_by_category(all_laureates):
    """
    Process laureates from v2.1 API and organize by category with location data
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
        'physiology or medicine': 'medicine',
        'literature': 'literature',
        'peace': 'peace',
        'economic sciences': 'economics'
    }

    print("\nProcessing laureates by category...")

    stats = {
        'total': 0,
        'has_affiliation': 0,
        'needs_enrichment': 0,
        'has_birth_coords': 0,
        'has_work_coords': 0
    }

    for laureate in all_laureates:
        laureate_api_id = laureate.get('id', '')

        if 'nobelPrizes' not in laureate:
            continue

        for prize in laureate['nobelPrizes']:
            # Get category
            category_obj = prize.get('category', {})
            category = category_obj.get('en', '') if isinstance(category_obj, dict) else ''
            category = category.lower()

            if category not in category_map:
                continue

            cat_key = category_map[category]
            year = int(prize.get('awardYear', 0))
            stats['total'] += 1

            # Get birth location from v2.1 structure
            birth_data = laureate.get('birth', {})
            birth_place = birth_data.get('place', {})

            birth_city = birth_place.get('city', {}).get('en', '') if isinstance(birth_place.get('city'), dict) else ''
            birth_country = birth_place.get('country', {}).get('en', '') if isinstance(birth_place.get('country'), dict) else ''
            birth_location = f"{birth_city}, {birth_country}" if birth_city else birth_country

            # Get birth coordinates from API (v2.1 includes coordinates!)
            birth_coords = (0, 0)
            city_now = birth_place.get('cityNow', {})
            if isinstance(city_now, dict):
                try:
                    lat = float(city_now.get('latitude', 0))
                    lon = float(city_now.get('longitude', 0))
                    if lat != 0 or lon != 0:
                        birth_coords = (lat, lon)
                        stats['has_birth_coords'] += 1
                except (ValueError, TypeError):
                    birth_coords = (0, 0)

            # Check if API has affiliation data
            has_affiliation_data = False
            work_location = ''
            work_coords = (0, 0)

            if 'affiliations' in prize and len(prize['affiliations']) > 0:
                aff = prize['affiliations'][0]
                if isinstance(aff, dict):
                    # Extract city and country
                    aff_name = aff.get('name', {}).get('en', '') if isinstance(aff.get('name'), dict) else ''
                    aff_city = aff.get('city', {}).get('en', '') if isinstance(aff.get('city'), dict) else ''
                    aff_country = aff.get('country', {}).get('en', '') if isinstance(aff.get('country'), dict) else ''

                    if aff_city or aff_country:
                        work_location = f"{aff_city}, {aff_country}" if aff_city else aff_country

                        # Get coordinates from API (v2.1 includes coordinates!)
                        city_now = aff.get('cityNow', {})
                        if isinstance(city_now, dict):
                            try:
                                lat = float(city_now.get('latitude', 0))
                                lon = float(city_now.get('longitude', 0))
                                if lat != 0 or lon != 0:
                                    work_coords = (lat, lon)
                                    has_affiliation_data = True
                                    stats['has_work_coords'] += 1
                            except (ValueError, TypeError):
                                work_coords = (0, 0)

            # Determine if we need enrichment
            if has_affiliation_data:
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
            full_name = laureate.get('fullName', {})
            if isinstance(full_name, dict):
                name = full_name.get('en', '')
            else:
                name = full_name or laureate.get('knownName', {}).get('en', '')

            # Get motivation
            motivation_obj = prize.get('motivation', {})
            if isinstance(motivation_obj, dict):
                motivation = motivation_obj.get('en', '').strip('"')
            else:
                motivation = str(motivation_obj).strip('"')

            entry = {
                'laureate_id': f"{cat_key}_{year}_{laureate_api_id}",
                'name': name,
                'birth_location': birth_location,
                'birth_lat': birth_coords[0],
                'birth_lon': birth_coords[1],
                'work_location': work_location,
                'work_lat': work_coords[0],
                'work_lon': work_coords[1],
                'work_years': f"{year-5}-{year}",
                'prize_year': year,
                'achievement': motivation,
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
    print("Data Source Statistics (v2.1 API):")
    print("=" * 60)
    print(f"Total laureates: {stats['total']}")
    print(f"Has birth coordinates from API: {stats['has_birth_coords']} ({stats['has_birth_coords']/stats['total']*100:.1f}%)")
    print(f"Has work affiliation from API: {stats['has_affiliation']} ({stats['has_affiliation']/stats['total']*100:.1f}%)")
    print(f"Has work coordinates from API: {stats['has_work_coords']} ({stats['has_work_coords']/stats['total']*100:.1f}%)")
    print(f"Needs enrichment: {stats['needs_enrichment']} ({stats['needs_enrichment']/stats['total']*100:.1f}%)")
    print("=" * 60)

    return category_data

def main():
    """Main function to fetch and process all Nobel Prize data from v2.1 API"""
    print("=" * 60)
    print("Stage 1: Fetch Nobel Prize Data from API v2.1")
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
