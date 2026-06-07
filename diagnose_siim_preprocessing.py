"""
Diagnose what went wrong with SIIM preprocessing
"""
import os
import glob
import pandas as pd

print("="*70)
print("SIIM Preprocessing Diagnostic")
print("="*70)

# Check source data
data_path = r"C:\Users\aya.alaswad\Downloads\archive"
print(f"\n1. Source Data Check: {data_path}")
print("-"*70)

png_images_path = os.path.join(data_path, "png_images")
if os.path.exists(png_images_path):
    png_files = glob.glob(os.path.join(png_images_path, "*.png"))
    print(f"✓ Found {len(png_files)} PNG images")
    if len(png_files) > 0:
        print(f"  Example filename: {os.path.basename(png_files[0])}")
        print(f"  Example filename: {os.path.basename(png_files[1])}")
else:
    print(f"✗ Directory not found: {png_images_path}")

csv_train_path = os.path.join(data_path, "stage_1_train_images.csv")
if os.path.exists(csv_train_path):
    csv_train = pd.read_csv(csv_train_path)
    print(f"✓ Found stage_1_train_images.csv with {len(csv_train)} rows")
    print(f"  Columns: {list(csv_train.columns)}")
    print(f"  First few rows:")
    print(csv_train.head())
else:
    print(f"✗ CSV not found: {csv_train_path}")

# Check preprocessed data
processed_datapath = r"C:\Users\aya.alaswad\remote\BenchX\datasets\SIIM"
print(f"\n2. Preprocessed Data Check: {processed_datapath}")
print("-"*70)

images_path = os.path.join(processed_datapath, "images")
if os.path.exists(images_path):
    processed_images = glob.glob(os.path.join(images_path, "*.png"))
    print(f"✓ Found {len(processed_images)} preprocessed images")
    if len(processed_images) > 0:
        print(f"  Example filename: {os.path.basename(processed_images[0])}")
else:
    print(f"✗ Directory not found: {images_path}")

# Check what the buggy glob pattern finds
print(f"\n3. Buggy Pattern Search (What Preprocessing Used)")
print("-"*70)
if os.path.exists(images_path):
    train_1_pattern = os.path.join(images_path, "*train_1*.png")
    train_0_pattern = os.path.join(images_path, "*train_0*.png")

    train_1_files = glob.glob(train_1_pattern)
    train_0_files = glob.glob(train_0_pattern)

    print(f"Pattern: {train_1_pattern}")
    print(f"  Found {len(train_1_files)} files matching *train_1*.png")
    print(f"Pattern: {train_0_pattern}")
    print(f"  Found {len(train_0_files)} files matching *train_0*.png")

    if len(train_1_files) == 0 and len(train_0_files) == 0:
        print("\n❌ PROBLEM CONFIRMED:")
        print("  Preprocessing script looked for *train_0*.png and *train_1*.png")
        print("  But found ZERO files with those patterns")
        print("  This is why all validation samples are class 0!")

# Check split files
print(f"\n4. Split Files Check")
print("-"*70)
for split_name in ['train_1.txt', 'train_10.txt', 'train.txt', 'val.txt', 'test.txt']:
    split_path = os.path.join(processed_datapath, split_name)
    if os.path.exists(split_path):
        with open(split_path, 'r') as f:
            lines = f.readlines()
        print(f"✓ {split_name}: {len(lines)} samples")
        if len(lines) > 0:
            print(f"  First sample: {lines[0].strip()}")
    else:
        print(f"✗ Not found: {split_name}")

print("\n" + "="*70)
print("Diagnosis Complete")
print("="*70)
