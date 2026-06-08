"""
SIIM Preprocessing - CSV-Based Labels Only
Read labels from stage_1_train_images.csv, no filename pattern matching.
"""
import os
import glob
import pandas as pd
from sklearn.model_selection import train_test_split

# Path to vbookshelf preprocessed dataset
data_path = 'C:/Users/aya.alaswad/Downloads/archive/siim-acr-pneumothorax'
processed_datapath = os.path.join(data_path, 'png_images')

# Output path for BenchX
output_path = 'C:/Users/aya.alaswad/remote/BenchX/data/SIIM'

def split_seg_dataset(seed=42):
    """
    Split SIIM dataset using CSV labels only.
    Maps ImageId from CSV to actual image files.
    """
    print(f"\nSearching for CSV in: {data_path}")

    # Read CSV file (vbookshelf uses stage_1_train_images.csv)
    csv_path = os.path.join(data_path, 'stage_1_train_images.csv')

    if not os.path.exists(csv_path):
        print(f"ERROR: CSV not found at {csv_path}")
        print("Available CSV files:")
        for csv in glob.glob(os.path.join(data_path, '*.csv')):
            print(f"  - {csv}")
        raise FileNotFoundError(f"CSV file not found: {csv_path}")

    print(f"Reading CSV: {csv_path}")
    df = pd.read_csv(csv_path)

    print(f"CSV columns: {list(df.columns)}")
    print(f"CSV shape: {df.shape}")
    print(f"\nFirst 5 rows:")
    print(df.head())

    # Get all PNG images
    all_images = sorted(glob.glob(os.path.join(processed_datapath, '*.png')))
    print(f"\nTotal PNG images found: {len(all_images)}")

    if len(all_images) == 0:
        raise ValueError(f"No PNG images found in {processed_datapath}")

    # Filter for training images only (exclude test images)
    train_images = [img for img in all_images if '_train_' in os.path.basename(img)]
    print(f"Training images (containing '_train_'): {len(train_images)}")

    # Extract labels from CSV
    # vbookshelf format: CSV might have ImageId and label columns
    # If CSV has EncodedPixels: label=1 if EncodedPixels != -1, else label=0

    # Create image_id to label mapping
    img_to_label = {}

    if 'EncodedPixels' in df.columns:
        print("\nUsing EncodedPixels column for labels")
        for idx, row in df.iterrows():
            img_id = str(row['ImageId']).strip()
            encoded_pixels = row['EncodedPixels']

            # Label = 1 if has pneumothorax (EncodedPixels not -1 or NaN)
            if pd.isna(encoded_pixels) or encoded_pixels == -1 or encoded_pixels == '-1':
                label = 0
            else:
                label = 1

            img_to_label[img_id] = label

    elif 'label' in df.columns:
        print("\nUsing label column directly")
        for idx, row in df.iterrows():
            img_id = str(row['ImageId']).strip()
            img_to_label[img_id] = int(row['label'])

    else:
        print("\nERROR: CSV doesn't have EncodedPixels or label column!")
        print("Falling back to filename-based labels...")
        # Fallback: use filename patterns
        for img_path in train_images:
            basename = os.path.basename(img_path)
            # Extract label from filename: {index}_train_{label}_.png
            if '_train_1_' in basename:
                img_to_label[basename.replace('.png', '')] = 1
            elif '_train_0_' in basename:
                img_to_label[basename.replace('.png', '')] = 0

    print(f"\nTotal labels in mapping: {len(img_to_label)}")

    # Match images to labels
    labeled_images = []
    labels = []

    for img_path in train_images:
        basename = os.path.basename(img_path)
        img_id = basename.replace('.png', '')

        # Try exact match first
        if img_id in img_to_label:
            labeled_images.append(img_path)
            labels.append(img_to_label[img_id])
        else:
            # Try without suffix
            img_id_clean = img_id.split('_train_')[0]
            if img_id_clean in img_to_label:
                labeled_images.append(img_path)
                labels.append(img_to_label[img_id_clean])

    print(f"\nMatched images with labels: {len(labeled_images)}")

    if len(labeled_images) == 0:
        print("\nERROR: No images matched with CSV labels!")
        print("Sample image names:")
        for img in train_images[:5]:
            print(f"  {os.path.basename(img)}")
        print("\nSample CSV ImageIds:")
        print(df['ImageId'].head())
        raise ValueError("Failed to match images with CSV labels")

    # Count class distribution
    pos_count = sum(labels)
    neg_count = len(labels) - pos_count
    print(f"Class distribution:")
    print(f"  Negative (class 0): {neg_count} ({neg_count/len(labels)*100:.1f}%)")
    print(f"  Positive (class 1): {pos_count} ({pos_count/len(labels)*100:.1f}%)")

    # Create output directory
    os.makedirs(output_path, exist_ok=True)

    # Create 3 data splits: 1%, 10%, 100%
    for pct in [1, 10, 100]:
        print(f"\n{'='*60}")
        print(f"Creating {pct}% split")
        print(f"{'='*60}")

        if pct == 100:
            train_imgs = labeled_images
            train_labels_split = labels
        else:
            train_imgs, _, train_labels_split, _ = train_test_split(
                labeled_images,
                labels,
                train_size=pct/100,
                stratify=labels,
                random_state=seed
            )

        # Split train into train/val (80/20 stratified)
        train_imgs_final, val_imgs, train_labels_final, val_labels = train_test_split(
            train_imgs,
            train_labels_split,
            test_size=0.2,
            stratify=train_labels_split,
            random_state=seed
        )

        print(f"Train: {len(train_imgs_final)} images ({sum(train_labels_final)} positive, {len(train_labels_final)-sum(train_labels_final)} negative)")
        print(f"Val: {len(val_imgs)} images ({sum(val_labels)} positive, {len(val_labels)-sum(val_labels)} negative)")

        # Write to files
        split_dir = os.path.join(output_path, f'{pct}%')
        os.makedirs(split_dir, exist_ok=True)

        with open(os.path.join(split_dir, 'train.txt'), 'w') as f:
            for img in train_imgs_final:
                f.write(img + '\n')

        with open(os.path.join(split_dir, 'train_labels.txt'), 'w') as f:
            for label in train_labels_final:
                f.write(str(label) + '\n')

        with open(os.path.join(split_dir, 'val.txt'), 'w') as f:
            for img in val_imgs:
                f.write(img + '\n')

        with open(os.path.join(split_dir, 'val_labels.txt'), 'w') as f:
            for label in val_labels:
                f.write(str(label) + '\n')

        print(f"Saved to: {split_dir}/")

    print(f"\n{'='*60}")
    print("SIIM preprocessing complete!")
    print(f"Output directory: {output_path}")
    print(f"{'='*60}")

if __name__ == '__main__':
    split_seg_dataset(seed=42)
