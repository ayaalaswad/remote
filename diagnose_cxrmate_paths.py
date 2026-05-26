"""
Diagnose what CXRMate is looking for and where files actually are
"""

import os
from pathlib import Path

def check_file(path, description):
    """Check if a file exists and show its size"""
    if os.path.exists(path):
        size_mb = os.path.getsize(path) / (1024 * 1024)
        print(f"  ✓ {description}")
        print(f"    Path: {path}")
        print(f"    Size: {size_mb:.1f} MB")
        return True
    else:
        print(f"  ✗ {description} NOT FOUND")
        print(f"    Expected: {path}")
        return False

def main():
    print("="*80)
    print("CXRMate Path Diagnosis")
    print("="*80)
    print()

    # Check config dataset_dir
    dataset_dir = Path("D:/datasets/mimic-cxr-jpg")
    print(f"Config dataset_dir: {dataset_dir}")
    print()

    # Check what exists in dataset_dir
    print("[1] Checking files in dataset_dir...")
    print()

    files_to_check = [
        (dataset_dir / "mimic-cxr-2.0.0-split.csv.gz", "Split CSV (original)"),
        (dataset_dir / "mimic-cxr-2.0.0-split.csv", "Split CSV (uncompressed)"),
        (dataset_dir / "mimic-cxr-2.0.0-metadata.csv.gz", "Metadata CSV (original)"),
        (dataset_dir / "mimic-cxr-2.0.0-metadata.csv", "Metadata CSV (uncompressed)"),
        (dataset_dir / "mimic_cxr_sectioned" / "mimic_cxr_sectioned.csv", "Sectioned reports CSV"),
    ]

    for file_path, description in files_to_check:
        check_file(file_path, description)

    print()
    print("[2] Checking files in parent dataset directory...")
    print()

    parent_dir = Path("D:/datasets")
    files_to_check_parent = [
        (parent_dir / "mimic_cxr_merged" / "splits_reports_metadata.csv", "Merged CSV"),
        (parent_dir / "mimic_cxr_sectioned" / "mimic_cxr_sectioned.csv", "Sectioned CSV (parent level)"),
    ]

    for file_path, description in files_to_check_parent:
        check_file(file_path, description)

    print()
    print("[3] Checking directory structure...")
    print()

    dirs_to_check = [
        (dataset_dir / "files", "Image files directory"),
        (dataset_dir / "physionet.org" / "files" / "mimic-cxr-jpg" / "2.0.0" / "files", "PhysioNet structure"),
        (parent_dir / "physionet.org" / "files" / "mimic-cxr-jpg" / "2.0.0", "PhysioNet structure (parent)"),
    ]

    for dir_path, description in dirs_to_check:
        if os.path.exists(dir_path):
            print(f"  ✓ {description} exists")
            print(f"    Path: {dir_path}")
        else:
            print(f"  ✗ {description} does not exist")
            print(f"    Expected: {dir_path}")

    print()
    print("="*80)
    print("Possible Issues")
    print("="*80)
    print()
    print("CXRMate might be looking for:")
    print("  1. Files in a 'physionet.org/files/mimic-cxr-jpg/2.0.0/' subdirectory")
    print("  2. Split/metadata CSVs in parent 'D:/datasets/' directory")
    print("  3. Uncompressed .csv files (not .csv.gz)")
    print()
    print("Next step: Check CXRMate code to see exact path expectations")
    print()

if __name__ == "__main__":
    main()
