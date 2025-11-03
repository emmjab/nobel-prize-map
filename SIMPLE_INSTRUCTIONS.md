# Simple Manual Work Location Entry

## Step 1: Open the CSV file

Open: `work_locations_to_fill.csv`

This file has 236 laureates that need work locations (I already did 35).

Columns:
- `laureate_id` - Don't change this
- `name` - The laureate's name
- `category` - physics, chemistry, literature, etc.
- `year` - Prize year
- `work_location` - **YOU FILL THIS IN**
- `notes` - Optional notes

## Step 2: Fill in work locations

For each row, add the work location in the `work_location` column.

**Examples:**
- `MIT, Cambridge, MA, USA`
- `University of Paris, France`
- `Stockholm, Sweden`
- `Caltech, Pasadena, CA`

**Tips:**
- Just city/institution names - NO need for coordinates!
- The script will geocode them automatically
- You can leave `notes` empty (it's optional)
- Skip any you can't find - fill in what you can

**How to research:**
Google: "where did [name] do his nobel prize winning work [category] [year]"

## Step 3: Convert to JSON

When you're done filling in locations (or want to test with a few):

```bash
cd /Users/emma/Documents/file_cabinet/people_projects/emma/nobel_map
python convert_csv_to_json.py
```

This creates `manual_overrides.json` combining:
- The 35 I already researched
- Whatever you added to the CSV

## Step 4: Run the pipeline

```bash
python run_pipeline.py
```

This will:
- Load your manual overrides
- **Automatically geocode** all work locations to lat/lon
- Generate the final dataset

## Notes

- You don't have to fill in all 236 at once - do as many as you want
- Run `convert_csv_to_json.py` anytime to update
- The script ignores empty rows
- You can always add more later and re-run
