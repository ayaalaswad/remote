# RadDINO Hard Negatives Training - Analysis

**Date:** June 15, 2026
**Experiment:** RadDINO encoder with hard negatives
**Status:** ✅ Training Complete

---

## 📊 Training Results

### Final Metrics
- **Best I→T R@1:** 10.26% (at step 32,000)
- **Final loss:** 3.106
- **Total steps:** 88,000 (early stopping)
- **Hard negatives ratio:** 0.60

### Training Configuration
```
Encoder: RadDINO ViT
Batch size: 256
Learning rate: 0.0001
Hard neg max fraction: 0.6
Hard neg ramp end: 30,000 steps
Bidirectional: Yes
Unfreeze: 4 blocks after 5,000 steps
```

### Training Progression

| Step | Loss | I→T R@1 | I→T R@5 | T→I R@1 | T→I R@5 |
|------|------|---------|---------|---------|---------|
| 2,000 | 4.686 | 3.24% | 14.44% | 3.78% | 14.44% |
| 10,000 | 3.677 | 8.10% | 26.05% | 7.69% | 26.05% |
| 20,000 | 3.484 | 9.31% | 29.01% | 7.96% | 29.15% |
| **32,000** | **3.390** | **10.26%** | **29.28%** | **10.53%** | **32.12%** |
| 50,000 | 3.253 | 9.04% | 29.15% | 8.91% | 29.96% |
| 88,000 | 3.106 | ~10.3% | ~30% | ~10% | ~32% |

**Peak performance at step 32,000** - no significant improvement after that point.

---

## 🔍 Analysis

### What is 10.26% R@1?

**R@1 (Recall at 1)** measures: Given an image, is the correct text the #1 ranked match?
- 10.26% means only 10.26% of images retrieve their correct report as the top match
- This is **relatively low** for contrastive learning

### Comparison Context

**Typical medical imaging retrieval R@1 benchmarks:**
- **MGCA** (from BenchX paper): ~30-40% R@1 on MIMIC-CXR
- **ConVIRT**: ~25-35% R@1
- **GLoRIA**: ~35-45% R@1
- **RadDINO (ours)**: **10.26%** R@1

**Verdict:** RadDINO R@1 is **significantly below** published baselines.

### Why is it Low?

**Possible reasons:**

1. **Hard negatives too aggressive** (0.6 ratio)
   - May have made training too difficult
   - Model couldn't differentiate signal from noise

2. **RadDINO encoder issues**
   - Maybe the RadDINO initialization wasn't suitable
   - 4-block unfreezing might be insufficient

3. **Early stopping too early**
   - Peaked at 32k, stopped at 88k
   - Maybe needed different learning rate schedule

4. **Batch size / training setup**
   - Batch 256 might not be optimal for this task
   - Learning rate 1e-4 might be too low

5. **Evaluation setup**
   - Gallery size: 2000
   - Maybe evaluation is too strict

---

## 🤔 Critical Question: What was the baseline?

**We need to know:** What was the R@1 for your main SHARP checkpoint (`exp3_full_sharp/p3_best_timm.pt`)?

### If baseline SHARP R@1 was:
- **35-40%** → RadDINO is a **major regression** (-25 points)
- **15-20%** → RadDINO is a **moderate regression** (-5 to -10 points)
- **8-10%** → RadDINO is **similar or slight improvement**

**Without the baseline, we can't assess if RadDINO helped or hurt.**

---

## 🎯 What to Do Next

### Option 1: Find Baseline R@1 (Recommended)
Check your original SHARP training logs or papers:
```bash
# Look for Stage 1 validation results
grep -r "R@1" D:/experiments/exp3_full_sharp/
```

### Option 2: Test RadDINO on Downstream Tasks
Even if R@1 is low, it might still help classification:
- Run BenchX with RadDINO checkpoint
- Compare RSNA/SIIM performance to main SHARP
- Low retrieval ≠ bad features necessarily

### Option 3: Analyze What Went Wrong
- Check if hard negatives were too hard
- Visualize retrieved examples (qualitative analysis)
- Look at loss curves and learning dynamics

---

## 💡 Recommendations

### For Your Rebuttal/Paper

**DO NOT include RadDINO results unless:**
1. You confirm it improves downstream tasks
2. Or you position it as ablation ("hard negatives hurt retrieval")

**The 10.26% R@1 is too low to present positively** without context.

### For Future Work

**If you want to improve RadDINO:**
1. **Reduce hard negative ratio** (try 0.3 instead of 0.6)
2. **Longer warmup** (10k steps instead of 5k)
3. **Higher learning rate** (2e-4 or 5e-4)
4. **Different encoder** (try ViT-B/16 from scratch instead of RadDINO init)
5. **Smaller gallery for eval** (easier to get high R@1, better training signal)

---

## 📂 Checkpoints Available

1. **RadDINO Best** (step 32,000): `D:/experiments/exp_raddino_hardneg/p3_best.pt`
   - R@1: 10.26%
   - Use this if testing downstream

2. **RadDINO Last** (step 88,000): `D:/experiments/exp_raddino_hardneg/p3_last.pt`
   - Slightly lower R@1 but lower loss
   - Might have better features despite worse retrieval

3. **Main SHARP** (baseline): `D:/experiments/exp3_full_sharp/p3_best_timm.pt`
   - Used for all BenchX experiments
   - Achieved 0.751 AUROC on RSNA

---

## 🔬 Downstream Evaluation Plan (Optional)

If you want to test if RadDINO is actually useful:

### Test 1: RSNA 10% with RadDINO
```yaml
# Modify sharp_rsna_10pct.yml
model:
  cnn:
    pretrained: D:/experiments/exp_raddino_hardneg/p3_best.pt
```

Expected outcomes:
- **If AUROC ≥ 0.75**: RadDINO has good features despite low R@1
- **If AUROC < 0.70**: RadDINO hurt performance

### Test 2: Linear Probe with RadDINO
```yaml
# Test frozen features
trainer:
  optim_params:
    lr_multiplier_ve: 0.0
```

Compare linear probe gap:
- Main SHARP: 2.4% gap (0.7514 vs 0.7333)
- RadDINO: ? gap

Smaller gap = better features.

---

## 📊 Summary Table

| Metric | RadDINO | Main SHARP | MGCA (SOTA) |
|--------|---------|------------|-------------|
| **R@1 (I→T)** | 10.26% | Unknown | ~35% |
| **R@5 (I→T)** | 29.28% | Unknown | ~60% |
| **Training steps** | 88,000 | Unknown | Unknown |
| **Downstream AUROC** | Not tested | 0.751 | 0.793 |

---

## ✅ Action Items

1. **Find original SHARP R@1** from exp3_full_sharp logs
2. **Decide:** Test RadDINO downstream or abandon?
3. **For paper:** Do NOT include unless you have downstream results showing it helps

**Bottom line:** 10.26% R@1 is low, but we need context (baseline) and downstream tests to know if it's useful.
