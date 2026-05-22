# Quick Start - Automatic Pipeline (Close and Forget!)

This guide is for running EVERYTHING automatically so you can close the remote desktop.

## One-Time Setup (Do Once)

### 1. Install Dependencies
```bash
pip install f1chexbert==0.0.2 transformers==4.43.3 lightning==2.6.1 dlhpcstarter==0.1.4 bert-score==0.3.13 radgraph==0.1.18 pycocoevalcap==1.2 nltk==3.8.1 rouge-score pandas
```

### 2. Download CheXbert (~438 MB)
```bash
mkdir -p checkpoints\stanford\chexbert
cd checkpoints\stanford\chexbert
```
Download from: https://github.com/stanfordmlgroup/CheXbert#checkpoint-download
Save as: `chexbert.pth`

### 3. Pull Latest Code
```bash
cd C:\Users\aya.alaswad\remote
git pull
```

---

## Run Everything Automatically

### Step 1: Wait for Exp4 Stage 1 to Finish

Check if ready:
```bash
dir D:\experiments\exp4_large_batch\p3_best.pt
```

If you see the file, you're ready!

### Step 2: Launch Automatic Pipeline

```bash
cd C:\Users\aya.alaswad\remote\stage2_training
RUN_EVERYTHING_AUTOMATIC.bat
```

**That's it!** The script will:
1. Train all 4 experiments (2 hours)
2. Test all 4 experiments (30 min)
3. Extract all results (1 min)

**Total: ~2.5 hours**

### Step 3: Close Remote Desktop

You can safely close the remote desktop window! Everything runs in the background.

### Step 4: Come Back Later

After 2-3 hours, reconnect and check results:

```bash
cd C:\Users\aya.alaswad\remote\stage2_training

# View summary
type logs\extract_results.txt

# View per-condition results
type logs\per_condition_analysis.txt

# View full results
notepad results_all_metrics.json
notepad results_per_condition.csv
```

---

## What Gets Created

After the pipeline completes, you'll have:

### Training Logs
- `logs\exp1_train.log` - Full training log for exp1
- `logs\exp2_train.log` - Full training log for exp2
- `logs\exp3_train.log` - Full training log for exp3
- `logs\exp4_train.log` - Full training log for exp4

### Testing Logs
- `logs\exp1_test.log` - Full testing log for exp1
- `logs\exp2_test.log` - Full testing log for exp2
- `logs\exp3_test.log` - Full testing log for exp3
- `logs\exp4_test.log` - Full testing log for exp4

### Results Files
- `results_all_metrics.json` - All metrics for all experiments
- `results_per_condition.csv` - Per-condition F1 for 14 conditions
- `logs\extract_results.txt` - Human-readable summary
- `logs\per_condition_analysis.txt` - Per-condition summary
- `logs\master_log.txt` - Timeline of entire pipeline

---

## Quick Results Preview

After completion, quickly check CheXbert F1:

```bash
cd C:\Users\aya.alaswad\remote\stage2_training
type logs\extract_results.txt | findstr "CheXbert F1"
```

You should see something like:
```
Baseline (bi, batch=32)          | 0.3032
Paired Sampling (100% co-pos)    | 0.27XX (worse as expected)
Full SHARP (hard neg 60%)        | 0.31XX (better?)
Large Batch (batch=512)          | 0.32XX (best?)
```

---

## For Your Paper Rebuttal

Use these files:
- **Overall CheXbert F1**: `logs\extract_results.txt`
- **Per-condition F1** (Fracture, Lung Lesion, Consolidation): `results_per_condition.csv`
- **All metrics**: `results_all_metrics.json`

You now have the actual downstream performance numbers the reviewers asked for!

---

## Troubleshooting

### Pipeline stops unexpectedly
Check `logs\master_log.txt` to see where it stopped.

### CUDA out of memory
The script should handle this automatically, but if it crashes:
- Check GPU usage: `nvidia-smi`
- Make sure no other processes are using GPU

### One experiment fails
Check individual log files (e.g., `logs\exp1_train.log`) for error messages.

### Need to restart
If you need to restart after a failure:
1. Delete the `.done` files: `del logs\*.done`
2. Re-run: `RUN_EVERYTHING_AUTOMATIC.bat`

---

## Timeline

- **Now**: Setup (one-time, ~10 min)
- **+5 min**: Launch automatic pipeline
- **+2.5 hours**: Everything done automatically!
- **Next day**: Write rebuttal with results

**Total hands-on time: 15 minutes**
**Total waiting time: 2.5 hours (remote desktop can be closed)**
