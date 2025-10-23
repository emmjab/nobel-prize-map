# Nobel Prize Map Explorer

An interactive web application that visualizes Nobel Prize laureates on a world map, showing where they were born and where they conducted their prize-winning research.

## Features

- **All Six Nobel Categories**: Physics, Chemistry, Physiology/Medicine, Literature, Peace, and Economic Sciences
- **Dual Location Markers**:
  - Purple markers show where laureates did their Nobel Prize work
  - Green markers show birthplaces
- **Visual Connections**: Dashed purple lines connect co-laureates who shared a prize
- **Interactive Cards**: Click on laureate cards to zoom to their location
- **Clickable Links**: Navigate between co-laureates through links in cards and popups
- **Rich Information**: View birth location, work location, work years, prize year, and achievements

## Setup

1. Navigate to the project:
```bash
cd /Users/emma/Documents/file_cabinet/people_projects/emma/nobel_map
```

2. Activate the virtual environment:
```bash
source venv/bin/activate
```

3. Install dependencies:
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

1. Select a Nobel Prize category from the dropdown menu
2. Browse laureate cards in the left panel
3. Click on any laureate card to highlight and zoom to their work location
4. Click on co-laureate links to navigate between prize-sharing scientists
5. Explore map markers:
   - Purple markers = Work locations where research was conducted
   - Green markers = Birthplaces
   - Purple dashed lines = Connect co-laureates who shared a prize
   - Green dashed lines = Connect birth to work location for each laureate

## Data

Currently uses curated sample data featuring recent notable Nobel Prize winners across all categories. Each entry includes:
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
- **Data**: Curated Nobel Prize information (Wikipedia scraping planned for future)

## Future Enhancements

- Wikipedia/Nobel Prize API integration for automatic data collection
- Search functionality for specific laureates
- Filter by year range
- Export laureate information
- Additional biographical details
- University/institution affiliations
- Timeline view of prizes over the years
