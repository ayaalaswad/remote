"""
SIIM Preprocessing - Simple Fix
The vbookshelf dataset already has labels embedded in filenames: {index}_{train/test}_{0/1}_.png
Just use correct glob patterns.
"""
import os
import glob
import random
from sklearn.model_selection import train_test_split

# Path to vbookshelf preprocessed dataset
data_path = 'C:/Users/aya.alaswad/Downloads/archive/siim-acr-pneumothorax'
processed_datapath = os.path.join(data_path, 'png_images')

# Output path for BenchX
output_path = 'C:/Users/aya.alaswad/remote/BenchX/data/SIIM'

def split_seg_dataset(seed=42):
    """
    Split SIIM dataset using filename patterns.
    vbookshelf dataset has labels in filenames: *_train_0_*.png and *_train_1_*.png
    """
    print(f"\nSearching for images in: {processed_datapath}")

    # FIXED PATTERN: Use underscore-based patterns
    train_neg_imgs = sorted(glob.glob(os.path.join(processed_datapath, '*_train_0_*.png')))
    train_pos_imgs = sorted(glob.glob(os.path.join(processed_datapath, '*_train_1_*.png')))

    print(f"Found {len(train_neg_imgs)} negative training images (no pneumothorax)")
    print(f"Found {len(train_pos_imgs)} positive training images (has pneumothorax)")

    if len(train_neg_imgs) == 0 or len(train_pos_imgs) == 0:
        print("\nERROR: No images found with expected patterns!")
        print("Expected patterns: *_train_0_*.png and *_train_1_*.png")
        print("\nFirst 10 actual filenames:")
        all_pngs = glob.glob(os.path.join(processed_datapath, '*.png'))[:10]
        for f in all_pngs:
            print(f"  {os.path.basename(f)}")
        raise ValueError("Image patterns don't match expected format")

    # Combine all images with labels
    all_train_imgs = train_neg_imgs + train_pos_imgs
    all_labels = [0] * len(train_neg_imgs) + [1] * len(train_pos_imgs)

    print(f"\nTotal training images: {len(all_train_imgs)}")
    print(f"Class distribution: {len(train_neg_imgs)} negative ({len(train_neg_imgs)/len(all_train_imgs)*100:.1f}%), {len(train_pos_imgs)} positive ({len(train_pos_imgs)/len(all_train_imgs)*100:.1f}%)")

    # Create output directory
    os.makedirs(output_path, exist_ok=True)

    # Create 3 data splits: 1%, 10%, 100%
    for pct in [1, 10, 100]:
        print(f"\n{'='*60}")
        print(f"Creating {pct}% split")
        print(f"{'='*60}")

        if pct == 100:
            # Use all data for training
            train_imgs = all_train_imgs
            train_labels_split = all_labels
        else:
            # Sample pct% of data with stratification
            train_imgs, _, train_labels_split, _ = train_test_split(
                all_train_imgs,
                all_labels,
                train_size=pct/100,
                stratify=all_labels,
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

        # Train files
        with open(os.path.join(split_dir, 'train.txt'), 'w') as f:
            for img in train_imgs_final:
                f.write(img + '\n')

        with open(os.path.join(split_dir, 'train_labels.txt'), 'w') as f:
            for label in train_labels_final:
                f.write(str(label) + '\n')

        # Val files
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
