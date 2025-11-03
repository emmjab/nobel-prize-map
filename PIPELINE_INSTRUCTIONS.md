# Nobel Prize Data Pipeline - Instructions

## Current Status

✅ **Backup created**: `backups/nobel_data_complete_backup_20251103_103225.json`
✅ **Root cause bug fixed**: `pipeline/01_fetch_from_api.py` line 129
✅ **Comprehensive stage 4 created**: `pipeline/04_fix_geocoding.py` with 4 integrated fixes
✅ **Pipeline runner created**: `run_full_pipeline.py`
✅ **Comparison tool created**: `compare_data.py`

## How to Run the Full Pipeline

### Step 1: Run the complete pipeline

```bash
cd /Users/emma/Documents/file_cabinet/people_projects/emma/nobel_map
source venv/bin/activate
python run_full_pipeline.py
```

This will:
- Stage 1: Fetch from Nobel Prize API (with bug fix - no longer copies birth coords to work coords)
- Stage 2: Enrich from nobelprize.org
- Stage 3: Enrich from Wikipedia
- Stage 4: Fix geocoding (4 comprehensive fixes)
- Stage 5: Apply manual overrides
- Stage 6: Validate final data

**Expected time**: 30-60 minutes (due to API rate limiting)

Final output will be in: `pipeline/data/06_validated.json`

### Step 2: Compare with backup

After the pipeline completes, compare the new output with your backup:

```bash
python compare_data.py \
  backups/nobel_data_complete_backup_20251103_103225.json \
  pipeline/data/06_validated.json \
  comparison_report.json
```

This will show you:
- Entries only in backup or only in new data
- Work location text changes
- Coordinate changes (with distance calculations)
- Which changes are improvements vs regressions

### Step 3: Analyze the comparison report

The comparison will print a summary and save detailed differences to `comparison_report.json`.

**What to look for:**
- **Coordinate fixes**: Should see many entries where coordinates changed to match location text better
- **Cambridge fixes**: MIT/Harvard laureates should now have Cambridge, MA coords (not UK)
- **Suspicious (0,0) fixes**: Should see entries that previously had (0,0) now have real coordinates
- **Regressions**: If backup data looks better for any entry, note it for pipeline adjustment

### Step 4: Review and iterate

Based on the comparison:

1. **If new data is better**: Copy it to production
   ```bash
   cp pipeline/data/06_validated.json nobel_data_complete.json
   ```

2. **If backup has better data for some entries**:
   - Note which entries and why
   - Add them to `manual_overrides.json`
   - Re-run the pipeline

3. **If you find new issues**:
   - Add new fix logic to `pipeline/04_fix_geocoding.py`
   - Or add to manual overrides
   - Re-run the pipeline

## Key Fixes in Stage 4

1. **Fix suspicious (0,0) coordinates**: Re-geocodes any entry with (0,0) coords
2. **Fix Cambridge confusion**: Corrects MIT/Harvard vs Cambridge UK mix-ups
3. **Extract clean locations**: Removes institution names, keeps just "City, Country"
4. **Verify all coordinates**: Re-geocodes all work_location strings to ensure coords match text

## What Changed vs Previous Approach

**Old bug (now fixed)**:
```python
if not work_coords:
    work_coords = birth_coords  # ❌ Silent data corruption
```

**New approach**:
```python
if not work_coords:
    work_coords = (0, 0)  # ✓ Flags for re-geocoding in stage 4
```

This prevents cases like Julius Axelrod where location text was "Bethesda, MD" but coordinates were NYC (from birth location).

## Files Reference

- `run_full_pipeline.py` - Master script to run all stages
- `compare_data.py` - Compare two data files
- `pipeline/01_fetch_from_api.py` - Fetch from API (bug fixed)
- `pipeline/04_fix_geocoding.py` - Comprehensive geocoding fixes
- `backups/` - Your backup data for comparison
- `pipeline/data/` - Intermediate and final output files
