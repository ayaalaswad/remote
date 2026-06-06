# BenchX SHARP - 3 Data Regimes (1%, 10%, 100%)

## Overview

BenchX evaluates MedVLP methods on **data efficiency** across 3 training regimes:

| Split | Samples | File | Time | Purpose |
|-------|---------|------|------|---------|
| **1%** | 186 | `sharp_rsna_1pct.yml` | 20-30 min | Low-data regime |
| **10%** | ~1,800 | `sharp_rsna_10pct.yml` | 1-1.5 hrs | **Most meaningful** |
| **100%** | ~18,000 | `sharp_rsna_100pct.yml` | 2-3 hrs | Full data |

## Key Insight from User

> "train_10 is the most meaningful split for a pretraining paper. It's large enough to be reliable but small enough that pretraining advantages are visible. Full training (train) is where all methods converge and differences shrink."

## Configuration Differences

All 3 configs use **identical MGCA protocol** except:

### Only Changes Between Configs

```yaml
# 1% Split
name: SHARP_1pct
ckpt_dir: experiments/classification/rsna/SHARP_1pct/
split: "train_1"
epochs: 30
eval_start: 5
eval_interval: 2

# 10% Split
name: SHARP_10pct
ckpt_dir: experiments/classification/rsna/SHARP_10pct/
split: "train_10"
epochs: 30
eval_start: 5
eval_interval: 2

# 100% Split
name: SHARP_100pct
ckpt_dir: experiments/classification/rsna/SHARP_100pct/
split: "train"
epochs: 50              # More epochs for full data
eval_start: 10          # Later eval start
eval_interval: 5        # Less frequent eval
```

### Shared Protocol (Matches MGCA Exactly)

```yaml
trainer:
  optimizer: SGD
  optim_params:
    lr: 1e-2
    momentum: 0.9
  batch_size: 64
  early_stop: 10
  # ... all other params identical
```

## How to Run

### Option 1: All 3 Splits (Full BenchX Comparison)

```cmd
cd C:\Users\aya.alaswad\remote
git pull origin main
run_rsna_all_splits.bat
```

Total time: **3-4 hours** (runs sequentially)

### Option 2: 10% Only (Time-Pressured)

```cmd
cd C:\Users\aya.alaswad\remote
git pull origin main
run_rsna_10pct_only.bat
```

Time: **1-1.5 hours** (most meaningful result)

### Option 3: Manual Individual Runs

```cmd
# Run 1% split
copy sharp_rsna_1pct.yml BenchX\configs\classification\RSNA\sharp.yml /Y
cd BenchX && python bin/train.py configs/classification/RSNA/sharp.yml

# Run 10% split
cd ..
copy sharp_rsna_10pct.yml BenchX\configs\classification\RSNA\sharp.yml /Y
cd BenchX && python bin/train.py configs/classification/RSNA/sharp.yml

# Run 100% split
cd ..
copy sharp_rsna_100pct.yml BenchX\configs\classification\RSNA\sharp.yml /Y
cd BenchX && python bin/train.py configs/classification/RSNA/sharp.yml
```

## Results Location

Each split saves to separate directory (no overwrites):

```
BenchX/experiments/classification/rsna/
├── SHARP_1pct/
│   └── [AUROC]_[epoch]_42.pth
├── SHARP_10pct/
│   └── [AUROC]_[epoch]_42.pth
└── SHARP_100pct/
    └── [AUROC]_[epoch]_42.pth
```

## Expected Outcomes

**Hypothesis (based on pretraining theory):**
- **1% split:** SHARP advantage most visible (limited downstream data)
- **10% split:** Clear SHARP advantage, statistically reliable
- **100% split:** Smaller advantage (methods converge with more data)

**Compare to BenchX Table 2:**
```
Method     | 1%   | 10%  | 100%
-----------|------|------|------
MGCA-ViT   | ?    | ?    | ?
MRM        | ?    | ?    | ?
SHARP      | TBD  | TBD  | TBD
```

## Recommendation

**If time-pressured:** Run `run_rsna_10pct_only.bat` first
**For full comparison:** Run `run_rsna_all_splits.bat` overnight

The 10% split is where SHARP's pretraining advantages should be most clear and statistically reliable.
