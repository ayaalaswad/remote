# Stage 2: CXRMate Fine-Tuning for Reviewer Response

This folder contains all configs and scripts to fine-tune CXRMate using the 4 Stage 1 checkpoints (exp1, exp2, exp3, exp4) and measure downstream CheXbert F1 scores.

## Purpose

**Reviewer Question**: "Does your Stage 1 pretraining actually improve downstream report generation?"

**Your Answer**: Run all 4 checkpoints through CXRMate Stage 2 fine-tuning and compare CheXbert F1 scores.

## Setup on Remote Desktop

### 1. Install Dependencies

```bash
# If not already installed
pip install f1chexbert==0.0.2
pip install transformers==4.43.3
pip install lightning==2.6.1
pip install dlhpcstarter==0.1.4
pip install bert-score==0.3.13
pip install radgraph==0.1.18
pip install pycocoevalcap==1.2
pip install nltk==3.8.1
pip install rouge-score
```

### 2. Download CheXbert Checkpoint

```bash
mkdir -p checkpoints/stanford/chexbert
cd checkpoints/stanford/chexbert
wget https://stanfordmedicine.box.com/shared/static/c5hxb8p78v6q33b0pxai32nqk6hd62jl.pth -O chexbert.pth
cd ../../..
```

**Alternative**: Download manually from https://github.com/stanfordmlgroup/CheXbert#checkpoint-download

### 3. Setup Directory Structure

```
C:\Users\aya.alaswad\remote\
├── stage2_training/                    # This folder
│   ├── configs/                        # Config files for 4 experiments
│   ├── run_all_experiments.bat         # Main training script
│   ├── run_all_tests.bat              # Main testing script
│   └── README.md                       # This file
│
├── cxrmate/                            # CXRMate code (from lrrg repo)
│
├── checkpoints/                        # Checkpoints directory
│   ├── stanford/chexbert/chexbert.pth  # CheXbert checkpoint
│   └── mimic-cxr-tokenizers/           # Tokenizer
│
├── datasets/                           # MIMIC-CXR data
│   └── mimic_cxr_merged/
│       └── splits_reports_metadata.csv
│
└── experiments/                        # Stage 1 checkpoints
    ├── exp1_baseline/p3_best.pt
    ├── exp2_paired_fixed/p3_best.pt
    ├── exp3_full_sharp/p3_best.pt
    └── exp4_large_batch/p3_best.pt
```

## Experiments

| ID | Name | Stage 1 Checkpoint | Expected F1 |
|----|------|--------------------|-------------|
| exp1 | Baseline (bi, batch=32) | D:/experiments/exp1_baseline/p3_best.pt | Baseline |
| exp2 | Paired Sampling (100% co-pos) | D:/experiments/exp2_paired_fixed/p3_best.pt | Lower (diversity issue) |
| exp3 | Full SHARP (hard neg 60%) | D:/experiments/exp3_full_sharp/p3_best.pt | Higher? |
| exp4 | Large Batch (batch=512) | D:/experiments/exp4_large_batch/p3_best.pt | Highest? |

## Quick Start

### Step 1: Copy CXRMate code from lrrg repo

```bash
# On remote desktop
cd C:\Users\aya.alaswad\remote
# Copy the cxrmate folder from your lrrg repository to here
```

### Step 2: Run Training (Fine-tune all 4 experiments)

```bash
cd C:\Users\aya.alaswad\remote\stage2_training
run_all_experiments.bat
```

This will:
- Fine-tune CXRMate with exp1 checkpoint (~2 hours)
- Fine-tune CXRMate with exp2 checkpoint (~2 hours)
- Fine-tune CXRMate with exp3 checkpoint (~2 hours)
- Fine-tune CXRMate with exp4 checkpoint (~2 hours)

**Total time: ~8 hours**

### Step 3: Run Testing (Evaluate all 4 experiments)

```bash
run_all_tests.bat
```

This will:
- Evaluate exp1 on test set (~30 min)
- Evaluate exp2 on test set (~30 min)
- Evaluate exp3 on test set (~30 min)
- Evaluate exp4 on test set (~30 min)

**Total time: ~2 hours**

### Step 4: Extract Results

```bash
python extract_results.py
```

This will create:
- `results_summary.txt` - Overall CheXbert F1 for all 4 experiments
- `results_per_condition.csv` - Per-condition F1 (Fracture, Lung Lesion, Consolidation)
- `results_statistical_tests.txt` - Paired bootstrap confidence intervals

## Expected Output

```
Experiment Results (CheXbert F1):
- exp1_baseline: 0.3032 (baseline)
- exp2_paired:   0.27XX (worse - diversity issue confirmed)
- exp3_full:     0.31XX (better? - hard negatives help)
- exp4_large:    0.32XX (best? - large batch hypothesis)

Statistical Tests:
- exp1 vs exp2: p < 0.001 (exp2 significantly worse)
- exp1 vs exp3: p = 0.0XX
- exp1 vs exp4: p = 0.0XX
```

## For Paper Rebuttal

Use these results to answer reviewers:

**R1**: "Show CheXbert F1 on downstream task"
→ exp1: 0.3032, exp3: 0.31XX, exp4: 0.32XX (p < 0.001)

**R2**: "Show per-condition F1 for Fracture, Lung Lesion, Consolidation"
→ See results_per_condition.csv

**R3**: "Statistical significance?"
→ Paired bootstrap with 10,000 resamples, see results_statistical_tests.txt

## Troubleshooting

### CheXbert checkpoint not found
```
ERROR: The CheXbert checkpoint does not exist at checkpoints/stanford/chexbert/
```
**Fix**: Download chexbert.pth as described in Setup step 2

### CUDA out of memory
**Fix**: Reduce batch size in configs (mbatch_size: 8 → 4)

### Missing MIMIC-CXR data
**Fix**: Ensure datasets/mimic_cxr_merged/splits_reports_metadata.csv exists

## Files in This Folder

- `README.md` - This file
- `configs/exp1_baseline.yaml` - Config for exp1
- `configs/exp2_paired.yaml` - Config for exp2
- `configs/exp3_full.yaml` - Config for exp3
- `configs/exp4_large.yaml` - Config for exp4
- `run_all_experiments.bat` - Train all 4 experiments
- `run_all_tests.bat` - Test all 4 experiments
- `extract_results.py` - Extract and summarize results
- `per_condition_analysis.py` - Per-condition F1 extraction

## Timeline

- **Now**: Wait for exp4 Stage 1 training to finish
- **Day 1**: Run Stage 2 fine-tuning (8 hours)
- **Day 2**: Run testing (2 hours) + extract results (10 min)
- **Day 3**: Write rebuttal with CheXbert F1 numbers

---

**Status**: Ready to run once exp4 Stage 1 completes
