"""
Test the fix script on just 10 laureates to validate the full process
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
    name_clean = name.strip()
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

        for row in infobox.find_all('tr'):
            header = row.find('th')
            if not header:
                continue

            header_text = header.get_text().strip().lower()

            if any(keyword in header_text for keyword in [
                'institution', 'workplace', 'affiliation'
            ]):
                value = row.find('td')
                if value:
                    text = value.get_text().strip()

                    # Try to extract institution name
                    institution_patterns = [
                        r'University of ([^,\n\[]+)',
                        r'([^,\n\[]+) University',
                        r'([^,\n\[]+) Institute',
                        r'Institute of ([^,\n\[]+)',
                        r'([^,\n\[]+) College',
                        r'College of ([^,\n\[]+)',
                        r'([^,\n\[]+) Laboratory',
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
        institution = re.sub(r'\[\d+\]', '', institution)

        # Remove date ranges like (1958–1960), (1878-82), etc.
        institution = re.sub(r'\s*\(\d{4}[–\-]?\d*\)', '', institution)

        # If we have concatenated universities (no separators), take just the first one
        if institution.count('University') > 1:
            first_univ_match = re.search(r'(University of [^U]+?(?=University)|[^U]+? University)', institution)
            if first_univ_match:
                institution = first_univ_match.group(1).strip()

        institution = institution.strip()

        print(f"  ✓ Found institution: {institution}")

        # Geocode the institution
        coords = geocode_location(institution)
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
            if (laureate['work_location'] == laureate['birth_location'] and
                laureate['work_lat'] == laureate['birth_lat'] and
                laureate['work_lon'] == laureate['birth_lon']):

                problematic.append({
                    'category': category,
                    'laureate': laureate
                })

    return problematic

# Main test
print("=" * 80)
print("TEST: Fix work locations from Wikipedia (first 10 laureates)")
print("=" * 80)

data = load_data('nobel_data_complete.json')
problematic = identify_problematic_laureates(data)

print(f"\nTotal problematic laureates: {len(problematic)}")
print(f"Testing on first 10...\n")

fixed = 0
failed = 0
skipped = 0

for i, item in enumerate(problematic[:10], 1):
    name = item['laureate']['name']
    year = item['laureate']['prize_year']
    category = item['category']

    print(f"\n[{i}/10] {name} ({year} {category.title()})")
    print(f"  Current location: {item['laureate']['work_location']}")

    work_location, work_lat, work_lon = extract_work_location_from_wikipedia(name, year)

    if work_location and work_lat and work_lon:
        print(f"  ✅ SUCCESS: {work_location} ({work_lat}, {work_lon})")
        fixed += 1
    elif work_location:
        print(f"  ⚠️  PARTIAL: Found '{work_location}' but couldn't geocode")
        skipped += 1
    else:
        print(f"  ❌ FAILED")
        failed += 1

print("\n" + "=" * 80)
print("SUMMARY:")
print(f"  Fixed: {fixed}")
print(f"  Failed: {failed}")
print(f"  Skipped: {skipped}")
print(f"  Success rate: {fixed}/{10} ({100*fixed/10:.0f}%)")
