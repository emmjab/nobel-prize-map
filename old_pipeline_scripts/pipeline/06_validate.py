"""
Stage 6: Validate data and generate manual review list
Final validation and output generation
"""
import json
import os

def load_data(filepath):
    """Load Nobel Prize data from JSON file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_data(data, filepath):
    """Save Nobel Prize data to JSON file"""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def validate_and_categorize(data):
    """
    Validate data quality and categorize laureates
    """
    categories = {
        'complete': [],  # Has good work location data
        'needs_manual_review': [],  # Couldn't be enriched automatically
        'suspicious': [],  # Has data but might be wrong
    }

    stats = {
        'total': 0,
        'from_api': 0,
        'from_nobelprize_org': 0,
        'from_wikipedia': 0,
        'from_manual': 0,
        'still_birth_fallback': 0,
        'geocoding_failed': 0,
    }

    for category, laureates in data.items():
        for laureate in laureates:
            stats['total'] += 1

            # Track data source
            source = laureate.get('data_source', 'unknown')
            if source == 'api':
                stats['from_api'] += 1
            elif source == 'nobelprize_org':
                stats['from_nobelprize_org'] += 1
            elif source == 'wikipedia':
                stats['from_wikipedia'] += 1
            elif source == 'manual':
                stats['from_manual'] += 1
            elif source == 'birth_fallback':
                stats['still_birth_fallback'] += 1

            # Check for geocoding failures (coordinates at 0,0)
            if laureate['work_lat'] == 0 and laureate['work_lon'] == 0:
                stats['geocoding_failed'] += 1

            # Categorize laureate
            if source == 'birth_fallback':
                # Still using birth location - definitely needs manual review
                categories['needs_manual_review'].append({
                    'laureate_id': laureate['laureate_id'],
                    'name': laureate['name'],
                    'category': category,
                    'prize_year': laureate['prize_year'],
                    'birth_location': laureate['birth_location'],
                    'current_work_location': laureate['work_location'],
                    'issue': 'No affiliation data from any source',
                    'enrichment_attempts': laureate.get('enrichment_attempts', []),
                })
            elif laureate['work_lat'] == 0 and laureate['work_lon'] == 0:
                # Has location text but failed geocoding
                categories['suspicious'].append({
                    'laureate_id': laureate['laureate_id'],
                    'name': laureate['name'],
                    'category': category,
                    'prize_year': laureate['prize_year'],
                    'work_location': laureate['work_location'],
                    'issue': 'Geocoding failed (coordinates are 0,0)',
                    'data_source': source,
                })
            elif source in ['api', 'nobelprize_org', 'wikipedia', 'manual']:
                # Has enriched data - looks good
                categories['complete'].append({
                    'laureate_id': laureate['laureate_id'],
                    'name': laureate['name'],
                    'data_source': source,
                })

    return categories, stats

def generate_manual_review_csv(needs_review):
    """Generate a CSV file for easy manual review"""
    csv_path = 'pipeline/data/needs_manual_review.csv'

    with open(csv_path, 'w', encoding='utf-8') as f:
        # Header - simplified to only require work_location
        f.write('laureate_id,name,category,year,birth_location,issue,enrichment_attempts,work_location_manual,notes\n')

        # Rows
        for laureate in needs_review:
            attempts = '; '.join(laureate.get('enrichment_attempts', []))
            f.write(f'"{laureate["laureate_id"]}",')
            f.write(f'"{laureate["name"]}",')
            f.write(f'"{laureate["category"]}",')
            f.write(f'{laureate["prize_year"]},')
            f.write(f'"{laureate["birth_location"]}",')
            f.write(f'"{laureate["issue"]}",')
            f.write(f'"{attempts}",')
            f.write(',\n')  # Empty columns for manual filling (work_location, notes)

    return csv_path

def main():
    """Main validation function"""
    print("=" * 80)
    print("Stage 6: Validate Data")
    print("=" * 80)

    # Load data from previous stage
    input_file = 'pipeline/data/05_with_manual_overrides.json'
    if not os.path.exists(input_file):
        print(f"⚠️  {input_file} not found, trying stage 4 output...")
        input_file = 'pipeline/data/04_fixed_geocoding.json'
        if not os.path.exists(input_file):
            print(f"❌ No input data found!")
            return

    print(f"Loading data from: {input_file}")
    data = load_data(input_file)

    print("\nValidating and categorizing data...")
    categories, stats = validate_and_categorize(data)

    # Print statistics
    print("\n" + "=" * 80)
    print("Data Quality Statistics")
    print("=" * 80)
    print(f"Total laureates: {stats['total']}")
    print(f"\nData sources:")
    print(f"  From API: {stats['from_api']} ({stats['from_api']/stats['total']*100:.1f}%)")
    print(f"  From NobelPrize.org: {stats['from_nobelprize_org']} ({stats['from_nobelprize_org']/stats['total']*100:.1f}%)")
    print(f"  From Wikipedia: {stats['from_wikipedia']} ({stats['from_wikipedia']/stats['total']*100:.1f}%)")
    print(f"  From manual overrides: {stats['from_manual']} ({stats['from_manual']/stats['total']*100:.1f}%)")
    print(f"  Still using birth fallback: {stats['still_birth_fallback']} ({stats['still_birth_fallback']/stats['total']*100:.1f}%)")
    print(f"\nIssues:")
    print(f"  Geocoding failed: {stats['geocoding_failed']}")
    print(f"\nCategories:")
    print(f"  Complete: {len(categories['complete'])} ({len(categories['complete'])/stats['total']*100:.1f}%)")
    print(f"  Needs manual review: {len(categories['needs_manual_review'])} ({len(categories['needs_manual_review'])/stats['total']*100:.1f}%)")
    print(f"  Suspicious: {len(categories['suspicious'])} ({len(categories['suspicious'])/stats['total']*100:.1f}%)")
    print("=" * 80)

    # Save final complete data
    final_output = '../nobel_data_complete.json'
    with open(final_output, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"\n✅ Final data saved to: {final_output}")

    # Save needs manual review list (JSON)
    if categories['needs_manual_review']:
        review_json = 'pipeline/data/needs_manual_review.json'
        save_data(categories['needs_manual_review'], review_json)
        print(f"⚠️  Manual review list saved to: {review_json}")

        # Also generate CSV for easy editing
        csv_path = generate_manual_review_csv(categories['needs_manual_review'])
        print(f"⚠️  Manual review CSV saved to: {csv_path}")

        print(f"\n{len(categories['needs_manual_review'])} laureates need manual review:")
        print("=" * 80)
        for i, laureate in enumerate(categories['needs_manual_review'][:10], 1):
            print(f"{i}. {laureate['name']} ({laureate['prize_year']} {laureate['category'].title()})")
            print(f"   Issue: {laureate['issue']}")
            if laureate.get('enrichment_attempts'):
                print(f"   Tried: {', '.join(laureate['enrichment_attempts'])}")
        if len(categories['needs_manual_review']) > 10:
            print(f"   ... and {len(categories['needs_manual_review']) - 10} more")
        print("=" * 80)

    # Save suspicious list
    if categories['suspicious']:
        suspicious_json = 'pipeline/data/suspicious_entries.json'
        save_data(categories['suspicious'], suspicious_json)
        print(f"⚠️  Suspicious entries saved to: {suspicious_json}")

    print("\n" + "=" * 80)
    print("Validation Complete")
    print("=" * 80)

if __name__ == '__main__':
    main()
