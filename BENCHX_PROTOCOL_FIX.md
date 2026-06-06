# BenchX Protocol Fix - CRITICAL

## Problem Identified

Previous RSNA training (AUROC 0.7175) used **NON-STANDARD hyperparameters** that differ from MGCA's protocol. This makes results **NOT comparable** to BenchX baselines.

## Previous Config (sharp_rsna_final.yml) - WRONG

```yaml
trainer:
  optimizer: AdamW          ❌ Different from MGCA
  optim_params:
    lr: 1e-4                ❌ Different from MGCA
  batch_size: 32            ❌ Different from MGCA
  epochs: 30
  eval_start: 5
  eval_interval: 2
```

## MGCA's Actual Protocol (from mgca_vit.yml)

```yaml
trainer:
  optimizer: SGD            ✓ BenchX standard
  optim_params:
    lr: 1e-2                ✓ BenchX standard
    momentum: 0.9
  batch_size: 64            ✓ BenchX standard
  epochs: 200 (NIH) / 30 (RSNA)
  eval_start: 10 (NIH) / 5 (RSNA)
  eval_interval: 5 (NIH) / 2 (RSNA)
```

## New Config (sharp_rsna_benchx.yml) - CORRECT

**Only changes from MGCA:**
- Checkpoint: `D:/experiments/exp3_full_sharp/p3_best_timm.pt` (instead of MGCA checkpoint)

**Everything else identical to MGCA:**
- optimizer: SGD (lr=1e-2, momentum=0.9)
- batch_size: 64
- lr_decay: WarmupCosineScheduler
- early_stop: 10
- All other hyperparameters match MGCA exactly

## Why This Matters

For fair comparison to BenchX Table 2 results, we must use **identical training protocol**:

| Aspect | Previous | Now | BenchX Standard |
|--------|----------|-----|-----------------|
| Optimizer | AdamW | SGD | SGD |
| Learning Rate | 1e-4 | 1e-2 | 1e-2 |
| Batch Size | 32 | 64 | 64 |
| Protocol | Custom | MGCA | MGCA |
| Comparable? | ❌ NO | ✅ YES | ✅ YES |

## Action Required

Run training with new config:

```cmd
cd C:\Users\aya.alaswad\remote
git pull origin main
run_rsna_only.bat
```

This will use **sharp_rsna_benchx.yml** which matches MGCA's protocol exactly.

## Expected Outcome

New AUROC will be directly comparable to:
- MGCA-ViT on RSNA
- MRM on RSNA
- All other BenchX baselines on RSNA

Previous 0.7175 result should be **discarded** as it used non-standard hyperparameters.
