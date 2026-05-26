"""
Debug what paths CXRMate is actually checking
"""

import os
from pathlib import Path

# Simulate what CXRMate does
dataset_dir = Path("D:/datasets/physionet.org/files/mimic-cxr-jpg/2.0.0")

print("="*80)
print("Debugging CXRMate Path Checking")
print("="*80)
print()
print(f"Config dataset_dir: {dataset_dir}")
print()

# Check what CXRMate might be looking for
possible_paths = [
    # Direct in dataset_dir
    dataset_dir / "mimic-cxr-2.0.0-split.csv.gz",
    dataset_dir / "mimic-cxr-2.0.0-split.csv",

    # In parent directories
    dataset_dir.parent / "mimic-cxr-2.0.0-split.csv.gz",
    dataset_dir.parent.parent / "mimic-cxr-2.0.0-split.csv.gz",
    dataset_dir.parent.parent.parent / "mimic-cxr-2.0.0-split.csv.gz",

    # With version number variations
    dataset_dir / "mimic-cxr-split.csv.gz",
    dataset_dir.parent / "mimic-cxr-split.csv.gz",
]

print("Checking possible paths CXRMate might look for:")
print()

for path in possible_paths:
    exists = path.exists()
    symbol = "✓" if exists else "✗"
    if exists:
        size = path.stat().st_size
        print(f"{symbol} EXISTS: {path}")
        print(f"           Size: {size:,} bytes")
    else:
        print(f"{symbol} NOT FOUND: {path}")
    print()

print("="*80)
print("Recommendation:")
print("="*80)
print()
print("Need to check CXRMate single.py line 285 to see exact path it constructs")
print()
