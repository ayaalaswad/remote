# BenchX SHARP Setup - Clean Instructions

## Step 1: Fix SIIM Dataset

The SIIM images are already converted, just fix the CSV:

```cmd
cd C:\Users\aya.alaswad\remote
python rebuild_siim_csv.py
```

Should show: "SUCCESS! Dataset will have 22 samples"

## Step 2: Copy SHARP Configs

```cmd
cd C:\Users\aya.alaswad\remote
copy sharp_siim_final.yml BenchX\configs\classification\SIIM\sharp.yml
copy sharp_rsna_final.yml BenchX\configs\classification\RSNA\sharp.yml
```

## Step 3: Train SIIM

```cmd
cd C:\Users\aya.alaswad\remote\BenchX
python bin/train.py configs/classification/SIIM/sharp.yml
```

Expected: ~30-45 minutes, should train without errors

## Step 4: Preprocess RSNA (while SIIM trains)

Open another terminal:

```cmd
cd C:\Users\aya.alaswad\remote
python preprocess_rsna_adapted.py
```

Expected: ~10-15 minutes to convert ~30k images

## Step 5: Train RSNA

```cmd
cd C:\Users\aya.alaswad\remote\BenchX
python bin/train.py configs/classification/RSNA/sharp.yml
```

Expected: ~1-1.5 hours

## Step 6: Check Results

```cmd
cd C:\Users\aya.alaswad\remote\BenchX
dir /s /b experiments\classification\siim\*\val_metrics.pt
dir /s /b experiments\classification\rsna\*\val_metrics.pt
```

Extract AUROC:
```cmd
python -c "import torch; print(torch.load('experiments/classification/siim/[folder]/val_metrics.pt'))"
```

## Key Differences from Before

1. Using BenchX's expected format (with `includes:` and proper structure)
2. SIIM uses NIHTransforms (no SIIM-specific transform exists)
3. RSNA uses RSNATransforms (exists in BenchX)
4. Both use extension: ".png" (overrides defaults)
5. AdamW optimizer (instead of Adam) for SHARP
6. Batch size 32 (instead of 64) to avoid OOM
7. 30 epochs (instead of 200) for faster evaluation

## If It Fails

Test with a working model first:
```cmd
python bin/train.py configs/classification/SIIM/convirt.yml
```

If ConVIRT works but SHARP doesn't, the issue is the checkpoint loading.
