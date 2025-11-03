"""
Stage 3: Enrich from Wikipedia
Only processes laureates still marked as needing enrichment
"""
import json
import os

print("=" * 80)
print("Stage 3: Enrich from Wikipedia")
print("=" * 80)
print("\nThis stage is not yet implemented.")
print("It will scrape Wikipedia for missing affiliations.")
print("For now, proceeding to next stage...")
print("=" * 80)

# For now, just copy input to output
input_file = 'pipeline/data/02_enriched_nobelprize_org.json'
output_file = 'pipeline/data/03_enriched_wikipedia.json'

if os.path.exists(input_file):
    with open(input_file, 'r') as f:
        data = json.load(f)

    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"Passed data through to: {output_file}")
