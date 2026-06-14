# BenchX Results Comparison - SHARP Encoder

**Model:** SHARP (ViT-B/16) with Multi-positive InfoNCE
**Checkpoint:** `D:/experiments/exp3_full_sharp/p3_best_timm.pt`
**Date:** 2026-06-14

---

## SHARP Results Summary

### RSNA Pneumonia Detection (10% data)

| Experiment | Method | AUROC | Accuracy | F1 Score | Epoch | Status |
|------------|--------|-------|----------|----------|-------|--------|
| **RSNA Fine-tuning** | Encoder fine-tuned | **0.7514** | ~77% | 43.1% | - | ✅ Complete |
| **RSNA Linear Probe** | Encoder frozen | **0.7333** | 76.87% | - | 29 | ✅ Complete |

**Key Insight:** Only 2.4% AUROC drop when freezing encoder → SHARP learned transferable features

---

### SIIM Pneumothorax Detection

| Experiment | Data Split | AUROC | Accuracy | F1 Score | Status |
|------------|------------|-------|----------|----------|--------|
| **SIIM 1%** | 1% training data | TBD | TBD | TBD | ⏳ Needs extraction |
| **SIIM 10%** | 10% training data | TBD | TBD | TBD | ⏳ Needs extraction |
| **SIIM 100%** | 100% training data | TBD | TBD | TBD | ⏳ Needs extraction |

**Training:** All 3 splits completed on remote desktop. Run `python extract_all_benchx_results.py` to extract metrics.

---

## Comparison with BenchX Baselines

### RSNA Pneumonia (10% data)

| Method | Type | AUROC | F1 Score | Gap from Best |
|--------|------|-------|----------|---------------|
| **MGCA** 🥇 | Contrastive (image-text) | 0.793 | 66.6% | - |
| **MRM** | Masked region modeling | 0.787 | 64.2% | -0.006 |
| **REFERS** | Report-guided pretraining | 0.781 | 62.8% | -0.012 |
| **SHARP (Fine-tune)** | Multi-positive InfoNCE | **0.751** | **43.1%** | **-0.042** |
| **ImageNet Init** | Supervised pretraining | 0.743 | 52.1% | -0.050 |
| **SHARP (Linear)** | Frozen encoder | **0.733** | - | **-0.060** |
| **Random Init** | No pretraining | 0.721 | 48.9% | -0.072 |

---

## Performance Analysis

### AUROC Performance
✅ **SHARP beats:**
- Random initialization (+0.030)
- ImageNet initialization (+0.008)

⚠️ **SHARP underperforms:**
- MGCA by 0.042 (-5.3%)
- MRM by 0.036 (-4.6%)
- REFERS by 0.030 (-3.8%)

### F1 Score Analysis
🔴 **Major gap in F1:**
- SHARP: 43.1%
- MGCA: 66.6% (54% better)

**Possible Causes:**
1. Conservative predictions (high specificity, low sensitivity)
2. Class imbalance (77.5% negative class)
3. Threshold not optimized for F1
4. Classifier head suboptimal

### Linear Probe Gap
✅ **Small gap (2.4%)** between frozen and fine-tuned:
- Fine-tuning: 0.7514
- Linear Probe: 0.7333
- Difference: 0.0181

This suggests SHARP learned good general-purpose features during pretraining.

---

## Fine-Tuning vs Linear Probe Comparison

| Metric | Fine-Tuning | Linear Probe | Difference | % Change |
|--------|-------------|--------------|------------|----------|
| AUROC | 0.7514 | 0.7333 | -0.0181 | -2.4% |
| Accuracy | ~77% | 76.87% | -0.13% | -0.2% |
| Trainable Params | Encoder + Classifier | Classifier only | - | - |
| Training Time | ~30 epochs | ~30 epochs | - | - |

**Recommendation:** For deployment, consider linear probe for:
- Faster adaptation to new tasks
- Lower risk of overfitting
- Only 2.4% performance trade-off

---

## Training Configuration (Following MGCA Protocol)

```yaml
Optimizer: SGD (momentum=0.9)
Learning Rate: 1e-2
  - Fine-tuning: lr_multiplier_ve: 0.1
  - Linear Probe: lr_multiplier_ve: 0.0
Batch Size: 64
Max Epochs: 30
Early Stopping: 10 epochs
LR Schedule: WarmupCosineScheduler
  - Warmup: 50 steps
  - Total: 3000 steps
Gradient Clipping: 1.0
Mixed Precision: Enabled (AMP)
```

---

## Next Steps

### Immediate
1. ⏳ **Extract SIIM results** - Run `extract_all_benchx_results.py` on remote desktop
2. 🔍 **Analyze F1 gap** - Check precision/recall curves, prediction distributions
3. 📊 **Complete RadDINO** - Check if training finished

### Analysis
4. **Investigate low F1:**
   - Plot precision-recall curves
   - Analyze prediction thresholds
   - Check class-wise performance
5. **Compare prediction distributions:**
   - SHARP vs MGCA predictions
   - Sensitivity vs specificity trade-offs

### Potential Improvements
6. **Try different classification heads:**
   - Deeper MLP
   - Different dropout values
   - Class weighting
7. **Threshold tuning:**
   - Optimize for F1 instead of AUROC
8. **Ensemble methods:**
   - Combine linear probe + fine-tuning

---

## Files & Commands

### Extract Results (Run on remote desktop)
```cmd
cd C:\Users\aya.alaswad\remote
python extract_all_benchx_results.py
```

### Config Files
- `sharp_rsna_10pct.yml` - RSNA fine-tuning
- `sharp_rsna_lp.yml` - RSNA linear probe
- `sharp_siim_1pct.yml`, `sharp_siim_10pct.yml`, `sharp_siim_100pct.yml` - SIIM experiments

### Results Locations
- **RSNA Fine-tuning:** `BenchX/experiments/classification/rsna/SHARP/SHARP/`
- **RSNA Linear Probe:** `BenchX/experiments/classification/rsna/SHARP_LP/SHARP_LinearProbe/`
- **SIIM 1%:** `BenchX/experiments/classification/siim/SHARP_1pct/SHARP_1pct/`
- **SIIM 10%:** `BenchX/experiments/classification/siim/SHARP_10pct/SHARP_10pct/`
- **SIIM 100%:** `BenchX/experiments/classification/siim/SHARP_100pct/SHARP_100pct/`

---

## Repository
📦 **GitHub:** https://github.com/ayaalaswad/remote
📁 **Results pushed:**
- `rsna_lp_results/` ✅
- `siim_results_latest/` ⏳ Pending
