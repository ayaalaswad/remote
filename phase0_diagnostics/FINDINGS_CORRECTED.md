# Phase 0 Diagnostic Findings (Corrected)

**Date**: 2026-05-22
**Status**: ⚠️ Phase 0 Complete - **EXP #2B CONTROL NEEDED**

---

## Executive Summary

**Critical Finding**: Exp #2 (paired sampling) collapsed to R@1=0.81% (vs 6.61% baseline) with 100% co-positive rate achieved.

**Status**: ⚠️ **CONFOUNDED** - Cannot definitively attribute cause without control experiment

**Confound**: Exp #2 changed TWO variables:
1. Co-positive rate: 37.2% → 100% (forced pairing)
2. Dataset size: 60k+ files → 20k files (3× reduction)

**Recommendation**: ✅ **RUN EXP #2B** (20k random control, ~12h GPU) to isolate the cause

**Current Decision**: ✅ SKIP Exp #2 in Stage 2 (known-bad checkpoint, fine-tuning won't rescue it)

---

## What Phase 0 PROVED

### ✓ Ruled Out: Training Was Broken
- Loss decreased smoothly (3.42 → 1.95)
- No divergence or plateau
- Training progressed normally

**Conclusion**: Not a training bug

### ✓ Ruled Out: Sampler Had a Bug
- 100% co-positive rate achieved (420 measurements, all = 100%)
- Perfect consistency (avg = 1.00, no variance)
- Manifest built successfully (590,976 pairs)

**Conclusion**: Sampler worked correctly

---

## What Phase 0 DID NOT PROVE

### ✗ NOT Isolated: Root Cause of Collapse

**Variables that changed between Exp #1 and Exp #2**:
1. **Co-positive rate**: 37.2% → 100%
2. **Dataset size**: ~60,000+ files → 20,000 files (3× smaller)

**Cannot determine which caused the collapse** without isolating variables.

**Possible explanations**:
- (A) Forced pairing eliminated diversity → trivial task
- (B) 3× smaller dataset → insufficient variation
- (C) Both factors combined

**Resolution**: Run Exp #2b (20k random control) to separate (A) from (B)

---

## Experiment #2: Paired Sampling Analysis

### Configuration
- **Sampling**: Paired (forced co-positives)
- **Batch Size**: 32
- **Bidirectional**: Yes
- **Hard Negatives**: 0%
- **Training Files**: 20,000 (sampled for manifest) ⚠️ **3× smaller than baseline**
- **Manifest Size**: 590,976 pairs

### Training Metrics

| Metric | Initial | Final | Change |
|--------|---------|-------|--------|
| Loss | 3.4210 | 1.9495 | -1.4715 ✓ |
| R@1 (validation) | 0.27% | 0.40% | +0.13% |
| R@1 (best) | 0.81% | - | - |

**Loss Behavior**: ✓ Decreased smoothly (normal training progression)
**R@1 Behavior**: ✗ Never exceeded 2% (severe failure)

### Co-Positive Statistics

| Metric | Value | Status |
|--------|-------|--------|
| Avg co-positives per sample | 1.00 | ✓ Perfect |
| Max co-positives in batch | 1.00 | ✓ Perfect |
| % batches with co-positives | 100.0% | ✓ Perfect |
| Consistency (range) | [1.00, 1.00] | ✓ No variance |

**Paired Sampler Verdict**: ✓ Working as designed (100% co-positive rate achieved)

### Performance Comparison

| Experiment | Dataset Size | Co-pos Rate | R@1 | Performance |
|------------|--------------|-------------|-----|-------------|
| Exp #1 (baseline) | 60k+ files | 37.2% | 6.61% | ✓ Good |
| **Exp #2 (paired)** | **20k files** | **100%** | **0.81%** | ✗ **Collapsed** |
| Exp #3 (hard neg) | 60k+ files | 36.9% | 6.21% | ✓ OK |

**Performance Drop**: -87.7% (0.81 vs 6.61)

---

## Hypotheses (Corrected)

### Hypothesis 1: Task Too Trivial (Forced Pairing) ⚠️ PLAUSIBLE
- Model sees same 16 concept keys repeated in pairs every batch
- Task becomes: "find the other instance of this exact same thing"
- No challenge → no learning of generalizable features
- **Evidence**: 100% co-positive rate achieved, but R@1 collapsed
- **Confound**: Dataset also 3× smaller

### Hypothesis 2: Limited Diversity (Dataset Size) ⚠️ PLAUSIBLE
- Only 20,000 files used (vs 60,000+ in baseline)
- Only 590,976 pairs (vs millions in baseline with 60k+ files)
- Model sees fewer unique examples
- **Evidence**: 3× smaller training set
- **Confound**: Also has forced pairing

### ~~Hypothesis 3: Wrong Learning Signal~~ ❌ REMOVED

**Previous claim**: "No hard negatives → wrong learning signal"

**Problem**: BOTH Exp #1 and Exp #2 had 0% hard negatives

**Corrected understanding**:
- Hard negatives: Exp #1 = 0%, Exp #2 = 0% (SAME)
- This is NOT a difference between them
- Cannot explain why Exp #2 collapsed while Exp #1 succeeded
- Relevant for Exp #3 vs Exp #1, not Exp #2 vs Exp #1

---

## Exp #2b Control Experiment (NEEDED)

### Purpose
Isolate the dataset size confound

### Design
- Same as Exp #1 (baseline)
- Random sampling (NO paired sampling)
- **Limit to 20k files** (same as Exp #2)

### Expected Outcomes

**Scenario A: R@1 ≈ 6.6%** (same as baseline)
→ Dataset size NOT the problem
→ Forced pairing IS the cause
→ **Can use strong language in rebuttal**

**Scenario B: R@1 ≈ 0.8%** (tanks like Exp #2)
→ Dataset size IS the problem
→ Cannot blame forced pairing alone
→ **Must use cautious language in rebuttal**

**Scenario C: R@1 ≈ 4-5%** (between baseline and Exp #2)
→ Both contribute
→ Can quantify each factor's contribution
→ **Use nuanced language in rebuttal**

### Timeline
- **Cost**: ~12 hours GPU
- **Value**: Turns soft claim into hard claim
- **Priority**: HIGH (run before Stage 2)

---

## Comparison Across All Experiments

### Co-Positive Rate Analysis (REBUTTAL-READY)

| Experiment | Batch | Files | Avg Co-pos | % w/ Co-pos | R@1 |
|------------|-------|-------|------------|-------------|-----|
| Exp #1 | 32 | 60k+ | 0.75 | 37.2% | 6.61% ✓ |
| Exp #2 | 32 | **20k** | 1.00 | **100%** | 0.81% ✗ |
| Exp #3 | 32 | 60k+ | 0.75 | 36.9% | 6.21% ✓ |
| Exp #4 | 512 | 60k+ | **11.90** | 62.2% | TBD |

**Key Finding for R3**:
- Exp #4 has **15.9x more co-positives** than batch=32 experiments
- Natural sampling at batch=512 gives 62.2% co-positive rate (vs 37% at batch=32)
- This is **strong evidence** that batch size solves the co-positive scarcity problem

---

## Implications for Rebuttal (CORRECTED)

### For R3: "Insufficient co-positives cause degeneracy"

**Conservative Response (without Exp #2b)**:

> "We systematically measured co-positive rates across all experiments:
>
> 1. **Baseline (batch=32, random)**: 37.2% batches with co-positives → R@1 = 6.61%
> 2. **Large batch (batch=512, random)**: 62.2% batches with co-positives, 15.9× more per sample → R@1 = TBD
>
> The large batch configuration naturally increases co-positive frequency while maintaining sample diversity. Exp #4 results will show whether this resolves the degeneracy concern without artificial constraints."

**Strong Response (IF Exp #2b shows R@1 ≈ 6.6%)**:

> "We tested whether forcing 100% co-positive rate improves performance. A paired-sampling experiment achieved 100% co-positive rate but collapsed to R@1=0.81% (vs 6.61% baseline). A 20k random control confirmed this was not due to dataset size (R@1=6.XX% with 20k random files), demonstrating that **diversity in batch composition is more critical than guaranteed co-positives**. Our large-batch approach (Exp #4) naturally increases co-positives to 11.90 per sample while preserving diversity."

---

## Decision Justification

### Why Skip Exp #2 in Stage 2?

1. **Known to Fail**: R@1 = 0.81%, worst of all experiments
2. **Stage 2 Won't Fix It**: Fine-tuning can't rescue collapsed Stage 1 representations
3. **GPU Time Savings**: 2-4 days saved by not fine-tuning this checkpoint
4. **Sufficient for Decision**: Even without isolating cause, it's a bad checkpoint

**This decision stands regardless of Exp #2b outcome**

### What We'll Do

**Stage 2 Training Plan** (3 checkpoints):
1. ✅ Exp #1 (baseline) - Reference point
2. ✅ Exp #3 (Full SHARP) - Main result for R1/MR
3. ✅ Exp #4 (Large batch) - Main result for R3
4. ❌ Exp #2 (Paired) - **SKIP** (known-bad)

**Exp #2b** (if run): Informs rebuttal language strength, NOT Stage 2 decision

---

## Next Steps (Priority Order)

1. ⚠️ **HIGH PRIORITY**: Run Exp #2b control (~12h GPU)
   - Isolates dataset size confound
   - Enables strong vs weak rebuttal language
   - Should be done BEFORE writing rebuttal

2. ⏳ Wait for Exp #4 Stage 1 to finish

3. 🔄 Install CheXbert checkpoint

4. ➡️ Phase 1: t-SNE/UMAP analysis

5. ➡️ Phase 2: Stage 2 training (Exp #1, #3, #4 only)

---

## Files Generated

1. `exp2_diagnostic_plots.png` - 4-panel loss/R@1 analysis
2. `copositive_rates_summary.json` - Co-positive statistics (REBUTTAL-READY)
3. `FINDINGS.md` - Original analysis (superseded by this document)
4. `FINDINGS_CORRECTED.md` - This document (with fixed logic)
5. `EXP2B_CONTROL.md` - Control experiment design

**Location**: `C:\Users\aya.alaswad\remote\phase0_diagnostics\`

---

## Appendix: What We Learned

### ✓ Conclusive Findings
1. Exp #2 training ran normally (not a bug)
2. Paired sampler worked correctly (100% co-pos achieved)
3. Exp #4 has 15.9× more co-positives than batch=32 (addresses R3)

### ⚠️ Inconclusive Findings
1. Why Exp #2 collapsed: forced pairing OR dataset size OR both?

### ❌ Incorrect Claims (Fixed)
1. ~~"No hard negatives" explains Exp #2 collapse~~ → Wrong, Exp #1 also had 0%
2. ~~"Forcing 100% co-positives collapsed performance"~~ → Confounded by dataset size

---

**Status**: Phase 0 complete with corrected analysis. Exp #2b control recommended before rebuttal writing.
