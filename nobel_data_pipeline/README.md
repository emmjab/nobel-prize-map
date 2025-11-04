# Nobel Data Pipeline

This directory contains the scripts used to generate the `nobel_data_complete.json` file that powers the Nobel Prize Map application.

## Pipeline Overview

The pipeline consists of 4 steps:

1. **Fetch from API** (automated)
2. **Generate CSV for manual entry** (automated)
3. **Manual data entry** (manual)
* run geocoding on the manually edited csv file so that the manually added location text can be geocoded
* check the file to manually add geocodes for locations that failed
4. **Merge to final JSON** (automated)

---

## Step-by-Step Process

### 1. Fetch Raw Data from Nobel Prize API

**Script:** `01_fetch_from_api.py`

Fetches raw laureate data from the Nobel Prize API v2.1.

**Output:**
- `../pipeline/data/01_raw_from_api.json` - Raw data including metadata (achievement, shared prizes, etc.)

**Run:**
```bash
python 01_fetch_from_api.py
```

---

### 2. Generate CSV for Manual Entry

**Script:** `create_data_csv.py`

Creates a CSV file from the API JSON data to facilitate manual data entry for missing locations and coordinates.

**Inputs:**
- `../pipeline/data/01_raw_from_api.json` - Raw API data
- `../work_locations_to_fill.csv` - Previously manually-filled work locations (merged in)

**Output:**
- `../laureates_data_to_fill.csv` - CSV showing which birth/work locations and coordinates need to be filled in

**Run:**
```bash
python create_data_csv.py
```

**Note:** I don't remmeber which script I initially ran to generate the work_locations_to_fill.csv file.
**Note:** But I ran it back when the raw data was coming from the Nobel API v1. Now using v2.
**Note:** Actually I think what happened is during the pipeline it wanted to generate a .json file with manual_overrides,
          but I wanted a csv file, so i got it to convert the .json to .csv, and then I made a copy of that file which I
          then made the edits to, because I didn't want to lose the list of people who didn't have data to begin with.
**Note:** Sigh. How am I going to account for that in here...
---

### 3. Manual Data Entry

**Manual step** - Fill in missing birth/work locations and coordinates in the CSV file.

**Input:** `../laureates_data_to_fill.csv`

**Process:**
- Open CSV in spreadsheet editor
- Fill in missing `birth_location`, `work_location`, and coordinate fields
- Save completed file

**Output:** `../laureates_data_to_fill_filledcoords_final.csv`

**Note:** Due to character encoding issues encountered during this process, multiple copies were created with different filename extensions. The final working version is `laureates_data_to_fill_filledcoords_final.csv`.

---

**Note:** There was another step at the end of this one where i ran a script to add geocoded locations to manually added location text in the csv file.
**Note:** I don't remember which script this was, but that's how I found out about the encoding issues.

---

### 4. Merge to Final JSON

**Script:** `create_nobel_complete_from_csv.py`

Creates the final `nobel_data_complete.json` by merging:
- Metadata from the API (achievement, shared prizes, etc.)
- Corrected location names and coordinates from the manually-filled CSV

**Inputs:**
- `../pipeline/data/01_raw_from_api.json` - API metadata
- `../laureates_data_to_fill_filledcoords_final.csv` - Corrected locations and coordinates

**Output:**
- `../nobel_data_complete.json` - **Final file served by the Flask application**

**Run:**
```bash
python create_nobel_complete_from_csv.py
```

---

## Quick Start

To regenerate the data from scratch:

```bash
# Step 1: Fetch from API
python 01_fetch_from_api.py

# Step 2: Generate CSV
python create_data_csv.py

# Step 3: Manually fill in the CSV
# Open laureates_data_to_fill.csv and complete the missing data

# Step 4: Merge to final JSON
python create_nobel_complete_from_csv.py
```

---

## Data Files

### Input Files
- `../pipeline/data/01_raw_from_api.json` - Raw Nobel Prize API data
- `../work_locations_to_fill.csv` - Previously filled work locations
- `../laureates_data_to_fill_filledcoords_final.csv` - Manually corrected locations

### Output File
- `../nobel_data_complete.json` - Final JSON file served by Flask app (1026 laureates)

---

## Notes

- The `pipeline/` directory contains additional experimental scripts that were used for exploration but are not part of the final pipeline.
- All other `fix_*.py` and `geocode_*.py` scripts in the parent directory were exploratory work and are not part of the production pipeline.
- Character encoding: UTF-8 should be used for all CSV files to handle international characters in laureate names and location names.
