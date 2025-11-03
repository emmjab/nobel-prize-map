#!/usr/bin/env python3
"""
Compare two Nobel Prize data files to identify differences
Useful for comparing backup data with pipeline output to ensure quality
"""
import json
import sys
from collections import defaultdict

def load_data(filepath):
    """Load JSON data file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def compare_laureates(backup_data, new_data):
    """Compare laureates between two datasets"""

    # Build lookup dictionaries
    backup_by_id = {}
    new_by_id = {}

    for category, laureates in backup_data.items():
        for l in laureates:
            backup_by_id[l['laureate_id']] = l

    for category, laureates in new_data.items():
        for l in laureates:
            new_by_id[l['laureate_id']] = l

    # Find differences
    differences = {
        'only_in_backup': [],
        'only_in_new': [],
        'location_changes': [],
        'coord_changes': [],
        'other_changes': []
    }

    all_ids = set(backup_by_id.keys()) | set(new_by_id.keys())

    for laureate_id in sorted(all_ids):
        backup_entry = backup_by_id.get(laureate_id)
        new_entry = new_by_id.get(laureate_id)

        if not new_entry:
            differences['only_in_backup'].append({
                'laureate_id': laureate_id,
                'name': backup_entry.get('name', 'Unknown')
            })
            continue

        if not backup_entry:
            differences['only_in_new'].append({
                'laureate_id': laureate_id,
                'name': new_entry.get('name', 'Unknown')
            })
            continue

        # Compare work location
        backup_work_loc = backup_entry.get('work_location', '')
        new_work_loc = new_entry.get('work_location', '')
        backup_work_lat = backup_entry.get('work_lat', 0)
        backup_work_lon = backup_entry.get('work_lon', 0)
        new_work_lat = new_entry.get('work_lat', 0)
        new_work_lon = new_entry.get('work_lon', 0)

        if backup_work_loc != new_work_loc:
            differences['location_changes'].append({
                'laureate_id': laureate_id,
                'name': new_entry.get('name', 'Unknown'),
                'backup_location': backup_work_loc,
                'new_location': new_work_loc,
                'backup_coords': (backup_work_lat, backup_work_lon),
                'new_coords': (new_work_lat, new_work_lon)
            })
        elif abs(backup_work_lat - new_work_lat) > 0.01 or abs(backup_work_lon - new_work_lon) > 0.01:
            # Coordinates changed significantly but location text stayed same
            differences['coord_changes'].append({
                'laureate_id': laureate_id,
                'name': new_entry.get('name', 'Unknown'),
                'work_location': new_work_loc,
                'backup_coords': (backup_work_lat, backup_work_lon),
                'new_coords': (new_work_lat, new_work_lon),
                'distance_change': ((backup_work_lat - new_work_lat)**2 + (backup_work_lon - new_work_lon)**2)**0.5
            })

    return differences

def print_summary(differences):
    """Print a summary of differences"""
    print("=" * 100)
    print("DATA COMPARISON SUMMARY")
    print("=" * 100)

    # Only in backup
    if differences['only_in_backup']:
        print(f"\n❌ Only in backup ({len(differences['only_in_backup'])} entries):")
        for entry in differences['only_in_backup'][:10]:
            print(f"  - {entry['name']} ({entry['laureate_id']})")
        if len(differences['only_in_backup']) > 10:
            print(f"  ... and {len(differences['only_in_backup']) - 10} more")

    # Only in new
    if differences['only_in_new']:
        print(f"\n✨ Only in new data ({len(differences['only_in_new'])} entries):")
        for entry in differences['only_in_new'][:10]:
            print(f"  - {entry['name']} ({entry['laureate_id']})")
        if len(differences['only_in_new']) > 10:
            print(f"  ... and {len(differences['only_in_new']) - 10} more")

    # Location text changes
    if differences['location_changes']:
        print(f"\n📍 Work location text changed ({len(differences['location_changes'])} entries):")
        for entry in differences['location_changes'][:10]:
            print(f"\n  {entry['name']} ({entry['laureate_id']})")
            print(f"    Backup:  {entry['backup_location']} → {entry['backup_coords']}")
            print(f"    New:     {entry['new_location']} → {entry['new_coords']}")
        if len(differences['location_changes']) > 10:
            print(f"\n  ... and {len(differences['location_changes']) - 10} more")

    # Coordinate changes (same location text)
    if differences['coord_changes']:
        print(f"\n🗺️  Work coordinates changed ({len(differences['coord_changes'])} entries):")
        print("(Same location text, different coordinates)")
        for entry in sorted(differences['coord_changes'], key=lambda x: x['distance_change'], reverse=True)[:20]:
            print(f"\n  {entry['name']} ({entry['laureate_id']})")
            print(f"    Location: {entry['work_location']}")
            print(f"    Backup:   ({entry['backup_coords'][0]:.4f}, {entry['backup_coords'][1]:.4f})")
            print(f"    New:      ({entry['new_coords'][0]:.4f}, {entry['new_coords'][1]:.4f})")
            print(f"    Distance: {entry['distance_change']:.4f} degrees (~{entry['distance_change']*111:.1f} km)")
        if len(differences['coord_changes']) > 20:
            print(f"\n  ... and {len(differences['coord_changes']) - 20} more")

    print("\n" + "=" * 100)
    print("TOTALS:")
    print(f"  Only in backup:        {len(differences['only_in_backup'])}")
    print(f"  Only in new:           {len(differences['only_in_new'])}")
    print(f"  Location text changed: {len(differences['location_changes'])}")
    print(f"  Coordinates changed:   {len(differences['coord_changes'])}")
    print("=" * 100)

def save_detailed_report(differences, output_file):
    """Save detailed differences to JSON file"""
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(differences, f, indent=2, ensure_ascii=False)
    print(f"\nDetailed report saved to: {output_file}")

def main():
    if len(sys.argv) < 3:
        print("Usage: python compare_data.py <backup_file> <new_file> [output_report]")
        print("\nExample:")
        print("  python compare_data.py backups/nobel_data_complete_backup_20251103_103225.json pipeline/data/06_validated.json")
        return

    backup_file = sys.argv[1]
    new_file = sys.argv[2]
    output_report = sys.argv[3] if len(sys.argv) > 3 else 'comparison_report.json'

    print(f"\nLoading backup data from: {backup_file}")
    backup_data = load_data(backup_file)

    print(f"Loading new data from: {new_file}")
    new_data = load_data(new_file)

    print("\nComparing data...")
    differences = compare_laureates(backup_data, new_data)

    # Print summary
    print_summary(differences)

    # Save detailed report
    save_detailed_report(differences, output_report)

if __name__ == '__main__':
    main()
