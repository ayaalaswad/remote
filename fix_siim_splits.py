"""
Fix SIIM data splits with proper stratification
Ensures train/val/test all have both positive and negative examples
"""
import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.model_selection import train_test_split

def fix_siim_splits():
    print("="*80)
    print("Fixing SIIM Data Splits with Stratification")
    print("="*80)
    print()

    # Find the CSV file
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
        return

    print(f"Reading: {csv_file}")
    df = pd.read_csv(csv_file)

    print(f"Total samples: {len(df)}")
    print()

    # Find label column
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

    # Check current distribution
    n_pos = (df[label_col] == 1).sum()
    n_neg = (df[label_col] == 0).sum()

    print(f"\nOverall distribution:")
    print(f"  Positive: {n_pos} ({n_pos/len(df)*100:.1f}%)")
    print(f"  Negative: {n_neg} ({n_neg/len(df)*100:.1f}%)")
    print()

    if n_pos == 0:
        print("ERROR: No positive examples in dataset!")
        return

    # Create stratified splits
    print("Creating stratified splits...")
    print("  Train: 70%, Val: 15%, Test: 15%")
    print()

    # First split: train+val (85%) vs test (15%)
    train_val_idx, test_idx = train_test_split(
        np.arange(len(df)),
        test_size=0.15,
        stratify=df[label_col],
        random_state=42
    )

    # Second split: train (70%) vs val (15%) from the train_val set
    # 15/(85) ≈ 0.176
    train_idx, val_idx = train_test_split(
        train_val_idx,
        test_size=0.176,  # 15% of total = 17.6% of train_val
        stratify=df.iloc[train_val_idx][label_col],
        random_state=42
    )

    # Assign splits
    df['split'] = 'train'
    df.loc[val_idx, 'split'] = 'val'
    df.loc[test_idx, 'split'] = 'test'

    # Verify splits
    print("Split distribution:")
    for split_name in ['train', 'val', 'test']:
        split_df = df[df['split'] == split_name]
        n_total = len(split_df)
        n_pos = (split_df[label_col] == 1).sum()
        n_neg = (split_df[label_col] == 0).sum()

        print(f"\n{split_name}:")
        print(f"  Total: {n_total} ({n_total/len(df)*100:.1f}%)")
        print(f"  Positive: {n_pos} ({n_pos/n_total*100:.1f}%)")
        print(f"  Negative: {n_neg} ({n_neg/n_total*100:.1f}%)")

        if n_pos == 0:
            print(f"  >>> ERROR: Still no positives in {split_name}!")

    # Save fixed CSV
    output_dir = csv_file.parent
    output_file = output_dir / "siim_labels_fixed.csv"

    df.to_csv(output_file, index=False)
    print(f"\n✓ Saved fixed CSV to: {output_file}")

    # Also save to BenchX datasets folder if it exists
    benchx_path = Path("C:/Users/aya.alaswad/remote/BenchX/datasets/SIIM")
    if benchx_path.exists():
        benchx_output = benchx_path / "siim_labels.csv"
        df.to_csv(benchx_output, index=False)
        print(f"✓ Saved to BenchX: {benchx_output}")

    print()
    print("="*80)
    print("NEXT STEPS")
    print("="*80)
    print()
    print("1. Verify the splits look correct above")
    print("2. Update SIIM config files to use 'siim_labels_fixed.csv' or the updated file")
    print("3. Retrain SIIM experiments:")
    print("   cd BenchX")
    print("   python bin/train.py configs/classification/SIIM/sharp_siim_1pct.yml")
    print("   python bin/train.py configs/classification/SIIM/sharp_siim_10pct.yml")
    print("   python bin/train.py configs/classification/SIIM/sharp_siim_100pct.yml")
    print()

if __name__ == "__main__":
    fix_siim_splits()
