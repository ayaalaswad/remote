# Quick Commands Reference

## Check Exp #4 v2 Status

```cmd
REM Watch training live
powershell Get-Content D:\experiments\exp4_v2_large_batch_PROPER\training.log -Wait -Tail 10

REM See current progress
type D:\experiments\exp4_v2_large_batch_PROPER\training.log | findstr "Step" | more

REM Check R@1 over time
type D:\experiments\exp4_v2_large_batch_PROPER\training.log | findstr "R@1"
```

**Current Status (as of 2026-05-26):**
- Step: 23,938 / 100,000 (24%)
- R@1: 8.9% (excellent! beating baseline 6.61%)
- Time elapsed: ~40 hours
- Estimated remaining: ~127 hours (~5.3 days)

---

## Check Stage 2 Training Logs

```cmd
REM Exp #1 training log
type C:\Users\aya.alaswad\remote\stage2_training\logs\exp1_train.log

REM Exp #3 training log
type C:\Users\aya.alaswad\remote\stage2_training\logs\exp3_train.log

REM Open in notepad
notepad C:\Users\aya.alaswad\remote\stage2_training\logs\exp1_train.log
```

---

## File Locations

### Preprocessing Output (Created Successfully)
```
D:\datasets\mimic-cxr-jpg\mimic_cxr_sectioned\mimic_cxr_sectioned.csv (153.6 MB)
D:\datasets\mimic_cxr_merged\splits_reports_metadata.csv (401.3 MB)
```

### MIMIC-CXR Original Files (Actual Location)
```
D:\datasets\mimic-cxr-jpg\mimic-cxr-2.0.0-split.csv.gz
D:\datasets\mimic-cxr-jpg\mimic-cxr-2.0.0-metadata.csv.gz
D:\datasets\mimic-cxr-jpg\files\p10\p10000032\s50414267\02aa804e-...
D:\datasets\mimic-cxr-reports\reports\files\
```

### CXRMate Expected Structure (Created via Junction)
```
D:\datasets\physionet.org\files\mimic-cxr-jpg\2.0.0\files\  -> junction to D:\datasets\mimic-cxr-jpg\files\
D:\datasets\physionet.org\files\mimic-cxr-jpg\2.0.0\mimic-cxr-2.0.0-split.csv.gz
D:\datasets\physionet.org\files\mimic-cxr-jpg\2.0.0\mimic-cxr-2.0.0-metadata.csv.gz
```

### Stage 1 Checkpoints
```
D:\experiments\exp1_baseline\p3_best.pt (6.61% R@1)
D:\experiments\exp3_full_sharp\p3_best.pt (6.21% R@1)
D:\experiments\exp4_v2_large_batch_PROPER\p3_best.pt (training...)
```

---

## Common Tasks

### Navigate to project
```cmd
cd C:\Users\aya.alaswad\remote
```

### Pull latest code
```cmd
git pull
```

### Check preprocessing status
```cmd
dir D:\datasets\mimic-cxr-jpg\mimic_cxr_sectioned\
dir D:\datasets\mimic_cxr_merged\
```

### Open logs folder
```cmd
explorer C:\Users\aya.alaswad\remote\stage2_training\logs
```

---

## Git Commands

```cmd
REM Check status
git status

REM Pull latest
git pull

REM View recent commits
git log --oneline -5
```

---

## Troubleshooting

### Check if CUDA/GPU is working
```cmd
python -c "import torch; print(f'CUDA: {torch.cuda.is_available()}, GPU: {torch.cuda.get_device_name(0)}')"
```

### Check Python packages
```cmd
pip list | findstr "lightning torch transformers"
```

### Check disk space
```cmd
dir D:\ | findstr "bytes free"
```
