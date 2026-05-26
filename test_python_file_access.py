"""
Test if Python can actually access the files from CXRMate's working directory
"""

import os
import sys

# Change to CXRMate's working directory (where it runs from)
cxrmate_dir = r"C:\Users\aya.alaswad\remote\cxrmate"
os.chdir(cxrmate_dir)

print("="*80)
print("Testing File Access from CXRMate Working Directory")
print("="*80)
print()
print(f"Current working directory: {os.getcwd()}")
print()

# Test the exact path construction CXRMate uses
dataset_dir = "D:/datasets/physionet.org/files/mimic-cxr-jpg/2.0.0"
print(f"Dataset dir: {dataset_dir}")
print()

# Test base_splits_path construction (lines 272-278)
base_splits_path = os.path.join(
    dataset_dir,
    'mimic-cxr-2.0.0-split'
)

print(f"base_splits_path: {base_splits_path}")
print()

# Test the exact checks CXRMate does (lines 280-283)
csv_path = base_splits_path + '.csv'
csv_gz_path = base_splits_path + '.csv.gz'

print(f"Testing: {csv_path}")
print(f"  os.path.exists(): {os.path.exists(csv_path)}")
print(f"  os.path.isfile(): {os.path.isfile(csv_path)}")
print()

print(f"Testing: {csv_gz_path}")
print(f"  os.path.exists(): {os.path.exists(csv_gz_path)}")
print(f"  os.path.isfile(): {os.path.isfile(csv_gz_path)}")
if os.path.exists(csv_gz_path):
    print(f"  File size: {os.path.getsize(csv_gz_path):,} bytes")
print()

# Test mimic_cxr_sections path
reports_path = os.path.join(dataset_dir, 'mimic_cxr_sections', 'mimic_cxr_sectioned.csv')
print(f"Testing: {reports_path}")
print(f"  os.path.exists(): {os.path.exists(reports_path)}")
print()

# Test with current name (mimic_cxr_sectioned)
reports_path_current = os.path.join(dataset_dir, 'mimic_cxr_sectioned', 'mimic_cxr_sectioned.csv')
print(f"Testing (current): {reports_path_current}")
print(f"  os.path.exists(): {os.path.exists(reports_path_current)}")
print()

# Test metadata
base_metadata_path = os.path.join(dataset_dir, 'mimic-cxr-2.0.0-metadata')
metadata_csv_gz = base_metadata_path + '.csv.gz'
print(f"Testing: {metadata_csv_gz}")
print(f"  os.path.exists(): {os.path.exists(metadata_csv_gz)}")
print()

print("="*80)
print("Summary")
print("="*80)
if os.path.exists(csv_gz_path):
    print("✓ Split CSV accessible from CXRMate working directory")
else:
    print("✗ Split CSV NOT accessible - junction/path issue")

if os.path.exists(metadata_csv_gz):
    print("✓ Metadata CSV accessible")
else:
    print("✗ Metadata CSV NOT accessible")

if os.path.exists(reports_path):
    print("✓ Reports CSV accessible (mimic_cxr_sections)")
elif os.path.exists(reports_path_current):
    print("! Reports CSV exists but wrong name (mimic_cxr_sectioned)")
    print("  Need to rename junction to mimic_cxr_sections")
else:
    print("✗ Reports CSV NOT accessible")
print()
