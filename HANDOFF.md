# HANDOFF: SHARP Rebuttal Preparation

**Date**: 2026-05-24
**Status**: Stage 1 complete, Phase 1 ready, awaiting Exp #4 v2 and Stage 2

---

## Project Context

This is rebuttal preparation for a medical imaging paper (SHARP) using multi-positive InfoNCE for chest X-ray report generation. Reviewers (R1/R2/R3) asked for: (1) downstream CheXbert F1 metrics (not just retrieval R@1), (2) per-condition F1 for specific diseases, (3) analysis of co-positive frequency effects. User needs to run experiments, extract metrics, and write rebuttal responses within ~1 week deadline.

---

## Current State

### ✅ COMPLETE
- **Stage 1 training**: 5 experiments done (Exp #1-4, #2b)
- **Confound analysis**: Dataset size vs paired sampling isolated
- **Key finding**: Forced 100% co-positive pairing collapses performance (4.99% → 0.81%)
- **Infrastructure**: Phase 1 scripts created, Exp #4 v2 script ready

### ⏳ IN PROGRESS
- **Exp #4 v2**: Not yet started (needs 18-20h GPU, proper LR scaling)
- **Phase 1**: Script ready but not executed (SIMPLE version works)

### ❌ BLOCKED
- **CheXbert download**: Google Drive blocked (user in restricted country)
- **Stage 2**: Cannot start without CheXbert checkpoint (438 MB)

---

## Key Decisions Made

### Experiment Design
- **Skip Exp #2 in Stage 2**: Collapsed to 0.81% R@1, not worth fine-tuning (saves 2-4 days)
- **Re-run Exp #4 as v2**: Original was under-trained (6.25k steps) AND had wrong LR (1e-4 instead of 1.6e-3). Need 100k steps + LR=1.6e-3 for fair test of R3's large-batch hypothesis
- **Run Exp #2b control (20k random)**: DONE. Isolated confound - proved paired sampling (not dataset size) is primary cause of collapse

### Technical Decisions
- **Use Phase 1 SIMPLE version**: Original had import errors (`ImageEncoder` doesn't exist, should be `ImageEncoderViT`). SIMPLE version has all code self-contained (no imports from training script)
- **Fair comparison = same optimization steps, not same samples**: Goyal et al. 2017 - large batches need full training schedule. Batch=512 needs 100k steps (not 6.25k) even though it sees 16x more samples
- **LR scaling for large batch**: Linear scaling rule - 1e-4 × (512/32) = 1.6e-3

### Rebuttal Strategy
- **Don't skip Exp #4 from rebuttal**: R3 specifically asked about large batches. Must answer definitively (even if negative result)
- **Strong claim on paired sampling**: Controlled experiment (Exp #2b) proves forced pairing is the problem, not dataset size
- **Stage 2 can be delayed**: If CheXbert blocked, write rebuttal with Stage 1 results + promise Stage 2 in camera-ready

---

## Relevant Files & Paths

### User Machine Paths
- **Remote machine** (where experiments run): `C:\Users\aya.alaswad\remote\`
- **Local machine** (where code is written): `C:\Users\ZA\lawer\MyReasearch\`
- **Experiments**: `D:\experiments\` (on remote)
- **Datasets**: `D:\datasets\mimic-cxr-jpg\` and `D:\datasets\mimic-ext-cxr-qba\` (on remote)

### Key Scripts
- `train_sharp_large_batch.py` - Main training script (ImageEncoderViT, ImprovedTextEncoder classes)
- `run_exp4_v2_PROPER.bat` - Re-run Exp #4 with correct config (100k steps, LR=1.6e-3)
- `phase1_analysis/run_phase1_SIMPLE.bat` - Extract embeddings (WORKING version, zero import dependencies)
- `phase1_analysis/extract_embeddings_SIMPLE.py` - Self-contained, no imports from training script

### Important Documents
- `EXP4_REVISED_PLAN.md` - Explains why Exp #4 FAIR was wrong and how to fix it
- `WHY_PHASE1_SIMPLE_WILL_WORK.md` - Why standalone version avoids import errors
- `FINDINGS_CORRECTED.md` - Analysis with confound acknowledged (in phase0_diagnostics/)
- `STOP_EXP4_AND_RERUN.md` - Decision to stop step 41k run and restart properly

### Checkpoint Locations
```
D:\experiments\exp1_baseline\p3_best.pt         (6.61% R@1, step ???)
D:\experiments\exp2_paired\p3_best.pt           (0.81% R@1, collapsed)
D:\experiments\exp2b_20k_random\p3_best.pt      (4.99% R@1, step 18k, control)
D:\experiments\exp3_full_sharp\p3_best.pt       (6.21% R@1, step 26k, hard negatives)
D:\experiments\exp4_large_batch\p3_best.pt      (8.50% R@1, step 24k, WRONG - overtrained)
D:\experiments\exp4_large_batch_FAIR\p3_best.pt (5.26% R@1, step 6.25k, WRONG - undertrained + wrong LR)
D:\experiments\exp4_v2_large_batch_PROPER\      (NOT CREATED YET - need to run)
```

### Vocabulary
- All experiments share: `D:\experiments\exp1_baseline\p3_vocab.json`

---

## Experiment Results Summary

| Experiment | Batch | Steps | Files | LR | Samples | R@1 | Co-pos % | Status |
|------------|-------|-------|-------|-------|---------|-----|----------|--------|
| **Exp #1** (baseline) | 32 | 100k | 60k+ | 1e-4 | 3.2M | **6.61%** | ~37% | ✅ Best |
| **Exp #3** (hard neg) | 32 | 46k | 60k+ | 1e-4 | 1.5M | **6.21%** | ~28-50% | ✅ Close 2nd |
| **Exp #2b** (20k ctrl) | 32 | 38k | 20k | 1e-4 | 1.2M | **4.99%** | ~37% | ✅ Control |
| **Exp #4 FAIR** | 512 | 6.25k | 60k+ | 1e-4 ❌ | 3.2M | **5.26%** | ~62% | ⚠️ Flawed |
| **Exp #2** (paired) | 32 | ~100k | 20k | 1e-4 | 3.2M | **0.81%** | 100% | ❌ Collapsed |
| **Exp #4 v2** (proper) | 512 | 100k | 60k+ | 1.6e-3 ✓ | 51.2M | **???** | ~62% | ⏳ TO RUN |

### Key Insights
- **Forced pairing collapses**: Exp #2 (100% co-pos) = 0.81%, Exp #2b (37% co-pos) = 4.99%
- **Dataset size matters but less**: 60k→20k files drops R@1 by ~1.6 points (6.61%→4.99%)
- **Hard negatives help slightly**: Exp #3 (6.21%) close to baseline (6.61%)
- **Large batch needs testing**: Exp #4 FAIR was under-trained + wrong LR, need v2

---

## Commands That Work

### Check Experiment Status
```cmd
REM Monitor training progress
powershell Get-Content D:\experiments\exp4_v2_large_batch_PROPER\training.log -Wait -Tail 5

REM Check best checkpoint
python check_exp4_best.py  # Shows step number and R@1
```

### Run Phase 1 (Embedding Extraction)
```cmd
cd C:\Users\aya.alaswad\remote\phase1_analysis
git pull
run_phase1_WORKING.bat
```
**Note**: Use WORKING version - extracts patient_id+study_id from scene graphs (not dicom_id which is empty)

### Start Exp #4 v2
```cmd
cd C:\Users\aya.alaswad\remote
git pull
run_exp4_v2_PROPER.bat
```
**Config**: batch=512, steps=100k, LR=1.6e-3, warmup=5k

### Git Workflow
```cmd
REM On local machine (ZA): edit code, commit, push
cd C:\Users\ZA\lawer\MyReasearch
git add <files>
git commit -m "message"
git push

REM On remote machine (aya.alaswad): pull and run
cd C:\Users\aya.alaswad\remote
git pull
```

---

## Open Questions / Next Steps

### Immediate (Today)
1. **Run Exp #4 v2** (~18-20h GPU): `run_exp4_v2_PROPER.bat`
2. **Run Phase 1** (~1h, parallel): `cd phase1_analysis && run_phase1_SIMPLE.bat`
3. **Solve CheXbert download**: VPN + Google Drive, OR colleague transfer, OR skip Stage 2

### After Exp #4 v2 Completes (~20h)
4. **Analyze Exp #4 v2 R@1**: Does large batch beat baseline (6.61%)? This answers R3's main question
5. **Decide on Stage 2 checkpoints**: Use Exp #1 (6.61%), Exp #3 (6.21%), Exp #4 v2 (??%)
6. **Create findings summary**: Integrate all 5 experiments + Exp #4 v2 result

### After Phase 1 Completes (~1h)
7. **Review t-SNE/UMAP figures**: `phase1_analysis/figures/*.png`
8. **Extract concept consistency metrics**: `phase1_analysis/consistency/*.json`

### Stage 2 (Blocked on CheXbert)
9. **Download CheXbert**: 438 MB file, Google Drive ID `1DS6NYirOXQf8qYieSVMvqNwuOlgAbM_E`
10. **Set up Stage 2 pipeline**: CXRMate fine-tuning scripts
11. **Run Stage 2 training**: ~3-4 days for 3 encoders (Exp #1, #3, #4v2)
12. **Extract CheXbert F1**: Macro + 14 per-condition metrics
13. **Compute bootstrap CIs**: 95% confidence intervals for significance tests

### Rebuttal Writing
14. **Write R1/R2 response**: CheXbert F1 results + per-condition analysis
15. **Write R3 response**: Co-positive frequency analysis + Exp #4 v2 result
16. **Create rebuttal figures**: Stage 1 comparison table, Phase 1 t-SNE, Stage 2 F1 comparison

---

## Gotchas

### Environment Issues
- **Arabic Windows (cp1256)**: Unicode characters (→, ✓, ×) cause `UnicodeEncodeError`. Use ASCII only (`->`, `OK`, `X`)
- **Git LF/CRLF warnings**: Ignore "will be replaced by CRLF" warnings - they're harmless
- **Restricted country**: Google Drive blocked, use VPN or manual transfer for CheXbert

### Import Issues in Phase 1
- **Phase 1 versions**: Original had import errors, SIMPLE had partitioning bug, FIXED had dicom_id bug
- **USE `run_phase1_WORKING.bat`**: Uses patient_id+study_id from scene graphs (dicom_id field is empty)
- **Scene graph format**: Has `patient_id` and `study_id` (NOT `dicom_id`)
- **Image lookup**: Find first .jpg in study directory (studies have multiple images)
- **Class names**: `ImageEncoderViT` and `ImprovedTextEncoder` (NOT `ImageEncoder` or `TextEncoder`)
- **Parameters**: `embedding_dim=256` (NOT `d_model=128`)

### Model Architecture
- **Embedding dimension**: 256 (for both image and text encoders)
- **Vocab size**: Load from `exp1_baseline/p3_vocab.json` (don't rebuild)
- **Image encoder**: ViT-B/16 with 768→512→256 projection
- **Text encoder**: BiLSTM with 256 hidden dim, projects to 256

### Checkpoint Loading
- **State dict keys**: May have prefixes like `img_encoder.` or `image_encoder.`
- **Handle both**: `{k.replace('img_encoder.', ''): v for k, v in state_dict.items() if 'img_encoder' in k}`
- **Best checkpoints**: Always use `p3_best.pt` (not `p3_last.pt`)

### Fair Comparison Rules
- **Sample parity ≠ fair**: Same samples seen doesn't mean fair optimization trajectory
- **Large batch needs**: (1) Full training schedule (100k steps), (2) Scaled LR (1.6e-3 for batch=512)
- **Cite Goyal et al. 2017**: "Accurate, Large Minibatch SGD" for large-batch training justification

### Experiment Naming
- **Exp #4 has 3 versions**:
  1. `exp4_large_batch` (step 41k, overtrained, WRONG)
  2. `exp4_large_batch_FAIR` (step 6.25k, undertrained + wrong LR, WRONG)
  3. `exp4_v2_large_batch_PROPER` (100k steps, LR=1.6e-3, CORRECT - not yet run)
- **Always use v2 going forward**

### CheXbert Download
- **NOT on PhysioNet**: PhysioNet hosts datasets, not CheXbert model
- **PhysioNet credentials don't help**: Separate systems
- **Primary source**: Google Drive (blocked in user's country)
- **File size**: 438 MB (if download is smaller, it's corrupted)
- **Alternative**: VPN + gdown, OR colleague transfer via Dropbox/OneDrive

### Rebuttal Strategy
- **Don't say "R@1 is not important"**: Reviewers will think you're deflecting
- **Frame as "Stage 1 is pre-training"**: CheXbert F1 is the real metric (Stage 2)
- **Be honest about Exp #4**: If v2 doesn't beat baseline, say so honestly (better than silence)
- **Emphasize controlled experiment**: Exp #2b proves paired sampling is the culprit

### Stage 2 Checkpoints to Use
- ✅ **Exp #1** (6.61%) - Baseline
- ✅ **Exp #3** (6.21%) - Hard negatives
- ✅ **Exp #4 v2** (???) - Large batch (after it completes)
- ❌ **Skip Exp #2** (0.81%) - Collapsed, not useful

### Paths Are Different
- **Local (ZA)**: `C:\Users\ZA\lawer\MyReasearch\`
- **Remote (aya.alaswad)**: `C:\Users\aya.alaswad\remote\`
- **Code is edited on local, run on remote** - always git pull on remote before running

### Phase 1 Output
- **Embeddings**: `phase1_analysis/embeddings/exp{1,2,3,4}_embeddings.npz`
- **Figures**: `phase1_analysis/figures/*.png` (t-SNE and UMAP)
- **Metrics**: `phase1_analysis/consistency/*.json`
- **Max samples**: 5000 (reduce to 1000 if OOM)

---

## Quick Start Commands

```cmd
REM On remote machine (aya.alaswad):

REM 1. Pull latest code
cd C:\Users\aya.alaswad\remote
git pull

REM 2. Start Exp #4 v2 (terminal 1, ~20h)
run_exp4_v2_PROPER.bat

REM 3. Run Phase 1 (terminal 2, ~30min for 1000 samples, parallel)
cd phase1_analysis
run_phase1_WORKING.bat

REM 4. Monitor progress
powershell Get-Content D:\experiments\exp4_v2_large_batch_PROPER\training.log -Wait -Tail 5
```

---

## Contact / Credentials

- **User**: aya.alaswad (remote machine where experiments run)
- **GitHub**: ayaalaswad/remote (https://github.com/ayaalaswad/remote.git)
- **PhysioNet**: User has credentials but CheXbert is NOT on PhysioNet (it's on Google Drive)
- **Country restriction**: Google Drive blocked (use VPN or manual transfer)

---

**Last updated**: 2026-05-24
**Session ID**: 8aff32f8-e444-4d11-b6ec-ca7e58dd8811
**Status**: Ready for Exp #4 v2 and Phase 1 execution
