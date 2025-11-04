#!/usr/bin/env python3
"""
Run the full Nobel Prize data pipeline from start to finish
"""
import subprocess
import sys
import os
import time

def run_stage(stage_number, script_name, description):
    """Run a single pipeline stage"""
    print("\n" + "=" * 100)
    print(f"STAGE {stage_number}: {description}")
    print("=" * 100)

    start_time = time.time()

    try:
        result = subprocess.run(
            ['python', script_name],
            cwd='/Users/emma/Documents/file_cabinet/people_projects/emma/nobel_map',
            check=True,
            capture_output=False,
            text=True
        )

        elapsed = time.time() - start_time
        print(f"\n✅ Stage {stage_number} completed in {elapsed:.1f} seconds")
        return True

    except subprocess.CalledProcessError as e:
        elapsed = time.time() - start_time
        print(f"\n❌ Stage {stage_number} FAILED after {elapsed:.1f} seconds")
        print(f"Error: {e}")
        return False

def main():
    print("=" * 100)
    print("NOBEL PRIZE DATA PIPELINE - FULL RUN")
    print("=" * 100)
    print("\nThis will run the complete pipeline from API fetch to final output.")
    print("Expected time: 30-60 minutes (due to API rate limiting)\n")

    response = input("Continue? (yes/no): ")
    if response.lower() not in ['yes', 'y']:
        print("Aborted.")
        return

    pipeline_start = time.time()

    stages = [
        (1, 'pipeline/01_fetch_from_api.py', 'Fetch data from Nobel Prize API'),
        (2, 'pipeline/02_enrich_from_nobelprize_org.py', 'Enrich from nobelprize.org'),
        (3, 'pipeline/03_enrich_from_wikipedia.py', 'Enrich from Wikipedia'),
        (4, 'pipeline/04_fix_geocoding.py', 'Fix geocoding errors'),
        (5, 'pipeline/05_apply_manual_overrides.py', 'Apply manual overrides'),
        (6, 'pipeline/06_validate.py', 'Validate final data'),
    ]

    completed = []
    failed = []

    for stage_num, script, desc in stages:
        success = run_stage(stage_num, script, desc)

        if success:
            completed.append(f"Stage {stage_num}: {desc}")
        else:
            failed.append(f"Stage {stage_num}: {desc}")
            print(f"\n❌ Pipeline stopped at stage {stage_num}")
            break

    # Summary
    total_time = time.time() - pipeline_start

    print("\n" + "=" * 100)
    print("PIPELINE SUMMARY")
    print("=" * 100)

    print(f"\n✅ Completed ({len(completed)}):")
    for item in completed:
        print(f"  - {item}")

    if failed:
        print(f"\n❌ Failed ({len(failed)}):")
        for item in failed:
            print(f"  - {item}")

    print(f"\nTotal time: {total_time/60:.1f} minutes")

    if len(completed) == len(stages):
        print("\n🎉 Pipeline completed successfully!")
        print("\nFinal output:")
        print("  - pipeline/data/06_validated.json")
        print("\nTo copy to main location:")
        print("  cp pipeline/data/06_validated.json nobel_data_complete.json")
    else:
        print("\n⚠️  Pipeline incomplete. Check errors above.")

    print("=" * 100)

if __name__ == '__main__':
    main()
