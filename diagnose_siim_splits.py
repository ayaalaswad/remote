"""
Diagnose SIIM data splits to find why validation has no positives
"""
import pandas as pd
from pathlib import Path
import numpy as np

def check_splits():
    print("="*80)
    print("SIIM Data Split Diagnosis")
    print("="*80)
    print()

    # Check the CSV file
    csv_paths = [
        Path("C:/Users/aya.alaswad/Downloads/archive/siim-acr-pneumothorax/siim_processed.csv"),
        Path("C:/Users/aya.alaswad/remote/BenchX/datasets/SIIM/siim_labels.csv"),
        Path("datasets/SIIM/siim_labels.csv"),
    ]

    csv_file = None
    for path in csv_paths:
        if path.exists():
            csv_file = path
            break

    if csv_file is None:
        print("ERROR: Could not find SIIM CSV file!")
        print("Tried:")
        for p in csv_paths:
            print(f"  - {p}")
        return

    print(f"Found CSV: {csv_file}")
    print()

    # Load and analyze
    df = pd.read_csv(csv_file)

    print(f"Total samples: {len(df)}")
    print(f"Columns: {list(df.columns)}")
    print()

    # Detect label column
    label_col = None
    for col in ['label', 'Label', 'pneumothorax', 'Pneumothorax', 'target']:
        if col in df.columns:
            label_col = col
            break

    if label_col is None:
        print("ERROR: Could not find label column!")
        print(f"Available columns: {list(df.columns)}")
        return

    print(f"Label column: {label_col}")
    print()

    # Overall distribution
    labels = df[label_col].values
    n_pos = np.sum(labels == 1)
    n_neg = np.sum(labels == 0)

    print("Overall Distribution:")
    print(f"  Positive: {n_pos} ({n_pos/len(df)*100:.1f}%)")
    print(f"  Negative: {n_neg} ({n_neg/len(df)*100:.1f}%)")
    print()

    # Check if there's a split column
    split_col = None
    for col in ['split', 'Split', 'subset']:
        if col in df.columns:
            split_col = col
            break

    if split_col is None:
        print("WARNING: No split column found. Need to check how BenchX creates splits.")
        print()
        print("Checking for train/val/test patterns in paths or filenames...")

        # Check if there's a path or filename column
        for col in ['path', 'Path', 'filename', 'image_id']:
            if col in df.columns:
                print(f"  Found column: {col}")
                # Sample some values
                print(f"  Sample values:")
                for val in df[col].head(5):
                    print(f"    {val}")
    else:
        print(f"Split column: {split_col}")
        print()

        # Analyze each split
        for split_name in df[split_col].unique():
            split_df = df[df[split_col] == split_name]
            split_labels = split_df[label_col].values

            n_total = len(split_df)
            n_pos = np.sum(split_labels == 1)
            n_neg = np.sum(split_labels == 0)

            print(f"{split_name}:")
            print(f"  Total: {n_total}")
            print(f"  Positive: {n_pos} ({n_pos/n_total*100:.1f}%)")
            print(f"  Negative: {n_neg} ({n_neg/n_total*100:.1f}%)")

            if n_pos == 0:
                print(f"  >>> ERROR: {split_name} HAS NO POSITIVES!")
            print()

    # Check BenchX dataset splits
    print("="*80)
    print("Checking BenchX Dataset Splits")
    print("="*80)
    print()

    benchx_dataset_path = Path("C:/Users/aya.alaswad/remote/BenchX/datasets/SIIM")
    if benchx_dataset_path.exists():
        print(f"BenchX SIIM path exists: {benchx_dataset_path}")

        # List files
        files = list(benchx_dataset_path.glob("*"))
        print(f"Files in BenchX SIIM directory:")
        for f in files:
            print(f"  {f.name}")
    else:
        print("BenchX SIIM path not found (will check on remote)")

    print()
    print("="*80)
    print("RECOMMENDATION")
    print("="*80)
    print()
    print("If validation split has 0 positives, you need to:")
    print("1. Create stratified train/val/test splits")
    print("2. Ensure each split has both positive and negative examples")
    print("3. Regenerate the CSV with proper split column")
    print()

if __name__ == "__main__":
    check_splits()
