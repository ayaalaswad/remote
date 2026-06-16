# SIIM Fix Plan - Complete Guide

## 🔍 Problem Diagnosis

**Issue:** SIIM validation set has NO positive examples
- Training loss collapsed to 0.00
- AUROC became NaN (can't calculate without both classes)
- Model learned to predict "negative" for everything
- Validation accuracy: 100% (on all-negative val set)
- Test F1: 0-2.35% (fails on real test with positives)

**Root Cause:** Data splitting not stratified - validation got only negative examples

---

## 🔧 Fix Steps

### Step 1: Diagnose Current Splits

**On remote desktop:**
```cmd
cd C:\Users\aya.alaswad\remote
git pull origin main
python diagnose_siim_splits.py
```

This will show:
- Total samples and label distribution
- How splits are currently divided
- Which splits have no positives

### Step 2: Fix the Splits with Stratification

**Run:**
```cmd
python fix_siim_splits.py
```

This will:
- Load the SIIM CSV
- Create stratified train (70%), val (15%), test (15%) splits
- Ensure each split has both positive and negative examples
- Save fixed CSV to:
  - `siim_labels_fixed.csv` (original location)
  - `BenchX/datasets/SIIM/siim_labels.csv` (BenchX location)

**Expected output:**
```
train:
  Total: ~7800 (70%)
  Positive: ~22%
  Negative: ~78%

val:
  Total: ~1700 (15%)
  Positive: ~22%  <-- SHOULD NOT BE 0%!
  Negative: ~78%

test:
  Total: ~1700 (15%)
  Positive: ~22%
  Negative: ~78%
```

### Step 3: Verify BenchX Will Use Fixed Splits

**Check how BenchX dataset class reads splits:**

The config uses:
- `split: "train_1"` (for 1% of training data)
- `split: "train_10"` (for 10% of training data)
- `split: "train_100"` (for 100% of training data)

BenchX creates these by:
1. Reading the base `train` split from CSV
2. Sampling 1%, 10%, or 100% of it
3. Using `val` split for validation (FROM CSV)
4. Using `test` split for final evaluation

**The issue:** If the original CSV had bad splits, all percentages inherit the problem.

### Step 4: Retrain SIIM (All Splits)

**After fixing splits, retrain:**

```cmd
cd C:\Users\aya.alaswad\remote\BenchX

# Train 1%
python bin/train.py configs/classification/SIIM/sharp_siim_1pct.yml

# Train 10%
python bin/train.py configs/classification/SIIM/sharp_siim_10pct.yml

# Train 100%
python bin/train.py configs/classification/SIIM/sharp_siim_100pct.yml
```

**Expected behavior after fix:**
- Loss should NOT collapse to 0.00
- AUROC should be a real number (not NaN)
- Validation accuracy should NOT be 100%
- Model should make some positive predictions

### Step 5: Verify Training

**Watch for these signs training is working:**
```
Epoch 5:
  Loss: ~0.4-0.6 (NOT 0.00)
  AUROC: 0.55-0.65 (NOT NaN)
  Accuracy: 75-85% (NOT 100%)
```

**If you see:**
- Loss = 0.00 → STILL BROKEN
- AUROC = NaN → STILL BROKEN
- Accuracy = 100% → STILL BROKEN

---

## 📊 Expected Results After Fix

### SIIM Should Perform Like RSNA (scaled down)

**RSNA Results (reference):**
| Split | AUROC | F1 |
|-------|-------|-----|
| 1% | 0.6900 | 24.24% |
| 10% | 0.7514 | 36.65% |
| 100% | 0.7923 | 45.87% |

**SIIM Expected (after fix):**
| Split | AUROC | F1 (Expected) |
|-------|-------|---------------|
| 1% | 0.6037 | ~15-25% |
| 10% | 0.6244 | ~25-35% |
| 100% | 0.6675 | ~35-45% |

SIIM will likely be lower than RSNA because:
- Pneumothorax is harder to detect than pneumonia
- Smaller dataset
- More subtle visual features

**But it should NOT be 0-2% F1!**

---

## 🔍 Alternative: Check BenchX Dataset Code

If the fix_siim_splits.py doesn't work, we may need to check how BenchX's `SIIM_Pneumothorax_Dataset` class creates splits.

**Find the dataset class:**
```cmd
cd C:\Users\aya.alaswad\remote\BenchX
grep -r "class SIIM_Pneumothorax_Dataset" unifier/
```

**Check if it:**
1. Reads split column from CSV correctly
2. Does stratified sampling for train_1, train_10, train_100
3. Validates that val/test have both classes

---

## 🎯 Backup Plan: Manual Split Creation

If automated fix doesn't work, create splits manually:

```python
import pandas as pd
from sklearn.model_selection import train_test_split

# Load data
df = pd.read_csv("siim_labels.csv")

# Get indices for each class
pos_idx = df[df['label'] == 1].index
neg_idx = df[df['label'] == 0].index

# Split positives: 70% train, 15% val, 15% test
pos_train_val, pos_test = train_test_split(pos_idx, test_size=0.15, random_state=42)
pos_train, pos_val = train_test_split(pos_train_val, test_size=0.176, random_state=42)

# Split negatives: same proportions
neg_train_val, neg_test = train_test_split(neg_idx, test_size=0.15, random_state=42)
neg_train, neg_val = train_test_split(neg_train_val, test_size=0.176, random_state=42)

# Combine
train_idx = list(pos_train) + list(neg_train)
val_idx = list(pos_val) + list(neg_val)
test_idx = list(pos_test) + list(neg_test)

# Assign splits
df['split'] = 'train'
df.loc[val_idx, 'split'] = 'val'
df.loc[test_idx, 'split'] = 'test'

# Verify
print("Train:", (df[df['split']=='train']['label']==1).sum(), "positives")
print("Val:", (df[df['split']=='val']['label']==1).sum(), "positives")
print("Test:", (df[df['split']=='test']['label']==1).sum(), "positives")

# ALL THREE SHOULD BE > 0!

df.to_csv("siim_labels_fixed.csv", index=False)
```

---

## ✅ Success Criteria

**After fixing and retraining, you should see:**

1. **Training logs show normal behavior:**
   - Loss: 0.4-0.6 (decreasing over time)
   - AUROC: 0.55-0.70 (improving over time)
   - Accuracy: 75-85% (not 100%)

2. **Validation has both classes:**
   - AUROC is a real number (not NaN)
   - Model makes some positive predictions

3. **Test F1 is reasonable:**
   - SIIM 1%: F1 > 15%
   - SIIM 10%: F1 > 25%
   - SIIM 100%: F1 > 35%

4. **Conservative but not broken:**
   - Specificity: 85-95% (OK)
   - Recall: 15-40% (OK for conservative model)
   - F1: NOT 0-2% (that's broken!)

---

## 📝 Summary

1. **Run:** `python diagnose_siim_splits.py` → See the problem
2. **Run:** `python fix_siim_splits.py` → Fix stratification
3. **Retrain:** All 3 SIIM experiments (1%, 10%, 100%)
4. **Verify:** Training logs show normal loss/AUROC (not 0.00/NaN)
5. **Test:** F1 should be 15-45% (not 0-2%)

**Estimated time:**
- Diagnosis + fix: 10 minutes
- Retraining (3 experiments): 3-6 hours

**Worth it?**
- Yes, if you want SIIM results for the paper
- No, if RSNA alone is sufficient (it matches MGCA!)
