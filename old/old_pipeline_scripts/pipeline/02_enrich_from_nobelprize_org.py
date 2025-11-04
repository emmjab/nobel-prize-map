"""
Stage 2: Enrich missing affiliations from NobelPrize.org
Only processes laureates marked as needing enrichment
"""
import json
import os
import sys

# This will use logic from the existing fix_from_nobelprize_website.py
# but only process laureates where needs_enrichment == True

print("=" * 80)
print("Stage 2: Enrich from NobelPrize.org")
print("=" * 80)
print("\nThis stage is not yet implemented.")
print("It will scrape nobelprize.org for missing affiliations.")
print("For now, proceeding to next stage...")
print("=" * 80)

# For now, just copy input to output
input_file = 'pipeline/data/01_raw_from_api.json'
output_file = 'pipeline/data/02_enriched_nobelprize_org.json'

if os.path.exists(input_file):
    with open(input_file, 'r') as f:
        data = json.load(f)

    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"Passed data through to: {output_file}")
