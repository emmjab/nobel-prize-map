# Automated Work Location Search

This script uses Claude API to automatically search for work locations of the 271 Nobel laureates that need manual review.

## Setup

### 1. Install required package

```bash
cd /Users/emma/Documents/file_cabinet/people_projects/emma/nobel_map
source venv/bin/activate
pip install anthropic
```

### 2. Set your API key

You need an Anthropic API key. Set it as an environment variable:

```bash
export ANTHROPIC_API_KEY='your-api-key-here'
```

Or add it permanently to your shell config:

```bash
# For bash
echo "export ANTHROPIC_API_KEY='your-api-key-here'" >> ~/.bashrc
source ~/.bashrc

# For zsh
echo "export ANTHROPIC_API_KEY='your-api-key-here'" >> ~/.zshrc
source ~/.zshrc
```

## Running the Script

```bash
cd /Users/emma/Documents/file_cabinet/people_projects/emma/nobel_map
source venv/bin/activate
python search_work_locations_with_claude.py
```

## What it does

1. **Loads laureates** from `pipeline/data/needs_manual_review.json` (271 laureates)
2. **Checks existing results** in `pipeline/data/search_results_work_locations.json`
3. **Skips already processed** laureates (currently 35 done)
4. **For each remaining laureate:**
   - Uses Claude Haiku (fast & cheap) to search for their work location
   - Asks Claude to find where they did their Nobel Prize-winning work
   - Extracts: work_location, confidence level, and source note
5. **Saves incrementally** after each laureate (won't lose progress if interrupted)
6. **Shows progress** every 10 laureates

## Output

Results are saved to: `pipeline/data/search_results_work_locations.json`

Format:
```json
{
  "laureate_id": {
    "name": "Name",
    "work_location": "Institution, City, Country",
    "confidence": "high/medium/low",
    "source": "Brief explanation"
  }
}
```

## Cost Estimate

- Using Claude 3.5 Haiku (cheapest model)
- ~500 tokens per laureate
- 236 remaining laureates
- Estimated cost: ~$0.50-$1.00 total

## Features

- ✅ **Resumable**: Can stop and restart - skips already processed laureates
- ✅ **Safe**: Saves after each laureate - won't lose progress
- ✅ **Progress tracking**: Shows updates every 10 laureates
- ✅ **Rate limiting**: 1 second delay between requests (polite to API)
- ✅ **Error handling**: Captures and logs any failures

## After completion

Once all 271 laureates are processed, the results can be:

1. **Reviewed** - Check confidence levels, fix any low-confidence entries
2. **Geocoded** - Use the existing pipeline stage 5 to geocode locations to lat/lon
3. **Imported** - Add to the main Nobel Prize data via manual_overrides.json

## Troubleshooting

**"ANTHROPIC_API_KEY environment variable not set"**
- Make sure you've exported the API key in your current terminal session
- Or add it to your shell config file

**"Module 'anthropic' not found"**
- Run: `pip install anthropic`

**Script is slow**
- This is normal - it waits 1 second between each request
- Processing 236 laureates will take ~4-5 minutes

**Want to test first?**
- Edit the script and change line with `for i, laureate in enumerate(laureates, 1):`
- To: `for i, laureate in enumerate(laureates[:5], 1):`
- This will only process the first 5 as a test
