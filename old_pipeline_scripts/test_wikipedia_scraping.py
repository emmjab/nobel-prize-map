"""
Test Wikipedia scraping on a few specific laureates to validate the approach
"""

import json
import requests
from bs4 import BeautifulSoup
import time
import re

def test_laureate(name, expected_location=None):
    """Test Wikipedia scraping for a specific laureate"""
    print(f"\n{'='*80}")
    print(f"Testing: {name}")
    print(f"Expected: {expected_location}" if expected_location else "")
    print(f"{'='*80}")

    # Get Wikipedia URL
    wiki_url = f"https://en.wikipedia.org/wiki/{name.replace(' ', '_')}"
    print(f"URL: {wiki_url}")

    try:
        headers = {
            'User-Agent': 'NobelPrizeMapBot/1.0 (Educational visualization project; Python/requests)'
        }
        response = requests.get(wiki_url, headers=headers, timeout=10)
        if response.status_code != 200:
            print(f"❌ Failed to fetch page (status {response.status_code})")
            return

        soup = BeautifulSoup(response.text, 'html.parser')

        # Find infobox
        infobox = soup.find('table', class_='infobox')
        if not infobox:
            print("❌ No infobox found")
            return

        print("\n📋 Infobox contents:")
        print("-" * 80)

        # Print all rows to see what's available
        for row in infobox.find_all('tr'):
            header = row.find('th')
            value = row.find('td')

            if header and value:
                header_text = header.get_text().strip()
                value_text = value.get_text().strip()

                # Clean up the text
                value_text = re.sub(r'\[\d+\]', '', value_text)  # Remove references
                value_text = ' '.join(value_text.split())  # Normalize whitespace

                print(f"{header_text:30} : {value_text[:100]}")

        print("-" * 80)

        # Now try to extract institution
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
                    text = re.sub(r'\[\d+\]', '', text)

                    print(f"\n✅ Found institution field: '{header_text}'")
                    print(f"   Raw value: {text[:200]}")

                    # Try to extract institution name
                    institution_patterns = [
                        r'University of ([^,\n\[]+)',
                        r'([^,\n\[]+) University',
                        r'([^,\n\[]+) Institute',
                        r'Institute of ([^,\n\[]+)',
                        r'([^,\n\[]+) College',
                    ]

                    for pattern in institution_patterns:
                        match = re.search(pattern, text, re.IGNORECASE)
                        if match:
                            institution = match.group(0)
                            print(f"   Extracted: {institution}")
                            break

    except Exception as e:
        print(f"❌ Error: {e}")

# Test on some known cases
print("Testing Wikipedia scraping on sample laureates")
print("This will help us validate the extraction logic\n")

# Marie Curie - should find University of Paris / Sorbonne
test_laureate("Marie_Curie", "University of Paris / Sorbonne")

# Albert Einstein - should find various institutions
test_laureate("Albert_Einstein", "University of Berlin / ETH Zurich")

# Thomas R. Cech - should find University of Colorado Boulder
test_laureate("Thomas_Cech", "University of Colorado Boulder")

print("\n" + "="*80)
print("✅ Test complete!")
print("\nIf the extraction looks good, we can proceed with the full fix script.")
