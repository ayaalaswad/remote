# Stage 2 Setup Instructions (Remote Desktop)

Follow these steps on your remote desktop (C:\Users\aya.alaswad\remote) to set up Stage 2 training.

## Step 1: Pull Latest Code

```bash
cd C:\Users\aya.alaswad\remote
git pull
```

This will download the `stage2_training/` folder with all configs and scripts.

## Step 2: Install Python Dependencies

```bash
pip install f1chexbert==0.0.2
pip install transformers==4.43.3
pip install lightning==2.6.1
pip install dlhpcstarter==0.1.4
pip install bert-score==0.3.13
pip install radgraph==0.1.18
pip install pycocoevalcap==1.2
pip install nltk==3.8.1
pip install rouge-score
pip install pandas
```

Or install from requirements file (if you have one):
```bash
pip install -r requirements.txt
```

## Step 3: Download CheXbert Checkpoint

### Option A: Using wget (if available)

```bash
mkdir -p checkpoints\stanford\chexbert
cd checkpoints\stanford\chexbert
wget https://stanfordmedicine.box.com/shared/static/c5hxb8p78v6q33b0pxai32nqk6hd62jl.pth -O chexbert.pth
cd ..\..\..
```

### Option B: Manual Download

1. Go to: https://github.com/stanfordmlgroup/CheXbert#checkpoint-download
2. Download `chexbert.pth` from the Stanford Box link
3. Place it at: `C:\Users\aya.alaswad\remote\checkpoints\stanford\chexbert\chexbert.pth`

### Verify Download

```bash
dir checkpoints\stanford\chexbert\chexbert.pth
```

You should see a file around 438 MB.

## Step 4: Copy CXRMate Code from lrrg Repository

You need the CXRMate code from your lrrg repository. Copy it to the remote directory:

```bash
# If you have lrrg repo locally:
xcopy /E /I C:\path\to\lrrg\cxrmate C:\Users\aya.alaswad\remote\cxrmate

# Or clone the lrrg repo and copy cxrmate folder
```

Alternatively, if the cxrmate code is already in your remote repo, skip this step.

## Step 5: Verify Directory Structure

Your directory should look like this:

```
C:\Users\aya.alaswad\remote\
├── stage2_training\              # NEW - just pulled from git
│   ├── configs\
│   │   ├── exp1_baseline.yaml
│   │   ├── exp2_paired.yaml
│   │   ├── exp3_full.yaml
│   │   └── exp4_large.yaml
│   ├── logs\
│   ├── run_all_experiments.bat
│   ├── run_all_tests.bat
│   ├── extract_results.py
│   ├── per_condition_analysis.py
│   └── README.md
│
├── cxrmate\                      # CXRMate code
│   ├── modules\
│   ├── tools\
│   └── ...
│
├── checkpoints\                  # Checkpoints
│   └── stanford\chexbert\chexbert.pth
│
├── datasets\                     # MIMIC-CXR data
│   └── mimic_cxr_merged\
│       └── splits_reports_metadata.csv
│
└── experiments\                  # Stage 1 results (already exists)
    ├── exp1_baseline\p3_best.pt
    ├── exp2_paired_fixed\p3_best.pt
    ├── exp3_full_sharp\p3_best.pt
    └── exp4_large_batch\p3_best.pt  # Will be ready soon
```

## Step 6: Wait for Exp4 to Complete

Check if Exp #4 Stage 1 training is done:

```bash
dir D:\experiments\exp4_large_batch\p3_best.pt
```

If you see the file, you're ready to start!

## Step 7: Run Stage 2 Training

Once Exp #4 is done:

```bash
cd C:\Users\aya.alaswad\remote\stage2_training
run_all_experiments.bat
```

This will train all 4 experiments sequentially (~8 hours total).

## Step 8: Run Testing

After training completes:

```bash
run_all_tests.bat
```

This will evaluate all 4 experiments (~2 hours total).

## Step 9: Extract Results

```bash
python extract_results.py
python per_condition_analysis.py
```

This will generate:
- `results_all_metrics.json` - All metrics for all experiments
- `results_per_condition.csv` - Per-condition F1 scores

## Troubleshooting

### CheXbert checkpoint not found

```
ERROR: The CheXbert checkpoint does not exist at checkpoints/stanford/chexbert/
```

**Solution**: Follow Step 3 to download chexbert.pth

### CUDA out of memory

**Solution**: Edit config files, change `mbatch_size: 8` to `mbatch_size: 4`

### Module 'dlhpcstarter' not found

**Solution**: `pip install dlhpcstarter==0.1.4`

### Missing MIMIC-CXR data

**Solution**: Ensure `datasets/mimic_cxr_merged/splits_reports_metadata.csv` exists

### Config file path errors

**Solution**: Make sure you run scripts from `C:\Users\aya.alaswad\remote\stage2_training\` directory

## Expected Timeline

- **Now**: Wait for Exp #4 to finish (~few hours remaining)
- **Day 1**: Run `run_all_experiments.bat` (~8 hours)
- **Day 2**: Run `run_all_tests.bat` (~2 hours)
- **Day 2**: Run `extract_results.py` and `per_condition_analysis.py` (~10 minutes)
- **Day 3**: Write paper rebuttal with CheXbert F1 results

## Questions?

If you encounter any issues, check:
1. All dependencies installed (Step 2)
2. CheXbert checkpoint downloaded (Step 3)
3. Directory structure correct (Step 5)
4. Running from correct directory (stage2_training/)

Good luck!
