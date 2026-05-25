"""
Create missing CSV files for Stage 2 CXRMate training

This script creates CSV files matching the OFFICIAL MIT-LCP MIMIC-CXR format:

1. mimic_cxr_sectioned.csv - Extracted report sections
   Official format (from MIT-LCP/mimic-cxr):
   Columns: ['study', 'impression', 'findings', 'last_paragraph', 'comparison']

2. splits_reports_metadata.csv - Merged splits + metadata + sections
   Combined from:
   - mimic-cxr-2.0.0-split.csv.gz (train/val/test splits)
   - mimic-cxr-2.0.0-metadata.csv.gz (image metadata)
   - mimic_cxr_sectioned.csv (report sections)

Based on MIMIC-CXR v2.0.0 structure.

Reference:
- https://github.com/MIT-LCP/mimic-cxr/blob/master/txt/create_section_files.py
- https://github.com/aehrc/cxrmate
"""

import os
import re
import gzip
import pandas as pd
from pathlib import Path
from tqdm import tqdm


def extract_section(text, section_name):
    """
    Extract a section from a MIMIC-CXR report using MIT-LCP's method.

    This matches the official MIT-LCP section extraction logic from create_section_files.py.

    Args:
        text: Full report text
        section_name: Section to extract (e.g., 'FINDINGS', 'IMPRESSION')

    Returns:
        Extracted section text, or None if not found (to match official format)
    """
    # Pattern to match section header
    # Looks for section name followed by colon or newline
    pattern = rf'\b{section_name}\s*:?\s*\n+(.*?)(?=\n\s*[A-Z]+\s*:|\Z)'

    match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)

    if match:
        section_text = match.group(1).strip()
        # Clean up extra whitespace
        section_text = re.sub(r'\s+', ' ', section_text)
        return section_text if section_text else None

    return None


def find_report_file(patient_id, study_id, reports_base_dir):
    """
    Find the report file for a given patient and study.

    Args:
        patient_id: Patient ID (e.g., 'p10000032' or '10000032')
        study_id: Study ID (e.g., 's50414267' or '50414267')
        reports_base_dir: Base directory for reports

    Returns:
        Path to report file, or None if not found
    """
    # Ensure IDs have correct prefixes
    if not patient_id.startswith('p'):
        patient_id = f'p{patient_id}'
    if not study_id.startswith('s'):
        study_id = f's{study_id}'

    # Extract first 3 characters for directory grouping (e.g., p10 from p10000032)
    p_prefix = patient_id[:3]

    # Construct path: files/p10/p10000032/s50414267.txt
    report_path = Path(reports_base_dir) / "files" / p_prefix / patient_id / f"{study_id}.txt"

    if report_path.exists():
        return report_path

    return None


def create_sectioned_csv(split_csv_path, reports_base_dir, output_path):
    """
    Create mimic_cxr_sectioned.csv with extracted FINDINGS and IMPRESSION.

    Args:
        split_csv_path: Path to mimic-cxr-2.0.0-split.csv.gz
        reports_base_dir: Base directory for report files
        output_path: Where to save mimic_cxr_sectioned.csv

    Returns:
        DataFrame with sectioned reports
    """
    print(f"\n{'='*80}")
    print("Step 1: Creating mimic_cxr_sectioned.csv")
    print(f"{'='*80}\n")

    # Load split CSV to get list of all studies
    print(f"Loading split CSV: {split_csv_path}")
    split_df = pd.read_csv(split_csv_path, compression='gzip')
    print(f"  Found {len(split_df)} studies")

    # Prepare output data
    sectioned_data = []

    # Process each study
    print(f"\nExtracting FINDINGS and IMPRESSION from reports...")

    found_count = 0
    missing_count = 0

    for idx, row in tqdm(split_df.iterrows(), total=len(split_df), desc="Processing reports"):
        subject_id = str(row['subject_id'])
        study_id = str(row['study_id'])

        # Find report file
        report_path = find_report_file(subject_id, study_id, reports_base_dir)

        if report_path is None:
            missing_count += 1
            # Add empty entry
            sectioned_data.append({
                'study': study_id,
                'subject_id': subject_id,
                'findings': '',
                'impression': ''
            })
            continue

        # Read report
        try:
            with open(report_path, 'r', encoding='utf-8') as f:
                report_text = f.read()

            # Extract sections (matching MIT-LCP official format)
            findings = extract_section(report_text, 'FINDINGS')
            impression = extract_section(report_text, 'IMPRESSION')
            comparison = extract_section(report_text, 'COMPARISON')

            # Extract last_paragraph: text from last recognized section to end
            # This is used as fallback for reports without standard sections
            last_paragraph = None
            if report_text:
                # Find the last section marker
                sections = ['FINDINGS', 'IMPRESSION', 'INDICATION', 'HISTORY', 'COMPARISON', 'TECHNIQUE']
                last_section_pos = -1
                for section in sections:
                    match = list(re.finditer(rf'\b{section}\s*:', report_text, re.IGNORECASE))
                    if match:
                        last_section_pos = max(last_section_pos, match[-1].end())

                if last_section_pos > -1:
                    last_para_text = report_text[last_section_pos:].strip()
                    if last_para_text:
                        last_paragraph = re.sub(r'\s+', ' ', last_para_text)

            # Official MIT-LCP format: ['study', 'impression', 'findings', 'last_paragraph', 'comparison']
            sectioned_data.append({
                'study': study_id,
                'impression': impression,
                'findings': findings,
                'last_paragraph': last_paragraph,
                'comparison': comparison
            })

            found_count += 1

        except Exception as e:
            print(f"\n  WARNING: Error reading {report_path}: {e}")
            missing_count += 1
            # Add empty entry with None values (matching official format)
            sectioned_data.append({
                'study': study_id,
                'impression': None,
                'findings': None,
                'last_paragraph': None,
                'comparison': None
            })

    # Create DataFrame with official MIT-LCP column order
    sectioned_df = pd.DataFrame(sectioned_data, columns=['study', 'impression', 'findings', 'last_paragraph', 'comparison'])

    # Save to CSV
    print(f"\nSaving to: {output_path}")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    sectioned_df.to_csv(output_path, index=False)

    print(f"\n✓ Created mimic_cxr_sectioned.csv")
    print(f"  - Total studies: {len(sectioned_df)}")
    print(f"  - Reports found: {found_count}")
    print(f"  - Reports missing: {missing_count}")
    print(f"  - Success rate: {found_count/len(sectioned_df)*100:.1f}%")

    return sectioned_df


def create_merged_csv(split_csv_path, metadata_csv_path, sectioned_df, output_path):
    """
    Create splits_reports_metadata.csv by merging all data.

    Args:
        split_csv_path: Path to mimic-cxr-2.0.0-split.csv.gz
        metadata_csv_path: Path to mimic-cxr-2.0.0-metadata.csv.gz
        sectioned_df: DataFrame from create_sectioned_csv
        output_path: Where to save splits_reports_metadata.csv

    Returns:
        Merged DataFrame
    """
    print(f"\n{'='*80}")
    print("Step 2: Creating splits_reports_metadata.csv")
    print(f"{'='*80}\n")

    # Load split CSV
    print(f"Loading split CSV: {split_csv_path}")
    split_df = pd.read_csv(split_csv_path, compression='gzip')
    print(f"  Columns: {list(split_df.columns)}")
    print(f"  Rows: {len(split_df)}")

    # Load metadata CSV
    print(f"\nLoading metadata CSV: {metadata_csv_path}")
    metadata_df = pd.read_csv(metadata_csv_path, compression='gzip')
    print(f"  Columns: {list(metadata_df.columns)}")
    print(f"  Rows: {len(metadata_df)}")

    # Merge split + metadata on dicom_id
    print(f"\nMerging split + metadata...")
    merged_df = pd.merge(
        split_df,
        metadata_df,
        on='dicom_id',
        how='left',
        suffixes=('', '_meta')
    )
    print(f"  Merged rows: {len(merged_df)}")

    # Merge with sectioned reports on study_id
    print(f"\nMerging with sectioned reports...")

    # Ensure study_id is string in both DataFrames
    merged_df['study_id'] = merged_df['study_id'].astype(str)
    sectioned_df['study'] = sectioned_df['study'].astype(str)

    # Merge on study_id
    final_df = pd.merge(
        merged_df,
        sectioned_df,
        left_on='study_id',
        right_on='study',
        how='left',
        suffixes=('', '_dup')
    )

    # Drop duplicate 'study' column (keep study_id from main data)
    if 'study' in final_df.columns:
        final_df = final_df.drop(columns=['study'])

    print(f"  Final rows: {len(final_df)}")
    print(f"  Final columns: {list(final_df.columns)}")

    # Save to CSV
    print(f"\nSaving to: {output_path}")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    final_df.to_csv(output_path, index=False)

    print(f"\n✓ Created splits_reports_metadata.csv")
    print(f"  - Total rows: {len(final_df)}")
    print(f"  - Columns: {len(final_df.columns)}")

    return final_df


def verify_output_structure(mimic_cxr_dir):
    """
    Verify the expected directory structure after preprocessing.
    """
    print(f"\n{'='*80}")
    print("Step 3: Verifying Output Structure")
    print(f"{'='*80}\n")

    required_files = [
        (Path(mimic_cxr_dir) / "mimic_cxr_sectioned" / "mimic_cxr_sectioned.csv", "Sectioned reports CSV"),
        (Path(mimic_cxr_dir).parent / "mimic_cxr_merged" / "splits_reports_metadata.csv", "Merged CSV"),
    ]

    all_ok = True

    for file_path, description in required_files:
        if file_path.exists():
            size_mb = file_path.stat().st_size / (1024 * 1024)
            print(f"✓ {description}")
            print(f"    Path: {file_path}")
            print(f"    Size: {size_mb:.1f} MB")
        else:
            print(f"✗ {description} NOT FOUND")
            print(f"    Expected: {file_path}")
            all_ok = False

    if all_ok:
        print(f"\n{'='*80}")
        print("✓ All required files created successfully!")
        print(f"{'='*80}")
    else:
        print(f"\n{'='*80}")
        print("✗ Some files are missing - check errors above")
        print(f"{'='*80}")

    return all_ok


def main():
    """
    Main preprocessing function.
    """
    print("\n" + "="*80)
    print("MIMIC-CXR Stage 2 Preprocessing")
    print("="*80)
    print("\nThis script will create:")
    print("  1. D:/datasets/mimic-cxr-jpg/mimic_cxr_sectioned/mimic_cxr_sectioned.csv")
    print("  2. D:/datasets/mimic_cxr_merged/splits_reports_metadata.csv")
    print("\n" + "="*80 + "\n")

    # Paths (adjust if needed)
    mimic_cxr_dir = Path(r"D:/datasets/mimic-cxr-jpg")
    reports_dir = Path(r"D:/datasets/mimic-cxr-reports/reports")

    split_csv = mimic_cxr_dir / "mimic-cxr-2.0.0-split.csv.gz"
    metadata_csv = mimic_cxr_dir / "mimic-cxr-2.0.0-metadata.csv.gz"

    sectioned_output = mimic_cxr_dir / "mimic_cxr_sectioned" / "mimic_cxr_sectioned.csv"
    merged_output = mimic_cxr_dir.parent / "mimic_cxr_merged" / "splits_reports_metadata.csv"

    # Verify inputs exist
    print("Checking input files...")
    if not split_csv.exists():
        print(f"ERROR: Split CSV not found: {split_csv}")
        return
    if not metadata_csv.exists():
        print(f"ERROR: Metadata CSV not found: {metadata_csv}")
        return
    if not reports_dir.exists():
        print(f"ERROR: Reports directory not found: {reports_dir}")
        return

    print("✓ All input files found\n")

    # Step 1: Create sectioned CSV
    sectioned_df = create_sectioned_csv(
        split_csv_path=split_csv,
        reports_base_dir=reports_dir,
        output_path=sectioned_output
    )

    # Step 2: Create merged CSV
    merged_df = create_merged_csv(
        split_csv_path=split_csv,
        metadata_csv_path=metadata_csv,
        sectioned_df=sectioned_df,
        output_path=merged_output
    )

    # Step 3: Verify outputs
    verify_output_structure(mimic_cxr_dir)

    print("\n" + "="*80)
    print("Preprocessing complete!")
    print("="*80)
    print("\nNext steps:")
    print("  1. Verify the CSV files look correct")
    print("  2. Run Stage 2 training: cd stage2_training && run_exp1_exp3.bat")
    print("\n" + "="*80 + "\n")


if __name__ == "__main__":
    main()
