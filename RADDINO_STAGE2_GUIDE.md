# RadDINO Stage 2 - Quick Guide

## Overview

**Stage 1 (DONE):** RadDINO contrastive pretraining → R@1 = 10.26%
**Stage 2 (NOW):** Fine-tune CXRMate for report generation → Get CheXbert F1

**Total time: ~2 hours**

---

## What You'll Get

After Stage 2, you can answer:
1. **Does RadDINO help downstream tasks?**
   - Compare CheXbert F1 with main SHARP (0.3032)
   - If RadDINO F1 ≥ 0.30: Good features despite low R@1
   - If RadDINO F1 < 0.28: RadDINO hurt performance

2. **Is low R@1 predictive of downstream performance?**
   - RadDINO R@1 = 10.26% (low)
   - Main SHARP R@1 = ? (unknown, but likely higher)
   - If RadDINO F1 is competitive → R@1 ≠ downstream performance

---

## How to Run (3 Steps)

### Step 1: Check Prerequisites

```batch
# Verify RadDINO Stage 1 checkpoint exists
dir D:\experiments\exp_raddino_hardneg\p3_best.pt

# Verify preprocessing is done
dir D:\datasets\mimic-cxr-jpg\mimic_cxr_sectioned\mimic_cxr_sectioned.csv
```

**If preprocessing CSV is missing:**
```batch
cd stage2_training
run_preprocessing.bat
```

### Step 2: Launch RadDINO Stage 2

```batch
cd C:\Users\aya.alaswad\remote\MyReasearch
run_raddino_stage2.bat
```

**This will:**
1. Fine-tune CXRMate with RadDINO encoder (10 epochs, ~2 hours)
2. Test on MIMIC-CXR test set (~15 min)
3. Save logs to `stage2_training\logs\raddino_train.log` and `raddino_test.log`

**You can close remote desktop after starting!**

### Step 3: Extract Results

After training completes (2+ hours), extract CheXbert F1:

```batch
cd C:\Users\aya.alaswad\remote\MyReasearch
python extract_raddino_results.py
```

**Output example:**
```
RadDINO Stage 2 Results
================================================================================

  CheXbert F1 (macro): 0.2987

Comparison with Main SHARP
================================================================================

  Main SHARP (Exp #3):  CheXbert F1 = 0.3032
  RadDINO (Stage 2):    CheXbert F1 = 0.2987

  Δ = -0.0045 (-1.5%) - RadDINO is WORSE
```

---

## Interpretation Guide

### Scenario 1: RadDINO F1 ≥ 0.30 (Good!)
**Conclusion:** RadDINO learned good visual features despite low R@1 (10.26%)

**For your paper:**
- ✓ Shows R@1 is not predictive of downstream performance
- ✓ RadDINO encoder can be used as alternative to ImageNet ViT
- ✓ Domain-specific pretraining (RadDINO) is competitive

### Scenario 2: RadDINO F1 = 0.28-0.30 (Close)
**Conclusion:** RadDINO is slightly worse but close

**For your paper:**
- ~ R@1 has weak correlation with downstream performance
- ~ RadDINO could work with better hard negative tuning (reduce from 0.6 to 0.3)
- ~ Not worth including unless you have space

### Scenario 3: RadDINO F1 < 0.28 (Bad)
**Conclusion:** RadDINO hurt performance, don't use

**For your paper:**
- ✗ Don't include RadDINO results
- ✗ Stick with main SHARP (ImageNet ViT)
- ✓ Your current paper is already strong

---

## Timeline

| Time | Action | Status |
|------|--------|--------|
| **Now** | Launch `run_raddino_stage2.bat` | ⏳ Pending |
| **+2 hours** | Training completes | ⏳ Pending |
| **+2h 15m** | Testing completes | ⏳ Pending |
| **+2h 20m** | Extract results with `extract_raddino_results.py` | ⏳ Pending |
| **+2h 25m** | Decide: Include in paper or not? | ⏳ Pending |

---

## What Gets Created

### Training Outputs
```
stage2_training/
├── logs/
│   ├── raddino_train.log    # Full training log
│   └── raddino_test.log     # Full testing log

C:/Users/aya.alaswad/remote/cxrmate/experiments/
└── [timestamp_experiment]/
    ├── checkpoints/
    │   └── best_model.ckpt  # Best checkpoint
    └── lightning_logs/
        └── version_0/
            └── test_results.json  # Test metrics
```

### Results Files
```
raddino_results/
└── stage2_results.json      # Extracted metrics
```

---

## Troubleshooting

### "RadDINO checkpoint not found"
RadDINO Stage 1 might not have completed. Check:
```batch
dir D:\experiments\exp_raddino_hardneg\
```

Should see: `p3_best.pt`, `p3_last.pt`, `p3_history.json`

### "Preprocessing CSV not found"
Run preprocessing first:
```batch
cd stage2_training
run_preprocessing.bat
```

### "CUDA out of memory"
Reduce batch size in `stage2_training/configs/exp_raddino.yaml`:
```yaml
mbatch_size: 4          # Was 8
accumulated_mbatch_size: 32  # Keep same
```

### Check GPU usage
```batch
nvidia-smi
```

---

## For Your Paper Decision Tree

```
                    Run RadDINO Stage 2
                            |
                            v
                Extract CheXbert F1
                            |
        +-------------------+-------------------+
        |                   |                   |
    F1 ≥ 0.30          F1 = 0.28-0.30      F1 < 0.28
        |                   |                   |
        v                   v                   v
  INCLUDE             MAYBE INCLUDE         DON'T INCLUDE
  (Good result!)      (Close call)          (Bad result)
        |                   |                   |
        v                   v                   v
  Shows R@1          Mention in           Stick with
  doesn't predict    discussion only       main SHARP
  downstream                               (already strong)
```

---

## Next Steps After Stage 2

1. **Extract results** with `extract_raddino_results.py`
2. **Compare with main SHARP** (F1 = 0.3032)
3. **Decide:** Include in paper or not?
4. **If including:** Add to ablation table or discussion
5. **If not including:** Focus on finishing paper revisions

---

## Important Notes

- **You don't need RadDINO for your workshop paper** - it's already strong without it
- **Only include if it strengthens your claims** (R@1 ≠ downstream, or domain encoder works)
- **Don't delay paper submission** for RadDINO - it's optional
- **For supervisor evaluation:** Focus on fixing SIIM first (more important)

---

## Summary

**What:** Fine-tune CXRMate with RadDINO encoder
**Why:** Test if low R@1 (10.26%) means bad downstream performance
**How long:** ~2 hours
**When:** Run now if you want, or skip and finish paper first
**Critical:** No - paper is strong without RadDINO
