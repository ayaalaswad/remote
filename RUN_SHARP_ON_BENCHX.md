# Run SHARP on BenchX - Simple Instructions

## Goal
Load SHARP's ViT encoder → Run on SIIM/RSNA → Compare to BenchX baselines

## Steps (On Remote Desktop)

### Step 1: Pull Latest Code

```cmd
cd C:\Users\aya.alaswad\remote
git pull origin main
```

### Step 2: Extract SHARP's ViT Encoder

```cmd
python extract_sharp_encoder.py
```

**Expected output:**
```
================================================================================
Extracting SHARP ViT Encoder for BenchX
================================================================================

Loading SHARP checkpoint: D:\experiments\exp3_full_sharp\p3_best.pt
Checkpoint keys: ['model_state_dict', 'optimizer_state_dict', 'step', ...]

Found XXX image encoder parameters
...
Extracted XXX ViT parameters
Excluded XXX projection head parameters

Saving extracted encoder to: D:\experiments\sharp_vit_encoder.pt
Saving BenchX-compatible version to: D:\experiments\sharp_vit_encoder_benchx.pt
✓ Saved successfully (XX.X MB)

SUCCESS! Extracted encoder ready for BenchX
================================================================================
```

**This creates:**
- `D:\experiments\sharp_vit_encoder.pt` - Full format
- `D:\experiments\sharp_vit_encoder_benchx.pt` - BenchX compatible ✅

### Step 3: Run on SIIM

```cmd
# Copy SHARP config
copy sharp_siim_DIRECT.yml BenchX\configs\classification\SIIM\sharp.yml /Y

# Train on SIIM
cd BenchX
python bin/train.py configs/classification/SIIM/sharp.yml
```

**Expected:** Training runs for 30 epochs, saves best model based on AUROC

### Step 4: Run on RSNA (Optional - After SIIM Works)

```cmd
cd C:\Users\aya.alaswad\remote

# Preprocess RSNA first (if not done)
python preprocess_rsna_adapted.py

# Copy SHARP config
copy sharp_rsna_DIRECT.yml BenchX\configs\classification\RSNA\sharp.yml /Y

# Train on RSNA
cd BenchX
python bin/train.py configs/classification/RSNA/sharp.yml
```

### Step 5: Extract Results

```cmd
cd BenchX

# Find SIIM results
dir /s /b experiments\classification\siim\*\val_metrics.pt

# Find RSNA results
dir /s /b experiments\classification\rsna\*\val_metrics.pt

# Load metrics
python -c "import torch; print(torch.load('experiments/classification/siim/[folder]/val_metrics.pt'))"
```

**Expected output:**
```python
{
    'binary_auroc': 0.XXXX,
    'binary_accuracy': 0.XXXX
}
```

## Comparison to BenchX Baselines

| Method | SIIM AUROC | RSNA AUROC | Source |
|--------|------------|------------|--------|
| **SHARP (yours)** | ??? | ??? | Your run |
| ConVIRT | ??? | ??? | BenchX paper Table X |
| MGCA | ??? | ??? | BenchX paper Table X |
| MRM | ??? | ??? | BenchX paper Table X |
| MedKLIP | ??? | ??? | BenchX paper Table X |

Fill in the table after your runs complete!

## If It Fails

### Error: "Cannot load checkpoint"

BenchX might not recognize the extracted checkpoint format.

**Solution:** Use the custom loader (`load_sharp_in_benchx.py`) instead.

### Error: "Key mismatch"

The extracted weights don't match ViT architecture.

**Debug:**
```cmd
python -c "import torch; ckpt=torch.load('D:/experiments/sharp_vit_encoder_benchx.pt'); print(list(ckpt.keys())); print(len(ckpt['state_dict']))"
```

Send me the output.

### Error: Still pickle error

Make sure `num_workers: 0` in the config.

## Success Looks Like

```
Epoch 1/30: 100%|██████████| 1/1 [00:05<00:00]
Train Loss: 0.6234
Val AUROC: 0.5123

Epoch 2/30: 100%|██████████| 1/1 [00:05<00:00]
Train Loss: 0.5891
Val AUROC: 0.6234
...

Early stopping triggered at epoch 15
Best Val AUROC: 0.7845
Checkpoint saved to: experiments/classification/siim/sharp_20260606_XXXXXX/best.pt
```

Then you have your SHARP AUROC to compare with baselines!

---

**Start with Step 1 on remote now!**
