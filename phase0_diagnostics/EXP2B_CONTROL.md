# Exp #2b: 20k Random Control Experiment

**Purpose**: Isolate the dataset size confound in Exp #2's failure.

**Critical Question**: Did Exp #2 collapse due to:
- (A) Forced 100% co-positive pairing? OR
- (B) 3× smaller training set (20k vs 60k+ files)?

**This experiment answers it definitively.**

---

## Experiment Design

**Exp #2b Configuration**:
- ✅ Same as Exp #1 (baseline)
- ✅ Random sampling (NO paired sampling)
- ✅ Bidirectional loss
- ✅ Hard negatives: 0%
- ✅ Batch size: 32
- ✅ **ONLY DIFFERENCE: Limit to 20k training files** (same as Exp #2's manifest)

**Expected Results**:

| Scenario | R@1 Result | Interpretation |
|----------|-----------|----------------|
| **R@1 ≈ 6.6%** | Similar to baseline | → Dataset size NOT the issue → Forced pairing IS the cause |
| **R@1 ≈ 0.8%** | Tanks like Exp #2 | → Dataset size IS the issue → Can't blame pairing alone |
| **R@1 ≈ 4-5%** | Between baseline and Exp #2 | → Both contribute (confounded) |

---

## Implementation

### Option 1: Add --max_train_files Parameter

Modify `train_sharp_large_batch.py` to accept this argument:

```python
parser.add_argument('--max_train_files', type=int, default=None,
                    help='Limit number of training files (for ablations)')
```

Then in the training data loading section:

```python
# After loading train_files
if args.max_train_files is not None:
    train_files = random.Random(42).sample(train_files, min(args.max_train_files, len(train_files)))
    print(f"Limited to {len(train_files):,} training files")
```

**Run command**:
```bash
python train_sharp_large_batch.py \
  --scene_dir D:\datasets\mimic-ext-cxr-qba\scene_graphs\scene_data \
  --image_dir D:\datasets\mimic-cxr-jpg \
  --split_csv D:\datasets\mimic-cxr-jpg\mimic-cxr-2.0.0-split.csv.gz \
  --output_dir D:\experiments\exp2b_20k_random \
  --batch_size 32 \
  --bidirectional \
  --hard_neg_max_frac 0.0 \
  --max_train_files 20000
```

### Option 2: Manually Sample Files

Create a temporary split CSV with only 20k training files:

```python
# create_20k_split.py
import pandas as pd
import random

# Load original split
df = pd.read_csv('D:/datasets/mimic-cxr-jpg/mimic-cxr-2.0.0-split.csv.gz')

# Sample 20k from train set
train_df = df[df['split'] == 'train']
sampled_train = train_df.sample(n=20000, random_state=42)

# Combine with val/test
val_df = df[df['split'] == 'validate']
test_df = df[df['split'] == 'test']
new_df = pd.concat([sampled_train, val_df, test_df])

# Save
new_df.to_csv('D:/datasets/mimic-cxr-jpg/mimic-cxr-2.0.0-split-20k.csv', index=False)
```

Then run with the new split:
```bash
python train_sharp_large_batch.py \
  --split_csv D:\datasets\mimic-cxr-jpg\mimic-cxr-2.0.0-split-20k.csv \
  ...
```

---

## Timeline

- **GPU Time**: ~12 hours (same as Exp #1)
- **Cost**: Minimal (1 quick experiment)
- **Value**: Turns soft claim into hard claim

---

## Decision Matrix

### After Exp #2b Completes:

#### Scenario A: R@1 ≈ 6.6% (same as baseline)

**Conclusion**: ✓ Dataset size is NOT the problem

**Rebuttal Language**:
> "To isolate the effect of forced pairing from dataset size, we ran a control experiment with 20k random files (matching Exp #2's manifest size but without pairing). This control achieved R@1=6.XX%, similar to the full baseline (6.61%), confirming that the 20k→60k dataset difference does not explain the collapse. Therefore, the 87.7% performance drop in Exp #2 is attributable to the forced 100% co-positive constraint, which eliminates batch diversity and reduces the task to trivial pair memorization."

**Next Steps**:
- Update FINDINGS.md with conclusive evidence
- Use strong language in rebuttal
- No further controls needed

---

#### Scenario B: R@1 ≈ 0.8% (tanks like Exp #2)

**Conclusion**: ✗ Dataset size IS a major factor

**Rebuttal Language**:
> "Exp #2's collapse was confounded by reduced dataset size (20k files vs 60k+ baseline). A 20k random-sampling control also achieved R@1=0.XX%, indicating that the reduced manifest size is the primary cause. While forced pairing may contribute, we cannot isolate its effect without matching dataset sizes. Our main SHARP results (Exp #3, #4) use the full training set and demonstrate effective multi-positive learning."

**Next Steps**:
- Don't blame forced pairing in rebuttal
- Focus on Exp #3 and #4 results
- Acknowledge Exp #2 as inconclusive

---

#### Scenario C: R@1 ≈ 4-5% (between baseline and Exp #2)

**Conclusion**: ~ Both factors contribute

**Rebuttal Language**:
> "Exp #2 (20k paired, R@1=0.81%) and a 20k random control (R@1=4.XX%) both underperform the full baseline (60k+ random, R@1=6.61%). The dataset size reduction accounts for ~2 percentage points of loss, while forced pairing accounts for an additional ~3-4 points, suggesting both factors contribute. Importantly, even with matched dataset size, forced pairing significantly harms performance, supporting our claim that diversity matters more than guaranteed co-positives."

**Next Steps**:
- Use nuanced language in rebuttal
- Quantify both contributions
- Still supports "diversity matters" thesis

---

## Recommended Action

**RUN THIS EXPERIMENT** (~12 hours GPU time)

**Why**:
1. Cheap (1 experiment, not 3-4 days like Stage 2)
2. Decisive (resolves the confound)
3. Strengthens rebuttal (hard claim vs soft claim)

**When**:
- Can run NOW (doesn't depend on Exp #4)
- Runs independently of other experiments

**Priority**: HIGH (do before Stage 2 if possible)

---

## Integration with Phase 0 Findings

### Current Status (Without Exp #2b):

**FINDINGS.md claims**:
> "Forcing 100% co-positive rate collapsed performance by 87.7%"

**Problem**: Confounded by dataset size (20k vs 60k+)

**Reviewer response**: "How do you know it wasn't the smaller dataset?"

### After Exp #2b:

**If Scenario A (R@1 ≈ 6.6%)**:
> "We controlled for dataset size with a 20k random baseline (R@1=6.XX%). The collapse is due to forced pairing, not dataset size."

**If Scenario B (R@1 ≈ 0.8%)**:
> "A 20k random control also collapsed, indicating dataset size is the primary factor. Exp #2 is inconclusive regarding forced pairing."

**If Scenario C (R@1 ≈ 4-5%)**:
> "Both factors contribute: dataset size reduces performance by ~2pp, forced pairing by an additional ~3-4pp."

---

## Cost-Benefit Analysis

| Option | Cost | Benefit | Risk |
|--------|------|---------|------|
| **Run Exp #2b** | 12h GPU | Hard claim, conclusive | Might show confound |
| **Skip Exp #2b** | 0h | Fast | Soft claim, reviewer skepticism |

**Recommendation**: RUN EXP #2B

The 12 hours is worth it to avoid a reviewer questioning your causal attribution.

---

## Files to Create/Modify

1. ✅ `run_exp2b_20k_random.bat` - Created
2. ⏳ `train_sharp_large_batch.py` - Add `--max_train_files` parameter
3. ⏳ Run Exp #2b
4. ⏳ Update `FINDINGS.md` with conclusive results

---

**Status**: Ready to run after adding `--max_train_files` parameter to training script.
