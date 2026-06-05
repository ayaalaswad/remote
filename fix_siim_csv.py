import os
import pandas as pd

# Paths
data_path = r"D:\datasets\siim-pneumothorax\siim-acr-pneumothorax-segmentation"
processed_datapath = r"C:\Users\aya.alaswad\remote\BenchX\datasets\SIIM"

csv_path = os.path.join(data_path, "stage_2_train.csv")
output_csvpath = os.path.join(processed_datapath, "siim_labels.csv")

print("Fixing SIIM CSV to add has_pneumo column...")

# Read the original CSV
df = pd.read_csv(csv_path)
print(f"Original CSV shape: {df.shape}")
print(f"Columns: {df.columns.tolist()}")

# Add new_filename column
if 'ImageId' in df.columns:
    df['new_filename'] = df['ImageId'].astype(str) + '.png'

# Add has_pneumo column (binary label)
# If EncodedPixels is not -1, there's pneumothorax
if ' EncodedPixels' in df.columns:
    df['has_pneumo'] = (df[' EncodedPixels'] != ' -1').astype(int)
    print(f"Using column: ' EncodedPixels'")
elif 'EncodedPixels' in df.columns:
    df['has_pneumo'] = (df['EncodedPixels'] != '-1').astype(int)
    print(f"Using column: 'EncodedPixels'")
else:
    print(f"WARNING: No EncodedPixels column found! Columns: {df.columns.tolist()}")
    df['has_pneumo'] = 0

# Show label distribution
print(f"\nLabel distribution:")
print(df['has_pneumo'].value_counts())

# Save
df.to_csv(output_csvpath, index=False)
print(f"\nSaved to: {output_csvpath}")
print(f"Final CSV shape: {df.shape}")
print(f"Final columns: {df.columns.tolist()[:10]}...")  # Show first 10 columns
