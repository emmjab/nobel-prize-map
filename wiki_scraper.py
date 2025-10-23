"""
Wikipedia scraper for Nobel Prize laureate data
Scrapes Nobel Prize winner information from Wikipedia
"""

import requests
from bs4 import BeautifulSoup
import re
import time

# Simple geocoding dictionary for common cities
# In production, you'd use a geocoding API like Nominatim or Google Maps
CITY_COORDS = {
    # Major research cities
    'cambridge, massachusetts': (42.3736, -71.1097),
    'cambridge, england': (52.2053, 0.1218),
    'cambridge': (52.2053, 0.1218),
    'oxford': (51.7520, -1.2577),
    'london': (51.5074, -0.1278),
    'paris': (48.8566, 2.3522),
    'berlin': (52.5200, 13.4050),
    'munich': (48.1351, 11.5820),
    'stockholm': (59.3293, 18.0686),
    'oslo': (59.9139, 10.7522),
    'copenhagen': (55.6761, 12.5683),
    'zurich': (47.3769, 8.5417),
    'geneva': (46.2044, 6.1432),
    'vienna': (48.2082, 16.3738),
    'amsterdam': (52.3676, 4.9041),
    'brussels': (50.8503, 4.3517),
    'moscow': (55.7558, 37.6173),
    'st. petersburg': (59.9311, 30.3609),
    'tokyo': (35.6762, 139.6503),
    'kyoto': (35.0116, 135.7681),
    'beijing': (39.9042, 116.4074),
    'shanghai': (31.2304, 121.4737),
    'new york': (40.7128, -74.0060),
    'new york city': (40.7128, -74.0060),
    'boston': (42.3601, -71.0589),
    'chicago': (41.8781, -87.6298),
    'los angeles': (34.0522, -118.2437),
    'san francisco': (37.7749, -122.4194),
    'berkeley': (37.8715, -122.2730),
    'princeton': (40.3573, -74.6672),
    'stanford': (37.4275, -122.1697),
    'pasadena': (34.1478, -118.1445),
    'baltimore': (39.2904, -76.6122),
    'philadelphia': (39.9526, -75.1652),
    'washington': (38.9072, -77.0369),
    'washington, d.c.': (38.9072, -77.0369),
    'seattle': (47.6062, -122.3321),
    'toronto': (43.6532, -79.3832),
    'montreal': (45.5017, -73.5673),
    'sydney': (-33.8688, 151.2093),
    'melbourne': (-37.8136, 144.9631),
    'wellington': (-41.2865, 174.7762),
    'auckland': (-36.8485, 174.7633),
    'cape town': (-33.9249, 18.4241),
    'tel aviv': (32.0853, 34.7818),
    'jerusalem': (31.7683, 35.2137),
    'delhi': (28.7041, 77.1025),
    'mumbai': (19.0760, 72.8777),
    'bangalore': (12.9716, 77.5946),
    'buenos aires': (-34.6037, -58.3816),
    'mexico city': (19.4326, -99.1332),
    'rio de janeiro': (-22.9068, -43.1729),
    'sao paulo': (-23.5505, -46.6333),
}

def get_coords(location_str):
    """
    Get coordinates for a location string.
    Returns tuple of (lat, lon) or None if not found.
    """
    if not location_str:
        return None

    # Clean up the location string
    location = location_str.lower().strip()

    # Remove country-specific suffixes for better matching
    location = re.sub(r',?\s*(usa|u\.s\.a\.|united states|uk|england|france|germany|sweden|norway|denmark|japan|china)$', '', location, flags=re.IGNORECASE)
    location = location.strip().rstrip(',').strip()

    # Direct lookup
    if location in CITY_COORDS:
        return CITY_COORDS[location]

    # Try to extract city name from "City, State" or "City, Country" format
    if ',' in location:
        city = location.split(',')[0].strip()
        if city in CITY_COORDS:
            return CITY_COORDS[city]

    # Default fallback for unknown locations
    print(f"Warning: No coordinates found for '{location_str}'")
    return None

def scrape_nobel_laureates():
    """
    Scrape Nobel Prize laureate data from Wikipedia.
    Returns dictionary with laureates organized by category.
    """

    # For now, use a curated list with Wikipedia links
    # In a full implementation, this would scrape from Nobel Prize Wikipedia pages

    # Use Nobel Prize API or Wikipedia list pages
    # For this implementation, I'll create a more comprehensive sample dataset
    # that demonstrates the full functionality

    data = {
        'physics': [],
        'chemistry': [],
        'medicine': [],
        'literature': [],
        'peace': [],
        'economics': []
    }

    # This is where you would add scraping logic
    # For now, return expanded sample data

    return data

def get_comprehensive_sample_data():
    """
    Get comprehensive sample data covering more years and laureates.
    This demonstrates the full functionality before implementing web scraping.
    """

    data = {
        'physics': [
            {
                'laureate_id': 'physics_2023_1',
                'name': 'Pierre Agostini',
                'birth_location': 'Tunis, Tunisia',
                'birth_lat': 36.8065,
                'birth_lon': 10.1815,
                'work_location': 'Columbus, Ohio',
                'work_lat': 39.9612,
                'work_lon': -82.9988,
                'work_years': '2000-2005',
                'prize_year': 2023,
                'achievement': 'Experimental methods that generate attosecond pulses of light',
                'shared_with': ['physics_2023_2', 'physics_2023_3']
            },
            {
                'laureate_id': 'physics_2023_2',
                'name': 'Ferenc Krausz',
                'birth_location': 'Mór, Hungary',
                'birth_lat': 47.3747,
                'birth_lon': 18.2061,
                'work_location': 'Garching, Germany',
                'work_lat': 48.2492,
                'work_lon': 11.6514,
                'work_years': '2000-2005',
                'prize_year': 2023,
                'achievement': 'Experimental methods that generate attosecond pulses of light',
                'shared_with': ['physics_2023_1', 'physics_2023_3']
            },
            {
                'laureate_id': 'physics_2023_3',
                'name': 'Anne L\'Huillier',
                'birth_location': 'Paris, France',
                'birth_lat': 48.8566,
                'birth_lon': 2.3522,
                'work_location': 'Lund, Sweden',
                'work_lat': 55.7047,
                'work_lon': 13.1910,
                'work_years': '1987-1995',
                'prize_year': 2023,
                'achievement': 'Experimental methods that generate attosecond pulses of light',
                'shared_with': ['physics_2023_1', 'physics_2023_2']
            },
            {
                'laureate_id': 'physics_2022_1',
                'name': 'Alain Aspect',
                'birth_location': 'Agen, France',
                'birth_lat': 44.2028,
                'birth_lon': 0.6167,
                'work_location': 'Paris, France',
                'work_lat': 48.8566,
                'work_lon': 2.3522,
                'work_years': '1980-1982',
                'prize_year': 2022,
                'achievement': 'Experiments with entangled photons, establishing the violation of Bell inequalities',
                'shared_with': ['physics_2022_2', 'physics_2022_3']
            },
            {
                'laureate_id': 'physics_2022_2',
                'name': 'John Clauser',
                'birth_location': 'Pasadena, California',
                'birth_lat': 34.1478,
                'birth_lon': -118.1445,
                'work_location': 'Berkeley, California',
                'work_lat': 37.8715,
                'work_lon': -122.2730,
                'work_years': '1969-1974',
                'prize_year': 2022,
                'achievement': 'Experiments with entangled photons, establishing the violation of Bell inequalities',
                'shared_with': ['physics_2022_1', 'physics_2022_3']
            },
            {
                'laureate_id': 'physics_2022_3',
                'name': 'Anton Zeilinger',
                'birth_location': 'Ried im Innkreis, Austria',
                'birth_lat': 48.2100,
                'birth_lon': 13.4881,
                'work_location': 'Vienna, Austria',
                'work_lat': 48.2082,
                'work_lon': 16.3738,
                'work_years': '1990-2010',
                'prize_year': 2022,
                'achievement': 'Experiments with entangled photons, establishing the violation of Bell inequalities',
                'shared_with': ['physics_2022_1', 'physics_2022_2']
            },
            {
                'laureate_id': 'physics_2021_1',
                'name': 'Syukuro Manabe',
                'birth_location': 'Shingu, Japan',
                'birth_lat': 33.7250,
                'birth_lon': 135.9958,
                'work_location': 'Princeton, New Jersey',
                'work_lat': 40.3573,
                'work_lon': -74.6672,
                'work_years': '1960-1990',
                'prize_year': 2021,
                'achievement': 'Physical modelling of Earth\'s climate, quantifying variability and reliably predicting global warming',
                'shared_with': ['physics_2021_2', 'physics_2021_3']
            },
            {
                'laureate_id': 'physics_2021_2',
                'name': 'Klaus Hasselmann',
                'birth_location': 'Hamburg, Germany',
                'birth_lat': 53.5511,
                'birth_lon': 9.9937,
                'work_location': 'Hamburg, Germany',
                'work_lat': 53.5511,
                'work_lon': 9.9937,
                'work_years': '1970-2000',
                'prize_year': 2021,
                'achievement': 'Physical modelling of Earth\'s climate, quantifying variability and reliably predicting global warming',
                'shared_with': ['physics_2021_1', 'physics_2021_3']
            },
            {
                'laureate_id': 'physics_2021_3',
                'name': 'Giorgio Parisi',
                'birth_location': 'Rome, Italy',
                'birth_lat': 41.9028,
                'birth_lon': 12.4964,
                'work_location': 'Rome, Italy',
                'work_lat': 41.9028,
                'work_lon': 12.4964,
                'work_years': '1970-2020',
                'prize_year': 2021,
                'achievement': 'Discovery of the interplay of disorder and fluctuations in physical systems from atomic to planetary scales',
                'shared_with': ['physics_2021_1', 'physics_2021_2']
            },
            {
                'laureate_id': 'physics_2020_1',
                'name': 'Roger Penrose',
                'birth_location': 'Colchester, England',
                'birth_lat': 51.8959,
                'birth_lon': 0.8919,
                'work_location': 'Oxford, England',
                'work_lat': 51.7520,
                'work_lon': -1.2577,
                'work_years': '1964-1970',
                'prize_year': 2020,
                'achievement': 'Discovery that black hole formation is a robust prediction of general relativity',
                'shared_with': ['physics_2020_2', 'physics_2020_3']
            },
            {
                'laureate_id': 'physics_2020_2',
                'name': 'Reinhard Genzel',
                'birth_location': 'Bad Homburg, Germany',
                'birth_lat': 50.2269,
                'birth_lon': 8.6176,
                'work_location': 'Garching, Germany',
                'work_lat': 48.2492,
                'work_lon': 11.6514,
                'work_years': '1990-2010',
                'prize_year': 2020,
                'achievement': 'Discovery of a supermassive compact object at the center of our galaxy',
                'shared_with': ['physics_2020_1', 'physics_2020_3']
            },
            {
                'laureate_id': 'physics_2020_3',
                'name': 'Andrea Ghez',
                'birth_location': 'New York City, USA',
                'birth_lat': 40.7128,
                'birth_lon': -74.0060,
                'work_location': 'Los Angeles, California',
                'work_lat': 34.0522,
                'work_lon': -118.2437,
                'work_years': '1990-2010',
                'prize_year': 2020,
                'achievement': 'Discovery of a supermassive compact object at the center of our galaxy',
                'shared_with': ['physics_2020_1', 'physics_2020_2']
            },
        ],
        'chemistry': [
            {
                'laureate_id': 'chemistry_2023_1',
                'name': 'Moungi Bawendi',
                'birth_location': 'Paris, France',
                'birth_lat': 48.8566,
                'birth_lon': 2.3522,
                'work_location': 'Cambridge, Massachusetts',
                'work_lat': 42.3736,
                'work_lon': -71.1097,
                'work_years': '1990-1995',
                'prize_year': 2023,
                'achievement': 'Discovery and synthesis of quantum dots',
                'shared_with': ['chemistry_2023_2', 'chemistry_2023_3']
            },
            {
                'laureate_id': 'chemistry_2023_2',
                'name': 'Louis Brus',
                'birth_location': 'Cleveland, Ohio',
                'birth_lat': 41.4993,
                'birth_lon': -81.6944,
                'work_location': 'New York City, USA',
                'work_lat': 40.7128,
                'work_lon': -74.0060,
                'work_years': '1980-1985',
                'prize_year': 2023,
                'achievement': 'Discovery and synthesis of quantum dots',
                'shared_with': ['chemistry_2023_1', 'chemistry_2023_3']
            },
            {
                'laureate_id': 'chemistry_2023_3',
                'name': 'Alexei Ekimov',
                'birth_location': 'St. Petersburg, Russia',
                'birth_lat': 59.9311,
                'birth_lon': 30.3609,
                'work_location': 'St. Petersburg, Russia',
                'work_lat': 59.9311,
                'work_lon': 30.3609,
                'work_years': '1975-1985',
                'prize_year': 2023,
                'achievement': 'Discovery and synthesis of quantum dots',
                'shared_with': ['chemistry_2023_1', 'chemistry_2023_2']
            },
            {
                'laureate_id': 'chemistry_2022_1',
                'name': 'Carolyn Bertozzi',
                'birth_location': 'Boston, Massachusetts',
                'birth_lat': 42.3601,
                'birth_lon': -71.0589,
                'work_location': 'Berkeley, California',
                'work_lat': 37.8715,
                'work_lon': -122.2730,
                'work_years': '1997-2010',
                'prize_year': 2022,
                'achievement': 'Development of click chemistry and bioorthogonal chemistry',
                'shared_with': ['chemistry_2022_2', 'chemistry_2022_3']
            },
            {
                'laureate_id': 'chemistry_2022_2',
                'name': 'Morten Meldal',
                'birth_location': 'Copenhagen, Denmark',
                'birth_lat': 55.6761,
                'birth_lon': 12.5683,
                'work_location': 'Copenhagen, Denmark',
                'work_lat': 55.6761,
                'work_lon': 12.5683,
                'work_years': '1995-2005',
                'prize_year': 2022,
                'achievement': 'Development of click chemistry and bioorthogonal chemistry',
                'shared_with': ['chemistry_2022_1', 'chemistry_2022_3']
            },
            {
                'laureate_id': 'chemistry_2022_3',
                'name': 'Barry Sharpless',
                'birth_location': 'Philadelphia, Pennsylvania',
                'birth_lat': 39.9526,
                'birth_lon': -75.1652,
                'work_location': 'La Jolla, California',
                'work_lat': 32.8328,
                'work_lon': -117.2713,
                'work_years': '1995-2005',
                'prize_year': 2022,
                'achievement': 'Development of click chemistry and bioorthogonal chemistry',
                'shared_with': ['chemistry_2022_1', 'chemistry_2022_2']
            },
            {
                'laureate_id': 'chemistry_2021_1',
                'name': 'Benjamin List',
                'birth_location': 'Frankfurt, Germany',
                'birth_lat': 50.1109,
                'birth_lon': 8.6821,
                'work_location': 'Mülheim, Germany',
                'work_lat': 51.4275,
                'work_lon': 6.8825,
                'work_years': '1995-2005',
                'prize_year': 2021,
                'achievement': 'Development of asymmetric organocatalysis',
                'shared_with': ['chemistry_2021_2']
            },
            {
                'laureate_id': 'chemistry_2021_2',
                'name': 'David MacMillan',
                'birth_location': 'Bellshill, Scotland',
                'birth_lat': 55.8167,
                'birth_lon': -4.0167,
                'work_location': 'Princeton, New Jersey',
                'work_lat': 40.3573,
                'work_lon': -74.6672,
                'work_years': '1995-2005',
                'prize_year': 2021,
                'achievement': 'Development of asymmetric organocatalysis',
                'shared_with': ['chemistry_2021_1']
            },
            {
                'laureate_id': 'chemistry_2020_1',
                'name': 'Emmanuelle Charpentier',
                'birth_location': 'Juvisy-sur-Orge, France',
                'birth_lat': 48.6897,
                'birth_lon': 2.3769,
                'work_location': 'Umeå, Sweden',
                'work_lat': 63.8258,
                'work_lon': 20.2630,
                'work_years': '2009-2012',
                'prize_year': 2020,
                'achievement': 'Development of CRISPR-Cas9 genetic scissors',
                'shared_with': ['chemistry_2020_2']
            },
            {
                'laureate_id': 'chemistry_2020_2',
                'name': 'Jennifer Doudna',
                'birth_location': 'Washington, D.C.',
                'birth_lat': 38.9072,
                'birth_lon': -77.0369,
                'work_location': 'Berkeley, California',
                'work_lat': 37.8715,
                'work_lon': -122.2730,
                'work_years': '2009-2012',
                'prize_year': 2020,
                'achievement': 'Development of CRISPR-Cas9 genetic scissors',
                'shared_with': ['chemistry_2020_1']
            },
        ],
        'medicine': [
            {
                'laureate_id': 'medicine_2023_1',
                'name': 'Katalin Karikó',
                'birth_location': 'Szolnok, Hungary',
                'birth_lat': 47.1730,
                'birth_lon': 20.1984,
                'work_location': 'Philadelphia, Pennsylvania',
                'work_lat': 39.9526,
                'work_lon': -75.1652,
                'work_years': '1990-2005',
                'prize_year': 2023,
                'achievement': 'Discoveries concerning nucleoside base modifications that enabled effective mRNA vaccines',
                'shared_with': ['medicine_2023_2']
            },
            {
                'laureate_id': 'medicine_2023_2',
                'name': 'Drew Weissman',
                'birth_location': 'Lexington, Massachusetts',
                'birth_lat': 42.4473,
                'birth_lon': -71.2245,
                'work_location': 'Philadelphia, Pennsylvania',
                'work_lat': 39.9526,
                'work_lon': -75.1652,
                'work_years': '1997-2005',
                'prize_year': 2023,
                'achievement': 'Discoveries concerning nucleoside base modifications that enabled effective mRNA vaccines',
                'shared_with': ['medicine_2023_1']
            },
            {
                'laureate_id': 'medicine_2022_1',
                'name': 'Svante Pääbo',
                'birth_location': 'Stockholm, Sweden',
                'birth_lat': 59.3293,
                'birth_lon': 18.0686,
                'work_location': 'Leipzig, Germany',
                'work_lat': 51.3397,
                'work_lon': 12.3731,
                'work_years': '1997-2020',
                'prize_year': 2022,
                'achievement': 'Discoveries concerning the genomes of extinct hominins and human evolution',
                'shared_with': []
            },
            {
                'laureate_id': 'medicine_2021_1',
                'name': 'David Julius',
                'birth_location': 'New York City, USA',
                'birth_lat': 40.7128,
                'birth_lon': -74.0060,
                'work_location': 'San Francisco, California',
                'work_lat': 37.7749,
                'work_lon': -122.4194,
                'work_years': '1997-2010',
                'prize_year': 2021,
                'achievement': 'Discoveries of receptors for temperature and touch',
                'shared_with': ['medicine_2021_2']
            },
            {
                'laureate_id': 'medicine_2021_2',
                'name': 'Ardem Patapoutian',
                'birth_location': 'Beirut, Lebanon',
                'birth_lat': 33.8886,
                'birth_lon': 35.4955,
                'work_location': 'La Jolla, California',
                'work_lat': 32.8328,
                'work_lon': -117.2713,
                'work_years': '2000-2010',
                'prize_year': 2021,
                'achievement': 'Discoveries of receptors for temperature and touch',
                'shared_with': ['medicine_2021_1']
            },
            {
                'laureate_id': 'medicine_2020_1',
                'name': 'Harvey Alter',
                'birth_location': 'New York City, USA',
                'birth_lat': 40.7128,
                'birth_lon': -74.0060,
                'work_location': 'Bethesda, Maryland',
                'work_lat': 38.9847,
                'work_lon': -77.0947,
                'work_years': '1972-1989',
                'prize_year': 2020,
                'achievement': 'Discovery of Hepatitis C virus',
                'shared_with': ['medicine_2020_2', 'medicine_2020_3']
            },
            {
                'laureate_id': 'medicine_2020_2',
                'name': 'Michael Houghton',
                'birth_location': 'London, England',
                'birth_lat': 51.5074,
                'birth_lon': -0.1278,
                'work_location': 'Emeryville, California',
                'work_lat': 37.8313,
                'work_lon': -122.2852,
                'work_years': '1982-1989',
                'prize_year': 2020,
                'achievement': 'Discovery of Hepatitis C virus',
                'shared_with': ['medicine_2020_1', 'medicine_2020_3']
            },
            {
                'laureate_id': 'medicine_2020_3',
                'name': 'Charles Rice',
                'birth_location': 'Sacramento, California',
                'birth_lat': 38.5816,
                'birth_lon': -121.4944,
                'work_location': 'New York City, USA',
                'work_lat': 40.7128,
                'work_lon': -74.0060,
                'work_years': '1995-2005',
                'prize_year': 2020,
                'achievement': 'Discovery of Hepatitis C virus',
                'shared_with': ['medicine_2020_1', 'medicine_2020_2']
            },
            {
                'laureate_id': 'medicine_2015_1',
                'name': 'Tu Youyou',
                'birth_location': 'Ningbo, China',
                'birth_lat': 29.8683,
                'birth_lon': 121.5440,
                'work_location': 'Beijing, China',
                'work_lat': 39.9042,
                'work_lon': 116.4074,
                'work_years': '1967-1972',
                'prize_year': 2015,
                'achievement': 'Discoveries concerning a novel therapy against Malaria',
                'shared_with': ['medicine_2015_2', 'medicine_2015_3']
            },
            {
                'laureate_id': 'medicine_2015_2',
                'name': 'William Campbell',
                'birth_location': 'Ramelton, Ireland',
                'birth_lat': 55.0358,
                'birth_lon': -7.6472,
                'work_location': 'Rahway, New Jersey',
                'work_lat': 40.6081,
                'work_lon': -74.2768,
                'work_years': '1975-1987',
                'prize_year': 2015,
                'achievement': 'Discoveries concerning therapies against roundworm parasites',
                'shared_with': ['medicine_2015_1', 'medicine_2015_3']
            },
            {
                'laureate_id': 'medicine_2015_3',
                'name': 'Satoshi Ōmura',
                'birth_location': 'Nirasaki, Japan',
                'birth_lat': 35.7079,
                'birth_lon': 138.4464,
                'work_location': 'Tokyo, Japan',
                'work_lat': 35.6762,
                'work_lon': 139.6503,
                'work_years': '1974-1979',
                'prize_year': 2015,
                'achievement': 'Discoveries concerning therapies against roundworm parasites',
                'shared_with': ['medicine_2015_1', 'medicine_2015_2']
            },
        ],
        'literature': [
            {
                'laureate_id': 'literature_2023_1',
                'name': 'Jon Fosse',
                'birth_location': 'Haugesund, Norway',
                'birth_lat': 59.4138,
                'birth_lon': 5.2680,
                'work_location': 'Bergen, Norway',
                'work_lat': 60.3913,
                'work_lon': 5.3221,
                'work_years': '1983-2023',
                'prize_year': 2023,
                'achievement': 'Innovative plays and prose which give voice to the unsayable',
                'shared_with': []
            },
            {
                'laureate_id': 'literature_2022_1',
                'name': 'Annie Ernaux',
                'birth_location': 'Lillebonne, France',
                'birth_lat': 49.5181,
                'birth_lon': 0.5372,
                'work_location': 'Paris, France',
                'work_lat': 48.8566,
                'work_lon': 2.3522,
                'work_years': '1974-2022',
                'prize_year': 2022,
                'achievement': 'For the courage and clinical acuity with which she uncovers the roots of personal memory',
                'shared_with': []
            },
            {
                'laureate_id': 'literature_2021_1',
                'name': 'Abdulrazak Gurnah',
                'birth_location': 'Zanzibar, Tanzania',
                'birth_lat': -6.1659,
                'birth_lon': 39.2026,
                'work_location': 'Canterbury, England',
                'work_lat': 51.2787,
                'work_lon': 1.0789,
                'work_years': '1987-2021',
                'prize_year': 2021,
                'achievement': 'Uncompromising and compassionate penetration of the effects of colonialism',
                'shared_with': []
            },
            {
                'laureate_id': 'literature_2020_1',
                'name': 'Louise Glück',
                'birth_location': 'New York City, USA',
                'birth_lat': 40.7128,
                'birth_lon': -74.0060,
                'work_location': 'Cambridge, Massachusetts',
                'work_lat': 42.3736,
                'work_lon': -71.1097,
                'work_years': '1968-2020',
                'prize_year': 2020,
                'achievement': 'Unmistakable poetic voice that makes individual existence universal',
                'shared_with': []
            },
            {
                'laureate_id': 'literature_2017_1',
                'name': 'Kazuo Ishiguro',
                'birth_location': 'Nagasaki, Japan',
                'birth_lat': 32.7503,
                'birth_lon': 129.8779,
                'work_location': 'London, England',
                'work_lat': 51.5074,
                'work_lon': -0.1278,
                'work_years': '1980-2017',
                'prize_year': 2017,
                'achievement': 'Novels of great emotional force uncovering the abyss beneath our sense of connection',
                'shared_with': []
            },
        ],
        'peace': [
            {
                'laureate_id': 'peace_2023_1',
                'name': 'Narges Mohammadi',
                'birth_location': 'Zanjan, Iran',
                'birth_lat': 36.6736,
                'birth_lon': 48.4787,
                'work_location': 'Tehran, Iran',
                'work_lat': 35.6892,
                'work_lon': 51.3890,
                'work_years': '2003-2023',
                'prize_year': 2023,
                'achievement': 'Fight against oppression of women in Iran and for human rights',
                'shared_with': []
            },
            {
                'laureate_id': 'peace_2022_1',
                'name': 'Ales Bialiatski',
                'birth_location': 'Vyartsilya, Russia',
                'birth_lat': 61.5667,
                'birth_lon': 30.6333,
                'work_location': 'Minsk, Belarus',
                'work_lat': 53.9045,
                'work_lon': 27.5615,
                'work_years': '1996-2022',
                'prize_year': 2022,
                'achievement': 'Outstanding effort to document war crimes and human rights abuses',
                'shared_with': ['peace_2022_2', 'peace_2022_3']
            },
            {
                'laureate_id': 'peace_2022_2',
                'name': 'Memorial (Organization)',
                'birth_location': 'Moscow, Russia',
                'birth_lat': 55.7558,
                'birth_lon': 37.6173,
                'work_location': 'Moscow, Russia',
                'work_lat': 55.7558,
                'work_lon': 37.6173,
                'work_years': '1987-2022',
                'prize_year': 2022,
                'achievement': 'Outstanding effort to document war crimes and human rights abuses',
                'shared_with': ['peace_2022_1', 'peace_2022_3']
            },
            {
                'laureate_id': 'peace_2022_3',
                'name': 'Center for Civil Liberties',
                'birth_location': 'Kyiv, Ukraine',
                'birth_lat': 50.4501,
                'birth_lon': 30.5234,
                'work_location': 'Kyiv, Ukraine',
                'work_lat': 50.4501,
                'work_lon': 30.5234,
                'work_years': '2007-2022',
                'prize_year': 2022,
                'achievement': 'Outstanding effort to document war crimes and human rights abuses',
                'shared_with': ['peace_2022_1', 'peace_2022_2']
            },
            {
                'laureate_id': 'peace_2021_1',
                'name': 'Maria Ressa',
                'birth_location': 'Manila, Philippines',
                'birth_lat': 14.5995,
                'birth_lon': 120.9842,
                'work_location': 'Manila, Philippines',
                'work_lat': 14.5995,
                'work_lon': 120.9842,
                'work_years': '2012-2021',
                'prize_year': 2021,
                'achievement': 'Efforts to safeguard freedom of expression',
                'shared_with': ['peace_2021_2']
            },
            {
                'laureate_id': 'peace_2021_2',
                'name': 'Dmitry Muratov',
                'birth_location': 'Samara, Russia',
                'birth_lat': 53.1950,
                'birth_lon': 50.1069,
                'work_location': 'Moscow, Russia',
                'work_lat': 55.7558,
                'work_lon': 37.6173,
                'work_years': '1993-2021',
                'prize_year': 2021,
                'achievement': 'Efforts to safeguard freedom of expression',
                'shared_with': ['peace_2021_1']
            },
            {
                'laureate_id': 'peace_2020_1',
                'name': 'World Food Programme',
                'birth_location': 'Rome, Italy',
                'birth_lat': 41.9028,
                'birth_lon': 12.4964,
                'work_location': 'Rome, Italy',
                'work_lat': 41.9028,
                'work_lon': 12.4964,
                'work_years': '1961-2020',
                'prize_year': 2020,
                'achievement': 'Efforts to combat hunger and bettering conditions for peace',
                'shared_with': []
            },
        ],
        'economics': [
            {
                'laureate_id': 'economics_2023_1',
                'name': 'Claudia Goldin',
                'birth_location': 'New York City, USA',
                'birth_lat': 40.7128,
                'birth_lon': -74.0060,
                'work_location': 'Cambridge, Massachusetts',
                'work_lat': 42.3736,
                'work_lon': -71.1097,
                'work_years': '1990-2020',
                'prize_year': 2023,
                'achievement': 'Advanced understanding of women\'s labour market outcomes',
                'shared_with': []
            },
            {
                'laureate_id': 'economics_2022_1',
                'name': 'Ben Bernanke',
                'birth_location': 'Augusta, Georgia',
                'birth_lat': 33.4735,
                'birth_lon': -82.0105,
                'work_location': 'Princeton, New Jersey',
                'work_lat': 40.3573,
                'work_lon': -74.6672,
                'work_years': '1979-1983',
                'prize_year': 2022,
                'achievement': 'Research on banks and financial crises',
                'shared_with': ['economics_2022_2', 'economics_2022_3']
            },
            {
                'laureate_id': 'economics_2022_2',
                'name': 'Douglas Diamond',
                'birth_location': 'Chicago, Illinois',
                'birth_lat': 41.8781,
                'birth_lon': -87.6298,
                'work_location': 'Chicago, Illinois',
                'work_lat': 41.8781,
                'work_lon': -87.6298,
                'work_years': '1979-1984',
                'prize_year': 2022,
                'achievement': 'Research on banks and financial crises',
                'shared_with': ['economics_2022_1', 'economics_2022_3']
            },
            {
                'laureate_id': 'economics_2022_3',
                'name': 'Philip Dybvig',
                'birth_location': 'Palo Alto, California',
                'birth_lat': 37.4419,
                'birth_lon': -122.1430,
                'work_location': 'St. Louis, Missouri',
                'work_lat': 38.6270,
                'work_lon': -90.1994,
                'work_years': '1980-1983',
                'prize_year': 2022,
                'achievement': 'Research on banks and financial crises',
                'shared_with': ['economics_2022_1', 'economics_2022_2']
            },
            {
                'laureate_id': 'economics_2021_1',
                'name': 'David Card',
                'birth_location': 'Guelph, Canada',
                'birth_lat': 43.5448,
                'birth_lon': -80.2482,
                'work_location': 'Berkeley, California',
                'work_lat': 37.8715,
                'work_lon': -122.2730,
                'work_years': '1990-2010',
                'prize_year': 2021,
                'achievement': 'Empirical contributions to labour economics',
                'shared_with': ['economics_2021_2', 'economics_2021_3']
            },
            {
                'laureate_id': 'economics_2021_2',
                'name': 'Joshua Angrist',
                'birth_location': 'Columbus, Ohio',
                'birth_lat': 39.9612,
                'birth_lon': -82.9988,
                'work_location': 'Cambridge, Massachusetts',
                'work_lat': 42.3736,
                'work_lon': -71.1097,
                'work_years': '1990-2010',
                'prize_year': 2021,
                'achievement': 'Methodological contributions to the analysis of causal relationships',
                'shared_with': ['economics_2021_1', 'economics_2021_3']
            },
            {
                'laureate_id': 'economics_2021_3',
                'name': 'Guido Imbens',
                'birth_location': 'Eindhoven, Netherlands',
                'birth_lat': 51.4416,
                'birth_lon': 5.4697,
                'work_location': 'Stanford, California',
                'work_lat': 37.4275,
                'work_lon': -122.1697,
                'work_years': '1995-2010',
                'prize_year': 2021,
                'achievement': 'Methodological contributions to the analysis of causal relationships',
                'shared_with': ['economics_2021_1', 'economics_2021_2']
            },
            {
                'laureate_id': 'economics_2020_1',
                'name': 'Paul Milgrom',
                'birth_location': 'Detroit, Michigan',
                'birth_lat': 42.3314,
                'birth_lon': -83.0458,
                'work_location': 'Stanford, California',
                'work_lat': 37.4275,
                'work_lon': -122.1697,
                'work_years': '1987-2000',
                'prize_year': 2020,
                'achievement': 'Improvements to auction theory and inventions of new auction formats',
                'shared_with': ['economics_2020_2']
            },
            {
                'laureate_id': 'economics_2020_2',
                'name': 'Robert Wilson',
                'birth_location': 'Geneva, Nebraska',
                'birth_lat': 40.5269,
                'birth_lon': -97.5956,
                'work_location': 'Stanford, California',
                'work_lat': 37.4275,
                'work_lon': -122.1697,
                'work_years': '1977-1995',
                'prize_year': 2020,
                'achievement': 'Improvements to auction theory and inventions of new auction formats',
                'shared_with': ['economics_2020_1']
            },
        ]
    }

    return data
