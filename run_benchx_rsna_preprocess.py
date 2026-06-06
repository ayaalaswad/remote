"""
Run BenchX's original RSNA preprocessing with correct paths
"""
import sys

# Add BenchX to path
sys.path.insert(0, r'C:\Users\aya.alaswad\remote\BenchX')

# Set the correct paths for your system
import os
os.chdir(r'C:\Users\aya.alaswad\remote\BenchX\preprocess\datasets\RSNA')

# Monkey-patch the paths in the preprocessing script
import preprocess_rsna
preprocess_rsna.data_path = r"D:\datasets\rsna-pneumonia\rsna-pneumonia-detection-challenge"
preprocess_rsna.processed_datapath = r"C:\Users\aya.alaswad\remote\BenchX\datasets\RSNA"

# Recreate the paths with new values
preprocess_rsna.imgpath = os.path.join(preprocess_rsna.data_path, "stage_2_train_images")
preprocess_rsna.csv_path = os.path.join(preprocess_rsna.data_path, "stage_2_train_labels.csv")
preprocess_rsna.raw_csv = preprocess_rsna.pd.read_csv(preprocess_rsna.csv_path)
preprocess_rsna.csv = preprocess_rsna.raw_csv.groupby("patientId").first()

preprocess_rsna.output_image_dir = os.path.join(preprocess_rsna.processed_datapath, "images")
if not os.path.exists(preprocess_rsna.output_image_dir):
    os.makedirs(preprocess_rsna.output_image_dir)

preprocess_rsna.output_mask_dir = os.path.join(preprocess_rsna.processed_datapath, "masks")
if not os.path.exists(preprocess_rsna.output_mask_dir):
    os.makedirs(preprocess_rsna.output_mask_dir)

print("="*80)
print("Running BenchX's Original RSNA Preprocessing")
print("="*80)
print(f"Data path: {preprocess_rsna.data_path}")
print(f"Output path: {preprocess_rsna.processed_datapath}")
print()

# Run the preprocessing
if __name__ == "__main__":
    preprocess_rsna.preprocess_rsna_data()
    preprocess_rsna.generate_rsna_masks()
    preprocess_rsna.split_seg_dataset(seed=42)

    print()
    print("="*80)
    print("RSNA preprocessing complete!")
    print("="*80)
