"""
Fix work locations by scraping Nobel Prize official website
The website has "Affiliation at the time of the award" data that's missing from the API
URL pattern: https://www.nobelprize.org/prizes/{category}/{year}/{surname}/facts/
"""

import json
import requests
from bs4 import BeautifulSoup
import time
import re

def load_data(filepath):
    """Load the Nobel Prize data from JSON file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_data(data, filepath):
    """Save the Nobel Prize data to JSON file"""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

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
            print(f"  ⚠️  No geocoding results for: {location_string}")
            return None
    except Exception as e:
        print(f"  ❌ Geocoding error for '{location_string}': {e}")
        return None

def extract_surname(full_name):
    """
    Extract surname from full name for URL construction
    Examples:
    - "Henri Becquerel" -> "becquerel"
    - "Marie Curie" -> "curie"
    - "Jean-Paul Sartre" -> "sartre"
    - "Martin Luther King Jr." -> "king"
    """
    # Remove titles and suffixes
    name = re.sub(r'\b(Jr\.?|Sr\.?|Dr\.?|Prof\.?|Sir|Lord|Lady|III|IV|II)\b', '', full_name, flags=re.IGNORECASE)

    # Split by whitespace and filter empty strings
    parts = [p for p in name.strip().split() if p]

    if not parts:
        return None

    # Last part is usually the surname
    surname = parts[-1].lower()

    # Remove any remaining punctuation
    surname = re.sub(r'[^\w-]', '', surname)

    return surname if surname else None

def get_affiliation_from_nobelprize_org(name, category, year):
    """
    Scrape affiliation from nobelprize.org/prizes/{category}/{year}/{surname}/facts/
    Returns: (affiliation_string, lat, lon) or (None, None, None)
    """
    surname = extract_surname(name)
    if not surname:
        print(f"  ❌ Could not extract surname from: {name}")
        return None, None, None

    # Construct URL
    url = f"https://www.nobelprize.org/prizes/{category}/{year}/{surname}/facts/"

    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        time.sleep(1)  # Rate limiting
        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code != 200:
            print(f"  ⚠️  Page not found: {url} (status {response.status_code})")
            return None, None, None

        soup = BeautifulSoup(response.text, 'html.parser')

        # Find "Affiliation at the time of the award:" text
        page_text = soup.get_text()

        # Look for the affiliation pattern
        match = re.search(r'Affiliation at the time of the award:\s*([^\n]+)', page_text, re.IGNORECASE)

        if not match:
            print(f"  ⚠️  No affiliation found on page")
            return None, None, None

        affiliation = match.group(1).strip()

        # Clean up the affiliation
        affiliation = re.sub(r'\s+', ' ', affiliation)  # Normalize whitespace
        affiliation = affiliation.strip()

        if not affiliation or affiliation == '-':
            print(f"  ⚠️  Empty affiliation")
            return None, None, None

        print(f"  ✓ Found affiliation: {affiliation}")

        # Geocode the affiliation
        coords = geocode_location(affiliation)
        if coords:
            print(f"  ✓ Geocoded to: {coords}")
            return affiliation, coords[0], coords[1]
        else:
            print(f"  ⚠️  Could not geocode: {affiliation}")
            return affiliation, None, None

    except Exception as e:
        print(f"  ❌ Error scraping Nobel Prize website for {name}: {e}")
        return None, None, None

def identify_problematic_laureates(data):
    """Find all laureates where work_location == birth_location"""
    problematic = []

    for category, laureates in data.items():
        for laureate in laureates:
            # Check if work location equals birth location
            if (laureate['work_location'] == laureate['birth_location'] and
                laureate['work_lat'] == laureate['birth_lat'] and
                laureate['work_lon'] == laureate['birth_lon']):

                problematic.append({
                    'category': category,
                    'laureate': laureate
                })

    return problematic

def fix_work_locations(data_file):
    """Main function to fix work locations"""
    print("Loading data...")
    data = load_data(data_file)

    print("\nIdentifying problematic laureates...")
    problematic = identify_problematic_laureates(data)

    print(f"\nFound {len(problematic)} laureates with work_location == birth_location")
    print("=" * 80)

    fixed_count = 0
    failed_count = 0
    skipped_count = 0

    for i, item in enumerate(problematic, 1):
        category = item['category']
        laureate = item['laureate']
        name = laureate['name']
        year = laureate['prize_year']

        print(f"\n[{i}/{len(problematic)}] {name} ({year} {category.title()})")
        print(f"  Current location: {laureate['work_location']}")

        # Try to get affiliation from nobelprize.org
        work_location, work_lat, work_lon = get_affiliation_from_nobelprize_org(name, category, year)

        if work_location and work_lat and work_lon:
            # Update the laureate data
            laureate['work_location'] = work_location
            laureate['work_lat'] = work_lat
            laureate['work_lon'] = work_lon

            print(f"  ✅ FIXED: {work_location} ({work_lat}, {work_lon})")
            fixed_count += 1
        elif work_location and not work_lat:
            print(f"  ⚠️  PARTIAL: Found affiliation '{work_location}' but couldn't geocode")
            skipped_count += 1
        else:
            print(f"  ❌ FAILED: Could not extract affiliation from Nobel Prize website")
            failed_count += 1

        # Save progress every 10 laureates
        if (i % 10 == 0):
            print(f"\n--- Saving progress ({fixed_count} fixed so far) ---")
            save_data(data, data_file)

    # Final save
    print("\n" + "=" * 80)
    print("Saving final results...")
    save_data(data, data_file)

    print("\n✅ SUMMARY:")
    print(f"   Fixed: {fixed_count}")
    print(f"   Failed: {failed_count}")
    print(f"   Skipped (partial): {skipped_count}")
    print(f"   Total processed: {len(problematic)}")

    return fixed_count, failed_count, skipped_count

if __name__ == '__main__':
    import sys

    data_file = 'nobel_data_complete.json'

    print("=" * 80)
    print("FIX WORK LOCATIONS FROM NOBELPRIZE.ORG WEBSITE")
    print("=" * 80)
    print(f"\nThis script will:")
    print("1. Find all laureates where work_location == birth_location")
    print("2. Scrape nobelprize.org for 'Affiliation at the time of the award'")
    print("3. Geocode the corrected work locations")
    print("4. Update the data file")
    print("\nThis will take some time due to rate limiting...")
    print("\nStarting fix...\n")

    fixed, failed, skipped = fix_work_locations(data_file)

    print("\n✅ Done!")
