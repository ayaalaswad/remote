# Bidirectional Loss Investigation - Final Findings

## Executive Summary

**CRITICAL FINDING:** There is NO evidence in the repository of any experiment achieving R@1 = 7.02% (unidirectional). The paper claims this value exists, but it cannot be verified from available code and results.

---

## What the Paper Claims (Section 4.2, lines 564-576)

```latex
Reviewers noted that ablations (A)--(D) used unidirectional loss (image→text)
while the symmetric baseline employed bidirectional loss (image↔text).
We re-ran ablation (B) with bidirectional multi-positive InfoNCE.
Stage 1 pretraining achieved validation R@1 = 6.61%
(vs. 7.02% unidirectional)
```

**Paper's assertions:**
1. ✓ Ablations (B), (C), (D) originally used **unidirectional** loss
2. ✓ Ablation (A) Symmetric InfoNCE used **bidirectional** (by definition)
3. ✓ Re-ran ablation (B) with **bidirectional**: R@1 = **6.61%**
4. ✓ Original ablation (B) **unidirectional**: R@1 = **7.02%**
5. ✓ Conclusion: Bidirectional got lower R@1 (6.61% < 7.02%)

---

## What the Repository Actually Shows

### 1. experiments.md (Line 22)

```markdown
- Bidirectional loss: Yes (all experiments)
```

**CONTRADICTION:** This explicitly states ALL experiments used bidirectional!

### 2. Actual Experiment Results (experiments.md lines 7-12)

| Exp | Name | R@1 (I→T) | Bidirectional |
|-----|------|-----------|---------------|
| #1 | Baseline | **6.61%** | ✓ YES |
| #2 | Paired Sampling | 0.81% | ✓ YES |
| #2b | 20k Random Control | 4.99% | ✓ YES |
| #3 | Hard Negatives (SHARP) | 6.21% | ✓ YES |
| #4 v2a | Large Batch (Fair) | 8.77% | ✓ YES |
| #4 v2b | Large Batch (Ceiling) | 8.9% | ✓ YES |

**KEY OBSERVATION:**
- ✓ R@1 = 6.61% exists (Exp #1)
- ❌ R@1 = 7.02% does NOT exist in any experiment

### 3. Code Timeline (Git Forensics)

| Date | Event | Evidence |
|------|-------|----------|
| Before May 17, 2026 | Code was unidirectional only | Commit d2a72ca |
| **May 17, 2026** | Bidirectional flag added | Commit 48ed0e7 |
| **May 19, 2026** | Paper.tex created | Commit 77c20b8 |

**CRITICAL:** Paper was created AFTER bidirectional was added to code!

### 4. Training Code (train_sharp_raddino_v2.py lines 163-212)

```python
def multi_positive_infonce(..., bidirectional=False):
    loss_i2t = ...  # Image → Text

    if bidirectional:
        loss_t2i = ...  # Text → Image
        return (loss_i2t + loss_t2i) / 2  # BIDIRECTIONAL
    else:
        return loss_i2t  # UNIDIRECTIONAL
```

**Finding:** Code implementation is correct. The `bidirectional` flag works as intended.

### 5. Launch Script Evidence

```batch
# run_exp4_v2a_FAIR.bat (line 58):
--bidirectional ^
```

At least one experiment explicitly uses `--bidirectional` flag.

---

## The Missing Evidence

### What I Could NOT Find:

1. ❌ No experiment directory with R@1 = 7.02%
2. ❌ No experiment config with `"bidirectional": false`
3. ❌ No training log showing "Unidirectional (i→t)" loss type
4. ❌ No checkpoint named `0.0702_*.pt`
5. ❌ No p3_history.json with max i2t_r1 = 0.0702

### Searched Locations:

- `D:/experiments/exp*/` - All experiments documented show bidirectional
- `./remote/` - No ablation configs found
- MyReasearch repo - No 7.02% value found (only 77.02% RSNA accuracy)
- lrrg repo Stage 2 configs - Point to `/workspace/experiments/vit_ablation_*/` on RunPod

---

## Ablation Study Mapping

From paper.tex (lines 537-541):

| Ablation | Setup | Paper Claims |
|----------|-------|--------------|
| **(A)** Sym. InfoNCE | Symmetric InfoNCE | Bidirectional (by definition) |
| **(B)** MP-InfoNCE | Multi-positive InfoNCE | Originally unidirectional (7.02%), re-ran bidirectional (6.61%) |
| **(C)** +curriculum | Fast ramp (s_ramp=5k) | Unidirectional |
| **(D)** +curriculum | Slow ramp (s_ramp=30k), no polarity HN | Unidirectional |
| **SHARP** | +polarity HN (full) | Unidirectional |

### Problem: Cannot Map to Actual Experiments

**Ablations in lrrg repo** (Stage 2 configs):
- `/workspace/experiments/vit_ablation_A/` - On RunPod server
- `/workspace/experiments/vit_ablation_B/` - On RunPod server
- `/workspace/experiments/vit_ablation_C/` - On RunPod server
- `/workspace/experiments/vit_phase3/` - On RunPod server

**Status:** These directories are on a RunPod server that may no longer be accessible.

---

## Three Possible Scenarios

### Scenario 1: Paper is Incorrect (MOST LIKELY)

**Theory:** All experiments (including ablations) were run with bidirectional, but the paper incorrectly states they used unidirectional.

**Evidence FOR:**
- ✓ experiments.md explicitly says "all experiments" used bidirectional
- ✓ Paper was written AFTER bidirectional flag was added
- ✓ Exp #1 matches the "bidirectional R@1 = 6.61%" claim
- ✓ No evidence of 7.02% experiment anywhere

**Evidence AGAINST:**
- Paper is very specific about re-running ablation (B)
- 7.02% value appears multiple times in paper

**Likelihood:** **85%**

### Scenario 2: Pre-Bidirectional Experiments Exist But Not Documented

**Theory:** Original experiments ran before May 17 with unidirectional, achieving 7.02%, but were never committed to git. Then experiments were re-run after May 17 with bidirectional.

**Evidence FOR:**
- Paper is specific about 7.02% vs 6.61% comparison
- Timeline makes sense (experiments before code change)

**Evidence AGAINST:**
- No experiment artifacts found anywhere
- experiments.md doesn't mention old experiments
- User said RunPod experiments were copied to GitHub, but no 7.02% found

**Likelihood:** **10%**

### Scenario 3: 7.02% is Theoretical/Estimated

**Theory:** The 7.02% value was never actually measured - it's either:
- A typo or calculation error
- An early preliminary result not properly documented
- A theoretical estimate

**Evidence FOR:**
- No experimental evidence exists
- Discrepancy between paper and experiments.md

**Evidence AGAINST:**
- Paper presents it as a concrete experimental result
- Too specific to be estimated

**Likelihood:** **5%**

---

## What Needs to Be Verified

### On RunPod Server (if still accessible)

Check these exact locations:

```bash
# Ablation A (Sym. InfoNCE)
cat /workspace/experiments/vit_ablation_A/experiment_config.json | grep bidirectional
cat /workspace/experiments/vit_ablation_A/training.log | grep "Loss type"

# Ablation B (MP-InfoNCE) - CRITICAL
cat /workspace/experiments/vit_ablation_B/experiment_config.json | grep bidirectional
cat /workspace/experiments/vit_ablation_B/training.log | grep "Loss type"
ls -la /workspace/experiments/vit_ablation_B/*.pt  # Check for R@1 in filename

# Ablation C (+curriculum)
cat /workspace/experiments/vit_ablation_C/experiment_config.json | grep bidirectional

# Phase3 / SHARP
cat /workspace/experiments/vit_phase3/experiment_config.json | grep bidirectional
```

**Expected if paper is correct:**
- Ablation B should have TWO directories:
  - One with `"bidirectional": false` and checkpoint showing ~7.02%
  - One with `"bidirectional": true` and checkpoint showing ~6.61%

**Expected if experiments.md is correct:**
- Only ONE Ablation B directory with `"bidirectional": true`
- No experiment with 7.02% R@1

---

## Recommendations

### Option 1: Correct the Paper (RECOMMENDED)

If RunPod verification shows all experiments used bidirectional:

**Change Section 2.2 (line 220):**
```latex
% BEFORE:
The loss is unidirectional (image anchors only)

% AFTER:
The loss is bidirectional, computing both image→text and text→image
directions and averaging them (similar to CLIP).
```

**Remove Section 4.2 bidirectional ablation paragraph (lines 564-576):**
- This entire paragraph becomes irrelevant if all experiments used bidirectional

### Option 2: Find/Re-run Unidirectional Experiments

If you want to keep the paper claims:

1. Check RunPod for original unidirectional experiments
2. If not found, re-run all experiments WITHOUT `--bidirectional` flag
3. Update all R@1 values in the paper with new results

**Effort:** High (multiple days of compute)
**Risk:** High (results may change significantly)

### Option 3: Clarify in Rebuttal

If RunPod is inaccessible and original results lost:

**In reviewer response:**
```
We acknowledge a documentation inconsistency regarding the bidirectional
loss configuration. Our final experiments (Exp #1-4) all used bidirectional
loss by default. The 7.02% unidirectional baseline was from preliminary
experiments no longer accessible. We have updated the paper to accurately
reflect that all reported results use bidirectional loss.
```

---

## Definitive Answer

**Question:** Were ablations (B), (C), (D) run with unidirectional or bidirectional?

**Answer:** **CANNOT DEFINITIVELY DETERMINE** from available repository evidence alone.

**Most Likely:** All experiments (including ablations) used **bidirectional**, and the paper's claim about unidirectional 7.02% is incorrect or based on preliminary results no longer documented.

**To Resolve:** Check the RunPod server at `/workspace/experiments/vit_ablation_B/` for the actual experiment_config.json file.

---

## Files Checked

### MyReasearch Repository
- ✓ experiments.md (line 22: "all experiments" bidirectional)
- ✓ train_sharp_raddino_v2.py (code implementation correct)
- ✓ run_exp4_v2a_FAIR.bat (has --bidirectional flag)
- ✓ check_r1_scores.py (expects 6.61%, 6.21%, 8.77% - no 7.02%)
- ✓ Git history (bidirectional added May 17, paper created May 19)
- ❌ No ablation experiment directories found
- ❌ No configs with bidirectional=false
- ❌ No results showing 7.02% R@1

### lrrg Repository
- ✓ Stage 2 configs point to `/workspace/experiments/vit_ablation_*/`
- ✓ bootstrap_ablation_analysis.py confirms ablations exist
- ❌ Actual experiment directories NOT in repo (on RunPod server)

---

**Last Updated:** 2026-06-26
**Status:** Investigation complete - Awaiting RunPod server verification
**Confidence:** 85% that all experiments used bidirectional and paper claim is incorrect
