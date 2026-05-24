# Exp #4 Revised Plan: Fix the Under-Training Issue

**Date**: 2026-05-24
**Status**: Critical fix needed for R3's question

---

## What Went Wrong with "Exp #4 FAIR"

### The Flawed Logic (My Mistake)

I thought: "Fair comparison = same number of samples seen"
```
Baseline: 32 × 100k steps = 3.2M samples
Exp #4:   512 × 6.25k steps = 3.2M samples ✓
```

**This was wrong.** Fair on samples ≠ fair on optimization trajectory.

---

### The Two Confounds

**Exp #4 FAIR had TWO problems**:

1. **Under-trained**: 6.25k steps vs 100k steps (16× fewer updates)
   - Large batches need many steps to converge (Goyal et al. 2017)
   - Lower-variance gradients, but still need trajectory through loss landscape

2. **Unscaled LR**: Used 1e-4 (baseline LR) instead of 1.6e-3
   - Standard practice: LR ∝ batch size (linear scaling rule)
   - Should be: 1e-4 × (512/32) = 1.6e-3

**Result**: 5.26% R@1 shows it's learning, just handicapped!

---

## Why This Matters for Rebuttal

**R3 specifically asked**: "Does large batch help MP-InfoNCE?"

**Current result (5.26%)**: Inconclusive - we handicapped it!

**Options**:

### Option A: Run Properly (RECOMMENDED)
- Exp #4 v2: 100k steps, LR=1.6e-3
- Runtime: ~18-20 hours
- Answers R3's question definitively
- If it beats 6.61%, strong positive story
- If it doesn't, honest negative result > silence

### Option B: Frame Honestly (Weaker)
- Report current 5.26%
- Acknowledge: "Under-trained due to insufficient steps"
- Cite Goyal et al. 2017
- Say: "Definitive test remains open"
- **Problem**: R3 will ask "why didn't you just run it properly?"

---

## Corrected Configuration: Exp #4 v2

```
Batch size: 512
Total steps: 100,000 (NOT 6,250)
Learning rate: 1.6e-3 (NOT 1e-4)
Warmup: 5,000 steps
Hard negatives: 0.6 max
Bidirectional: YES

Runtime: ~18-20 hours
Samples: 51.2M (16× more than baseline, but proper convergence)
```

---

## Evidence That This Will Work

**Exp #4 FAIR reached 5.26% in only 6.25k steps**:
- Step 1250: 2.16%
- Step 2500: 3.78%
- Step 5000: 4.86%
- Step 6250: 5.26%

**Clear upward trend!** If we let it train to 100k steps with proper LR, it should exceed baseline.

---

## Parallel Execution Plan

**Don't wait sequentially - parallelize:**

1. **Start Exp #4 v2** (~18-20h) - Run in background
2. **Check Exp #3 results** (5 min) - We still don't know its R@1!
3. **Run Phase 1** (t-SNE/UMAP, ~1h) - Parallel, no GPU conflict
4. **Set up Stage 2 pipeline** - Script once, queue all checkpoints
5. **When Exp #4 v2 finishes** - Add to Stage 2 queue

---

## Updated Experiment Table (After Exp #4 v2)

| Experiment | Batch | Steps | LR | Samples | R@1 | Status |
|------------|-------|-------|-------|---------|-----|--------|
| **Exp #1** | 32 | 100k | 1e-4 | 3.2M | **6.61%** | ✓ Done |
| **Exp #2b** | 32 | 38k | 1e-4 | 1.2M | **4.99%** | ✓ Done |
| **Exp #2** | 32 | ~100k | 1e-4 | 3.2M | **0.81%** | ✓ Done |
| **Exp #3** | 32 | ??? | 1e-4 | ??? | **???** | ❓ Check |
| **Exp #4 FAIR** | 512 | 6.25k | 1e-4 ❌ | 3.2M | **5.26%** | ⚠️ Flawed |
| **Exp #4 v2** | 512 | 100k | 1.6e-3 ✓ | 51.2M | **???** | ⏳ Run now |

---

## Recommended Actions (In Order)

### 1. Check Exp #3 (5 minutes)
```cmd
powershell Get-Content D:\experiments\exp3_full_sharp\training.log -Tail 100
```

### 2. Start Exp #4 v2 (~18-20h)
```cmd
cd C:\Users\aya.alaswad\remote
git pull
run_exp4_v2_PROPER.bat
```

### 3. Download CheXbert (10 min, parallel)
```cmd
pip install gdown
gdown 1DS6NYirOXQf8qYieSVMvqNwuOlgAbM_E -O checkpoints\stanford\chexbert\chexbert.pth
```

### 4. Start Phase 1 (1h, parallel)
```cmd
cd phase1_analysis
run_phase1.bat
```

---

## Bottom Line

**DO NOT skip Exp #4.** R3 asked for it specifically. Current result (5.26%) is evidence of under-training, not evidence that large batch doesn't work. Running properly (~20h) is the right call.

**Revised timeline**:
- Exp #4 v2: 18-20 hours (start now)
- Phase 1: 1 hour (parallel)
- Phase 2: 3-4 days (after Exp #4 v2 + CheXbert)

**Net cost**: 20 more hours GPU time to answer R3's main question definitively.
