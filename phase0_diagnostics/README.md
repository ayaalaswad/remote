# Phase 0 Diagnostics (Run First!)

**DO NOT proceed to Stage 2 until these diagnostics are complete!**

These scripts diagnose whether Exp #2's failure (R@1=0.81%) is a bug or a real finding.

## Quick Start (Run on Remote Desktop)

```bash
cd C:\Users\aya.alaswad\remote\phase0_diagnostics

# 1. Analyze Exp #2 loss curve
python analyze_exp2_loss.py

# 2. Sanity-check paired sampler
python sanity_check_paired_sampler.py

# 3. Compute empirical co-positive rates
python compute_copositive_rates.py
```

---

## Script 1: analyze_exp2_loss.py

**Purpose**: Diagnose if Exp #2 training was broken.

**What it does**:
- Plots loss curves for Exp #1 and Exp #2
- Plots R@1 curves for both
- Analyzes first 10k steps (to catch early divergence)
- Computes loss gradient (rate of change)

**Outputs**:
- `exp2_diagnostic_plots.png` - 4-panel diagnostic figure
- Console summary with diagnosis

**Interpretation**:
- If loss decreased smoothly BUT R@1 collapsed → **REAL finding** (diversity matters)
- If loss diverged or plateaued → **BUG** (broken training, fix before claiming)

---

## Script 2: sanity_check_paired_sampler.py

**Purpose**: Verify PairedBatchSampler works correctly.

**What it does**:
- Builds small test manifest (1000 files)
- Samples 10 random batches
- Checks each batch for:
  - 32 unique items?
  - 16 pairs (each concept key appears exactly 2x)?
  - 100% co-positive rate?
  - No duplicate indices?

**Outputs**:
- Console report for each of 10 batches
- PASS/FAIL verdict

**Interpretation**:
- PASS → Sampler works, Exp #2 failure is real
- FAIL → Sampler has bugs, fix before claiming

---

## Script 3: compute_copositive_rates.py

**Purpose**: Extract actual co-positive rates from training logs (R3 asked for this).

**What it does**:
- Parses all 4 training logs for MP-InfoNCE stats
- Extracts: avg co-positives, max co-positives, % with co-pos
- Computes summary statistics (mean, min, max, final)
- Creates comparison table

**Outputs**:
- `copositive_rates_summary.json` - Machine-readable results
- Console comparison table

**Expected Results**:
- Exp #1 (batch=32, random): ~40% co-pos rate
- Exp #2 (batch=32, paired): ~100% co-pos rate
- Exp #3 (batch=32, hard neg): ~50% co-pos rate
- Exp #4 (batch=512, hard neg): ~70-80% co-pos rate (TBD)

**Use for Rebuttal**:
R3 asked: "What's the actual co-positive frequency?"
Answer: "Exp #1 had 40%, Exp #4 had 75%, confirming our hypothesis that batch size matters."

---

## Decision Tree

```
Run analyze_exp2_loss.py
│
├─ Loss decreased smoothly?
│  ├─ YES → Run sanity_check_paired_sampler.py
│  │        │
│  │        ├─ Sampler PASS?
│  │        │  ├─ YES → Exp #2 is REAL finding
│  │        │  │        → Skip Exp #2 in Stage 2
│  │        │  │        → Use for rebuttal: "forcing co-pos hurts"
│  │        │  │
│  │        │  └─ NO → Sampler has bugs
│  │        │         → Fix sampler, re-run Exp #2
│  │        │
│  └─ NO → Training was broken
│           → Fix and re-run Exp #2
│
└─ All done? Run compute_copositive_rates.py
             → Use results for R3's rebuttal point
```

---

## Next Steps After Phase 0

### If Exp #2 is REAL:
1. Skip Exp #2 in Stage 2 (save 2-4 days GPU time!)
2. Run Stage 2 only on: Exp #1, Exp #3, Exp #4
3. Use Exp #2 result for rebuttal:
   - "We tested forced co-positives (100% rate)"
   - "Performance collapsed (0.81% vs 6.61%)"
   - "Diversity > guaranteed pairs"

### If Exp #2 is BROKEN:
1. Fix the bug (sampler or training)
2. Re-run Exp #2 Stage 1
3. Don't use Exp #2 results in rebuttal until fixed

---

## Expected Timeline

- Script 1: ~2 minutes
- Script 2: ~5 minutes
- Script 3: ~1 minute

**Total: ~10 minutes to diagnose**

This saves you 2-4 days of GPU time if Exp #2 should be skipped!

---

## Files Required

Scripts expect these logs to exist:
- `D:/experiments/exp1_baseline/training.log`
- `D:/experiments/exp2_paired_fixed/training.log`
- `D:/experiments/exp3_full_sharp/training.log`
- `D:/experiments/exp4_large_batch/training.log` (when available)

And these for sanity check:
- `D:/datasets/mimic-ext-cxr-qba/scene_graphs/scene_data/`
- `D:/datasets/mimic-cxr-jpg/`

---

**REMINDER**: Don't start Stage 2 CXRMate fine-tuning until Phase 0 is complete!
