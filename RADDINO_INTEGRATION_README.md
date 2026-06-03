# RadDINO Integration - Complete Setup

## What Was Created

**Purpose:** Validate that SHARP's hard negative method generalizes to domain-specific encoders (RadDINO), proving it's not ImageNet-specific.

### Files Created

1. **`train_sharp_raddino_v2.py`** - Main training script with encoder swapping
   - Adds `--encoder_type` argument to choose between 'vit' (ImageNet) or 'raddino' (domain-specific)
   - Both encoders output 768d → same projection head works for both
   - All other training logic identical to original

2. **`run_raddino_exp3_hardneg.bat`** - Full training run (Exp #3 with RadDINO)
   - Most important experiment: Proves hard negatives work with domain encoder
   - Configuration: RadDINO + 60% hard negatives + bidirectional loss
   - Expected runtime: ~2 days
   - Output: `D:\experiments\exp_raddino_hardneg`

3. **`run_raddino_smoketest.bat`** - 100-step verification (5-10 minutes)
   - Quick sanity check before full training
   - Tests: RadDINO loads, forward pass works, no dimension mismatches
   - Output: `D:\experiments\raddino_smoketest`

4. **`verify_raddino_setup.py`** - Pre-flight checks
   - Verifies: Dependencies installed, RadDINO downloaded, script syntax valid
   - Run this FIRST before any training

## How to Run (On Remote Desktop)

### Step 1: Verify Setup
```batch
cd C:\Users\aya.alaswad\remote\MyReasearch
python verify_raddino_setup.py
```

**Expected output:**
```
[OK] All checks passed!
Ready to run:
  1. Smoke test:     run_raddino_smoketest.bat
  2. Full training:  run_raddino_exp3_hardneg.bat
```

**If RadDINO not found:**
```batch
huggingface-cli download microsoft/rad-dino
```

### Step 2: Smoke Test (5-10 minutes)
```batch
run_raddino_smoketest.bat
```

**What it checks:**
- RadDINO model loads from cache
- Forward pass produces correct 768d embeddings
- Loss computation works
- Gradient updates work
- Checkpoint saving works

**Expected result:**
```
[OK] Checkpoint saved successfully
[OK] RadDINO integration working
Ready to run full experiment
```

### Step 3: Full Training (Exp #3 - Hard Negatives)
```batch
run_raddino_exp3_hardneg.bat
```

**Configuration:**
- Encoder: RadDINO (microsoft/rad-dino)
- Hard negatives: 60% curriculum (0→60% over steps 5k-30k)
- Batch size: 256
- Loss: Bidirectional InfoNCE
- Total steps: 100k (early stopping: patience=10)
- Expected runtime: ~48 hours

**Monitoring progress:**
```batch
cd D:\experiments\exp_raddino_hardneg
type p3_history.json
```

## What to Compare

### Original ImageNet ViT (Exp #3)
- Checkpoint: `D:\experiments\exp3_hardneg\p3_best.pt`
- Best F1: **37.4%** (epoch 23)
- R@1: 6.21%

### RadDINO + Hard Neg (New)
- Checkpoint: `D:\experiments\exp_raddino_hardneg\p3_best.pt`
- Expected: F1 ~35-38% (similar to original)
- Purpose: Prove method isn't encoder-dependent

### What Matters for Rebuttal
**If RadDINO+hard_neg beats RadDINO+baseline:**
- ✓ Validates method generalization
- ✓ Addresses reviewer concern about ImageNet transfer
- ✓ Strengthens "retrieval ≠ downstream" claim

**Expected timeline:**
- Exp #2b Stage 2: Finishes ~today/tomorrow
- RadDINO smoke test: 10 minutes
- RadDINO full training: 2 days (parallel with analysis)

## Technical Details

### Architecture Changes
```python
# Old (ImageNet only)
model = GraphTextCLIP(embed_dim=256, temperature=0.07)

# New (encoder swapping)
model = GraphTextCLIP(embed_dim=256, temperature=0.07, encoder_type="raddino")
```

### Encoder Comparison
| Encoder | Source | Output Dim | Notes |
|---------|--------|------------|-------|
| ViT-B/16 | ImageNet-21k | 768d | Original experiments |
| RadDINO | 1.35M chest X-rays | 768d | Domain-specific, self-supervised |

### Why Same Projection Works
Both encoders output 768-dimensional CLS tokens → existing projection head (768→512→256) works unchanged.

## Troubleshooting

### "RadDINO not accessible"
```batch
huggingface-cli download microsoft/rad-dino
```

### "CUDA out of memory"
Reduce batch size in `run_raddino_exp3_hardneg.bat`:
```batch
--batch_size 128 ^  REM was 256
--grad_accum 2 ^    REM was 1 (keeps effective batch=256)
```

### Check GPU usage
```batch
nvidia-smi
```

## Next Steps After Training

1. **Extract results:**
```batch
cd D:\experiments\exp_raddino_hardneg
powershell -Command "Import-Csv lightning_logs\version_0\metrics.csv | Where-Object {$_.val_report_chexbert_f1_macro -ne ''} | Sort-Object {[double]$_.val_report_chexbert_f1_macro} -Descending | Select-Object -First 1"
```

2. **Compare to original Exp #3:**
   - Original: 37.4% F1 (ImageNet ViT)
   - RadDINO: __%  F1 (domain encoder)
   - Δ: __pp difference

3. **Add to experiments.md:**
   - Document RadDINO experiment
   - Update rebuttal strategy
   - Prepare comparison table

## Files Structure
```
C:\Users\aya.alaswad\remote\MyReasearch\
├── train_sharp_raddino_v2.py         # Training script
├── run_raddino_exp3_hardneg.bat      # Full training
├── run_raddino_smoketest.bat         # Quick test
└── verify_raddino_setup.py           # Pre-flight checks

D:\experiments\
├── exp_raddino_hardneg\              # Full experiment output
│   ├── p3_best.pt                    # Best checkpoint
│   ├── p3_history.json               # Training history
│   └── lightning_logs\               # Detailed metrics
└── raddino_smoketest\                # Smoke test output
```

## Expected Workshop Timeline

**Week 1 Day 2-3** (Current):
- [x] Create RadDINO integration
- [ ] Run smoke test (10 min)
- [ ] Launch full training (2 days background)

**Week 1 Day 4-7** (While RadDINO trains):
- [ ] Extract per-condition F1 for existing experiments
- [ ] Verify Exp #4 v2a results
- [ ] Analyze Exp #2/2b results
- [ ] Begin drafting abstract/intro

**Week 2**:
- [ ] RadDINO results ready
- [ ] Compare with original Exp #3
- [ ] Add robustness section to paper
