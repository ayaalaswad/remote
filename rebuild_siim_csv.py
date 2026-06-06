"""
Rebuild SIIM CSV to match actual image files
"""
import os
import pandas as pd
import glob

# Paths
data_path = r"D:\datasets\siim-pneumothorax\siim-acr-pneumothorax-segmentation"
processed_datapath = r"C:\Users\aya.alaswad\remote\BenchX\datasets\SIIM"
images_dir = os.path.join(processed_datapath, "images")

print("="*80)
print("Rebuilding SIIM CSV")
print("="*80)
print()

# 1. Get all actual image files
all_images = glob.glob(os.path.join(images_dir, "*.png"))
print(f"Found {len(all_images)} PNG images in images/ directory")
print()

# 2. Extract image IDs (without .png)
image_ids = [os.path.basename(p).replace(".png", "") for p in all_images]
print(f"Sample image IDs:")
for i, img_id in enumerate(image_ids[:5]):
    print(f"  {i+1}. {img_id}")
print()

# 3. Read the original Kaggle CSV to get labels
csv_path = os.path.join(data_path, "stage_2_train.csv")
print(f"Reading original CSV: {csv_path}")
original_df = pd.read_csv(csv_path)
print(f"Original CSV shape: {original_df.shape}")
print(f"Original CSV columns: {original_df.columns.tolist()}")
print()

# 4. Create new CSV with actual image files
new_rows = []
for img_id in image_ids:
    # Try to find this ImageId in the original CSV
    matching_rows = original_df[original_df['ImageId'] == img_id]

    if len(matching_rows) > 0:
        # Get the first match
        row = matching_rows.iloc[0]
        has_pneumo = 0 if row[' EncodedPixels'] == ' -1' else 1

        new_rows.append({
            'ImageId': img_id,
            'new_filename': img_id + '.png',
            'has_pneumo': has_pneumo,
            'EncodedPixels': row[' EncodedPixels']
        })
    else:
        # Image exists but not in CSV - default to no pneumothorax
        print(f"WARNING: {img_id} not found in original CSV")
        new_rows.append({
            'ImageId': img_id,
            'new_filename': img_id + '.png',
            'has_pneumo': 0,
            'EncodedPixels': ' -1'
        })

new_df = pd.DataFrame(new_rows)
print(f"Created new CSV with {len(new_df)} rows")
print()

# 5. Show label distribution
print("Label distribution:")
print(new_df['has_pneumo'].value_counts())
print()

# 6. Save
output_path = os.path.join(processed_datapath, "siim_labels.csv")
new_df.to_csv(output_path, index=False)
print(f"Saved to: {output_path}")
print()

# 7. Verify it will work
split_path = os.path.join(processed_datapath, "train_1.txt")
if os.path.exists(split_path):
    with open(split_path, 'r') as f:
        data_split = [line.strip() for line in f]

    data_split_with_ext = [x + '.png' for x in data_split]
    filtered = new_df[new_df["new_filename"].isin(data_split_with_ext)]

    print(f"Verification with train_1.txt:")
    print(f"  Split has {len(data_split)} entries")
    print(f"  After filtering CSV: {len(filtered)} samples")
    print(f"  ✓ Dataset will have {len(filtered)} samples")

    if len(filtered) > 0:
        print()
        print("SUCCESS! Dataset will load correctly now.")
    else:
        print()
        print("ERROR: Still 0 samples after filtering!")

print()
print("="*80)
