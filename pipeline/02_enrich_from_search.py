"""
Stage 2: Enrich from Web Search
Uses web search to find work locations for laureates with missing data
"""
import json
import os
import time

def load_data(filepath):
    """Load Nobel Prize data from JSON file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_data(data, filepath):
    """Save Nobel Prize data to JSON file"""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def search_for_work_location(name, category, year):
    """
    Search for laureate's work location using web search
    Returns the location string if found, None otherwise
    """
    # Import here to avoid issues if running outside Claude Code
    try:
        # This will only work when run through Claude Code's WebSearch tool
        # For standalone execution, this would need to use an actual search API
        print(f"  Searching for work location...")
        query = f"where did {name} do his nobel prize winning work {category} {year}"

        # NOTE: This is a placeholder - the actual search would be done
        # by calling this script through Claude Code which has WebSearch capability
        # Or by integrating with a search API like SerpAPI, Google Custom Search, etc.

        return None  # Placeholder for now
    except Exception as e:
        print(f"  ⚠️  Search error: {e}")
        return None

def enrich_from_search(data, max_searches=None):
    """
    Enrich laureates with missing work locations using web search

    Args:
        data: Nobel Prize data dict
        max_searches: Maximum number of searches to perform (None for unlimited)
    """
    enriched_count = 0
    searches_performed = 0

    for category, laureates in data.items():
        for laureate in laureates:
            # Only search for laureates that need enrichment
            if not laureate.get('needs_enrichment', False):
                continue

            # Check if we've hit the search limit
            if max_searches and searches_performed >= max_searches:
                print(f"\nReached search limit ({max_searches})")
                return enriched_count

            laureate_id = laureate['laureate_id']
            name = laureate['name']
            prize_year = laureate['prize_year']

            print(f"\n{laureate_id}: {name} ({prize_year} {category.title()})")

            # Search for work location
            work_location = search_for_work_location(name, category, prize_year)

            if work_location:
                print(f"  ✅ Found: {work_location}")
                laureate['work_location'] = work_location
                laureate['data_source'] = 'web_search'
                laureate['needs_enrichment'] = False
                laureate.setdefault('enrichment_attempts', []).append('web_search')
                enriched_count += 1
            else:
                print(f"  ❌ No location found")
                laureate.setdefault('enrichment_attempts', []).append('web_search')

            searches_performed += 1

            # Rate limiting - be nice to search engines
            time.sleep(2)

    return enriched_count

def main():
    """Main enrichment function"""
    print("=" * 80)
    print("Stage 2: Enrich from Web Search")
    print("=" * 80)

    # Load data from previous stage
    input_file = 'pipeline/data/01_raw_from_api.json'
    print(f"Loading data from: {input_file}")
    data = load_data(input_file)

    # Count how many need enrichment
    needs_enrichment = sum(
        1 for cat_laureates in data.values()
        for l in cat_laureates
        if l.get('needs_enrichment', False)
    )
    print(f"\nFound {needs_enrichment} laureates needing enrichment")

    print("\n⚠️  NOTE: This stage requires web search capability.")
    print("   It should be run through Claude Code or integrated with a search API.")
    print("   For now, this is a placeholder stage.\n")

    # For testing, you could set max_searches to a small number like 5
    # enriched_count = enrich_from_search(data, max_searches=5)

    enriched_count = 0  # Placeholder

    print(f"\n✅ Enriched {enriched_count} laureate(s) from web search")

    # Save output
    output_file = 'pipeline/data/02_enriched_from_search.json'
    save_data(data, output_file)
    print(f"\nData saved to: {output_file}")
    print("=" * 80)

if __name__ == '__main__':
    main()
