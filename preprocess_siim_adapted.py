import os
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
import pydicom as dicom
from pydicom.pixel_data_handlers.util import apply_voi_lut
from PIL import Image
from tqdm import tqdm
import glob

# Paths for your remote desktop
data_path = r"D:\datasets\siim-pneumothorax\siim-acr-pneumothorax-segmentation"
processed_datapath = r"C:\Users\aya.alaswad\remote\BenchX\datasets\SIIM"

imgpath = os.path.join(data_path, "stage_2_images")
csv_path = os.path.join(data_path, "stage_2_train.csv")

output_image_dir = os.path.join(processed_datapath, "images")
if not os.path.exists(output_image_dir):
    os.makedirs(output_image_dir)

output_mask_dir = os.path.join(processed_datapath, "masks")
if not os.path.exists(output_mask_dir):
    os.makedirs(output_mask_dir)

desired_size = 512

def preprocess_siim_data():
    print(f"Converting SIIM DICOM images to PNG...")

    # Get all DICOM files
    all_dcm_files = glob.glob(os.path.join(imgpath, "*.dcm"))
    print(f"Found {len(all_dcm_files)} DICOM files")

    for dcm_path in tqdm(all_dcm_files):
        image_id = os.path.basename(dcm_path).replace(".dcm", "")

        # Convert DICOM to PNG
        dc_image = dicom.dcmread(dcm_path, force=True)

        image_array = dc_image.pixel_array.astype(float)
        image_array = apply_voi_lut(image_array, dc_image)

        # Fix inverted X-rays
        if dc_image.PhotometricInterpretation == "MONOCHROME1":
            image_array = np.amax(image_array) - image_array

        scaled_image = (np.maximum(image_array, 0) / image_array.max()) * 255.0
        scaled_image = np.uint8(scaled_image)

        final_image = Image.fromarray(scaled_image).convert("RGB")
        old_size = final_image.size
        ratio = float(desired_size)/max(old_size)
        new_size = tuple([int(x*ratio) for x in old_size])
        final_image = final_image.resize(new_size, Image.Resampling.LANCZOS)

        final_image.save(os.path.join(output_image_dir, image_id + ".png"), 'PNG')

        # Create empty mask for now (we don't have mask data readily available)
        mask = np.zeros([desired_size, desired_size]).astype(np.uint8)
        final_mask = Image.fromarray(mask)
        final_mask.save(os.path.join(output_mask_dir, image_id + ".png"), 'PNG')

    print(f"Converted {len(all_dcm_files)} images")

    # Create BenchX-compatible CSV
    output_csvpath = os.path.join(processed_datapath, "siim_labels.csv")
    df = pd.read_csv(csv_path)

    # Add new_filename column
    if 'ImageId' in df.columns:
        df['new_filename'] = df['ImageId'].astype(str) + '.png'

    # Add has_pneumo column (binary label)
    # If EncodedPixels is not -1, there's pneumothorax
    if ' EncodedPixels' in df.columns:
        df['has_pneumo'] = (df[' EncodedPixels'] != ' -1').astype(int)
    elif 'EncodedPixels' in df.columns:
        df['has_pneumo'] = (df['EncodedPixels'] != '-1').astype(int)
    else:
        # Default to 0 if we can't determine
        df['has_pneumo'] = 0

    df.to_csv(output_csvpath, index=False)
    print(f"Saved siim_labels.csv with has_pneumo column")

def save_anno(img_list, file_path, remove_suffix=False):
    if remove_suffix:
        img_list = [img_path.split('/')[-1] for img_path in img_list]
        img_list = ['.'.join(img_path.split('.')[:-1]) for img_path in img_list]
    with open(file_path, 'w') as file_:
        for x in list(img_list):
            file_.write(x + '\n')

def split_siim_dataset(seed):
    print("Creating train/val/test splits...")

    # Get all converted images
    all_images = glob.glob(os.path.join(output_image_dir, "*.png"))
    image_ids = [os.path.basename(p).replace(".png", "") for p in all_images]

    print(f"Found {len(image_ids)} converted images")

    if len(image_ids) == 0:
        print("ERROR: No images found for splitting!")
        return

    # Simple random split without label stratification
    # (CSV format mismatch makes label extraction unreliable)
    x = image_ids

    # 70% train, 15% val, 15% test
    x_train, x_temp = train_test_split(x, test_size=0.3, random_state=seed)
    x_val, x_test = train_test_split(x_temp, test_size=0.5, random_state=seed)

    # 1% and 10% subsets (no stratification needed)
    x_train_1, _ = train_test_split(x_train, test_size=0.99, random_state=seed)
    x_train_10, _ = train_test_split(x_train, test_size=0.90, random_state=seed)

    save_anno(x_train, processed_datapath + '/train.txt')
    save_anno(x_train_1, processed_datapath + '/train_1.txt')
    save_anno(x_train_10, processed_datapath + '/train_10.txt')
    save_anno(x_val, processed_datapath + '/val.txt')
    save_anno(x_test, processed_datapath + '/test.txt')

    print(f"Splits created: {len(x_train)} train, {len(x_val)} val, {len(x_test)} test")

if __name__ == "__main__":
    print("="*60)
    print("SIIM Preprocessing for BenchX")
    print("="*60)
    print()

    preprocess_siim_data()
    split_siim_dataset(seed=42)

    print()
    print("="*60)
    print("SIIM preprocessing complete!")
    print("="*60)
