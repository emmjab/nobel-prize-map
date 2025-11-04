# Manual Review Workflow - Simplified!

## Overview
You only need to research and provide **location text** (institutions or cities).
The pipeline will **automatically geocode** them to get coordinates!

## Step-by-Step Process

### 1. Review the List
Open: `pipeline/data/needs_manual_review.csv`

**271 laureates** need work location data (API had no affiliation information).

### 2. Research & Fill In
For each laureate, research their work location and fill in the `work_location_manual` column.

**Examples:**
- `MIT, Cambridge, MA, USA`
- `Stanford University, California`
- `University of Cambridge, UK`
- `Paris, France`
- `Tokyo, Japan`

**No need to find coordinates!** Just provide a location string the geocoder can understand.

### 3. Add to manual_overrides.json
Convert your CSV entries to JSON format:

```json
{
  "physics_2017_941": {
    "work_location": "MIT, Cambridge, MA, USA",
    "note": "Worked at LIGO/MIT"
  },
  "chemistry_1993_278": {
    "work_location": "La Jolla, California",
    "note": "Worked at UCSD"
  }
}
```

### 4. Run the Pipeline
```bash
cd nobel_map
source venv/bin/activate
python run_pipeline.py
```

The pipeline will:
1. Load your manual overrides
2. **Automatically geocode** each work_location
3. Apply the coordinates to the data
4. Generate the final `nobel_data_complete.json`

### 5. Check Results
The script will show:
```
Processing: Rainer Weiss (physics_2017_941)
  Work location: MIT, Cambridge, MA, USA
  Geocoding...
  ✅ Geocoded to: (42.3582529, -71.0966272)
```

If geocoding fails for any location, you'll see a warning and can manually provide coordinates in the old format:
```json
{
  "laureate_id_123": {
    "work_location": "Some Hard to Find Place",
    "work_lat": 12.3456,
    "work_lon": -78.9012,
    "note": "Manually provided coordinates"
  }
}
```

## Data Sources Priority

The pipeline tracks where data came from:
1. **API** (73.6% of laureates) - Original Nobel Prize API data
2. **nobelprize.org** - Scraped from official website
3. **Wikipedia** - Scraped from Wikipedia
4. **Manual** - Your manual overrides
5. **Birth fallback** - Used birth location (needs fixing)

## Current Status

- ✅ **755 laureates (73.6%)** - Have good data from API
- ⚠️  **271 laureates (26.4%)** - Need manual review (your task!)
- ⚠️  **237 laureates (23.1%)** - Suspicious (geocoding failed)

## Tips for Research

Good sources for finding work locations:
1. **NobelPrize.org** - Official Nobel Prize website
2. **Wikipedia** - Usually has institution info in infobox
3. **University websites** - Look for faculty pages
4. **Google Scholar** - Shows institutional affiliations
5. **News articles** - About the prize announcement

For **Literature** and **Peace** laureates without institutional affiliations:
- Use their primary residence city at time of award
- Or the city where they did their notable work
- Note the source in the `notes` column

## Example Manual Overrides

```json
{
  "_comment": "Manual fixes for Nobel Prize laureate work locations",

  "physics_2017_941": {
    "work_location": "MIT, Cambridge, MA, USA",
    "note": "LIGO Scientific Collaboration, MIT"
  },

  "literature_1901_569": {
    "work_location": "Paris, France",
    "note": "French poet, lived and worked in Paris"
  },

  "peace_1901_462": {
    "work_location": "Geneva, Switzerland",
    "note": "Founded International Committee of the Red Cross in Geneva"
  }
}
```

## Need Help?

- **Geocoding failed?** Try being more specific: "Cambridge, Massachusetts, USA" instead of just "Cambridge"
- **Multiple affiliations?** Use the primary one at time of award
- **Unsure?** Leave a note in the `notes` field explaining uncertainty
