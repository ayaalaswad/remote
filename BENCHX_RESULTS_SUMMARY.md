# SHARP BenchX Results Summary

**Updated:** 2026-06-14
**Model:** SHARP (ViT-B/16) trained with Multi-positive InfoNCE
**Checkpoint:** `D:/experiments/exp3_full_sharp/p3_best_timm.pt`

---

## RSNA Pneumonia Detection (10% data)

### Fine-Tuning Results
- **AUROC:** 0.7514
- **F1 Score:** 43.1%
- **Accuracy:** ~77%
- **Training:** Encoder fine-tuned (lr_multiplier_ve: 0.1)
- **Config:** `sharp_rsna_10pct.yml` (Exp #3)

### Linear Probe Results ⭐ NEW
- **AUROC:** 0.7333 (best checkpoint: epoch 29)
- **Accuracy:** 76.87%
- **Training:** Encoder frozen (lr_multiplier_ve: 0.0)
- **Config:** `sharp_rsna_lp.yml`

### Comparison
| Metric | Fine-Tuning | Linear Probe | Difference |
|--------|-------------|--------------|------------|
| AUROC  | 0.7514      | 0.7333       | -0.0181 (-2.4%) |
| Accuracy | ~77%     | 76.87%       | -0.13% |

**Interpretation:** Fine-tuning provides a modest 2.4% AUROC improvement over frozen features, suggesting SHARP learned reasonably transferable representations during pretraining.

---

## SIIM Pneumothorax Detection ⭐ NEW

### 1% Data Split
- **Best Checkpoint:** TBD (results pushed, need extraction)
- **Config:** `sharp_siim_1pct.yml`

### 10% Data Split
- **Best Checkpoint:** TBD (results pushed, need extraction)
- **Config:** `sharp_siim_10pct.yml`

### 100% Data Split
- **Best Checkpoint:** TBD (results pushed, need extraction)
- **Config:** `sharp_siim_100pct.yml`

**Status:** All three splits completed and pushed. Metrics extraction pending.

---

## BenchX Baseline Comparison

From the BenchX paper (Gloria et al.), on RSNA Pneumonia 10%:

| Method | AUROC | F1 Score |
|--------|-------|----------|
| **MGCA** | 0.793 | 66.6% |
| **MRM** | 0.787 | 64.2% |
| **REFERS** | 0.781 | 62.8% |
| ImageNet Init | 0.743 | 52.1% |
| Random Init | 0.721 | 48.9% |
| **SHARP (Fine-tune)** | **0.751** | **43.1%** |
| **SHARP (Linear Probe)** | **0.733** | **N/A** |

**Analysis:**
- SHARP AUROC is competitive with ImageNet initialization (0.751 vs 0.743)
- SHARP significantly underperforms contrastive baselines (MGCA: 0.793)
- F1 score is notably low (43.1% vs 66.6% for MGCA), suggesting:
  - Conservative predictions (favoring specificity over sensitivity)
  - Class imbalance issues (77.5% negative class)
  - Possible threshold optimization needed

---

## Training Details

### Protocol (Following MGCA)
- **Optimizer:** SGD (momentum=0.9)
- **Learning Rate:** 1e-2
- **Batch Size:** 64
- **Max Epochs:** 30
- **Early Stopping:** 10 epochs
- **LR Schedule:** WarmupCosineScheduler (warmup=50 steps, total=3000 steps)
- **Gradient Clipping:** 1.0

### Architecture
- **Encoder:** ViT-B/16 with projection head
- **Classifier:** Linear layer with FC normalization, dropout=0.0
- **Mixed Precision:** Enabled (AMP)

### Dataset Split
- **RSNA:** 10% of training data (~2,600 images)
- **SIIM:** 1%, 10%, 100% splits

---

## Next Steps

1. **Extract SIIM metrics** from pushed results
2. **Complete RadDINO training** (in progress)
3. **Analyze low F1 scores** on RSNA:
   - Check prediction distributions
   - Analyze precision/recall curves
   - Consider threshold tuning
4. **Compare with other methods:**
   - Test different pretraining checkpoints
   - Try different classification heads
   - Experiment with class balancing

---

## Files & Locations

### Results
- RSNA Fine-tuning: `rsnaresults/` (local)
- RSNA Linear Probe: `rsna_lp_results/` ✅ Pushed
- SIIM Results: `siim_results_latest/` ✅ Pushed

### Configs
- `sharp_rsna_10pct.yml` - RSNA fine-tuning
- `sharp_rsna_lp.yml` - RSNA linear probe
- `sharp_siim_1pct.yml`, `sharp_siim_10pct.yml`, `sharp_siim_100pct.yml`

### Scripts
- `extract_all_results.py` - Extract metrics from all experiments
- `push_rsna_lp_results.bat` - Push linear probe results
- `push_siim_results.bat` - Push SIIM results
- `resume_all_auto.bat` - Auto-resume unfinished experiments
