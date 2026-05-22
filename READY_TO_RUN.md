# Ready to Run: Exp #2b + Phase 1 (In Parallel)

**Date**: 2026-05-22
**Status**: ✅ All infrastructure complete - ready to execute

---

## What's Ready

### ✅ Exp #2b Control (20k Random Sampling)
- **Purpose**: Isolate dataset size confound (20k vs 60k+ files)
- **Duration**: ~12 hours
- **Script**: `run_exp2b_20k_random.bat`
- **Implementation**: ✅ Complete (`--max_train_files` added to training script)

### ✅ Phase 1 Analysis (t-SNE/UMAP + Concept Consistency)
- **Purpose**: Visualize Stage 1 encoder representations
- **Duration**: ~30-60 minutes
- **Script**: `phase1_analysis\run_phase1.bat`
- **Infrastructure**: ✅ Complete (3 scripts created)

---

## Execution Plan

### Step 1: Start Exp #2b (12h training)
```batch
cd C:\Users\ZA\lawer\MyReasearch
run_exp2b_20k_random.bat
```

**What this does**:
- Trains baseline configuration (same as Exp #1)
- **Only difference**: Limits to 20k training files (matches Exp #2's manifest)
- Uses random sampling (NOT paired sampling)
- Saves checkpoint to `D:\experiments\exp2b_20k_random\`

**Expected outcome (decision matrix)**:
- **R@1 ≈ 6.6%** (similar to baseline) → Dataset size NOT the issue → Can strongly blame forced pairing in rebuttal
- **R@1 ≈ 0.8%** (tanks like Exp #2) → Dataset size IS the issue → Must use cautious language
- **R@1 ≈ 4-5%** (between) → Both contribute → Quantify each factor's contribution

### Step 2: Start Phase 1 (in parallel, ~1h)
**Open a new terminal** and run:
```batch
cd C:\Users\ZA\lawer\MyReasearch\phase1_analysis
run_phase1.bat
```

**What this does**:
1. Extracts embeddings from 4 Stage 1 checkpoints
2. Creates t-SNE and UMAP visualizations (2×2 panel figures)
3. Computes concept consistency @ top-5 metric

**Outputs**:
- Figures: `phase1_analysis\figures\stage1_comparison_tsne_entity.png` (and UMAP)
- Metrics: `phase1_analysis\consistency\concept_consistency_k5.json`

**Why parallel is safe**:
- Exp #2b: Heavy GPU training (~90% GPU utilization)
- Phase 1: Light GPU inference (~10% GPU utilization)
- No conflict: Phase 1 finishes in ~1h, Exp #2b continues for ~12h

---

## What Was Completed

### 1. Fixed Exp #2b Implementation
**File**: `train_sharp_large_batch.py` (lines 852-857)

Added parameter:
```python
p.add_argument("--max_train_files", type=int, default=None,
               help="Limit number of training files (for dataset size ablations like Exp 2b)")
```

Added limiting logic after `partition_scene_files()`:
```python
# -- 3b. [ABLATION] Limit training files if requested (for Exp 2b control)
if args.max_train_files is not None:
    import random
    original_count = len(train_files)
    train_files = random.Random(42).sample(train_files, min(args.max_train_files, len(train_files)))
    print(f"\n[ABLATION] Limited training files: {original_count:,} → {len(train_files):,} (max_train_files={args.max_train_files})")
```

### 2. Created Phase 1 Infrastructure
**Files created**:
- `phase1_analysis/extract_embeddings.py` - Loads checkpoints, extracts embeddings
- `phase1_analysis/visualize_embeddings.py` - Creates t-SNE/UMAP figures
- `phase1_analysis/concept_consistency_probe.py` - Computes consistency metric
- `phase1_analysis/run_phase1.bat` - Runs all 3 steps
- `PHASE1_README.md` - Detailed documentation

**Key features**:
- Supports all 4 experiments (skips missing checkpoints gracefully)
- Configurable: `--max_samples`, `--k`, `--color_by`, `--method`
- Produces publication-ready figures (300 DPI)
- Exports JSON metrics for rebuttal writing

---

## Timeline

### Immediate (Today)
1. **Start Exp #2b**: Run `run_exp2b_20k_random.bat` (~12h)
2. **Start Phase 1**: Run `phase1_analysis\run_phase1.bat` (~1h, parallel)

### After Exp #2b Completes (~12h)
3. **Analyze Exp #2b results**: Check final R@1 to resolve confound
4. **Update FINDINGS_CORRECTED.md**: Add Exp #2b outcome to Scenario A/B/C
5. **Determine rebuttal language strength**: Strong vs cautious based on outcome

### After Exp #4 Finishes (ongoing)
6. **Re-run Phase 1 with Exp #4**: Add 4th checkpoint to embeddings/visualizations
7. **Install CheXbert**: Prepare for Phase 2
8. **Start Phase 2**: Stage 2 training on 3 checkpoints (Exp #1, #3, #4)

---

## Current Status Summary

### ✅ Phase 0: Diagnostics (Complete)
- Loss curves analyzed → Training not broken
- Co-positive rates extracted → Sampler working correctly
- Confound identified → Need Exp #2b control
- Decision made → Skip Exp #2 in Stage 2

### ⏳ Phase 0.5: Exp #2b Control (Ready to run)
- Infrastructure: ✅ Complete
- Script: ✅ Ready
- Execution: ⏳ Pending (run now)

### ⏳ Phase 1: t-SNE/UMAP (Ready to run in parallel)
- Infrastructure: ✅ Complete
- Scripts: ✅ Ready (3 scripts)
- Execution: ⏳ Pending (run now)

### ⏳ Phase 2: Stage 2 Training (Waiting for Exp #4)
- Infrastructure: ✅ Complete (from previous work)
- CheXbert: ⏳ Not installed yet
- Execution: ⏳ Blocked (need Exp #4 checkpoint)

### ⏳ Phase 3: Statistical Tests (Waiting for Phase 2)
- Infrastructure: ⏳ Partial (bootstrap code needs update)
- Execution: ⏳ Blocked (need Stage 2 results)

### ⏳ Phase 4: Writing (Waiting for Phase 3)
- Infrastructure: ⏳ Not started
- Execution: ⏳ Blocked (need all results)

---

## Next Actions

**YOU (User)**:
1. Open terminal 1: Run `run_exp2b_20k_random.bat`
2. Open terminal 2: Run `phase1_analysis\run_phase1.bat`
3. Check Phase 1 outputs in ~1 hour (figures + consistency metrics)
4. Check Exp #2b results in ~12 hours (final R@1, resolves confound)

**ME (Assistant)**:
- Monitoring for questions/issues
- Ready to analyze results when complete
- Ready to proceed to Phase 2 once Exp #4 finishes

---

## Commands to Run

### Terminal 1 (Exp #2b, 12h)
```batch
cd C:\Users\ZA\lawer\MyReasearch
run_exp2b_20k_random.bat
```

### Terminal 2 (Phase 1, 1h)
```batch
cd C:\Users\ZA\lawer\MyReasearch\phase1_analysis
run_phase1.bat
```

Both can run simultaneously without conflict.

---

**Status**: ✅ ALL INFRASTRUCTURE COMPLETE - READY TO EXECUTE
