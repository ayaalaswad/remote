# Linear Probe vs Fine-Tuning Comparison

## Side-by-Side: Key Differences

| Setting | Fine-Tuning (sharp_rsna_10pct.yml) | Linear Probe (sharp_rsna_10pct_lp.yml) |
|---------|-------------------------------------|----------------------------------------|
| **name** | `SHARP_10pct` | `SHARP_10pct_LinearProbe` |
| **ckpt_dir** | `experiments/classification/rsna/SHARP_10pct/` | `experiments/classification/rsna/SHARP_10pct_LP/` |
| **lr_multiplier_ve** | `0.1` ⚠️ | `0.0` ✅ **FROZEN** |
| **Comment** | `# EXACT MGCA TRAINING PROTOCOL` | `# LINEAR PROBE - Encoder frozen` |

## The Critical Line

**Fine-Tuning (encoder trains at 10% of classifier LR):**
```yaml
trainer:
  optim_params:
    lr_multiplier_ve: 0.1  # Encoder LR = 1e-2 * 0.1 = 1e-3
```

**Linear Probe (encoder completely frozen):**
```yaml
trainer:
  optim_params:
    lr_multiplier_ve: 0.0  # Encoder LR = 1e-2 * 0.0 = 0.0 (FROZEN)
```

## What This Means

### Fine-Tuning (0.1):
- Encoder trains at 0.001 LR
- Classifier trains at 0.01 LR
- Both encoder and classifier adapt to RSNA
- **Your result:** F1 = 43.1%, AUROC = 0.7514

### Linear Probe (0.0):
- Encoder completely frozen (no gradient updates)
- Classifier trains at 0.01 LR
- Only classifier adapts to RSNA
- Tests how good SHARP's frozen features are

## Expected Outcome

**If Linear Probe ≈ Fine-Tuning:**
→ SHARP's frozen features are already very good for RSNA
→ Fine-tuning didn't help much

**If Linear Probe << Fine-Tuning:**
→ Fine-tuning is necessary
→ SHARP's features need adaptation

## Commands

### Run Linear Probe (10% data, ~1-2 hours):
```cmd
cd C:\Users\aya.alaswad\remote
git pull origin main

copy sharp_rsna_10pct_lp.yml BenchX\configs\classification\RSNA\sharp.yml /Y

cd BenchX
python bin/train.py configs/classification/RSNA/sharp.yml
```

### Results will be saved to:
```
D:\experiments\classification\rsna\SHARP_10pct_LP\
```

### Extract F1 scores after training:
```cmd
cd C:\Users\aya.alaswad\remote
python calculate_rsna_f1_all.py
```

## Comparison Table (Fill After Linear Probe Completes)

| Method | AUROC | F1 | Accuracy | Notes |
|--------|-------|-----|----------|-------|
| **Fine-Tuning** | 0.7514 | 43.1% | 76.5% | Encoder trained |
| **Linear Probe** | ??? | ??? | ??? | Encoder frozen |
| **Difference** | ??? | ??? | ??? | Shows value of fine-tuning |

If Linear Probe F1 ≈ 40-43%, fine-tuning didn't help much.
If Linear Probe F1 < 30%, fine-tuning is crucial for SHARP.
