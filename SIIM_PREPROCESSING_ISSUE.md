# SIIM Preprocessing Issue - Root Cause Analysis

## Which Script Was Used?

**Custom script (NOT BenchX's original):**
```
preprocess_siim_benchx.py
```

Based on BenchX's template from `paths/preprocess_siim.py` but with paths adapted.

## The Critical Bug (Line 66-67)

```python
def split_seg_dataset(seed=42):
    """Create train/val/test splits (1%, 10%, 100%)"""
    # THIS IS THE BUG:
    train_pos_imgs = sorted(glob.glob(os.path.join(processed_datapath, 'images', '*train_1*.png')))
    train_neg_imgs = sorted(glob.glob(os.path.join(processed_datapath, 'images', '*train_0*.png')))
```

**Problem:** This searches for files that are **ALREADY split** with labels in the filename:
- `*train_1*.png` = files with "train_1" in the name (pneumothorax present)
- `*train_0*.png` = files with "train_0" in the name (no pneumothorax)

**But the Kaggle dataset doesn't have these labels in filenames!**

## What the Kaggle Dataset Actually Contains

```
archive/
├── png_images/
│   ├── 1.2.276.0.7230010.3.1.4.8323329.300.1517875162.117067.png
│   ├── 1.2.276.0.7230010.3.1.4.8323329.300.1517875162.117068.png
│   └── ... (~12,000 PNG files with DICOM UIDs as names)
│
├── png_masks/
│   ├── 1.2.276.0.7230010.3.1.4.8323329.300.1517875162.117067.png
│   └── ... (matching masks)
│
├── stage_1_train_images.csv  ← Contains labels!
└── stage_1_test_images.csv   ← Contains labels!
```

**Filename format:** DICOM UIDs (e.g., `1.2.276.0.7230010.3.1.4.8323329.300.1517875162.117067.png`)

**NO `train_0` or `train_1` in filenames!**

## What Happened

1. **Step 1: `preprocess_pneumothorax_data()`** ✅ Works fine
   - Finds all ~12k images in `png_images/`
   - Resizes them to 512x512
   - Saves to `BenchX/datasets/SIIM/images/`

2. **Step 2: `split_seg_dataset()`** ❌ **FAILS**
   ```python
   train_pos_imgs = glob.glob('*train_1*.png')  # Finds 0 files
   train_neg_imgs = glob.glob('*train_0*.png')  # Finds 0 files
   ```
   - Searches for files with `train_1` / `train_0` in name
   - Finds **ZERO files** (because filenames are DICOM UIDs)
   - `train_pos_imgs = []` (empty!)
   - `train_neg_imgs = []` (empty!)

3. **train_test_split() crashes or creates empty splits**
   - If `x = []` and `y = []`, can't stratify
   - Or it might use ALL images as negative class by default

4. **Result: Validation set has only class 0**
   - All 480 validation samples = "no pneumothorax"
   - AUROC = NaN (need both classes)
   - F1 = 0 (no true positives possible)

## Comparison: BenchX Original vs What Was Used

### BenchX Original (`paths/preprocess_siim.py`)
```python
# SAME BUG - expects pre-labeled filenames
train_pos_imgs = sorted(glob.glob(processed_datapath + '/images/*train_1*.png'))
train_neg_imgs = sorted(glob.glob(processed_datapath + '/images/*train_0*.png'))
```

### What Was Used (`preprocess_siim_benchx.py`)
```python
# IDENTICAL BUG - just with os.path.join instead of string concat
train_pos_imgs = sorted(glob.glob(os.path.join(processed_datapath, 'images', '*train_1*.png')))
train_neg_imgs = sorted(glob.glob(os.path.join(processed_datapath, 'images', '*train_0*.png')))
```

**Both have the same bug!** This means:
- BenchX's "original" script is actually a template/example
- Real BenchX preprocessing must be different
- Or they expect a different Kaggle dataset download

## The Correct Approach

**Read labels from CSV files instead of filenames:**

```python
def split_seg_dataset(seed=42):
    # Read labels from CSV
    csv_train = pd.read_csv(os.path.join(data_path, "stage_1_train_images.csv"))
    csv_test = pd.read_csv(os.path.join(data_path, "stage_1_test_images.csv"))

    # Get all preprocessed images
    all_imgs = sorted(glob.glob(os.path.join(processed_datapath, 'images', '*.png')))

    # Match images to labels from CSV
    train_imgs = []
    train_labels = []

    for img_path in all_imgs:
        img_id = os.path.basename(img_path).replace('.png', '')

        # Find label in CSV (by matching ImageId or DICOM UID)
        # This is where the logic needs to be dataset-specific
        label = csv_train[csv_train['ImageId'] == img_id]['Label'].values

        if len(label) > 0:
            train_imgs.append(img_path)
            train_labels.append(label[0])

    # Now split with actual labels
    x_train, x_val, y_train, y_val = train_test_split(
        train_imgs, train_labels,
        test_size=0.2,
        stratify=train_labels,
        random_state=seed
    )
```

## Why BenchX's Script Expects `train_0` / `train_1` Filenames

**Hypothesis:** BenchX might expect a **different dataset source** than the Kaggle download:
1. Perhaps a pre-processed version from the official SIIM-ACR competition
2. Or they renamed files during preprocessing
3. Or the script in `paths/` is outdated/template

## What Needs to Happen

**Option 1: Find the correct SIIM dataset**
- Download from SIIM-ACR official competition (not Kaggle repackage)
- Check if files are already named with `train_0` / `train_1` patterns

**Option 2: Fix the preprocessing script**
- Read labels from CSV files
- Match image IDs to labels
- Create splits based on actual labels, not filename patterns

**Option 3: Check BenchX's actual preprocessing**
- Clone BenchX repo
- Check `BenchX/preprocess/datasets/prepare_SIIM.py`
- Use their official preprocessing script

## Impact on Results

**Current SIIM results are INVALID:**
- Training: Only learned to predict "no pneumothorax" (class 0)
- Validation: 100% accuracy but AUROC = NaN (all same class)
- F1 = 0 (no true positives possible)

**Cannot compare to BenchX baselines** until preprocessing is fixed.
