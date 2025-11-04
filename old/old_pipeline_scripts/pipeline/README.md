# Nobel Prize Data Pipeline

This directory contains the data processing pipeline for Nobel Prize laureate data.

## Pipeline Stages

### 1. Fetch (`01_fetch_from_api.py`)
- Fetches data from Nobel Prize API v1
- Tracks which laureates have affiliation data from API
- Marks laureates needing enrichment
- Output: `data/01_raw_from_api.json`

### 2. Enrich from NobelPrize.org (`02_enrich_from_nobelprize_org.py`)
- Scrapes nobelprize.org for missing affiliations
- Only processes laureates marked as needing enrichment
- Output: `data/02_enriched_nobelprize_org.json`

### 3. Enrich from Wikipedia (`03_enrich_from_wikipedia.py`)
- Scrapes Wikipedia for remaining missing affiliations
- Only processes laureates still needing enrichment
- Output: `data/03_enriched_wikipedia.json`

### 4. Fix Geocoding (`04_fix_geocoding.py`)
- Fixes known geocoding issues (Cambridge, historical names, etc.)
- Output: `data/04_fixed_geocoding.json`

### 5. Apply Manual Overrides (`05_apply_manual_overrides.py`)
- Applies manually curated fixes from `manual_overrides.json`
- Output: `data/05_with_manual_overrides.json`

### 6. Validate (`06_validate.py`)
- Validates data quality
- Generates reports and statistics
- Output: `data/nobel_data_complete.json` (final)
- Output: `data/needs_manual_review.json` (for manual fixing)

## Running the Pipeline

Run the entire pipeline:
```bash
python run_pipeline.py
```

Or run individual stages:
```bash
python pipeline/01_fetch_from_api.py
python pipeline/02_enrich_from_nobelprize_org.py
# etc.
```

## Manual Overrides

The pipeline automatically geocodes work locations, so you only need to provide the location text!

### Easy Way: Edit CSV
1. Open `pipeline/data/needs_manual_review.csv` in Excel/Google Sheets
2. Fill in the `work_location_manual` column with institution or city names
3. The script will automatically geocode them when you run the pipeline

### Direct Way: Edit JSON
Edit `manual_overrides.json` to add manual fixes:
```json
{
  "physics_2017_941": {
    "work_location": "MIT, Cambridge, MA, USA",
    "note": "Worked at LIGO/MIT"
  }
}
```

The script will automatically geocode "MIT, Cambridge, MA, USA" to get the lat/lon coordinates!

**No need to manually look up coordinates** - just provide:
- Institution names: "MIT, Cambridge, MA, USA" or "Stanford University, CA"
- City names: "Paris, France" or "New York, NY, USA"
- Any location string that a geocoder can understand
