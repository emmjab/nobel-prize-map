"""
Manual coordinate mapping for locations that can't be automatically geocoded
"""

import json

# Manually researched coordinates for remaining locations
MANUAL_COORDS = {
    'Aldea Chimel, Guatemala': (15.43, -91.22),  # Small village in Guatemala
    'Casteldàwson, Northern Ireland': (54.76, -6.52),  # Castledawson, County Londonderry
    'Dabrovica, Poland': (52.14, 19.41),  # Dąbrowice, Poland
    'Frankfurt-on-the-Main, Germany': (50.1109, 8.6821),  # Frankfurt am Main
    'Kibbutz Sde-Nahum, British Mandate of Palestine (now Israel)': (32.706, 35.559),  # Sde Nahum kibbutz
    'Mit Abu al-Kawm, Egypt': (30.57, 30.93),  # Mit Abu al-Kom, Egypt
    'Tardebigg, United Kingdom': (52.31, -2.03),  # Tardebigg, Worcestershire
    'Wailacama, East Timor': (-8.55, 126.42),  # Wailacama, East Timor
}

def apply_manual_coordinates():
    """Apply manually researched coordinates to the dataset"""

    # Load the current data
    with open('nobel_data_complete.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    updated_count = 0

    for category, laureates in data.items():
        for laureate in laureates:
            birth_loc = laureate.get('birth_location', '')
            work_loc = laureate.get('work_location', '')

            # Update birth coordinates
            if birth_loc in MANUAL_COORDS:
                if laureate['birth_lat'] == 0 and laureate['birth_lon'] == 0:
                    coords = MANUAL_COORDS[birth_loc]
                    laureate['birth_lat'], laureate['birth_lon'] = coords
                    print(f"  Fixed {laureate['name']} birth: {birth_loc} -> {coords}")
                    updated_count += 1

            # Update work coordinates
            if work_loc in MANUAL_COORDS:
                if laureate['work_lat'] == 0 and laureate['work_lon'] == 0:
                    coords = MANUAL_COORDS[work_loc]
                    laureate['work_lat'], laureate['work_lon'] = coords
                    print(f"  Fixed {laureate['name']} work: {work_loc} -> {coords}")
                    updated_count += 1

    # Save updated data
    with open('nobel_data_complete.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"\nUpdated {updated_count} coordinate pairs")

    # Count remaining zeros
    zero_count = 0
    for category, laureates in data.items():
        for laureate in laureates:
            if (laureate['birth_lat'] == 0 and laureate['birth_lon'] == 0) or \
               (laureate['work_lat'] == 0 and laureate['work_lon'] == 0):
                zero_count += 1

    print(f"Remaining entries with (0,0) coordinates: {zero_count}")

if __name__ == '__main__':
    print("=" * 60)
    print("Apply Manual Coordinates")
    print("=" * 60)
    apply_manual_coordinates()
    print("=" * 60)
