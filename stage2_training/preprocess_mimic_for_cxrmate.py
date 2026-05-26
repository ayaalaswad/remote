"""
Stage 2 Preprocessing: Prepare MIMIC-CXR data for CXRMate (Option A - Proper)

This script:
1. Extracts Findings and Impression sections from raw reports
2. Creates mimic_cxr_sectioned.csv
3. Creates splits_reports_metadata.csv (merged)
4. Organizes directory structure for CXRMate

Based on MIT-LCP MIMIC-CXR section extraction approach.
"""

import pandas as pd
import numpy as np
from pathlib import Path
import re
from tqdm import tqdm
import gzip
import json

def extract_sections_from_report(report_text):
    """
    Extract Findings and Impression sections from a radiology report.

    Based on MIT-LCP/mimic-cxr section extraction logic.

    Args:
        report_text: Full report text

    Returns:
        findings: Findings section text
        impression: Impression section text
    """
    if not report_text or pd.isna(report_text):
        return "", ""

    # Convert to lowercase for matching
    text = report_text.strip()
    text_lower = text.lower()

    # Common section headers
    findings_headers = [
        'findings:', 'finding:', 'findings and impression:',
        'exam:', 'examination:', 'report:', 'findings/impression:'
    ]

    impression_headers = [
        'impression:', 'impressions:', 'conclusion:',
        'conclusions:', 'summary:', 'assessment:'
    ]

    # Find impression section first (usually at end)
    impression = ""
    impression_start = -1

    for header in impression_headers:
        idx = text_lower.find(header)
        if idx != -1:
            impression_start = idx + len(header)
            # Extract from header to end
            impression = text[impression_start:].strip()
            break

    # Find findings section (usually before impression)
    findings = ""

    for header in findings_headers:
        idx = text_lower.find(header)
        if idx != -1:
            findings_start = idx + len(header)
            # Extract from header to impression (or end if no impression)
            if impression_start > 0:
                findings = text[findings_start:impression_start].strip()
                # Remove impression header from findings
                for imp_header in impression_headers:
                    findings = findings.replace(imp_header, '').strip()
            else:
                findings = text[findings_start:].strip()
            break

    # If no headers found, use heuristics
    if not findings and not impression:
        # If text is short, assume it's all impression
        if len(text) < 200:
            impression = text
        else:
            # Split roughly in half (common for reports without headers)
            lines = text.split('\n')
            mid = len(lines) // 2
            findings = '\n'.join(lines[:mid]).strip()
            impression = '\n'.join(lines[mid:]).strip()

    # Clean up
    findings = re.sub(r'\s+', ' ', findings).strip()
    impression = re.sub(r'\s+', ' ', impression).strip()

    return findings, impression

def process_reports(reports_dir, output_path):
    """
    Process all MIMIC-CXR reports and extract sections.

    Args:
        reports_dir: Path to mimic-cxr-reports/reports/files
        output_path: Where to save mimic_cxr_sectioned.csv
    """
    print("="*70)
    print("Step 1: Extracting Report Sections")
    print("="*70)
    print(f"Reports directory: {reports_dir}")
    print(f"Output: {output_path}")
    print()

    # Find all report files
    reports_dir = Path(reports_dir)
    report_files = list(reports_dir.glob("p*/p*/s*/*.txt"))

    print(f"Found {len(report_files)} report files")

    results = []

    for report_file in tqdm(report_files, desc="Processing reports"):
        # Parse path: p10/p10000032/s50414267/s50414267.txt
        parts = report_file.parts
        study_id = parts[-2]  # s50414267
        patient_id = parts[-3]  # p10000032

        # Read report
        try:
            with open(report_file, 'r', encoding='utf-8') as f:
                report_text = f.read()
        except Exception as e:
            print(f"Error reading {report_file}: {e}")
            continue

        # Extract sections
        findings, impression = extract_sections_from_report(report_text)

        results.append({
            'study_id': study_id,
            'patient_id': patient_id,
            'findings': findings,
            'impression': impression,
            'full_report': report_text
        })

    # Create DataFrame
    df = pd.DataFrame(results)

    print(f"\nExtracted sections from {len(df)} reports")
    print(f"  - Reports with findings: {(df['findings'] != '').sum()}")
    print(f"  - Reports with impression: {(df['impression'] != '').sum()}")

    # Save
    df.to_csv(output_path, index=False)
    print(f"\nSaved: {output_path}")

    return df

def merge_splits_reports_metadata(mimic_cxr_dir, sectioned_csv, output_path):
    """
    Merge splits, reports, and metadata into one CSV for CXRMate.

    Args:
        mimic_cxr_dir: Path to D:/datasets/mimic-cxr-jpg
        sectioned_csv: Path to mimic_cxr_sectioned.csv
        output_path: Where to save splits_reports_metadata.csv
    """
    print("\n" + "="*70)
    print("Step 2: Merging Splits, Reports, and Metadata")
    print("="*70)

    mimic_cxr_dir = Path(mimic_cxr_dir)

    # Load splits
    print("Loading splits...")
    splits_file = mimic_cxr_dir / 'mimic-cxr-2.0.0-split.csv.gz'
    splits_df = pd.read_csv(splits_file)
    print(f"  Loaded {len(splits_df)} studies")

    # Load metadata
    print("Loading metadata...")
    metadata_file = mimic_cxr_dir / 'mimic-cxr-2.0.0-metadata.csv.gz'
    metadata_df = pd.read_csv(metadata_file)
    print(f"  Loaded {len(metadata_df)} studies")

    # Load sectioned reports
    print("Loading sectioned reports...")
    reports_df = pd.read_csv(sectioned_csv)
    print(f"  Loaded {len(reports_df)} reports")

    # Convert study_id to match (remove 's' prefix for merging)
    reports_df['study_id_int'] = reports_df['study_id'].str.replace('s', '').astype(int)

    # Merge splits + metadata
    print("\nMerging splits and metadata...")
    merged = pd.merge(splits_df, metadata_df, on=['subject_id', 'study_id'], how='left')
    print(f"  After merge: {len(merged)} rows")

    # Merge with reports
    print("Merging with sectioned reports...")
    merged = pd.merge(merged, reports_df,
                     left_on='study_id', right_on='study_id_int',
                     how='left', suffixes=('', '_report'))
    print(f"  After merge: {len(merged)} rows")

    # Drop unnecessary columns
    columns_to_keep = [
        'subject_id', 'study_id', 'split',
        'dicom_id', 'ViewPosition', 'StudyDate', 'StudyTime',
        'findings', 'impression', 'patient_id'
    ]

    merged = merged[columns_to_keep]

    # Fill missing reports with empty strings
    merged['findings'] = merged['findings'].fillna('')
    merged['impression'] = merged['impression'].fillna('')

    print(f"\nFinal dataset:")
    print(f"  Total rows: {len(merged)}")
    print(f"  With findings: {(merged['findings'] != '').sum()}")
    print(f"  With impression: {(merged['impression'] != '').sum()}")
    print(f"  Train: {(merged['split'] == 'train').sum()}")
    print(f"  Validate: {(merged['split'] == 'validate').sum()}")
    print(f"  Test: {(merged['split'] == 'test').sum()}")

    # Save
    merged.to_csv(output_path, index=False)
    print(f"\nSaved: {output_path}")

    return merged

def create_directory_structure(dataset_dir, mimic_cxr_dir):
    """
    Create symlinks/junctions to match CXRMate's expected directory structure.

    Args:
        dataset_dir: Base directory (D:/datasets)
        mimic_cxr_dir: Path to mimic-cxr-jpg
    """
    print("\n" + "="*70)
    print("Step 3: Creating Directory Structure")
    print("="*70)

    dataset_dir = Path(dataset_dir)
    mimic_cxr_dir = Path(mimic_cxr_dir)

    # Create physionet.org structure
    physionet_dir = dataset_dir / 'physionet.org' / 'files' / 'mimic-cxr-jpg' / '2.0.0'
    physionet_dir.mkdir(parents=True, exist_ok=True)

    print(f"Created: {physionet_dir}")

    # Create symlinks for CSV files
    csv_files = [
        'mimic-cxr-2.0.0-split.csv.gz',
        'mimic-cxr-2.0.0-metadata.csv.gz',
        'mimic-cxr-2.0.0-chexpert.csv.gz',
        'mimic-cxr-2.0.0-negbio.csv.gz'
    ]

    for csv_file in csv_files:
        src = mimic_cxr_dir / csv_file
        dst = physionet_dir / csv_file

        if src.exists() and not dst.exists():
            # Copy file (symlinks don't work well on Windows for files)
            import shutil
            shutil.copy2(src, dst)
            print(f"  Copied: {csv_file}")

    # Create junction for files/ directory (images)
    files_src = mimic_cxr_dir / 'files'
    files_dst = physionet_dir / 'files'

    if files_src.exists() and not files_dst.exists():
        import subprocess
        try:
            # Use mklink /J for directory junction on Windows
            subprocess.run(['mklink', '/J', str(files_dst), str(files_src)],
                          shell=True, check=True)
            print(f"  Created junction: files/ -> {files_src}")
        except Exception as e:
            print(f"  Warning: Could not create junction: {e}")
            print(f"  Manual step needed: mklink /J \"{files_dst}\" \"{files_src}\"")

    print("\nDirectory structure ready!")

def main():
    # Paths
    reports_dir = Path('D:/datasets/mimic-cxr-reports/reports/files')
    mimic_cxr_dir = Path('D:/datasets/mimic-cxr-jpg')
    dataset_dir = Path('D:/datasets')

    # Output directories
    sections_dir = dataset_dir / 'mimic_cxr_sections'
    sections_dir.mkdir(exist_ok=True)

    merged_dir = dataset_dir / 'mimic_cxr_merged'
    merged_dir.mkdir(exist_ok=True)

    # Output files
    sectioned_csv = sections_dir / 'mimic_cxr_sectioned.csv'
    merged_csv = merged_dir / 'splits_reports_metadata.csv'

    print("="*70)
    print("MIMIC-CXR Preprocessing for CXRMate (Option A - Proper)")
    print("="*70)
    print("\nThis will:")
    print("  1. Extract Findings/Impression sections from raw reports")
    print("  2. Create mimic_cxr_sectioned.csv")
    print("  3. Merge splits + metadata + reports")
    print("  4. Create directory structure for CXRMate")
    print()
    print("Estimated time: 30-60 minutes")
    print()

    # Step 1: Extract sections
    if not sectioned_csv.exists():
        sectioned_df = process_reports(reports_dir, sectioned_csv)
    else:
        print(f"Sectioned CSV already exists: {sectioned_csv}")
        print("Loading existing file...")
        sectioned_df = pd.read_csv(sectioned_csv)
        print(f"  Loaded {len(sectioned_df)} reports")

    # Step 2: Merge everything
    if not merged_csv.exists():
        merged_df = merge_splits_reports_metadata(mimic_cxr_dir, sectioned_csv, merged_csv)
    else:
        print(f"\nMerged CSV already exists: {merged_csv}")
        merged_df = pd.read_csv(merged_csv)
        print(f"  Loaded {len(merged_df)} rows")

    # Step 3: Create directory structure
    create_directory_structure(dataset_dir, mimic_cxr_dir)

    print("\n" + "="*70)
    print("Preprocessing Complete!")
    print("="*70)
    print("\nCreated files:")
    print(f"  1. {sectioned_csv}")
    print(f"  2. {merged_csv}")
    print(f"  3. D:/datasets/physionet.org/files/mimic-cxr-jpg/2.0.0/")
    print()
    print("Now update CXRMate configs:")
    print("  dataset_dir: D:/datasets")
    print()
    print("Then run Stage 2 training!")

if __name__ == '__main__':
    main()
