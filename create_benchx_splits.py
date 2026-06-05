"""
Create train/val/test split files for BenchX SIIM and RSNA datasets.

BenchX expects:
  datasets/SIIM/train_1.txt  - list of training image IDs
  datasets/SIIM/val.txt      - list of validation image IDs
  datasets/SIIM/test.txt     - list of test image IDs
"""

import pandas as pd
import os
from pathlib import Path

# Paths
benchx_dir = Path(r"C:\Users\aya.alaswad\remote\BenchX")
siim_dir = benchx_dir / "datasets" / "SIIM"
rsna_dir = benchx_dir / "datasets" / "RSNA"

# ============================================================================
# SIIM Dataset Splits
# ============================================================================
print("Creating SIIM splits...")

siim_csv = siim_dir / "stage_2_train.csv"
if siim_csv.exists():
    df = pd.read_csv(siim_csv)

    # Get unique image IDs (remove .dcm if present)
    image_ids = df['ImageId'].unique()

    # Split: 80% train, 10% val, 10% test
    n = len(image_ids)
    train_end = int(0.8 * n)
    val_end = int(0.9 * n)

    train_ids = image_ids[:train_end]
    val_ids = image_ids[train_end:val_end]
    test_ids = image_ids[val_end:]

    # Write split files
    with open(siim_dir / "train_1.txt", 'w') as f:
        for img_id in train_ids:
            f.write(f"{img_id}\n")

    with open(siim_dir / "val.txt", 'w') as f:
        for img_id in val_ids:
            f.write(f"{img_id}\n")

    with open(siim_dir / "test.txt", 'w') as f:
        for img_id in test_ids:
            f.write(f"{img_id}\n")

    print(f"  SIIM: {len(train_ids)} train, {len(val_ids)} val, {len(test_ids)} test")
else:
    print(f"  [ERROR] {siim_csv} not found!")

# ============================================================================
# RSNA Dataset Splits
# ============================================================================
print("Creating RSNA splits...")

rsna_csv = rsna_dir / "stage_2_train_labels.csv"
if rsna_csv.exists():
    df = pd.read_csv(rsna_csv)

    # Get unique patient IDs (RSNA has multiple images per patient)
    if 'patientId' in df.columns:
        image_ids = df['patientId'].unique()
    else:
        # Fall back to using all rows if patientId column doesn't exist
        image_ids = df.iloc[:, 0].unique()

    # Split: 80% train, 10% val, 10% test
    n = len(image_ids)
    train_end = int(0.8 * n)
    val_end = int(0.9 * n)

    train_ids = image_ids[:train_end]
    val_ids = image_ids[train_end:val_end]
    test_ids = image_ids[val_end:]

    # Write split files
    with open(rsna_dir / "train_1.txt", 'w') as f:
        for img_id in train_ids:
            f.write(f"{img_id}\n")

    with open(rsna_dir / "val.txt", 'w') as f:
        for img_id in val_ids:
            f.write(f"{img_id}\n")

    with open(rsna_dir / "test.txt", 'w') as f:
        for img_id in test_ids:
            f.write(f"{img_id}\n")

    print(f"  RSNA: {len(train_ids)} train, {len(val_ids)} val, {len(test_ids)} test")
else:
    print(f"  [ERROR] {rsna_csv} not found!")

print("\nDone! Split files created.")
