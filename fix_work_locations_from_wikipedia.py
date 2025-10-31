"""
Fix work locations by scraping Wikipedia for laureates where work_location == birth_location
This happens when the Nobel Prize API has incomplete affiliations data.
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

def get_wikipedia_url(name):
    """Get Wikipedia URL for a laureate by searching"""
    # Clean up name for URL
    name_clean = name.strip()

    # Try direct Wikipedia article
    url = f"https://en.wikipedia.org/wiki/{name_clean.replace(' ', '_')}"

    try:
        headers = {
            'User-Agent': 'NobelPrizeMapBot/1.0 (Educational visualization project; Python/requests)'
        }
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            return url
    except:
        pass

    # If direct URL doesn't work, search Wikipedia
    search_url = "https://en.wikipedia.org/w/api.php"
    params = {
        'action': 'opensearch',
        'search': name_clean,
        'limit': 1,
        'format': 'json'
    }

    try:
        headers = {
            'User-Agent': 'NobelPrizeMapBot/1.0 (Educational visualization project; Python/requests)'
        }
        time.sleep(0.5)  # Rate limiting
        response = requests.get(search_url, params=params, headers=headers, timeout=10)
        results = response.json()

        if len(results) > 3 and len(results[3]) > 0:
            return results[3][0]
    except Exception as e:
        print(f"  ⚠️  Wikipedia search error for {name}: {e}")

    return None

def extract_work_location_from_wikipedia(name, year):
    """
    Scrape Wikipedia to find work location/affiliation for a laureate
    Returns: (work_location_string, lat, lon) or (None, None, None)
    """
    wiki_url = get_wikipedia_url(name)
    if not wiki_url:
        print(f"  ❌ No Wikipedia page found for {name}")
        return None, None, None

    try:
        headers = {
            'User-Agent': 'NobelPrizeMapBot/1.0 (Educational visualization project; Python/requests)'
        }
        time.sleep(1)  # Rate limiting
        response = requests.get(wiki_url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # Look for infobox
        infobox = soup.find('table', class_='infobox')
        if not infobox:
            print(f"  ⚠️  No infobox found for {name}")
            return None, None, None

        # Try to find institution/workplace in infobox
        institution = None

        # Look for rows with institution-related labels
        for row in infobox.find_all('tr'):
            header = row.find('th')
            if not header:
                continue

            header_text = header.get_text().strip().lower()

            # Check for various institution/affiliation labels
            if any(keyword in header_text for keyword in [
                'institution', 'workplace', 'affiliation', 'known for',
                'doctoral advisor', 'academic advisor', 'employer'
            ]):
                value = row.find('td')
                if value:
                    # Extract text and clean it up
                    text = value.get_text().strip()

                    # Try to find university/institution names
                    # Look for patterns like "University of X", "X University", etc.
                    institution_patterns = [
                        r'University of ([^,\n\[]+)',
                        r'([^,\n\[]+) University',
                        r'([^,\n\[]+) Institute',
                        r'Institute of ([^,\n\[]+)',
                        r'([^,\n\[]+) College',
                        r'College of ([^,\n\[]+)',
                        r'([^,\n\[]+) Laboratory',
                        r'([^,\n\[]+) Research',
                    ]

                    for pattern in institution_patterns:
                        match = re.search(pattern, text, re.IGNORECASE)
                        if match:
                            if 'University of' in match.group(0) or 'Institute of' in match.group(0) or 'College of' in match.group(0):
                                institution = match.group(0)
                            else:
                                institution = match.group(1).strip()
                            break

                    if institution:
                        break

        if not institution:
            print(f"  ⚠️  No institution found in infobox for {name}")
            return None, None, None

        # Clean up the institution name
        # Remove references like [1], [2], etc.
        institution = re.sub(r'\[\d+\]', '', institution)

        # Remove date ranges like (1958–1960), (1878-82), etc.
        institution = re.sub(r'\s*\(\d{4}[–\-]?\d*\)', '', institution)

        # If we have concatenated universities (no separators), take just the first one
        # Split by "University" and take the first complete match
        if institution.count('University') > 1:
            # Find the first complete university name
            first_univ_match = re.search(r'(University of [^U]+?(?=University)|[^U]+? University)', institution)
            if first_univ_match:
                institution = first_univ_match.group(1).strip()

        institution = institution.strip()

        print(f"  ✓ Found institution: {institution}")

        # Geocode the institution
        coords = geocode_location(institution)

        # If geocoding failed, try with additional context
        if not coords:
            # Try some common patterns
            if 'University' in institution and 'of' in institution:
                # Extract location from "University of X" pattern
                match = re.search(r'University of ([\w\s]+)', institution)
                if match:
                    city = match.group(1).strip()
                    enhanced_query = f"{institution}, {city}"
                    print(f"  → Retrying with: {enhanced_query}")
                    coords = geocode_location(enhanced_query)

        if coords:
            print(f"  ✓ Geocoded to: {coords}")
            return institution, coords[0], coords[1]
        else:
            print(f"  ⚠️  Could not geocode: {institution}")
            return institution, None, None

    except Exception as e:
        print(f"  ❌ Error scraping Wikipedia for {name}: {e}")
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

        # Try to get work location from Wikipedia
        work_location, work_lat, work_lon = extract_work_location_from_wikipedia(name, year)

        if work_location and work_lat and work_lon:
            # Update the laureate data
            laureate['work_location'] = work_location
            laureate['work_lat'] = work_lat
            laureate['work_lon'] = work_lon

            print(f"  ✅ FIXED: {work_location} ({work_lat}, {work_lon})")
            fixed_count += 1
        elif work_location and not work_lat:
            print(f"  ⚠️  PARTIAL: Found institution '{work_location}' but couldn't geocode")
            skipped_count += 1
        else:
            print(f"  ❌ FAILED: Could not extract work location from Wikipedia")
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
    print("FIX WORK LOCATIONS FROM WIKIPEDIA")
    print("=" * 80)
    print(f"\nThis script will:")
    print("1. Find all laureates where work_location == birth_location")
    print("2. Scrape Wikipedia to find their actual work institutions")
    print("3. Geocode the corrected work locations")
    print("4. Update the data file")
    print("\nThis will take some time due to rate limiting...")
    print("\nStarting fix...\n")

    fixed, failed, skipped = fix_work_locations(data_file)

    print("\n✅ Done!")
