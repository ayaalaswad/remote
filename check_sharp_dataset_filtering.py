"""
Check SHARP dataset filtering and image counts
Shows what images were used for training and how they were filtered
"""
import pandas as pd
from pathlib import Path
import json

def check_mimic_metadata():
    """Check MIMIC-CXR metadata for filtering details"""

    print("="*80)
    print("SHARP Dataset Filtering Analysis")
    print("="*80)
    print()

    # Common MIMIC-CXR metadata locations
    metadata_paths = [
        Path("C:/Users/aya.alaswad/Downloads/physionet.org/files/mimic-cxr/2.0.0/mimic-cxr-2.0.0-metadata.csv"),
        Path("C:/Users/aya.alaswad/Downloads/mimic-cxr-2.0.0-metadata.csv"),
        Path("D:/mimic-cxr/mimic-cxr-2.0.0-metadata.csv"),
        Path("D:/datasets/mimic-cxr/mimic-cxr-2.0.0-metadata.csv"),
    ]

    metadata_file = None
    for path in metadata_paths:
        if path.exists():
            metadata_file = path
            break

    if metadata_file is None:
        print("[NOT FOUND] MIMIC-CXR metadata file not found")
        print("Tried:")
        for p in metadata_paths:
            print(f"  - {p}")
        print()
        return None

    print(f"[1/4] Loading metadata: {metadata_file}")
    df_meta = pd.read_csv(metadata_file)
    print(f"      Total records: {len(df_meta):,}")
    print()

    # Check ViewPosition distribution
    print(f"[2/4] ViewPosition Distribution")
    if 'ViewPosition' in df_meta.columns:
        view_counts = df_meta['ViewPosition'].value_counts()
        total = len(df_meta)
        print()
        for view, count in view_counts.items():
            pct = (count / total) * 100
            print(f"      {view:15s}: {count:8,} ({pct:5.1f}%)")
        print(f"      {'TOTAL':15s}: {total:8,} (100.0%)")
    else:
        print("      ViewPosition column not found")
    print()

    return df_meta

def check_split_files():
    """Check MIMIC-CXR split files"""

    print(f"[3/4] Checking MIMIC-CXR split files")
    print()

    split_paths = [
        Path("C:/Users/aya.alaswad/Downloads/physionet.org/files/mimic-cxr/2.0.0/mimic-cxr-2.0.0-split.csv"),
        Path("C:/Users/aya.alaswad/Downloads/mimic-cxr-2.0.0-split.csv"),
        Path("D:/mimic-cxr/mimic-cxr-2.0.0-split.csv"),
        Path("D:/datasets/mimic-cxr/mimic-cxr-2.0.0-split.csv"),
    ]

    split_file = None
    for path in split_paths:
        if path.exists():
            split_file = path
            break

    if split_file is None:
        print("      Split file not found")
        return None

    print(f"      Loading: {split_file}")
    df_split = pd.read_csv(split_file)

    split_counts = df_split['split'].value_counts()
    total = len(df_split)

    print()
    for split, count in split_counts.items():
        pct = (count / total) * 100
        print(f"      {split:10s}: {count:8,} ({pct:5.1f}%)")
    print(f"      {'TOTAL':10s}: {total:8,} (100.0%)")
    print()

    return df_split

def check_training_config():
    """Check SHARP training configuration"""

    print(f"[4/4] Checking SHARP training configuration")
    print()

    # Look for experiment configs
    exp_dirs = [
        Path("D:/experiments/exp3_full_sharp"),
        Path("D:/experiments/exp1_baseline"),
        Path("C:/Users/aya.alaswad/remote"),
    ]

    config_found = False

    for exp_dir in exp_dirs:
        if not exp_dir.exists():
            continue

        # Look for config files
        config_files = list(exp_dir.glob("*.json")) + list(exp_dir.glob("config*.yml")) + list(exp_dir.glob("*.yaml"))

        for config_file in config_files:
            if config_file.name.startswith('.'):
                continue

            print(f"      Found config: {config_file}")
            config_found = True

            # Try to read and show relevant parts
            try:
                if config_file.suffix == '.json':
                    with open(config_file, 'r') as f:
                        config = json.load(f)

                    # Look for dataset-related keys
                    relevant_keys = ['dataset_size', 'num_samples', 'view_position',
                                   'filter', 'frontal_only', 'batch_size', 'total_steps']

                    for key in relevant_keys:
                        if key in config:
                            print(f"        {key}: {config[key]}")

            except Exception as e:
                pass

    if not config_found:
        print("      No config files found in experiment directories")

    print()

def analyze_filtering():
    """Analyze what filtering was likely applied"""

    print("="*80)
    print("SHARP Image Filtering Summary")
    print("="*80)
    print()

    print("Based on standard SHARP/MGCA practice:")
    print()
    print("1. ViewPosition Filtering:")
    print("   - FRONTAL ONLY (PA + AP views)")
    print("   - Excludes: LATERAL, LL views")
    print("   - Reason: Text-image pairs are study-level, not view-level")
    print()

    print("2. Quality Filtering:")
    print("   - Requires valid DICOM image")
    print("   - Requires paired radiology report")
    print("   - Removes corrupted/unreadable images")
    print()

    print("3. Split Usage:")
    print("   - Uses TRAIN split only for pretraining")
    print("   - VAL and TEST reserved for downstream evaluation")
    print()

    print("Estimated Training Set Size:")
    print("   - MIMIC-CXR total: ~377,110 images")
    print("   - After frontal-only filter: ~243,000 images (64%)")
    print("   - After train split: ~170,000-180,000 images")
    print()

    print("="*80)
    print("To verify exact numbers, check:")
    print("  1. Training logs in D:/experiments/exp3_full_sharp/")
    print("  2. Look for 'Dataset size' or 'Total samples' in logs")
    print("  3. Check dataloader initialization messages")
    print("="*80)

def main():
    print()

    # Check metadata
    df_meta = check_mimic_metadata()

    # Check splits
    df_split = check_split_files()

    # Check training config
    check_training_config()

    # Analyze filtering
    analyze_filtering()

    # If we have both metadata and splits, calculate exact numbers
    if df_meta is not None and df_split is not None:
        print()
        print("="*80)
        print("EXACT CALCULATION (if metadata + splits available)")
        print("="*80)
        print()

        # Merge to get view + split info
        merged = df_meta.merge(df_split, on=['dicom_id', 'subject_id', 'study_id'], how='inner')

        print("Full dataset breakdown:")
        print()

        for split in ['train', 'validate', 'test']:
            split_df = merged[merged['split'] == split]
            total = len(split_df)

            if 'ViewPosition' in split_df.columns:
                frontal = split_df[split_df['ViewPosition'].isin(['PA', 'AP'])]
                n_frontal = len(frontal)
                pct_frontal = (n_frontal / total * 100) if total > 0 else 0

                print(f"{split.upper():10s}:")
                print(f"  Total images:    {total:8,}")
                print(f"  Frontal (PA+AP): {n_frontal:8,} ({pct_frontal:5.1f}%)")
                print()

        # Training set frontal only
        train_df = merged[merged['split'] == 'train']
        if 'ViewPosition' in train_df.columns:
            train_frontal = train_df[train_df['ViewPosition'].isin(['PA', 'AP'])]

            print("="*80)
            print(f"SHARP TRAINING SET (FRONTAL ONLY): {len(train_frontal):,} images")
            print("="*80)

if __name__ == "__main__":
    main()
