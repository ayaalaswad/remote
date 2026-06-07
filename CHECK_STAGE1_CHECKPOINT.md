# Check for Stage 1 Checkpoint

## What We Need

**Stage 1 checkpoint** from Exp #3 (before Stage 2 report generation fine-tuning)

## Current Situation

**Currently using:**
```
D:/experiments/exp3_full_sharp/p3_best.pt
```

This is the **Stage 2 checkpoint** (after report generation fine-tuning with F1=37.4%)

## Possible Stage 1 Checkpoint Locations

Based on typical checkpoint naming patterns, check for:

```
D:/experiments/exp3_full_sharp/
├── p1_best.pt              ← Stage 1 checkpoint (retrieval training)
├── p2_best.pt              ← Stage 2 checkpoint (report generation)
├── p3_best.pt              ← Stage 3? Or final checkpoint
├── best_r1.pt              ← Best R@1 checkpoint
├── contrastive_best.pt     ← Contrastive training checkpoint
├── stage1_best.pt          ← Explicit Stage 1 checkpoint
└── checkpoint_epoch_X.pt   ← Intermediate checkpoints
```

## Commands to Run on Remote Desktop

```cmd
REM List all checkpoint files in exp3_full_sharp
dir D:\experiments\exp3_full_sharp\*.pt

REM Check file sizes (Stage 1 and Stage 2 should be similar)
dir D:\experiments\exp3_full_sharp\*.pt /O:-S

REM Look for any checkpoint metadata or logs
dir D:\experiments\exp3_full_sharp\*.log
dir D:\experiments\exp3_full_sharp\*.json
type D:\experiments\exp3_full_sharp\training.log
```

## Alternative: Check Training Scripts

The training script that created these checkpoints should indicate the checkpoint naming convention.

Look for:
```
remote/train_stage1.py
remote/train_stage2.py
remote/run_exp3.sh
```

## Why This Matters

**Stage 1 (Contrastive):**
- Pure image-text alignment
- Should have better visual features for classification
- R@1 = 6.21% for Exp #3

**Stage 2 (Report Generation):**
- Fine-tuned for report generation
- May have degraded visual features for classification
- F1 = 37.4% (CheXbert)

**Hypothesis:** Stage 1 checkpoint will perform MUCH better on RSNA/SIIM classification than Stage 2 checkpoint.

## Expected BenchX Performance Improvement

If Stage 2 degraded visual features:
- **Current (Stage 2):** F1 = 24.2 / 43.1 / 45.9
- **Expected (Stage 1):** F1 = 50-60 / 60-70 / 65-75 (competitive with baselines)

This could be a **20-30 point improvement** in F1 scores!
