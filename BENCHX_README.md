# BenchX Evaluation - Quick Start Guide

**Goal:** Evaluate SHARP on 4 downstream classification datasets (RSNA, SIIM, NIH, VinDr-CXR) against 9 published baselines.

**Total Time:** 1-2 days (mostly downloads + GPU time)
**GPU Requirement:** 1 GPU with ≥16 GB VRAM

---

## Step-by-Step Commands

### Step 1: Stop RadDINO (Press Ctrl+C in training window)

RadDINO has auto-resume - you can continue it later.

---

### Step 2: Pull BenchX Files from GitHub

```batch
cd C:\Users\aya.alaswad\remote\MyReasearch
git pull origin main
```

**Files you should now have:**
- `benchx_setup.bat` - Clone repo + create conda env
- `benchx_integrate_sharp.bat` - Install SHARP into BenchX
- `benchx_sharp_model.py` - SHARP model wrapper
- `benchx_config_*.yml` - Config files for 4 datasets
- `benchx_download_data.md` - Data download instructions
- `benchx_run_all.bat` - Run all 4 datasets
- `benchx_test.bat` - Quick test before running

---

### Step 3: Setup BenchX Environment

```batch
cd C:\Users\aya.alaswad\remote\MyReasearch
benchx_setup.bat
```

**This will:**
- Clone BenchX repo to `C:\Users\aya.alaswad\remote\BenchX`
- Create conda environment `benchx` with Python 3.10
- Install dependencies (PyTorch, transformers, etc.)

**Time:** ~10 minutes

---

### Step 4: Integrate SHARP into BenchX

```batch
benchx_integrate_sharp.bat
```

**This will:**
- Copy `benchx_sharp_model.py` → `BenchX/models/sharp.py`
- Copy config files → `BenchX/configs/classification/*/sharp.yml`

**Time:** <1 minute

---

### Step 5: Test SHARP Integration

```batch
benchx_test.bat
```

**This verifies:**
- Conda environment works
- SHARP model imports
- Checkpoint loads and forward pass works

**Time:** ~1 minute

**If test passes:** ✓ Ready to download data
**If test fails:** Check error messages

---

### Step 6: Download Datasets (Choose Your Strategy)

**Option A: Quick Start - SIIM Only (Recommended for testing)**
1. Open `benchx_download_data.md`
2. Download **SIIM only** (Section 1 - ~30 minutes)
3. Skip to Step 7 and run SIIM only

**Option B: Full Evaluation - All 4 Datasets**
1. Open `benchx_download_data.md`
2. Follow download instructions for all 4 datasets
3. **Order:** SIIM (30 min) → RSNA (1 hr) → VinDr (30 min + credential wait) → NIH (2 hrs)

**Total download time:** 2-4 hours
**Total size:** ~150 GB

**Important:** VinDr-CXR requires PhysioNet credentialed access (1-2 day approval).

---

### Step 7: Run Evaluation

**Option A: Quick Test - SIIM Only**
```batch
cd C:\Users\aya.alaswad\remote\BenchX
conda activate benchx
python bin/train.py configs/classification/siim/sharp.yml
```
**Time:** ~30-60 minutes
**Output:** `D:\experiments\benchx_results\siim_sharp\`

**Option B: Full Evaluation - All 4 Datasets**
```batch
cd C:\Users\aya.alaswad\remote\MyReasearch
benchx_run_all.bat
```
**Time:** ~8-12 hours GPU time
**Output:** `D:\experiments\benchx_results\*\`

---

### Step 8: Extract Results

**After each dataset finishes, get AUROC:**

```batch
cd D:\experiments\benchx_results\siim_sharp
type metrics.csv | findstr "val_auroc"
```

**Or use the summary from `benchx_run_all.bat` output** (it extracts AUROC automatically after each dataset).

---

## Expected Results Format

| Dataset | SHARP AUROC | MGCA AUROC | Best Baseline |
|---------|-------------|------------|---------------|
| SIIM    | ____%       | ____%      | ____%         |
| RSNA    | ____%       | ____%      | ____%         |
| VinDr   | ____%       | ____%      | ____%         |
| NIH     | ____%       | ____%      | ____%         |

**Baseline numbers:** Get from BenchX paper (Zhou et al., NeurIPS 2024)

---

## Troubleshooting

### "Conda environment not found"
```batch
benchx_setup.bat
```

### "SHARP model not found"
```batch
benchx_integrate_sharp.bat
```

### "Checkpoint not found"
Check that `D:\experiments\exp3_hardneg\p3_best.pt` exists.

### "CUDA out of memory"
Reduce batch size in config files:
```yaml
training:
  batch_size: 16  # was 32
```

### Data download fails
See `benchx_download_data.md` for alternative download sources (Kaggle, HuggingFace mirrors).

---

## After BenchX Completes

### Resume RadDINO Training

```batch
cd C:\Users\aya.alaswad\remote\MyReasearch
run_raddino_exp3_hardneg.bat
```

RadDINO will auto-resume from `D:\experiments\exp_raddino_hardneg\p3_last.pt`

---

## File Structure

```
C:\Users\aya.alaswad\remote\
├── MyReasearch\
│   ├── benchx_*.bat            # Setup & run scripts
│   ├── benchx_*.py             # SHARP model wrapper
│   ├── benchx_config_*.yml     # Dataset configs
│   └── benchx_*.md             # Documentation
├── BenchX\                      # (created by benchx_setup.bat)
│   ├── models\sharp.py         # (copied from MyReasearch)
│   ├── configs\classification\ # (configs copied here)
│   └── bin\train.py            # BenchX training script
└── D:\
    ├── datasets\                # Downloaded datasets
    │   ├── rsna-pneumonia\
    │   ├── siim-pneumothorax\
    │   ├── vindr-cxr\
    │   └── nih-chestxray14\
    └── experiments\
        └── benchx_results\      # Results output
            ├── rsna_sharp\
            ├── siim_sharp\
            ├── vindr_sharp\
            └── nih_sharp\
```

---

## Timeline

**Day 1:**
- Morning: Setup + integrate + test (~30 min)
- Afternoon: Download SIIM + RSNA (2 hrs)
- Evening: Run SIIM + RSNA (3 hrs GPU)

**Day 2:**
- Morning: Download VinDr + NIH (2 hrs)
- Afternoon: Run VinDr + NIH (6 hrs GPU)
- Evening: Extract results, compare to baselines

**Total:** 1-2 days wall time

---

## What This Achieves

**For Your Paper:**
- Validates SHARP's image representations on standard benchmarks
- Direct comparison to 9 published vision-language methods
- Shows SHARP isn't just good at report generation (Stage 2), but also learns strong visual features (BenchX)

**For Supervisor:**
- Addresses request to see "where SHARP stands from other benchmarks"
- Complements retrieval (R@1) and clinical metrics (CheXbert F1)
- Standard evaluation protocol (BenchX is NeurIPS 2024 benchmark)

**For Rebuttal:**
- Robustness check: SHARP works on diverse downstream tasks
- Fair comparison: Same protocol as baselines
- Publication-quality results: BenchX is peer-reviewed benchmark

---

## Quick Reference

| Command | Purpose | Time |
|---------|---------|------|
| `benchx_setup.bat` | Clone repo + create env | 10 min |
| `benchx_integrate_sharp.bat` | Install SHARP | 1 min |
| `benchx_test.bat` | Verify setup | 1 min |
| `benchx_run_all.bat` | Run all 4 datasets | 8-12 hrs |

**Minimum viable test:** SIIM only (~1 hour total)
**Full evaluation:** All 4 datasets (~1-2 days)

---

**Status:** READY TO RUN
**Next:** Pull from GitHub and run `benchx_setup.bat`
