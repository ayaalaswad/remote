# SHARP Experiments - Complete Results Summary

## Stage 1: Contrastive Pretraining (Image-Text Retrieval)

| Exp | Name | Batch | Steps | LR | Samples | Hard Neg | Paired | Dataset | R@1 (I→T) | Status |
|-----|------|-------|-------|----|---------|---------:|-------:|---------|-----------|--------|
| #1 | Baseline | 32 | 100k | 1e-4 | 3.2M | 0.0 | No | 60k+ | **6.61%** | ✓ Complete |
| #2 | Paired Sampling | 32 | ~100k | 1e-4 | 3.2M | 0.0 | 100% | 20k | **0.81%** | ✓ Complete (collapsed) |
| #2b | 20k Random Control | 32 | 38k | 1e-4 | 1.2M | 0.0 | ~37% | 20k | **4.99%** | ✓ Complete |
| #3 | Hard Negatives | 32 | 46k | 1e-4 | 1.5M | 0.6 | No | 60k+ | **6.21%** | ✓ Complete |
| #4 v2a | Large Batch (Fair) | 512 | 6.25k | 1.6e-3 | 3.2M | 0.6 | No | 60k+ | **8.77%** | ✓ Complete |
| #4 v2b | Large Batch (Ceiling) | 512 | 100k | 1.6e-3 | 51.2M | 0.6 | No | 60k+ | **8.9%** | ⏳ Running/Complete? |

### Stage 1 Key Settings

**Common across all:**
- Dataset: MIMIC-CXR + MIMIC-Ext scene graphs
- Architecture: ViT-B/16 (ImageNet pretrained) + BiLSTM text encoder
- Embedding dim: 256
- Optimizer: AdamW
- Image size: 224×224
- Bidirectional loss: Yes (all experiments)
- Warmup: 5k steps (or 5% of total for v2a)
- LR schedule: Linear warmup → Cosine decay
- Unfreeze: Last 4 ViT blocks at step 5k (or 5% for v2a)

**Experiment-specific:**
- **Exp #1:** Vanilla multi-positive InfoNCE, no hard negatives
- **Exp #2:** Forced 100% co-positive pairing (all batch pairs share concept)
- **Exp #2b:** Same as #1 but only 20k files (controls for dataset size)
- **Exp #3:** Hard negatives ramped 0→60% over steps 5k→30k
- **Exp #4 v2a:** Large batch (512) + LR scaled (1.6e-3) + hard negatives, matched samples to baseline
- **Exp #4 v2b:** Large batch (512) + LR scaled (1.6e-3) + hard negatives, full 100k steps (scaling ceiling)

---

## Stage 2: Report Generation Fine-tuning (Downstream CheXbert F1)

| Exp | Stage 1 Checkpoint | Stage 1 R@1 | Model | Epochs | Batch | Accum Batch | Best CheXbert F1 | Best Epoch | Status |
|-----|-------------------|-------------|-------|--------|-------|-------------|------------------|------------|--------|
| #1 | exp1_baseline/p3_best.pt | 6.61% | CXRMate Single | 32 | 8 | 32 | **31.2%** | 25 | ✓ Complete |
| #2 | exp2_paired/p3_best.pt | 0.81% | CXRMate Single | 32 | 8 | 32 | **TBD** | - | ❌ **NEED TO RUN** |
| #2b | exp2b_20k_random/p3_best.pt | 4.99% | CXRMate Single | 32 | 8 | 32 | **TBD** | - | ❌ **NEED TO RUN** |
| #3 | exp3_full_sharp/p3_best.pt | 6.21% | CXRMate Single | 32 | 8 | 32 | **37.4%** 🏆 | 23 | ✓ Complete |
| #4 v2a | exp4_v2a_matched_epochs/p3_best.pt | 8.77% | CXRMate Single | 32 | 8 | 32 | **34.6%** | 21 | ✓ Complete |
| #4 v2b | exp4_v2_large_batch_PROPER/p3_best.pt | 8.9% | CXRMate Single | 32 | 8 | 32 | **TBD** | - | ⏳ **PENDING** |

### Stage 2 Key Settings

**Common across all:**
- Framework: CXRMate (official implementation)
- Dataset: MIMIC-CXR (same as Stage 1)
- Training examples: 118,290
- Validation examples: 933
- Architecture: Single-image report generation (not longitudinal)
- Decoder: Transformer decoder with teacher forcing
- Max epochs: 32
- Learning rate: 5e-5
- Optimizer: AdamW
- Precision: 16-bit mixed
- Monitor metric: val_report_chexbert_f1_macro
- Early stopping: Best checkpoint saved based on CheXbert F1
- Evaluation: CheXbert F1 (14 conditions), BLEU, ROUGE, CIDEr
- Strategy: auto (single GPU)

**Evaluation metrics computed:**
- CheXbert F1 (macro + per-condition for 14 diseases)
- CheXbert accuracy
- CheXbert precision/recall
- NLG metrics: BLEU-1/2/3/4, ROUGE-L, CIDEr

---

## Key Findings

### 1. Retrieval vs Downstream Divergence

**Critical insight:** Best retrieval R@1 ≠ Best downstream CheXbert F1

| Experiment | Stage 1 R@1 | Stage 2 F1 | Interpretation |
|------------|-------------|------------|----------------|
| Exp #4 v2a | **8.77%** (best) | 34.6% | Large batch → good retrieval |
| Exp #3 | 6.21% (lower) | **37.4%** (best) | Hard negatives → better clinical representations |
| Exp #1 | 6.61% | 31.2% (baseline) | - |

**Implication:** Hard negatives produce more clinically meaningful representations even when they slightly reduce retrieval performance.

### 2. Large Batch Effects (R3)

**Fair matched-sample comparison (Exp #4 v2a vs Exp #1):**
- Stage 1: +2.16pp R@1 improvement (6.61% → 8.77%, +32.7% relative)
- Stage 2: +3.4pp F1 improvement (31.2% → 34.6%, +10.9% relative)
- **Conclusion:** Large batch helps both retrieval and downstream when LR scaled properly

**But hard negatives matter more:**
- Exp #3 (small batch + hard neg): 37.4% F1
- Exp #4 v2a (large batch + hard neg): 34.6% F1
- **Conclusion:** Hard negative sampling more important than batch size for downstream

### 3. Paired Sampling Collapse (R3)

**Stage 1 results:**
- Exp #2 (100% paired): 0.81% R@1 (collapsed)
- Exp #2b (37% paired, 20k files): 4.99% R@1
- Exp #1 (37% paired, 60k+ files): 6.61% R@1

**Stage 2 results:** ❌ NEED TO RUN Exp #2 and #2b Stage 2 to confirm collapse propagates

### 4. Downstream Improvement (R1/R2)

**Multi-positive InfoNCE + hard negatives (Exp #3) vs baseline (Exp #1):**
- Stage 1: -0.4pp R@1 (6.21% vs 6.61%, slight decrease)
- Stage 2: **+6.2pp F1** (37.4% vs 31.2%, **+19.9% relative improvement**)

**This directly answers R1/R2's concern about downstream performance.**

---

## Missing Experiments (Critical for Rebuttal)

### High Priority (Run ASAP)

1. **Exp #2 Stage 2** (~5 hours)
   - Confirms paired-sampling collapse propagates to downstream
   - Strongest evidence for R3 response
   - Expected: Very low CheXbert F1 (if Stage 1 collapsed)

2. **Exp #2b Stage 2** (~5 hours)
   - Controls for dataset size at downstream level
   - Confirms 20k files sufficient for downstream
   - Expected: F1 between Exp #1 and Exp #3

3. **Per-condition CheXbert F1 extraction** (~1 hour, no retraining)
   - R2 explicitly asked for this
   - Extract from existing checkpoints for Exp #1, #3, #4 v2a
   - 14 conditions: Atelectasis, Cardiomegaly, Consolidation, Edema, etc.

### Medium Priority

4. **Exp #4 v2b Stage 2** (~20 hours after v2b Stage 1 completes)
   - Tests scaling-ceiling on downstream
   - If F1 doesn't exceed Exp #3 → major finding about batch scaling limits

---

## Directory Structure

### Stage 1 Checkpoints
```
D:/experiments/
├── exp1_baseline/p3_best.pt (6.61% R@1)
├── exp2_paired/p3_best.pt (0.81% R@1)
├── exp2b_20k_random/p3_best.pt (4.99% R@1)
├── exp3_full_sharp/p3_best.pt (6.21% R@1)
├── exp4_v2a_matched_epochs/p3_best.pt (8.77% R@1)
└── exp4_v2_large_batch_PROPER/p3_best.pt (8.9% R@1)
```

### Stage 2 Results
```
C:/Users/aya.alaswad/remote/cxrmate/experiments/cxrmate/single_tf/
├── trial_0/ (Exp #1: 31.2% F1)
├── trial_1/ (Exp #3: 37.4% F1)
├── trial_2/ (Exp #4 v2a: 34.6% F1)
├── trial_3/ (AVAILABLE for Exp #2)
├── trial_4/ (AVAILABLE for Exp #2b)
└── trial_5/ (AVAILABLE for Exp #4 v2b)
```

---

## Rebuttal Strategy

### For R1/R2 (Downstream Performance Concern)

**Response:**
> "We now provide comprehensive Stage 2 results showing our method (Exp #3: multi-positive InfoNCE + hard negatives) improves downstream CheXbert F1 from 31.2% to 37.4% (+6.2 absolute points, +19.9% relative). This improvement is larger than any Stage 1 retrieval gain, demonstrating that hard negatives produce representations specifically beneficial for clinical report generation. Per-condition F1 gains are concentrated in [X, Y, Z] (see Table X)."

**Evidence:**
- ✓ Exp #1 vs Exp #3 Stage 2 comparison (complete)
- ❌ Per-condition F1 breakdown (need to extract)

### For R3 (Large Batch & Co-positive Frequency)

**Response:**
> "We test large batch in two controlled regimes: (1) matched samples (Exp #4 v2a, 6,250 steps, 3.2M samples) achieving R@1=8.77% and F1=34.6%, and (2) extended training (Exp #4 v2b, 100k steps). While large batch improves retrieval (+2.16pp vs baseline), hard negatives are more important for downstream performance (Exp #3: 37.4% F1 vs v2a: 34.6% F1).
>
> Regarding co-positive frequency: forced 100% pairing (Exp #2) collapses to R@1=0.81% and F1=[TBD], while natural 37% co-positive rate (Exp #2b, 20k files) achieves R@1=4.99% and F1=[TBD]. This demonstrates the collapse is due to excessive pairing, not dataset size."

**Evidence:**
- ✓ Exp #4 v2a complete (fair large-batch test)
- ⏳ Exp #4 v2b running (scaling ceiling)
- ❌ Exp #2 Stage 2 (critical for collapse narrative)
- ❌ Exp #2b Stage 2 (controls for dataset size)

---

## Next Actions (Priority Order)

1. **Run Exp #2 Stage 2** → Confirms collapse propagates to downstream
2. **Run Exp #2b Stage 2** → Controls for dataset size
3. **Extract per-condition F1** → Answers R2 directly
4. **When Exp #4 v2b finishes, run Stage 2** → Scaling ceiling story
5. **Verify Exp #4 v2a 8.77%** → Check loss curve, eval set consistency

**Can run in parallel:** Items 1, 2, and 3 (no dependencies)

---

**Last updated:** 2026-05-29
**Status:** 3/6 Stage 2 experiments complete, 3 critical gaps remain
