# Nobel Prize Map Explorer

An interactive web application that visualizes Nobel Prize laureates on a world map, showing where they were born and where they conducted their prize-winning research.
see it live here: https://emma.jablonski.us/nobel-map/

## Features

- **All Six Nobel Categories**: Physics, Chemistry, Physiology/Medicine, Literature, Peace, and Economic Sciences
- **Dual Location Markers**:
  - Color dots show where laureates did their Nobel Prize work
  - Cake markers show birthplaces
- **Visual Connections**: Dashed purple lines connect co-laureates who shared a prize
- **Interactive Cards**: Click on laureate cards to zoom to their location
- **Clickable Links**: Navigate between co-laureates through links in cards and popups
- **Rich Information**: View birth location, work location, work years, prize year, and achievements

## Setup

3. Install dependencies (e.g. in a virtualenv):
```bash
pip install -r requirements.txt
```

4. Run the application:
```bash
python app.py
```
Or use the quick start script:
```bash
./run.sh
```

5. Open your browser to: `http://localhost:5000` (or the port shown in terminal)

## How to Use

1. Show all categories or select a Nobel Prize category from the dropdown menu
2. Search a laureate name (autocompleted)
3. Browse laureate cards in the left panel
4. Click on any laureate card to highlight and zoom to their work location
5. Click on co-laureate links to navigate between prize-sharing scientists
6. Explore map markers:
   - Color markers = Work locations where research was conducted
   - Cake markers = Birthplaces
   - Purple dashed lines = Connect co-laureates who shared a prize
   - Green dashed lines = Connect birth to work location for each laureate

## Data

Nobel Prize winners across all categories from https://app.swaggerhub.com/apis/NobelMedia/NobelMasterData/2.1. Each entry includes:
- Laureate name
- Birth location with coordinates
- Work location with coordinates
- Years of prize-winning research
- Nobel Prize year
- Achievement description
- Co-laureate connections

## Technology Stack

- **Backend**: Flask
- **Frontend**: HTML, CSS, JavaScript
- **Mapping**: Leaflet.js with OpenStreetMap tiles
- **Data**: Nobel Prize data https://www.nobelprize.org/about/developer-zone-2/, manually edited where missing.
- **Note**: Spot a mistake? Let me know!

## Future Enhancements

- Filter by year range
- Export laureate information
- Additional biographical details
- University/institution affiliations
- Timeline view of prizes over the years
