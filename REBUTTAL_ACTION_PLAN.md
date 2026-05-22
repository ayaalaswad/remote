# Rebuttal Action Plan - Phased Approach

**Last Updated**: 2026-05-22

This document outlines the complete, phased approach to generating rebuttal data for the SHARP paper reviewers.

---

## ⚠️ Critical Watch-Outs

**Read these BEFORE starting ANY phase!**

1. **R@1 ≠ CheXbert F1**
   - Don't make rebuttal claims based on retrieval numbers alone
   - Reviewers asked about downstream F1 → answer with downstream F1

2. **Exp #2 (0.81%) is NOT a finding yet**
   - Might be a bug (20k files vs 60k+ baseline)
   - Might be paired-sampler issue
   - **Diagnose in Phase 0 FIRST** before making claims

3. **Hard negatives framing**
   - Never say "they don't help"
   - Frame as: "they need scale to be effective, which Exp #4 directly tests"
   - Keeps Exp #3 and #4 as one coherent story

4. **t-SNE / concept probe**
   - Goes on Stage 1 encoders, NOT Stage 2
   - R2's claim "model learned what it was taught" is about pretraining
   - Stage 2 fine-tuning shifts the representations

5. **Save per-sample predictions**
   - Not just aggregate F1
   - Need them for bootstrap CIs and post-hoc analysis
   - Cannot recover statistics later without re-running inference

6. **Per-condition F1 requirements**
   - Must include: Fracture, Lung Lesion, Consolidation
   - R2 named these specifically
   - Show numbers for them, not just macro F1

7. **Bidirectional vs unidirectional is settled**
   - 0.41pp difference from Exp #1
   - Don't re-litigate this
   - Just cite it in rebuttal

8. **Standardize Stage 2 evaluation**
   - Same test split across all 4 runs
   - Same CheXbert version
   - Same generation hyperparameters (greedy vs beam, max_len, etc.)
   - Otherwise comparisons aren't fair

---

## Phase 0: Diagnostics (Today, ~1 hour)

**Goal**: Diagnose Exp #2 before wasting GPU time on Stage 2.

**Budget**: 1 hour of work, no training

**Critical**: Do NOT proceed to Phase 1/2 until this is complete!

### Tasks

1. **Plot Exp #2 loss curve**
   ```bash
   cd C:\Users\aya.alaswad\remote\phase0_diagnostics
   python analyze_exp2_loss.py
   ```
   **Decision**: If loss diverged/plateaued → broken training → fix and re-run
   **Decision**: If loss decreased smoothly but R@1 collapsed → real finding → skip in Stage 2

2. **Sanity-check paired sampler**
   ```bash
   python sanity_check_paired_sampler.py
   ```
   **Decision**: PASS → sampler works, Exp #2 is real
   **Decision**: FAIL → fix sampler, re-run Exp #2

3. **Compute empirical co-positive rates**
   ```bash
   python compute_copositive_rates.py
   ```
   **Use for**: R3's rebuttal point about co-positive frequency

4. **Wait for Exp #4 Stage 1 to finish**
   ```bash
   dir D:\experiments\exp4_large_batch\p3_best.pt
   ```

### Outputs

- `exp2_diagnostic_plots.png` - Loss/R@1 curves
- `copositive_rates_summary.json` - Actual co-pos rates for all 4 experiments
- **Decision**: Skip Exp #2 in Stage 2? (Yes/No)

### Next Steps

- **If Exp #2 is real**: Skip in Stage 2, save 2-4 days GPU time
- **If Exp #2 is broken**: Fix and re-run before Phase 2

---

## Phase 1: Stage 1 Analysis (1-2 days, no new training)

**Goal**: Analyze Stage 1 encoders to address R2's concerns.

**Budget**: 1-2 days of scripting/analysis

### Tasks

1. **t-SNE / UMAP on all 4 Stage 1 encoders**
   - Color by (region, entity, polarity)
   - Produce 2×2 panel figure with shared axes
   - Shows: Does model cluster by concept keys?

2. **Compute "concept consistency @ top-5" retrieval probe**
   - For each query, check if top-5 results share same concept key
   - Put results in table next to R@1
   - Shows: Does retrieval respect concept boundaries?

3. **Diagnose Exp #2 from visualizations**
   - If embeddings collapsed → confirms degenerate training
   - If embeddings have structure → deeper investigation needed

### Outputs

- `stage1_tsne_comparison.png` - 2×2 panel figure
- `concept_consistency_table.csv` - Top-5 probe results
- **Diagnosis**: Is Exp #2 a bug or a feature?

### Use for Rebuttal

- R2: "Model learned what it was taught"
  - Show t-SNE clustering by concept keys
  - Show concept consistency metric

---

## Phase 2: Stage 2 (CXRMate Fine-Tuning) - Main Event

**Goal**: Measure actual downstream CheXbert F1 for reviewer response.

**Budget**: ~9 days of GPU time (3 checkpoints × ~3 days each)

**Critical**: This is what reviewers ACTUALLY care about!

### Setup (One-Time)

1. **Cache CheXbert labels on ground-truth test reports**
   ```bash
   python cache_chexbert_labels.py
   ```
   Saves time, ensures consistency across all 4 evaluations

2. **Install dependencies**
   ```bash
   pip install f1chexbert==0.0.2 transformers==4.43.3 lightning==2.6.1 dlhpcstarter==0.1.4
   ```

3. **Download CheXbert checkpoint**
   - From: https://github.com/stanfordmlgroup/CheXbert#checkpoint-download
   - Save to: `checkpoints/stanford/chexbert/chexbert.pth`

### Training Runs

**Run in this order**:

1. **Exp #1 (Baseline)** - Your reference point
   ```bash
   cd C:\Users\aya.alaswad\remote\stage2_training
   python -m dlhpcstarter -t cxrmate -c configs/exp1_baseline.yaml --stages_module tools.stages --train
   ```
   **Why first**: Without this, no other number anchors
   **Expected F1**: ~0.30-0.31 (similar to paper's ImageNet baseline)

2. **Exp #3 (Full SHARP at batch=32)** - Main answer to R1 and MR
   ```bash
   python -m dlhpcstarter -t cxrmate -c configs/exp3_full.yaml --stages_module tools.stages --train
   ```
   **Why important**: This is your main SHARP result with hard negatives
   **Expected F1**: ~0.31-0.32 (should beat baseline)

3. **Exp #4 (Batch=512)** - Main answer to R3
   ```bash
   python -m dlhpcstarter -t cxrmate -c configs/exp4_large.yaml --stages_module tools.stages --train
   ```
   **Why important**: Tests if large batch solves degeneracy concern
   **Expected F1**: ~0.32-0.33 (should be best)

4. **Exp #2 (Paired Sampling)** - SKIP unless Phase 0 shows it's real
   - If skipped: Save 2-4 days GPU time
   - If included: Run last, lowest priority

### Per Run, Save:

- Checkpoint (`.ckpt` file)
- Loss curve (from training log)
- **Per-sample generated reports** (for bootstrap CIs)
- **Per-sample CheXbert predictions** (for bootstrap CIs)
- Configuration file

### Testing Runs

After training each checkpoint:
```bash
python -m dlhpcstarter -t cxrmate -c configs/expX_XXX.yaml --stages_module tools.stages --test
```

Extract metrics from test log:
- CheXbert F1 (macro)
- CheXbert F1 per-condition (14 conditions)
- RadGraph F1
- CXR-BERT
- BLEU-1/4, ROUGE-L, METEOR, BERTScore

### Timeline

| Checkpoint | Training | Testing | Total |
|------------|----------|---------|-------|
| Exp #1     | 2 days   | 0.5 day | 2.5 days |
| Exp #3     | 2 days   | 0.5 day | 2.5 days |
| Exp #4     | 3 days   | 0.5 day | 3.5 days |
| **Total**  | **7 days** | **1.5 days** | **8.5 days** |

### Parallel Option

If GPU memory allows (~20GB free):
- Train Exp #1 and Exp #3 in parallel → Save 2 days
- Test all 3 in parallel → Save 1 day
- **New total**: ~6 days

### Outputs

- `exp1_baseline/` - Checkpoint + logs + results
- `exp3_full/` - Checkpoint + logs + results
- `exp4_large/` - Checkpoint + logs + results
- `stage2_results_summary.json` - All metrics
- `stage2_per_condition_f1.csv` - Per-condition breakdown

---

## Phase 3: Statistical Analysis (Minutes, after Phase 2)

**Goal**: Compute significance tests for rebuttal.

**Budget**: <1 hour

### Tasks

1. **Bootstrap 95% CIs on F1**
   ```bash
   python compute_bootstrap_cis.py
   ```
   For each model: resample 1000 times, compute F1 distribution

2. **Paired bootstrap tests**
   ```bash
   python paired_bootstrap_test.py --baseline exp1 --compare exp3
   python paired_bootstrap_test.py --baseline exp1 --compare exp4
   ```
   Answers R1's significance complaint directly

3. **Per-condition F1 for all 14 CheXbert conditions**
   ```bash
   python extract_per_condition_f1.py
   ```
   Highlight: Fracture, Lung Lesion, Consolidation (R2 asked)

### Outputs

- `bootstrap_cis.json` - CIs for all models
- `significance_tests.txt` - p-values for all comparisons
- `per_condition_f1_all.csv` - Full breakdown
- `per_condition_f1_reviewer.csv` - Just Fracture/Lung Lesion/Consolidation

### Use for Rebuttal

- R1: "Statistical significance?"
  → "Paired bootstrap with 1000 resamples: p < 0.001"

- R2: "Per-condition F1?"
  → "Fracture: 0.XX, Lung Lesion: 0.XX, Consolidation: 0.XX"

---

## Phase 4: Writing (Hours, no compute)

**Goal**: Turn all results into rebuttal text.

**Budget**: 4-8 hours of writing

### Tasks

1. **Error analysis paragraph**
   - Discuss low-gain conditions (Fracture, Lung Lesion, Consolidation)
   - Hypothesize why: sparse scene-graph coverage, class imbalance
   - Show you understand the limitations

2. **Dataset adaptation paragraph**
   - Outline two paths forward:
     - Path 1: Pseudo scene-graphs via NER + region proposals
     - Path 2: Report-level concept extraction only
   - Shows reviewers you have a plan

3. **Update reviewer tracker**
   - For each reviewer point, add:
     - Actual results (numbers)
     - Statistical tests (p-values)
     - Status (Addressed/Partially/Pending)

4. **Draft rebuttal letter**
   - Point-by-point responses
   - Cite specific tables/figures
   - Include new results from Phases 2-3

### Outputs

- `error_analysis.txt` - Draft paragraph
- `dataset_adaptation.txt` - Draft paragraph
- `reviewer_tracker_updated.xlsx` - Complete status
- `rebuttal_draft.txt` - Full letter

---

## Decision Points

### After Phase 0:

**Q**: Is Exp #2 real or broken?
- **Real** → Skip in Stage 2, save 2-4 days
- **Broken** → Fix and re-run

### After Phase 2:

**Q**: Do results support resubmission?
- **Yes** (Exp #3 or #4 > baseline, p < 0.05) → Proceed with rebuttal
- **No** (no significant gains) → Major revision needed

### Budget Check:

**Q**: Can you run all 3 Stage 2 experiments?
- **Yes** (~9 days available) → Run all
- **No** (< 9 days) → Prioritize Exp #3 and #4, skip Exp #1 or use paper's baseline

---

## Final Reminders

1. **One thing at a time**
   - Don't start Stage 2 before Phase 0 diagnostics
   - May save 2-4 days on Exp #2 just by checking a loss curve

2. **Reproducibility matters**
   - Script everything in Phase 2
   - If you have to re-run, you don't want to rebuild from memory

3. **The tracker is your memory**
   - Update after each phase
   - Rebuttal letter writes itself when time comes

4. **Standardize everything**
   - Same CheXbert version
   - Same test split
   - Same generation hyperparameters
   - Otherwise comparisons aren't fair

5. **Save everything**
   - Per-sample predictions (for bootstrap)
   - Training curves (for debugging)
   - Configs (for reproducibility)

---

## Current Status

- [x] Stage 1: All 4 experiments complete (except Exp #4, running)
- [x] Phase 0 scripts created
- [ ] Phase 0 diagnostics run
- [ ] Phase 1 analysis
- [ ] Phase 2 Stage 2 training
- [ ] Phase 3 statistical tests
- [ ] Phase 4 writing

---

## Next Actions (In Order)

1. Wait for Exp #4 Stage 1 to finish
2. Run Phase 0 diagnostics (~1 hour)
3. Decide: Skip Exp #2 in Stage 2?
4. Run Phase 1 analysis (1-2 days)
5. Start Phase 2 Stage 2 training (~9 days)
6. Run Phase 3 statistical tests (<1 hour)
7. Write Phase 4 rebuttal (4-8 hours)

**Total estimated time**: ~12-14 days
