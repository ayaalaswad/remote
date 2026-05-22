# Phase 1: Stage 1 Encoder Analysis (t-SNE/UMAP + Concept Consistency)

**Status**: ✅ Ready to run (infrastructure complete)

**Purpose**: Visualize and quantify what Stage 1 encoders learned by analyzing their embedding spaces.

---

## What Phase 1 Does

### 1. Extract Embeddings
- Loads all 4 Stage 1 checkpoints (Exp #1-4)
- Extracts image and text embeddings on validation set (~5000 samples)
- Saves embeddings + metadata (concept keys, regions, entities, polarities)

### 2. Visualize with t-SNE and UMAP
- Runs dimensionality reduction (128D → 2D)
- Creates 2×2 panel figure comparing all experiments
- Colors points by entity type or polarity
- **Key insight**: Good encoders cluster same concepts together

### 3. Compute Concept Consistency @ Top-5
- For each text embedding, retrieve top-5 most similar embeddings
- Measure what % share the same concept key (region, entity, polarity)
- **High consistency** = encoder learned semantic grouping
- **Low consistency** = encoder confused, needs more training

---

## How to Run

### Option A: Run Everything (Recommended)
```batch
run_phase1.bat
```
This runs all 3 steps sequentially (~30-60 minutes).

### Option B: Run Steps Individually
```batch
# Step 1: Extract embeddings
python phase1_analysis\extract_embeddings.py ^
  --scene_dir D:\datasets\mimic-ext-cxr-qba\scene_graphs\scene_data ^
  --image_dir D:\datasets\mimic-cxr-jpg ^
  --split_csv D:\datasets\mimic-cxr-jpg\mimic-cxr-2.0.0-split.csv.gz ^
  --output_dir phase1_analysis\embeddings ^
  --max_samples 5000 ^
  --device cuda

# Step 2: Visualize
python phase1_analysis\visualize_embeddings.py ^
  --embedding_dir phase1_analysis\embeddings ^
  --output_dir phase1_analysis\figures ^
  --method both ^
  --color_by entity

# Step 3: Compute consistency
python phase1_analysis\concept_consistency_probe.py ^
  --embedding_dir phase1_analysis\embeddings ^
  --output_dir phase1_analysis\consistency ^
  --k 5
```

---

## Expected Outputs

### Embeddings (Step 1)
- `phase1_analysis/embeddings/exp1_baseline_embeddings.npz`
- `phase1_analysis/embeddings/exp2_paired_embeddings.npz`
- `phase1_analysis/embeddings/exp3_full_sharp_embeddings.npz`
- `phase1_analysis/embeddings/exp4_large_batch_embeddings.npz`

Each `.npz` file contains:
- `image_embs`: (N, 128) image embeddings
- `text_embs`: (N, 128) text embeddings
- `concept_keys`: (N,) array of (region, entity, polarity) tuples
- `regions`, `entities`, `polarities`: (N,) arrays
- `dicom_ids`: (N,) array of DICOM IDs

### Figures (Step 2)
- `phase1_analysis/figures/stage1_comparison_tsne_entity.png` - t-SNE colored by entity
- `phase1_analysis/figures/stage1_comparison_umap_entity.png` - UMAP colored by entity
- `phase1_analysis/figures/stage1_comparison_tsne_polarity.png` - t-SNE colored by polarity
- `phase1_analysis/figures/stage1_comparison_umap_polarity.png` - UMAP colored by polarity

**What to look for**:
- Tight clusters = encoder groups same concepts together (good)
- Scattered points = encoder confused (bad)
- Compare Exp #2 (failed) vs others: expect Exp #2 to be more scattered

### Consistency Metrics (Step 3)
- `phase1_analysis/consistency/concept_consistency_k5.json`

Contains for each experiment:
- `overall_consistency`: Average % of top-5 with same concept key
- `entity_consistency`: Breakdown by entity type
- `top_entities`: Best-performing entities
- `bottom_entities`: Worst-performing entities

**Expected values**:
- Exp #1 (baseline): ~40-60% consistency
- Exp #2 (paired, failed): ~20-30% consistency (lower due to collapse)
- Exp #3 (full SHARP): ~45-65% consistency
- Exp #4 (large batch): ~50-70% consistency (best due to more co-positives)

---

## Timeline

- **Step 1 (embeddings)**: ~15-20 minutes
- **Step 2 (visualization)**: ~10-20 minutes
- **Step 3 (consistency)**: ~5-10 minutes
- **Total**: ~30-60 minutes

**GPU usage**: Minimal (inference only), can run in parallel with Exp #2b training.

---

## Parallel Execution with Exp #2b

Phase 1 can run **in parallel** with Exp #2b control experiment:
- Exp #2b uses GPU for training (~12h)
- Phase 1 uses GPU for inference (~30-60 min)
- No conflict: inference is lightweight, won't slow training

**Recommended workflow**:
1. Start Exp #2b: `run_exp2b_20k_random.bat`
2. Immediately start Phase 1: `cd phase1_analysis && run_phase1.bat`
3. Phase 1 finishes in ~1h, Exp #2b continues for ~12h

---

## Troubleshooting

### "Checkpoint not found"
- Check that Stage 1 training completed for that experiment
- Expected paths:
  - `D:\experiments\exp1_baseline\checkpoints\best_model.ckpt`
  - `D:\experiments\exp2_paired_sampling\checkpoints\best_model.ckpt`
  - `D:\experiments\exp3_full_sharp\checkpoints\best_model.ckpt`
  - `D:\experiments\exp4_large_batch\checkpoints\best_model.ckpt`
- If Exp #4 hasn't finished, Phase 1 will skip it and process the other 3

### "ModuleNotFoundError"
- Make sure you're running from the root directory (`C:\Users\ZA\lawer\MyReasearch`)
- Scripts use `sys.path.insert(0, ...)` to import from parent

### Out of memory
- Reduce `--max_samples` from 5000 to 2000 or 1000
- Close other GPU processes

---

## Next Steps After Phase 1

1. Review visualizations - look for clustering quality
2. Compare consistency scores - identify which experiments learned better representations
3. Use findings in rebuttal:
   - "Exp #4 shows tighter clustering with XX% concept consistency vs YY% baseline"
   - "Exp #2's scattered embedding space confirms the collapse (ZZ% consistency)"
4. Proceed to Phase 2 (Stage 2 training) once Exp #4 finishes

---

**Status**: Infrastructure complete. Ready to run once Exp #4 checkpoint is available (or run on Exp #1-3 now).
