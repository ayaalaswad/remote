# Pre-Flight Check: SIIM Training

## Issues to Verify Before Running

### 1. ✅ Preprocessing Script (VERIFIED - OK)
- Using `preprocess_siim_fixed.py` ✅
- Reads labels from CSV (not filenames) ✅
- Creates stratified splits ✅

### 2. ⚠️ Dataset Class Name (NEEDS CHECK)

**Current config:**
```yaml
proto: SIIM_Dataset
```

**Should be (from troubleshooting docs):**
```yaml
proto: SIIM_Pneumothorax_Dataset
```

**Action:** Check on remote if training starts, or if it crashes with:
```
NameError: name 'SIIM_Dataset' is not defined
```

If it crashes, change all 3 configs:
- `sharp_siim_1pct.yml`
- `sharp_siim_10pct.yml`
- `sharp_siim_100pct.yml`

Change line 10:
```yaml
proto: SIIM_Pneumothorax_Dataset
```

### 3. ✅ Everything Else Matches RSNA (VERIFIED - OK)
- Same checkpoint: `p3_best_timm.pt` ✅
- Same optimizer: SGD ✅
- Same hyperparameters ✅
- Same ViT base config ✅

## What To Watch For During Preprocessing

### Expected Output:
```
Found 12089 images to process
Processing SIIM images: 100%

Reading labels from CSV...
Found CSV: stage_2_train.csv (or train-rle.csv)
Loaded CSV with XXXXX rows

Matched XXXX images to labels
  Positive (pneumothorax): ~20-30%
  Negative (no pneumothorax): ~70-80%

Split sizes:
  train_1 (1%): XX samples (Pos: X, Neg: X)
  train_10 (10%): XXX samples (Pos: XX, Neg: XX)
  train (100%): XXXX samples (Pos: XXX, Neg: XXX)
  val: XXX samples (Pos: XX, Neg: XX)
  test: XXX samples (Pos: XX, Neg: XX)

✓ All split files created
```

### Red Flags:
❌ "Matched 0 images to labels" → CSV format issue
❌ "Positive: 0" or "Negative: 0" → One class missing
❌ "ValueError: The least populated class" → Not enough samples to stratify

## What To Watch For During Training

### First Few Lines Should Show:
```
SIIM_Pneumothorax_Dataset num_samples=XX transforms=[...]
Epoch 1/50: [progress bar]
Train Loss: 0.XXXX
Val AUROC: 0.XXXX
```

### Red Flags:
❌ `NameError: name 'SIIM_Dataset' is not defined` → Fix dataset class name
❌ `RuntimeError: Dataset has 0 samples` → Preprocessing failed
❌ `Val AUROC: nan` → Only one class in validation set

## Quick Fix Commands (If Needed)

### If dataset class name error:
```cmd
cd C:\Users\aya.alaswad\remote

# Fix all 3 configs
powershell -Command "(gc sharp_siim_1pct.yml) -replace 'proto: SIIM_Dataset', 'proto: SIIM_Pneumothorax_Dataset' | Out-File -encoding ASCII sharp_siim_1pct.yml"
powershell -Command "(gc sharp_siim_10pct.yml) -replace 'proto: SIIM_Dataset', 'proto: SIIM_Pneumothorax_Dataset' | Out-File -encoding ASCII sharp_siim_10pct.yml"
powershell -Command "(gc sharp_siim_100pct.yml) -replace 'proto: SIIM_Dataset', 'proto: SIIM_Pneumothorax_Dataset' | Out-File -encoding ASCII sharp_siim_100pct.yml"

# Re-run
run_siim_all_splits.bat
```

### If preprocessing failed:
```cmd
cd C:\Users\aya.alaswad\remote

# Check archive contents
dir C:\Users\aya.alaswad\Downloads\archive

# Re-run preprocessing manually
python preprocess_siim_fixed.py
```

## Decision Point

**Option 1: Let it run and see if dataset class name is OK**
- Preprocessing takes 10-15 min
- If training crashes on dataset class name, fix is quick (1 min)
- Total wasted time: ~15 min max

**Option 2: Stop now and fix dataset class name preemptively**
- Stop current run
- Fix 3 config files
- Re-run from scratch
- Guaranteed to work

**Recommendation:** Let preprocessing finish (already started). If it crashes on dataset class name, it'll crash quickly (within 1 min of training start). Then fix and re-run.

## Post-Training Checks

After 3-4 hours, verify:

1. **Check results exist:**
```cmd
dir C:\Users\aya.alaswad\remote\BenchX\experiments\classification\siim\SHARP_*\*\*.pth
```

2. **Extract F1 scores:**
```cmd
python calculate_f1_scores.py --dataset siim
```

3. **Compare to RSNA:**
- RSNA 10%: F1 = 43.1%
- SIIM 10%: F1 = ???

If SIIM >> RSNA (e.g., SIIM = 65%), then SHARP struggles with RSNA specifically.
If SIIM ≈ RSNA (e.g., SIIM = 45%), then SHARP struggles with binary classification generally.
