# Phase B: Rigorous Geometry Analysis

## Why Phase B?

**Problem with original Phase 1:**
- UMAP plots showed "tight clusters" for better models
- This is **overinterpreting UMAP artifacts**
- UMAP is a visualization tool, not a quantitative metric
- Reviewers will (correctly) question these claims

**Phase B Solution:**
Use rigorous, quantitative metrics that directly explain retrieval performance:
1. **Cosine similarity distributions** - Shows actual retrieval signal
2. **Alignment + uniformity** (Wang & Isola 2020) - Theoretically grounded metrics
3. **UMAP for Exp #2 collapse ONLY** - Legitimate use case

---

## Phase B Scripts

### 1. Cosine Similarity Distributions
**File:** `compute_cosine_similarity.py`

**What it does:**
- Computes cosine similarity for positive pairs (image, matching_text)
- Computes cosine similarity for negative pairs (image, random_text)
- Plots distributions showing separation

**Why it matters:**
- This IS the retrieval signal
- Greater separation = better R@1
- Directly explains performance differences
- Quantitative, not subjective

**Output:**
- `plots/cosine_similarity_distributions.png` - Histograms for all 4 experiments
- `plots/cosine_similarity_stats.txt` - Mean, std, separation for each

### 2. Alignment & Uniformity
**File:** `compute_alignment_uniformity.py`

**What it does:**
- Computes alignment: How close are positive pairs? (lower = better)
- Computes uniformity: How spread out on hypersphere? (lower = better)
- Based on Wang & Isola 2020 paper

**Why it matters:**
- Two numbers per experiment (quantitative!)
- Theoretically grounded (established metric)
- Reviewers respect this (cited 500+ times)
- Directly interpretable

**Output:**
- `plots/alignment_uniformity.png` - Scatter plot (lower-left = better)
- `plots/alignment_uniformity_metrics.txt` - Exact numbers for each experiment

### 3. Exp #2 Collapse UMAP
**File:** `plot_exp2_collapse_UMAP.py`

**What it does:**
- UMAP visualization for Exp #2 ONLY
- Shows poor image-text separation
- Visual evidence of representation collapse

**Why it matters:**
- This is the ONE legitimate use of UMAP in our analysis
- Shows WHY Exp #2 collapsed to 0.81%
- Visual evidence supporting quantitative metrics

**Output:**
- `plots/exp2_collapse_umap.png` - Single UMAP plot for Exp #2

---

## How to Run

### Full Analysis
```bash
cd phase1_analysis
run_phase1_ANALYSIS.bat
```

This runs all three scripts in sequence (~5-10 minutes).

### Individual Scripts
```bash
# Cosine similarity
python compute_cosine_similarity.py

# Alignment + uniformity
python compute_alignment_uniformity.py

# Exp #2 UMAP
python plot_exp2_collapse_UMAP.py
```

---

## For Your Rebuttal

### What to Say

**For R3 (co-positives & large batch):**
> We analyzed representation quality using rigorous geometry metrics:
>
> 1. **Cosine similarity distributions**: Exp #4 (large batch) shows greater separation between positive pairs (image, matching_text) and negative pairs (image, random_text) compared to baseline. Mean separation: 0.XXX vs 0.YYY.
>
> 2. **Alignment & uniformity** (Wang & Isola 2020): Exp #4 achieves lower alignment (0.XXX vs 0.YYY) and uniformity (0.AAA vs 0.BBB), indicating better contrastive learning quality.
>
> 3. **Exp #2 collapse**: Forced 100% co-positive pairing shows poor image-text separation (UMAP visualization), explaining the 0.81% R@1 performance.

**What NOT to say:**
- ❌ "UMAP shows tighter clusters for better models"
- ❌ "Better separation in 2D projection"
- ❌ Any subjective UMAP interpretation beyond Exp #2 collapse

### Figures for Rebuttal

1. **Main figure**: `cosine_similarity_distributions.png`
   - Shows the actual retrieval geometry
   - 2x2 grid for all 4 experiments
   - Clear visual + quantitative

2. **Supplementary**: `alignment_uniformity.png`
   - Scatter plot with 4 data points
   - Shows theoretical metrics
   - Cites established literature

3. **Evidence figure**: `exp2_collapse_umap.png`
   - Shows WHY paired sampling failed
   - Legitimate use of UMAP
   - Supports the confound analysis

---

## Important Notes

### When to Re-run

**After Exp #4 v2 completes:**
1. Extract embeddings with correct checkpoint:
   ```bash
   cd phase1_analysis
   python extract_embeddings_WORKING.py --checkpoint D:/experiments/exp4_v2_large_batch_PROPER/p3_best.pt --output embeddings/exp4_embeddings.npz
   ```

2. Re-run Phase B analysis:
   ```bash
   run_phase1_ANALYSIS.bat
   ```

This replaces the invalid exp4 embeddings with correct ones.

### Dependencies

All scripts need:
- `numpy`
- `matplotlib`
- `umap-learn` (for Exp #2 plot only)
- `tqdm`

Already installed from previous Phase 1 work.

---

## Comparison: Old vs New

### Old Approach (Phase 1)
- ❌ UMAP "tight clusters" for all experiments
- ❌ Subjective interpretation
- ❌ Reviewers will question

### New Approach (Phase B)
- ✅ Cosine similarity distributions
- ✅ Alignment + uniformity metrics
- ✅ UMAP only for collapse evidence
- ✅ Quantitative, defensible

---

## References

**Wang & Isola (2020)**
"Understanding Contrastive Representation Learning through Alignment and Uniformity on the Hypersphere"
- ICML 2020
- 500+ citations
- Establishes alignment/uniformity as standard metrics

**Cite in rebuttal:**
> Following Wang & Isola (2020), we measure alignment (positive pair closeness) and uniformity (hypersphere coverage). Lower values indicate better contrastive learning quality.

---

**Created:** 2026-05-26
**Status:** Ready to run (pending Exp #4 v2 completion for final results)
