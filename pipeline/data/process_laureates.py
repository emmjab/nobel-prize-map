#!/usr/bin/env python3
"""
Process Nobel laureates to find their work locations through web searches.
"""
import json
import sys

def load_laureates():
    """Load the laureates data from JSON file."""
    with open('/Users/emma/Documents/file_cabinet/people_projects/emma/nobel_map/pipeline/data/needs_manual_review.json', 'r') as f:
        return json.load(f)

def main():
    laureates = load_laureates()
    print(f"Loaded {len(laureates)} laureates")

    # Print them all for processing
    for i, laureate in enumerate(laureates):
        print(f"{i+1}. {laureate['laureate_id']}: {laureate['name']} ({laureate['category']} {laureate['prize_year']})")

if __name__ == '__main__':
    main()
