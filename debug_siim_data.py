"""
Debug SIIM dataset loading issue
"""
import os
import pandas as pd
import glob

data_path = r"C:\Users\aya.alaswad\remote\BenchX\datasets\SIIM"
split = "train_1"

print("="*80)
print("SIIM Dataset Debug")
print("="*80)
print()

# Check split file
split_path = os.path.join(data_path, f"{split}.txt")
print(f"1. Checking split file: {split_path}")
if os.path.exists(split_path):
    with open(split_path, 'r') as f:
        data_split = [line.strip() for line in f]
    print(f"   ✓ File exists")
    print(f"   ✓ Contains {len(data_split)} entries")
    print(f"   First 5 entries:")
    for i, entry in enumerate(data_split[:5]):
        print(f"      {i+1}. '{entry}'")
else:
    print(f"   ✗ File NOT FOUND!")
print()

# Check CSV
csv_path = os.path.join(data_path, "siim_labels.csv")
print(f"2. Checking CSV: {csv_path}")
if os.path.exists(csv_path):
    df = pd.read_csv(csv_path)
    print(f"   ✓ File exists")
    print(f"   ✓ Shape: {df.shape}")
    print(f"   ✓ Columns: {df.columns.tolist()}")
    if 'new_filename' in df.columns:
        print(f"   ✓ Has new_filename column")
        print(f"   First 5 new_filename values:")
        for i, val in enumerate(df['new_filename'].head()):
            print(f"      {i+1}. '{val}'")
    else:
        print(f"   ✗ Missing new_filename column!")
    if 'has_pneumo' in df.columns:
        print(f"   ✓ Has has_pneumo column")
        print(f"   Label distribution: {df['has_pneumo'].value_counts().to_dict()}")
    else:
        print(f"   ✗ Missing has_pneumo column!")
else:
    print(f"   ✗ File NOT FOUND!")
print()

# Check images
images_path = os.path.join(data_path, "images")
print(f"3. Checking images directory: {images_path}")
if os.path.exists(images_path):
    all_images = glob.glob(os.path.join(images_path, "*.png"))
    print(f"   ✓ Directory exists")
    print(f"   ✓ Contains {len(all_images)} PNG images")
    if all_images:
        print(f"   First 5 image filenames:")
        for i, img in enumerate(all_images[:5]):
            print(f"      {i+1}. '{os.path.basename(img)}'")
else:
    print(f"   ✗ Directory NOT FOUND!")
print()

# Simulate the dataset loading logic
print("4. Simulating dataset loading logic:")
if os.path.exists(split_path) and os.path.exists(csv_path):
    with open(split_path, 'r') as f:
        data_split = [line.strip() for line in f]

    # Add extension
    extension = ".png"
    data_split_with_ext = pd.Series(data_split).apply(lambda x: x + extension)

    print(f"   Split entries with extension added:")
    for i, val in enumerate(list(data_split_with_ext)[:5]):
        print(f"      {i+1}. '{val}'")
    print()

    # Filter CSV
    df = pd.read_csv(csv_path)
    if 'new_filename' in df.columns:
        filtered = df[df["new_filename"].isin(data_split_with_ext)]
        print(f"   CSV rows before filtering: {len(df)}")
        print(f"   CSV rows after filtering: {len(filtered)}")
        print(f"   ✓ Dataset would have {len(filtered)} samples")

        if len(filtered) == 0:
            print()
            print("   ✗ PROBLEM: No matches found!")
            print()
            print("   Checking for format mismatch...")
            # Check if any split entry matches any CSV entry
            csv_files = set(df['new_filename'].values)
            split_files = set(data_split_with_ext.values)

            print(f"   Unique filenames in CSV: {len(csv_files)}")
            print(f"   Unique filenames in split: {len(split_files)}")

            # Check intersection
            intersection = csv_files.intersection(split_files)
            print(f"   Matching filenames: {len(intersection)}")

            if len(intersection) == 0:
                print()
                print("   Sample CSV filename formats:")
                for val in list(csv_files)[:3]:
                    print(f"      '{val}'")
                print()
                print("   Sample split filename formats (with .png added):")
                for val in list(split_files)[:3]:
                    print(f"      '{val}'")
else:
    print("   ✗ Cannot simulate - missing files")

print()
print("="*80)
