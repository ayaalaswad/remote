"""
Complete SIIM fix pipeline: diagnose, fix, and verify
"""
import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.model_selection import train_test_split

def diagnose_and_fix():
    print("="*80)
    print("SIIM Complete Fix Pipeline")
    print("="*80)
    print()

    # Find CSV
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
        print("[ERROR] Could not find SIIM CSV file!")
        print("Tried:")
        for p in csv_paths:
            print(f"  - {p}")
        return False

    print(f"[1/4] Loading CSV: {csv_file}")
    df = pd.read_csv(csv_file)
    print(f"      Total samples: {len(df)}")
    print()

    # Find label column
    label_col = None
    for col in ['label', 'Label', 'pneumothorax', 'Pneumothorax', 'target']:
        if col in df.columns:
            label_col = col
            break

    if label_col is None:
        print("[ERROR] Could not find label column!")
        print(f"      Available columns: {list(df.columns)}")
        print()
        print("      Trying to find any column with binary values (0/1)...")
        # Try to find any column with binary 0/1 values
        for col in df.columns:
            if df[col].dtype in ['int64', 'float64', 'int32', 'float32']:
                unique_vals = df[col].unique()
                if len(unique_vals) == 2 and set(unique_vals) == {0, 1}:
                    print(f"      Found binary column: '{col}'")
                    label_col = col
                    break

        if label_col is None:
            print("      Could not find any binary column!")
            return False
        else:
            print(f"      Using '{label_col}' as label column")
            print()

    print(f"[2/4] Analyzing current distribution")
    n_pos = (df[label_col] == 1).sum()
    n_neg = (df[label_col] == 0).sum()
    print(f"      Positive: {n_pos} ({n_pos/len(df)*100:.1f}%)")
    print(f"      Negative: {n_neg} ({n_neg/len(df)*100:.1f}%)")
    print()

    if n_pos == 0:
        print("[ERROR] No positive examples in dataset!")
        return False

    # Check existing splits
    if 'split' in df.columns:
        print("      Existing splits found:")
        for split_name in ['train', 'val', 'test']:
            if split_name in df['split'].values:
                split_df = df[df['split'] == split_name]
                n_pos_split = (split_df[label_col] == 1).sum()
                print(f"        {split_name}: {len(split_df)} samples, {n_pos_split} positives", end="")
                if n_pos_split == 0:
                    print(" <- BROKEN!")
                else:
                    print()
        print()

    # Create new stratified splits
    print(f"[3/4] Creating stratified splits (70% train, 15% val, 15% test)")

    # First split: train+val (85%) vs test (15%)
    train_val_idx, test_idx = train_test_split(
        np.arange(len(df)),
        test_size=0.15,
        stratify=df[label_col],
        random_state=42
    )

    # Second split: train (70%) vs val (15%)
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

    # Verify
    print()
    print("[4/4] Verifying new splits:")
    all_good = True
    for split_name in ['train', 'val', 'test']:
        split_df = df[df['split'] == split_name]
        n_total = len(split_df)
        n_pos = (split_df[label_col] == 1).sum()
        n_neg = (split_df[label_col] == 0).sum()

        status = "OK" if n_pos > 0 else "ERROR"
        print(f"      {split_name:5s}: {n_total:5d} samples, {n_pos:4d} pos ({n_pos/n_total*100:5.1f}%), {n_neg:5d} neg ({n_neg/n_total*100:5.1f}%) [{status}]")

        if n_pos == 0:
            all_good = False

    print()

    if not all_good:
        print("[ERROR] Some splits still have no positives!")
        return False

    # Save
    print("[SAVE] Saving fixed CSV files...")

    # Save to original location
    output_file = csv_file.parent / "siim_labels_fixed.csv"
    df.to_csv(output_file, index=False)
    print(f"       OK: {output_file}")

    # Save to BenchX location
    benchx_path = Path("C:/Users/aya.alaswad/remote/BenchX/datasets/SIIM/siim_labels.csv")
    if benchx_path.parent.exists():
        df.to_csv(benchx_path, index=False)
        print(f"       OK: {benchx_path}")

    # Also create backup
    backup_path = benchx_path.parent / "siim_labels_original.csv"
    if csv_file != benchx_path and benchx_path.exists():
        import shutil
        if not backup_path.exists():
            shutil.copy(benchx_path, backup_path)
            print(f"       OK: Backup created at {backup_path}")

    print()
    print("="*80)
    print("SUCCESS - SIIM Splits Fixed!")
    print("="*80)
    print()
    print("Next steps:")
    print("  1. Run: fix_and_retrain_siim.bat         (sequential training)")
    print("     OR: fix_and_retrain_siim_parallel.bat (parallel training)")
    print()
    print("  2. After training, verify with:")
    print("     python calculate_f1_from_pushed_results.py")
    print()
    print("  3. Push results:")
    print("     push_siim_results.bat")
    print()

    return True

if __name__ == "__main__":
    success = diagnose_and_fix()
    if not success:
        print()
        print("[FAILED] Could not fix SIIM splits. Check errors above.")
        exit(1)
