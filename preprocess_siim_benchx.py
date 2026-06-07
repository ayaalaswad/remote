"""
SIIM Pneumothorax Preprocessing for BenchX
Based on BenchX's original preprocessing script
Dataset: https://www.kaggle.com/datasets/vbookshelf/pneumothorax-chest-xray-images-and-masks
"""
import os
import numpy as np
import pandas as pd
from tqdm import tqdm
from sklearn.model_selection import train_test_split
from PIL import Image
import glob

# Paths - update these on remote desktop
data_path = r"C:\Users\aya.alaswad\Downloads\archive"  # Downloaded Kaggle dataset
processed_datapath = r"C:\Users\aya.alaswad\remote\BenchX\datasets\SIIM"

output_image_dir = os.path.join(processed_datapath, "images")
if not os.path.exists(output_image_dir):
    os.makedirs(output_image_dir)
output_mask_dir = os.path.join(processed_datapath, "masks")
if not os.path.exists(output_mask_dir):
    os.makedirs(output_mask_dir)

def preprocess_pneumothorax_data():
    """Resize images and masks to 512x512"""
    desired_size = 512
    all_imgs = sorted(glob.glob(os.path.join(data_path, 'png_images', '*.png')))

    print(f"Found {len(all_imgs)} images to process")

    for img_path in tqdm(all_imgs, desc="Processing SIIM images"):
        img_name = os.path.basename(img_path)
        mask_path = os.path.join(data_path, "png_masks", img_name)

        # Load image and mask
        img = Image.open(img_path).convert("RGB")
        mask = Image.open(mask_path)

        # Resize and save image
        old_size = img.size
        ratio = float(desired_size) / max(old_size)
        new_size = tuple([int(x*ratio) for x in old_size])
        final_image = img.resize(new_size, Image.Resampling.LANCZOS)
        final_image.save(os.path.join(output_image_dir, img_name), 'PNG')

        # Resize and save mask
        final_mask = mask.resize(new_size, Image.Resampling.LANCZOS)
        final_mask = np.array(final_mask) > 128
        final_mask = Image.fromarray(final_mask)
        final_mask.save(os.path.join(output_mask_dir, img_name), 'PNG')


def save_anno(img_list, file_path, remove_suffix=True):
    """Save image list to text file"""
    if remove_suffix:
        img_list = [os.path.basename(img_path) for img_path in img_list]
        img_list = ['.'.join(img_path.split('.')[:-1]) for img_path in img_list]
    with open(file_path, 'w') as file_:
        for x in list(img_list):
            file_.write(x + '\n')


def split_seg_dataset(seed=42):
    """Create train/val/test splits (1%, 10%, 100%)"""
    train_pos_imgs = sorted(glob.glob(os.path.join(processed_datapath, 'images', '*train_1*.png')))
    train_neg_imgs = sorted(glob.glob(os.path.join(processed_datapath, 'images', '*train_0*.png')))

    x = train_pos_imgs + train_neg_imgs
    y = [1] * len(train_pos_imgs) + [0] * len(train_neg_imgs)
    x_test = sorted(glob.glob(os.path.join(processed_datapath, 'images', '*test*.png')))

    print(f"\nDataset statistics:")
    print(f"  Training (total): {len(x)} images (Pos: {len(train_pos_imgs)}, Neg: {len(train_neg_imgs)})")
    print(f"  Test: {len(x_test)} images")

    x_train, x_val, y_train, y_val = train_test_split(x, y, test_size=len(x_test), stratify=y, random_state=seed)

    # Create 1% and 10% subsets
    x_train_1, _ = train_test_split(x_train, test_size=0.99, stratify=y_train, random_state=seed)
    x_train_10, _ = train_test_split(x_train, test_size=0.90, stratify=y_train, random_state=seed)

    print(f"\nSplit sizes:")
    print(f"  train_1 (1%): {len(x_train_1)} samples")
    print(f"  train_10 (10%): {len(x_train_10)} samples")
    print(f"  train (100%): {len(x_train)} samples")
    print(f"  val: {len(x_val)} samples")
    print(f"  test: {len(x_test)} samples")

    save_anno(x_train, os.path.join(processed_datapath, 'train.txt'))
    save_anno(x_train_1, os.path.join(processed_datapath, 'train_1.txt'))
    save_anno(x_train_10, os.path.join(processed_datapath, 'train_10.txt'))
    save_anno(x_val, os.path.join(processed_datapath, 'val.txt'))
    save_anno(x_test, os.path.join(processed_datapath, 'test.txt'))

    # Combine train and test CSVs
    csv_train = pd.read_csv(os.path.join(data_path, "stage_1_train_images.csv"))
    csv_test = pd.read_csv(os.path.join(data_path, "stage_1_test_images.csv"))
    csv = pd.concat([csv_train, csv_test], axis=0)
    csv.to_csv(os.path.join(processed_datapath, "siim_labels.csv"), index=False)

    print(f"\nSaved siim_labels.csv with {len(csv)} rows")

if __name__ == "__main__":
    print("="*60)
    print("SIIM Pneumothorax Preprocessing for BenchX")
    print("="*60)
    print(f"\nSource: {data_path}")
    print(f"Output: {processed_datapath}\n")

    # Step 1: Preprocess images and masks
    preprocess_pneumothorax_data()

    # Step 2: Create splits
    split_seg_dataset(seed=42)

    print("\n" + "="*60)
    print("Preprocessing complete!")
    print("="*60)
    print(f"\nFiles created:")
    print(f"  - {processed_datapath}/images/ (resized PNG images)")
    print(f"  - {processed_datapath}/masks/ (resized PNG masks)")
    print(f"  - {processed_datapath}/train_1.txt (1% split)")
    print(f"  - {processed_datapath}/train_10.txt (10% split)")
    print(f"  - {processed_datapath}/train.txt (100% split)")
    print(f"  - {processed_datapath}/val.txt (validation)")
    print(f"  - {processed_datapath}/test.txt (test)")
    print(f"  - {processed_datapath}/siim_labels.csv (labels)")
