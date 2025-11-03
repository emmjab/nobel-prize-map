"""
Nobel Prize Data Pipeline Runner
Orchestrates the entire data processing pipeline
"""
import os
import sys
import subprocess
import json
from datetime import datetime

# Pipeline stages in order
STAGES = [
    ('01_fetch_from_api.py', 'Fetch data from Nobel Prize API'),
    ('02_enrich_from_nobelprize_org.py', 'Enrich from NobelPrize.org'),
    ('03_enrich_from_wikipedia.py', 'Enrich from Wikipedia'),
    ('04_fix_geocoding.py', 'Fix geocoding errors'),
    ('05_apply_manual_overrides.py', 'Apply manual overrides'),
    ('06_validate.py', 'Validate and finalize data'),
]

def print_header(text):
    """Print a formatted header"""
    print("\n" + "=" * 80)
    print(f"  {text}")
    print("=" * 80 + "\n")

def run_stage(script_name, description):
    """Run a single pipeline stage"""
    print_header(f"Stage: {description}")
    script_path = os.path.join('pipeline', script_name)

    if not os.path.exists(script_path):
        print(f"⚠️  Script not found: {script_path}")
        print(f"   Skipping...")
        return False

    try:
        result = subprocess.run(
            [sys.executable, script_path],
            check=True,
            capture_output=True,
            text=True
        )
        print(result.stdout)
        if result.stderr:
            print("Warnings/Errors:")
            print(result.stderr)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed!")
        print(f"Error output:")
        print(e.stderr)
        return False

def main():
    """Run the entire pipeline"""
    start_time = datetime.now()

    print_header("Nobel Prize Data Pipeline")
    print(f"Started at: {start_time.strftime('%Y-%m-%d %H:%M:%S')}\n")

    # Create data directory if it doesn't exist
    os.makedirs('pipeline/data', exist_ok=True)

    completed = []
    failed = []
    skipped = []

    for script_name, description in STAGES:
        success = run_stage(script_name, description)
        if success:
            completed.append(description)
        elif os.path.exists(os.path.join('pipeline', script_name)):
            failed.append(description)
        else:
            skipped.append(description)

        # Stop if a stage fails
        if not success and os.path.exists(os.path.join('pipeline', script_name)):
            print("\n⚠️  Pipeline stopped due to failure")
            break

    # Final summary
    end_time = datetime.now()
    duration = end_time - start_time

    print_header("Pipeline Summary")
    print(f"Completed: {len(completed)}")
    for stage in completed:
        print(f"  ✅ {stage}")

    if skipped:
        print(f"\nSkipped: {len(skipped)}")
        for stage in skipped:
            print(f"  ⏭️  {stage}")

    if failed:
        print(f"\nFailed: {len(failed)}")
        for stage in failed:
            print(f"  ❌ {stage}")

    print(f"\nTotal time: {duration.total_seconds():.1f} seconds")
    print(f"Finished at: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")

    # Check for final output
    final_output = 'nobel_data_complete.json'
    if os.path.exists(final_output):
        print(f"\n✅ Final output: {final_output}")

    # Check for manual review list
    review_list = 'pipeline/data/needs_manual_review.json'
    if os.path.exists(review_list):
        with open(review_list, 'r') as f:
            needs_review = json.load(f)
        print(f"⚠️  {len(needs_review)} laureates need manual review")
        print(f"   See: {review_list}")

    print("=" * 80)

if __name__ == '__main__':
    main()
