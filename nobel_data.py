"""
Nobel Prize data module
Loads complete Nobel Prize laureate data from JSON file
"""

import json
import os

# Cache for the loaded data
_cached_data = None

def load_complete_data():
    """Load complete Nobel Prize data from JSON file"""
    global _cached_data

    if _cached_data is not None:
        return _cached_data

    data_file = 'nobel_data_complete.json'

    if not os.path.exists(data_file):
        print(f"Warning: {data_file} not found. Run fetch_nobel_data.py first.")
        # Fall back to sample data
        from wiki_scraper import get_comprehensive_sample_data
        _cached_data = get_comprehensive_sample_data()
        return _cached_data

    with open(data_file, 'r', encoding='utf-8') as f:
        _cached_data = json.load(f)

    return _cached_data

def get_nobel_laureates(category):
    """
    Get Nobel laureates for a specific category.
    Returns list of laureates with their work locations, birth info, and co-laureates.
    """
    all_data = load_complete_data()
    return all_data.get(category, [])

def get_all_laureates():
    """
    Get all Nobel laureates across all categories.
    Returns dictionary organized by category.
    """
    return load_complete_data()
