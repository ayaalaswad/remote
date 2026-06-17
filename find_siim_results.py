"""
Find where SIIM training results are actually saved
"""
import os
from pathlib import Path
from datetime import datetime

def find_recent_files(base_path, pattern="*", hours=24):
    """Find files modified in the last N hours"""
    cutoff = datetime.now().timestamp() - (hours * 3600)
    results = []

    for root, dirs, files in os.walk(base_path):
        for file in files:
            filepath = Path(root) / file
            try:
                if filepath.stat().st_mtime > cutoff:
                    results.append(filepath)
            except:
                pass

    return results

print("="*80)
print("Finding SIIM Training Results")
print("="*80)
print()

base_paths = [
    Path("C:/Users/aya.alaswad/remote/BenchX/experiments"),
    Path("C:/Users/aya.alaswad/remote/experiments"),
]

for base_path in base_paths:
    if not base_path.exists():
        continue

    print(f"Searching in: {base_path}")
    print()

    # Find files modified in last 24 hours
    recent_files = find_recent_files(base_path, hours=24)

    # Filter for SIIM-related files
    siim_files = [f for f in recent_files if 'siim' in str(f).lower() or 'sharp' in str(f).lower()]

    if siim_files:
        print(f"Found {len(siim_files)} recent SIIM-related files:")
        print()

        # Group by directory
        by_dir = {}
        for f in siim_files:
            parent = f.parent
            if parent not in by_dir:
                by_dir[parent] = []
            by_dir[parent].append(f)

        for directory, files in sorted(by_dir.items()):
            print(f"Directory: {directory}")
            print(f"  Files ({len(files)}):")
            for f in sorted(files)[:10]:  # Show first 10 files
                size_kb = f.stat().st_size / 1024
                mod_time = datetime.fromtimestamp(f.stat().st_mtime).strftime("%H:%M:%S")
                print(f"    - {f.name} ({size_kb:.1f} KB, modified at {mod_time})")
            if len(files) > 10:
                print(f"    ... and {len(files)-10} more files")
            print()

print("="*80)
print("Looking for specific result files:")
print("="*80)
print()

# Check for specific patterns
patterns_to_check = [
    "experiments/**/SHARP_*pct/**/val_42_hyps.txt",
    "experiments/**/SHARP_*pct/**/val_42_refs.txt",
    "experiments/**/SHARP_*pct/**/*.pt",
    "experiments/**/SHARP_*pct/**/*.pth",
    "experiments/**/SHARP_*pct/**/metrics.json",
    "experiments/**/SHARP_*pct/**/log.txt",
]

for base_path in base_paths:
    if not base_path.exists():
        continue

    print(f"\nSearching in: {base_path}")

    for pattern in patterns_to_check:
        matches = list(base_path.glob(pattern))
        siim_matches = [m for m in matches if 'siim' in str(m).lower()]

        if siim_matches:
            print(f"\n  Pattern: {pattern}")
            for match in siim_matches[:5]:
                rel_path = match.relative_to(base_path)
                print(f"    - {rel_path}")

print()
print("="*80)
print("Checking standard locations:")
print("="*80)

standard_locations = [
    "C:/Users/aya.alaswad/remote/BenchX/experiments/classification/siim/SHARP_1pct",
    "C:/Users/aya.alaswad/remote/BenchX/experiments/classification/siim/SHARP_10pct",
    "C:/Users/aya.alaswad/remote/BenchX/experiments/classification/siim/SHARP_100pct",
]

for loc in standard_locations:
    path = Path(loc)
    print(f"\n{path.name}:")
    if path.exists():
        print(f"  EXISTS: {path}")
        subdirs = [d for d in path.iterdir() if d.is_dir()]
        if subdirs:
            print(f"  Subdirectories:")
            for subdir in subdirs:
                files = list(subdir.iterdir())
                print(f"    - {subdir.name}/ ({len(files)} files)")
    else:
        print(f"  NOT FOUND: {path}")
