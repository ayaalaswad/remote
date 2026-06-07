# SIIM Pneumothorax - BenchX Setup

## Dataset

**SIIM-ACR Pneumothorax Segmentation Challenge**
- Task: Binary classification (pneumothorax detection)
- Kaggle dataset: https://www.kaggle.com/datasets/vbookshelf/pneumothorax-chest-xray-images-and-masks
- Downloaded to: `C:\Users\aya.alaswad\Downloads\archive`

## Expected Dataset Structure

The downloaded archive should contain:
```
archive/
├── png_images/       # PNG images (already converted from DICOM)
├── png_masks/        # Segmentation masks
├── stage_1_train_images.csv
└── stage_1_test_images.csv
```

## BenchX Baseline Results (F1 Scores)

From BenchX Table 2:

| Method | 1% | 10% | 100% | Backbone |
|--------|-----|-----|------|----------|
| **MRM** | **60.2** | **72.4** | **74.7** | ViT-B |
| **MGCA-ViT** | 51.7 | 67.9 | 72.7 | ViT-B |
| **REFERS** | 56.2 | 68.1 | 72.0 | ViT-B |
| MedCLIP-ViT | 52.0 | 67.7 | 71.5 | ViT-B |
| ConVIRT | 50.6 | 62.8 | 69.6 | ResNet-50 |
| GLoRIA | 47.3 | 61.1 | 69.2 | ResNet-50 |

**MRM is the top performer** on SIIM across all data regimes.

## Setup Steps

### 1. Verify Downloaded Dataset

On remote desktop, check the archive contents:

```cmd
dir C:\Users\aya.alaswad\Downloads\archive
dir C:\Users\aya.alaswad\Downloads\archive\png_images
dir C:\Users\aya.alaswad\Downloads\archive\png_masks
```

Should show:
- `png_images/` with ~12,000 PNG files
- `png_masks/` with ~12,000 PNG files
- `stage_1_train_images.csv`
- `stage_1_test_images.csv`

### 2. Run Preprocessing + Training

**Option 1: All 3 splits (recommended)**

```cmd
cd C:\Users\aya.alaswad\remote
git pull origin main
run_siim_all_splits.bat
```

This will:
1. Preprocess SIIM dataset (resize to 512x512, create splits)
2. Train on 1% split (~20-30 min)
3. Train on 10% split (~1-1.5 hrs)
4. Train on 100% split (~2-3 hrs)

**Total time:** ~3-4 hours

**Option 2: Just preprocessing (to verify dataset)**

```cmd
cd C:\Users\aya.alaswad\remote
git pull origin main
python preprocess_siim_benchx.py
```

This will show dataset statistics and verify all files are present.

### 3. Verify Preprocessing Output

After preprocessing, check:

```cmd
dir BenchX\datasets\SIIM\images     # Should have ~12k PNG files
dir BenchX\datasets\SIIM\masks      # Should have ~12k PNG files
type BenchX\datasets\SIIM\train_1.txt   # Should show ~100 samples (1%)
type BenchX\datasets\SIIM\train_10.txt  # Should show ~1k samples (10%)
type BenchX\datasets\SIIM\train.txt     # Should show ~10k samples (100%)
```

## Configuration Details

All 3 configs use **identical MGCA protocol**:

### Shared Parameters (BenchX Standard)

```yaml
optimizer: SGD
lr: 1e-2 (with 0.1x multiplier for backbone)
momentum: 0.9
batch_size: 64
early_stop: 10
```

### Split-Specific Parameters

| Config | Split | Samples | Epochs | Eval Start | Eval Interval |
|--------|-------|---------|--------|------------|---------------|
| `sharp_siim_1pct.yml` | train_1 | ~100 | 30 | 5 | 2 |
| `sharp_siim_10pct.yml` | train_10 | ~1,000 | 30 | 5 | 2 |
| `sharp_siim_100pct.yml` | train | ~10,000 | 50 | 10 | 5 |

## Expected Results

After training completes, results will be in:

```
BenchX/experiments/classification/siim/
├── SHARP_1pct/[AUROC]_[epoch]_42.pth
├── SHARP_10pct/[AUROC]_[epoch]_42.pth
└── SHARP_100pct/[AUROC]_[epoch]_42.pth
```

## Calculate F1 Scores

After training, calculate F1 scores to compare with BenchX baselines:

```python
# Update calculate_f1_scores.py with SIIM paths
# Run: python calculate_f1_scores_siim.py
```

## Why SIIM Matters

After RSNA showed poor performance (F1: 24.2 / 43.1 / 45.9 vs baselines 60-67), SIIM is important because:

1. **Different dataset** - Different hospital, different pathology (pneumothorax vs pneumonia)
2. **Different challenge** - Pneumothorax detection has different visual patterns
3. **Second data point** - Helps determine if RSNA performance was dataset-specific or systemic
4. **BenchX comparison** - MRM achieves 60.2 / 72.4 / 74.7 on SIIM (similar to RSNA range)

If SHARP performs poorly on SIIM too, it suggests a fundamental issue with the pretraining or finetuning approach rather than dataset-specific problems.

## Troubleshooting

### Error: "png_images not found"

Check if the downloaded archive needs to be extracted:

```cmd
# If it's a .zip file
cd C:\Users\aya.alaswad\Downloads
unzip archive.zip
```

Or verify the exact folder name.

### Error: "ModuleNotFoundError: No module named 'PIL'"

Install Pillow:

```cmd
pip install Pillow
```

### Error: Dataset has 0 samples

Check that:
1. Preprocessing completed successfully
2. Split files (train_1.txt, etc.) contain image IDs
3. Images exist in BenchX/datasets/SIIM/images/

## Files Created

- `preprocess_siim_benchx.py` - Preprocessing script (BenchX's original logic)
- `sharp_siim_1pct.yml` - 1% split config
- `sharp_siim_10pct.yml` - 10% split config
- `sharp_siim_100pct.yml` - 100% split config
- `run_siim_all_splits.bat` - Automated script for all 3 splits
