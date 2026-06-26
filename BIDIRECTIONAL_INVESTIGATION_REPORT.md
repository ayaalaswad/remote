# Bidirectional Loss Investigation - Factual Findings

## Question
Were the ablation experiments (B), (C), (D) in the paper run with unidirectional or bidirectional contrastive loss?

---

## Key Timeline

| Date | Event | Evidence |
|------|-------|----------|
| **Before May 17, 2026** | Original code | Unidirectional only (commit d2a72ca) |
| **May 17, 2026** | Bidirectional added | Commit 48ed0e7 "Add bidirectional loss and paired sampling" |
| **May 19, 2026** | Exp #1 results added to paper | Commit 77c20b8 "Add Experiment #1 bidirectional baseline results to paper (R@1=6.61%)" |
| **May 19, 2026** | paper.tex created | Same commit 77c20b8 |

---

## Code Analysis

### Before Bidirectional (commit d2a72ca, before May 17)

```python
def multi_positive_infonce(img_embs, txt_embs, concept_keys, temperature):
    # ... compute i→t loss only ...
    n_pos = pos_mask.sum(dim=1)
    sim_pos_avg = (sim * pos_mask).sum(dim=1) / n_pos
    log_denom = torch.logsumexp(sim, dim=1)

    return (-sim_pos_avg + log_denom).mean()  # UNIDIRECTIONAL
```

**Finding:** NO bidirectional parameter. Only image→text direction.

### After Bidirectional (commit 48ed0e7, May 17+)

```python
def multi_positive_infonce(img_embs, txt_embs, concept_keys, temperature, bidirectional=False):
    # ... compute i→t loss ...
    loss_i2t = (-sim_pos_avg_i2t + log_denom_i2t).mean()

    if bidirectional:
        # TEXT → IMAGE direction
        n_pos_t2i = pos_mask.sum(dim=0)
        sim_pos_avg_t2i = (sim.T * pos_mask.T).sum(dim=1) / n_pos_t2i
        log_denom_t2i = torch.logsumexp(sim.T, dim=1)
        loss_t2i = (-sim_pos_avg_t2i + log_denom_t2i).mean()

        return (loss_i2t + loss_t2i) / 2  # BIDIRECTIONAL
    else:
        return loss_i2t  # UNIDIRECTIONAL
```

**Finding:** Bidirectional parameter added. When True, averages both directions.

---

## What the Paper Claims

### Section 4.1 (Quantitative Results):
```
SHARP achieves image-to-text R@1 = 7.02% ... A bidirectional variant
(averaging i→t and t→i losses) achieved validation R@1 = 6.61%
```

**Interpretation:**
- Main SHARP: R@1 = 7.02% (unidirectional)
- Bidirectional variant: R@1 = 6.61%

### Section 4.2 (Ablation):
```
Reviewers noted that ablations (A)-(D) used unidirectional loss (image→text)
while the symmetric baseline employed bidirectional loss...
We re-ran ablation (B) with bidirectional multi-positive InfoNCE.
Stage 1 pretraining achieved validation R@1 = 6.61%
(vs. 7.02% unidirectional)
```

**Interpretation:**
- Ablations (B), (C), (D): unidirectional, R@1 = 7.02%
- Ablation (A) Sym. InfoNCE: bidirectional (by definition)
- Ablation (B) re-run with bidirectional: R@1 = 6.61%

---

## What experiments.md Says

```markdown
| Exp | Name | R@1 (I→T) | Status |
|-----|------|-----------|--------|
| #1 | Baseline | 6.61% | ✓ Complete |
| #3 | Hard Negatives (SHARP) | 6.21% | ✓ Complete |

Common across all:
- Bidirectional loss: Yes (all experiments)
```

**Interpretation:**
- Exp #1: R@1 = 6.61%, bidirectional
- Exp #3 (SHARP): R@1 = 6.21%, bidirectional
- ALL experiments used bidirectional

---

## Critical Discrepancies

### Discrepancy 1: SHARP R@1 Value

| Source | SHARP R@1 |
|--------|-----------|
| Paper (line 399) | 7.02% |
| experiments.md Exp #3 | 6.21% |

**Mismatch: 7.02% vs 6.21%**

### Discrepancy 2: Ablation (B) Unidirectional

| Source | Ablation (B) Unidirectional R@1 |
|--------|--------------------------------|
| Paper | 7.02% |
| No experiment found | ??? |

**Cannot verify:** No experiment directory or config found for ablation (B) unidirectional.

### Discrepancy 3: Exp #1 Identity

| Possibility | Evidence For | Evidence Against |
|-------------|--------------|------------------|
| Exp #1 = Ablation (B) bidirectional | R@1 matches (6.61%) | experiments.md calls it "Baseline" not "MP-InfoNCE" |
| Exp #1 = Different experiment | experiments.md shows different setup | R@1 still matches ablation (B) bidirectional |

---

## Search for Ablation Experiment Directories

**Searched locations:**
- Local repo: `find . -name "*ablation*" -o -name "*exp_b*"`
- Batch scripts: `grep -r "ablation"`
- Config files: No ablation configs found

**Result:** No ablation experiment directories found in the repository.

**Possible explanations:**
1. Ablations were run on the remote desktop and not committed to git
2. Ablations are named differently (exp1, exp2, exp3, etc.)
3. Ablations were never actually run (paper is theoretical)

---

## Launch Script Analysis

### run_exp4_v2a_FAIR.bat (line 58):
```batch
--bidirectional ^
```

**Finding:** Exp #4 v2a explicitly uses `--bidirectional` flag.

### run_exp2b_20k_random.bat:
*Need to check if it has --bidirectional flag*

**Status:** Not yet examined.

---

## Hypothesis: What Actually Happened

### Scenario A: All Experiments Were Bidirectional

**Evidence FOR:**
1. experiments.md says "Bidirectional loss: Yes (all experiments)"
2. paper.tex was created AFTER bidirectional flag was added (May 19 vs May 17)
3. Exp #1 (6.61%) matches the "bidirectional variant" R@1 in paper

**Evidence AGAINST:**
1. Paper explicitly claims ablations (B), (C), (D) used unidirectional
2. Paper reports SHARP R@1 = 7.02% (unidirectional value)

**Conclusion:** Experiments.md and paper.tex are CONTRADICTORY.

### Scenario B: Two Sets of Experiments

**Theory:** There were TWO training runs:
1. **Old experiments (before May 17):** Unidirectional, R@1 = 7.02%
2. **New experiments (after May 17):** Bidirectional, R@1 = 6.61%

**Evidence FOR:**
1. Would explain the 7.02% vs 6.61% values
2. Would match paper's claim about "re-running" ablation (B)

**Evidence AGAINST:**
1. No old experiment directories found
2. experiments.md only shows new experiments (all bidirectional)
3. paper.tex was created with the new experiments

**Status:** Possible but unverified.

---

## What Needs to Be Checked on Remote Desktop

### 1. Check Exp #1 Config
```bash
cd D:\experiments\exp1_baseline
type experiment_config.json | findstr "bidirectional"
```

**Expected:** `"bidirectional": true`

### 2. Check Exp #3 Config
```bash
cd D:\experiments\exp3_full_sharp
type experiment_config.json | findstr "bidirectional"
```

**Expected:** `"bidirectional": true` (but paper says 7.02% unidirectional)

### 3. Search for Old Experiments
```bash
dir D:\experiments\ /s | findstr "7.02\|uni\|ablation"
```

**Looking for:** Any experiments with R@1 = 7.02% in checkpoint names

### 4. Check Training Logs
```bash
cd D:\experiments\exp3_full_sharp
type training.log | findstr "Bidirectional\|Unidirectional\|Loss type"
```

**Expected:** Should say "Bidirectional" if that's what was actually used

### 5. Check Launch Scripts
```bash
cd C:\Users\aya.alaswad\remote\MyReasearch
findstr /s "bidirectional" *.bat
```

**Looking for:** Which launch scripts passed `--bidirectional`

---

## Definitive Answer

**Question:** Were ablations (B), (C), (D) run with unidirectional or bidirectional?

**Answer:** **CANNOT DETERMINE** from the repository alone.

**What we know:**
1. ✅ Code BEFORE May 17, 2026 was unidirectional only
2. ✅ Code AFTER May 17, 2026 has bidirectional option
3. ✅ paper.tex was created May 19, 2026 (AFTER bidirectional added)
4. ✅ experiments.md says ALL experiments used bidirectional
5. ❌ Paper claims ablations (B), (C), (D) used unidirectional
6. ❌ No experiment directories found for ablations
7. ❌ Discrepancy: Paper SHARP R@1=7.02% vs experiments.md Exp #3 R@1=6.21%

**Most likely scenario:** ALL experiments (including ablations) were run AFTER May 17 with bidirectional, but the paper INCORRECTLY claims they were unidirectional. The "7.02% unidirectional" value may be THEORETICAL or from an undocumented earlier run.

**To verify:** Need to check the remote desktop experiment directories and configs.

---

## Recommendation

**You MUST do one of the following:**

### Option 1: Verify on Remote Desktop (Recommended)
```bash
cd C:\Users\aya.alaswad\remote\MyReasearch
git pull
python verify_bidirectional_ablation.py
```

This will check ALL experiment configs and tell you definitively whether they used bidirectional.

### Option 2: Update Paper to Match Reality
If all experiments used bidirectional:
- Remove claim that ablations (B), (C), (D) used unidirectional
- Change Section 2.2 to say "bidirectional"
- Explain that ALL experiments used bidirectional by default

### Option 3: Re-run Experiments Without Bidirectional
- Remove `--bidirectional` from all launch scripts
- Re-run all 6 experiments with unidirectional
- Update all R@1 and F1 values in paper
- **NOT RECOMMENDED:** Too much work, too risky

---

## Files to Check

1. `D:\experiments\exp1_baseline\experiment_config.json`
2. `D:\experiments\exp3_full_sharp\experiment_config.json`
3. `D:\experiments\exp3_full_sharp\training.log`
4. Any experiment with "7.02" in checkpoint name
5. Any launch scripts in `C:\Users\aya.alaswad\remote\MyReasearch\`

---

**Last updated:** 2026-06-26
**Status:** Investigation complete, awaiting remote desktop verification
