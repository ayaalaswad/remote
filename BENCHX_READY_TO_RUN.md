# BenchX SHARP Training - Ready to Run

## Summary

✅ **SIIM preprocessing complete** - 3,205 images converted and split
✅ **Configs created and pushed to GitHub**
✅ **Full automation script ready**

## What's Ready

### 1. SIIM Dataset
- **Status:** ✅ Preprocessed and ready
- **Location:** `C:\Users\aya.alaswad\remote\BenchX\datasets\SIIM`
- **Data:**
  - 3,205 PNG images (512x512)
  - Train: 2,243 images
  - Val: 481 images
  - Test: 481 images
- **Config:** `sharp_siim.yml` (points to preprocessed data)

### 2. RSNA Dataset
- **Status:** ⏳ Preprocessing script ready, not yet run
- **Location:** Raw data at `D:\datasets\rsna-pneumonia`
- **Will preprocess to:** `C:\Users\aya.alaswad\remote\BenchX\datasets\RSNA`
- **Expected:** ~30k images, ~10-15 min to preprocess
- **Config:** `sharp_rsna.yml` (points to preprocessed data)

## How to Run

### Option 1: Run Everything (Recommended)

On the remote desktop, run:

```cmd
cd C:\Users\aya.alaswad\remote
run_benchx_siim_rsna.bat
```

This will automatically:
1. **[0/4]** Pull latest code from GitHub
2. **[1/4]** Train SHARP on SIIM (30-45 min)
3. **[2/4]** Preprocess RSNA dataset (10-15 min)
4. **[3/4]** Train SHARP on RSNA (1-1.5 hours)
5. **[4/4]** Extract AUROC results

**Total time:** ~2 hours (unattended)

### Option 2: Run Step-by-Step

#### SIIM Only:
```cmd
cd C:\Users\aya.alaswad\remote
git pull origin main
copy sharp_siim.yml BenchX\configs\classification\SIIM\sharp.yml /Y
cd BenchX
python bin/train.py configs/classification/SIIM/sharp.yml
```

#### RSNA Preprocessing:
```cmd
cd C:\Users\aya.alaswad\remote
python preprocess_rsna_adapted.py
```

#### RSNA Training:
```cmd
cd C:\Users\aya.alaswad\remote
copy sharp_rsna.yml BenchX\configs\classification\RSNA\sharp.yml /Y
cd BenchX
python bin/train.py configs/classification/RSNA/sharp.yml
```

## Expected Outputs

### Training Results Location
- SIIM: `C:\Users\aya.alaswad\remote\BenchX\results\[timestamp]_SIIM_sharp\`
- RSNA: `C:\Users\aya.alaswad\remote\BenchX\results\[timestamp]_RSNA_sharp\`

### Key Metrics File
- `val_metrics.pt` in each results folder
- Contains: `{'binary_auroc': X.XX, 'binary_accuracy': Y.YY}`

### Extract AUROC
```cmd
cd C:\Users\aya.alaswad\remote\BenchX
python -c "import torch; print(torch.load('results/[folder]/val_metrics.pt'))"
```

## Config Details

Both configs use:
- **Model:** SHARP (ViT-B/16)
- **Checkpoint:** `D:/experiments/exp3_full_sharp/p3_best.pt`
- **Training split:** `train_1` (1% subset for quick evaluation)
- **Batch size:** 32
- **Learning rate:** 1e-4
- **Optimizer:** AdamW
- **Metric:** binary_auroc

## Next Steps After Training

1. **Extract AUROC scores** from both datasets
2. **Compare to BenchX baselines:**
   - MGCA (ViT-B): SIIM=X.XX, RSNA=Y.YY
   - MRM (ViT-B): SIIM=X.XX, RSNA=Y.YY
   - Other baselines in BenchX paper
3. **Add to paper:** Results table comparing SHARP vs 9 baselines
4. **Optional:** Run on NIH and VinDr datasets (requires downloading)

## Troubleshooting

If training fails:
1. Check GPU is available: `nvidia-smi`
2. Verify conda env is active: `conda activate benchx` (or your env name)
3. Check preprocessed data exists:
   - `dir C:\Users\aya.alaswad\remote\BenchX\datasets\SIIM\images`
   - `dir C:\Users\aya.alaswad\remote\BenchX\datasets\SIIM\*.txt`
4. Verify checkpoint exists:
   - `dir D:\experiments\exp3_full_sharp\p3_best.pt`

## Files Pushed to GitHub

- ✅ `sharp_siim.yml` - SIIM config (preprocessed data paths)
- ✅ `sharp_rsna.yml` - RSNA config (preprocessed data paths)
- ✅ `run_benchx_siim_rsna.bat` - Full automation script
- ✅ `preprocess_siim_adapted.py` - SIIM preprocessing (already run)
- ✅ `preprocess_rsna_adapted.py` - RSNA preprocessing (ready to run)

## Status

**You're ready to run!** The automation script will handle everything from config setup through result extraction.

Just run `run_benchx_siim_rsna.bat` on the remote desktop and let it run for ~2 hours.
