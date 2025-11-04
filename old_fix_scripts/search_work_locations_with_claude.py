#!/usr/bin/env python3
"""
Search for Nobel laureate work locations using Claude API
Processes laureates that need manual review and finds their work locations
"""

import json
import os
import time
from anthropic import Anthropic

def load_json(filepath):
    """Load JSON file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json(data, filepath):
    """Save JSON file"""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def search_work_location_with_claude(client, name, category, year):
    """
    Use Claude to search for and extract work location
    Returns dict with work_location, confidence, and source
    """
    prompt = f"""Please search for where {name} did their Nobel Prize-winning work in {category} ({year}).

I need you to find the specific institution or city where they conducted the work that earned them the Nobel Prize.

For scientists: Find their university/lab affiliation at the time of the prize
For literature laureates: Their primary residence or where they wrote their major works
For peace laureates: The organization/location of their peace work

Please provide:
1. work_location: The specific institution and/or city (e.g., "MIT, Cambridge, MA, USA" or "University of Paris, France")
2. confidence: high, medium, or low
3. source: Brief note about what you found (1-2 sentences)

Format your response as JSON:
{{
  "work_location": "Institution/City, Country",
  "confidence": "high/medium/low",
  "source": "Brief explanation"
}}

If you cannot find reliable information, return:
{{
  "work_location": null,
  "confidence": "low",
  "source": "Could not find reliable information"
}}"""

    try:
        message = client.messages.create(
            model="claude-3-5-haiku-20241022",  # Using Haiku for cost-effectiveness
            max_tokens=500,
            messages=[{
                "role": "user",
                "content": prompt
            }]
        )

        response_text = message.content[0].text

        # Extract JSON from response (it might have markdown code blocks)
        if "```json" in response_text:
            start = response_text.find("```json") + 7
            end = response_text.find("```", start)
            json_text = response_text[start:end].strip()
        elif "```" in response_text:
            start = response_text.find("```") + 3
            end = response_text.find("```", start)
            json_text = response_text[start:end].strip()
        else:
            json_text = response_text.strip()

        result = json.loads(json_text)
        return result

    except Exception as e:
        print(f"  ⚠️  Error with Claude API: {e}")
        return {
            "work_location": None,
            "confidence": "low",
            "source": f"Error: {str(e)}"
        }

def main():
    """Main function"""
    print("=" * 80)
    print("Search Work Locations Using Claude API")
    print("=" * 80)

    # Check for API key
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("\n❌ Error: ANTHROPIC_API_KEY environment variable not set")
        print("\nPlease set your API key:")
        print("  export ANTHROPIC_API_KEY='your-api-key-here'")
        print("\nOr add it to your ~/.bashrc or ~/.zshrc")
        return

    # Initialize Anthropic client
    client = Anthropic(api_key=api_key)

    # Load laureates needing review
    needs_review_file = 'pipeline/data/needs_manual_review.json'
    print(f"\nLoading laureates from: {needs_review_file}")
    laureates = load_json(needs_review_file)
    print(f"Found {len(laureates)} laureates needing review")

    # Load existing results
    results_file = 'pipeline/data/search_results_work_locations.json'
    if os.path.exists(results_file):
        print(f"Loading existing results from: {results_file}")
        results = load_json(results_file)
        print(f"Already processed: {len(results)} laureates")
    else:
        results = {}
        print("Starting fresh - no existing results found")

    # Process each laureate
    total = len(laureates)
    skipped = 0
    processed = 0
    failed = 0

    print(f"\n{'=' * 80}")
    print("Processing laureates...")
    print(f"{'=' * 80}\n")

    for i, laureate in enumerate(laureates, 1):
        laureate_id = laureate['laureate_id']
        name = laureate['name']
        category = laureate['category']
        year = laureate['prize_year']

        # Skip if already processed
        if laureate_id in results:
            skipped += 1
            continue

        print(f"[{i}/{total}] {name} ({year} {category})")

        # Search using Claude
        result = search_work_location_with_claude(client, name, category, year)

        # Add to results
        results[laureate_id] = {
            "name": name,
            "work_location": result.get("work_location"),
            "confidence": result.get("confidence", "low"),
            "source": result.get("source", "")
        }

        # Print result
        if result.get("work_location"):
            print(f"  ✅ {result['work_location']} (confidence: {result['confidence']})")
            processed += 1
        else:
            print(f"  ❌ Not found")
            failed += 1

        # Save results after each laureate (to avoid losing progress)
        save_json(results, results_file)

        # Rate limiting - be nice to the API
        time.sleep(1)

        # Progress update every 10 laureates
        if i % 10 == 0:
            print(f"\n--- Progress: {len(results)}/{total} ({len(results)/total*100:.1f}%) ---\n")

    # Final summary
    print(f"\n{'=' * 80}")
    print("Summary")
    print(f"{'=' * 80}")
    print(f"Total laureates: {total}")
    print(f"Already processed (skipped): {skipped}")
    print(f"Newly processed: {processed}")
    print(f"Failed to find: {failed}")
    print(f"Total in results file: {len(results)}")
    print(f"\nResults saved to: {results_file}")
    print(f"{'=' * 80}")

if __name__ == '__main__':
    main()
