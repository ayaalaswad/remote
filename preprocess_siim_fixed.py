"""
SIIM Pneumothorax Preprocessing - FIXED VERSION
Reads labels from CSV instead of filename patterns
"""
import os
import numpy as np
import pandas as pd
from tqdm import tqdm
from sklearn.model_selection import train_test_split
from PIL import Image
import glob

# Paths - update these on remote desktop
data_path = r"C:\Users\aya.alaswad\Downloads\archive"
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
    """
    FIXED VERSION: Read labels from CSV instead of filename patterns
    """
    print("\nReading labels from CSV...")

    # Try multiple possible CSV filenames
    csv_candidates = [
        "stage_2_train.csv",
        "train-rle.csv",
        "stage_1_train_images.csv",
        "train_labels.csv"
    ]

    csv_data = None
    csv_used = None

    for csv_name in csv_candidates:
        csv_path = os.path.join(data_path, csv_name)
        if os.path.exists(csv_path):
            print(f"Found CSV: {csv_name}")
            csv_data = pd.read_csv(csv_path)
            csv_used = csv_name
            break

    if csv_data is None:
        # List available CSV files
        print("\nAvailable CSV files in archive:")
        csv_files = glob.glob(os.path.join(data_path, "*.csv"))
        for f in csv_files:
            print(f"  - {os.path.basename(f)}")
        raise FileNotFoundError(f"Could not find SIIM CSV file. Tried: {csv_candidates}")

    print(f"Loaded CSV with {len(csv_data)} rows")
    print(f"Columns: {list(csv_data.columns)}")
    print(f"\nFirst few rows:")
    print(csv_data.head())

    # Determine label column name (varies by dataset version)
    label_col = None
    id_col = None

    if 'EncodedPixels' in csv_data.columns or ' EncodedPixels' in csv_data.columns:
        label_col = 'EncodedPixels' if 'EncodedPixels' in csv_data.columns else ' EncodedPixels'
        id_col = 'ImageId' if 'ImageId' in csv_data.columns else ' ImageId'
        print(f"\nUsing EncodedPixels format (SIIM Kaggle dataset)")
        print(f"  ID column: {id_col}")
        print(f"  Label column: {label_col}")
    else:
        raise ValueError(f"Unknown CSV format. Columns: {list(csv_data.columns)}")

    # Get all preprocessed images
    all_imgs = sorted(glob.glob(os.path.join(processed_datapath, 'images', '*.png')))
    print(f"\nFound {len(all_imgs)} preprocessed images")

    # Match images to labels from CSV
    img_paths = []
    img_labels = []

    for img_path in tqdm(all_imgs, desc="Matching images to labels"):
        # Get image ID (filename without extension)
        img_id = os.path.basename(img_path).replace('.png', '')

        # Find label in CSV
        # ImageId in CSV might have .dcm extension, so try both
        matches = csv_data[csv_data[id_col].str.replace('.dcm', '', regex=False) == img_id]

        if len(matches) == 0:
            # Try exact match
            matches = csv_data[csv_data[id_col] == img_id]

        if len(matches) > 0:
            # Get EncodedPixels value
            encoded_pixels = matches[label_col].values[0]

            # Assign label: has_pneumo=1 if EncodedPixels is not -1 or empty
            if pd.isna(encoded_pixels) or encoded_pixels == -1 or encoded_pixels == '-1' or encoded_pixels == '':
                has_pneumo = 0
            else:
                has_pneumo = 1

            img_paths.append(img_path)
            img_labels.append(has_pneumo)
        else:
            print(f"Warning: No label found for {img_id}")

    print(f"\nMatched {len(img_paths)} images to labels")
    print(f"  Positive (pneumothorax): {sum(img_labels)}")
    print(f"  Negative (no pneumothorax): {len(img_labels) - sum(img_labels)}")

    if len(img_paths) == 0:
        raise ValueError("No images matched to labels! Check ImageId format.")

    # Convert to numpy arrays
    img_paths = np.array(img_paths)
    img_labels = np.array(img_labels)

    # Split into train and test (70/30 split, stratified)
    x_train_all, x_test, y_train_all, y_test = train_test_split(
        img_paths, img_labels,
        test_size=0.3,
        stratify=img_labels,
        random_state=seed
    )

    # Split train into train and val (85/15 split of the training data)
    x_train, x_val, y_train, y_val = train_test_split(
        x_train_all, y_train_all,
        test_size=0.15,
        stratify=y_train_all,
        random_state=seed
    )

    # Create 1% and 10% subsets of training data
    x_train_1, _, y_train_1, _ = train_test_split(
        x_train, y_train,
        train_size=0.01,
        stratify=y_train,
        random_state=seed
    )

    x_train_10, _, y_train_10, _ = train_test_split(
        x_train, y_train,
        train_size=0.10,
        stratify=y_train,
        random_state=seed
    )

    print(f"\nSplit sizes:")
    print(f"  train_1 (1%): {len(x_train_1)} samples (Pos: {sum(y_train_1)}, Neg: {len(y_train_1)-sum(y_train_1)})")
    print(f"  train_10 (10%): {len(x_train_10)} samples (Pos: {sum(y_train_10)}, Neg: {len(y_train_10)-sum(y_train_10)})")
    print(f"  train (100%): {len(x_train)} samples (Pos: {sum(y_train)}, Neg: {len(y_train)-sum(y_train)})")
    print(f"  val: {len(x_val)} samples (Pos: {sum(y_val)}, Neg: {len(y_val)-sum(y_val)})")
    print(f"  test: {len(x_test)} samples (Pos: {sum(y_test)}, Neg: {len(y_test)-sum(y_test)})")

    # Save split files
    save_anno(x_train.tolist(), os.path.join(processed_datapath, 'train.txt'))
    save_anno(x_train_1.tolist(), os.path.join(processed_datapath, 'train_1.txt'))
    save_anno(x_train_10.tolist(), os.path.join(processed_datapath, 'train_10.txt'))
    save_anno(x_val.tolist(), os.path.join(processed_datapath, 'val.txt'))
    save_anno(x_test.tolist(), os.path.join(processed_datapath, 'test.txt'))

    # Create labels CSV for BenchX
    # Combine all images with their labels
    all_image_ids = []
    all_labels = []

    for img_path, label in zip(list(x_train) + list(x_val) + list(x_test),
                                 list(y_train) + list(y_val) + list(y_test)):
        img_id = os.path.basename(img_path).replace('.png', '')
        all_image_ids.append(img_id)
        all_labels.append(label)

    labels_df = pd.DataFrame({
        'new_filename': [f"{img_id}.png" for img_id in all_image_ids],
        'has_pneumo': all_labels
    })

    labels_csv_path = os.path.join(processed_datapath, "siim_labels.csv")
    labels_df.to_csv(labels_csv_path, index=False)
    print(f"\nSaved siim_labels.csv with {len(labels_df)} rows")
    print(f"  Columns: {list(labels_df.columns)}")


if __name__ == "__main__":
    print("="*70)
    print("SIIM Pneumothorax Preprocessing - FIXED VERSION")
    print("="*70)
    print(f"\nSource: {data_path}")
    print(f"Output: {processed_datapath}\n")

    # Step 1: Preprocess images and masks
    print("Step 1: Preprocessing images and masks...")
    preprocess_pneumothorax_data()

    # Step 2: Create splits using CSV labels
    print("\nStep 2: Creating splits from CSV labels...")
    split_seg_dataset(seed=42)

    print("\n" + "="*70)
    print("Preprocessing complete!")
    print("="*70)
    print(f"\nFiles created:")
    print(f"  - {processed_datapath}/images/ (resized PNG images)")
    print(f"  - {processed_datapath}/masks/ (resized PNG masks)")
    print(f"  - {processed_datapath}/train_1.txt (1% split)")
    print(f"  - {processed_datapath}/train_10.txt (10% split)")
    print(f"  - {processed_datapath}/train.txt (100% split)")
    print(f"  - {processed_datapath}/val.txt (validation)")
    print(f"  - {processed_datapath}/test.txt (test)")
    print(f"  - {processed_datapath}/siim_labels.csv (labels)")
    print("\nValidation set now contains BOTH positive and negative samples!")
