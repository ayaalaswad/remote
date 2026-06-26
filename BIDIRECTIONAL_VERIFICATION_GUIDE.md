# How to Verify Bidirectional Ablation Study

## ❓ Your Question

"How can I make sure if the ablation study is done on bidirectional?"

---

## 📋 What the Paper Claims

According to **paper.tex lines 564-576**:

> **Bidirectional loss ablation.**
> Reviewers noted that ablations (A)--(D) used **unidirectional loss** (image→text)
> while the symmetric baseline employed **bidirectional loss** (image↔text).
> We **re-ran ablation (B)** with **bidirectional multi-positive InfoNCE**.
> Stage 1 pretraining achieved validation **R@1 = 6.61%**
> (vs. 7.02% unidirectional).

**Key claims:**
1. ✓ Original ablations (A-D) used **unidirectional** (image→text only)
2. ✓ Re-ran **ablation (B)** with **bidirectional** (image↔text)
3. ✓ Bidirectional R@1 = **6.61%**
4. ✓ Unidirectional R@1 = **7.02%**
5. ✓ Conclusion: Bidirectional got **lower** R@1 (6.61% < 7.02%)

---

## ✅ How to Verify (3 Methods)

### Method 1: Run Verification Script (Easiest)

**On remote desktop:**

```bash
cd C:\Users\aya.alaswad\remote\MyReasearch
python verify_bidirectional_ablation.py
```

**What it checks:**
- ✓ Which experiments have `"bidirectional": true` in config
- ✓ What R@1 each experiment achieved
- ✓ If results match paper claims (6.61% for bidirectional)

**Expected output:**

```
| Experiment          | Bidirectional | Best R@1 | Matches Paper? |
|---------------------|---------------|----------|----------------|
| exp2_paired         | ✓ Yes         | 6.61%    | ✓ Yes (6.61%)  |
| exp3_hardneg        | ✗ No          | 7.02%    | -              |
```

---

### Method 2: Manual Check in Experiment Directory

**On remote desktop:**

1. **Navigate to experiment:**
   ```bash
   cd D:\experiments\exp2_paired
   # or wherever ablation (B) bidirectional is stored
   ```

2. **Look for config file:**
   ```bash
   type experiment_config.json
   # or
   type args.json
   ```

3. **Check for bidirectional flag:**
   ```json
   {
     "bidirectional": true,    ← Should be true
     ...
   }
   ```

4. **Check R@1 result:**
   - Look at checkpoint filename: `0.0661_23_42.pt` → R@1 = 6.61%
   - Or look at `p3_history.json` for best val_r1
   - Or look at training logs

---

### Method 3: Check Training Code Implementation

**Verify the code actually implements bidirectional:**

```python
# In train_sharp_raddino_v2.py, lines 163-206:

def multi_positive_infonce(img_embs, txt_embs, concept_keys, temperature, bidirectional=False):
    # ... image → text loss ...
    loss_i2t = (-sim_pos_avg_i2t + log_denom_i2t).mean()

    if bidirectional:
        # TEXT → IMAGE direction (transpose similarity matrix)
        n_pos_t2i = pos_mask.sum(dim=0)
        sim_pos_avg_t2i = (sim.T * pos_mask.T).sum(dim=1) / n_pos_t2i
        log_denom_t2i = torch.logsumexp(sim.T, dim=1)
        loss_t2i = (-sim_pos_avg_t2i + log_denom_t2i).mean()

        return (loss_i2t + loss_t2i) / 2  # Average both directions
    else:
        return loss_i2t  # Unidirectional only
```

**✓ Code is correct** - when `bidirectional=True`, it computes both directions and averages them.

---

## 🔍 What to Look For

### Experiment Must Have:

1. **Config file with bidirectional flag:**
   ```json
   "bidirectional": true
   ```

2. **Training completed successfully:**
   - Checkpoint file exists: `p3_best.pt` or similar
   - R@1 result available

3. **R@1 matches paper claim:**
   - Bidirectional experiment: R@1 ≈ 6.61%
   - Unidirectional experiment: R@1 ≈ 7.02%

4. **Training logs confirm bidirectional:**
   - Search logs for "Bidirectional" or "i<->t"
   - Should say: `Loss type: Bidirectional (i<->t)`

---

## 🎯 Expected Experiments

Based on your paper, you should have:

| Experiment | Description | Bidirectional | Expected R@1 |
|------------|-------------|---------------|--------------|
| **Ablation (B)** - Unidirectional | Original run | ✗ No | 7.02% |
| **Ablation (B)** - Bidirectional | Re-run for reviewer | ✓ Yes | 6.61% |

**Ablation (B)** = Multi-positive InfoNCE without hard negatives, no curriculum

---

## ⚠️ Common Issues

### Issue 1: Can't Find Bidirectional Experiment

**Check:**
```bash
# Search for config with bidirectional=true
find D:\experiments -name "*.json" -exec grep -l "bidirectional.*true" {} \;
```

**If not found:**
- The ablation might not have been run yet
- Or it's stored in a different location
- Or the config uses a different format

### Issue 2: R@1 Doesn't Match Paper

**Possible reasons:**
- Different experiment checkpoint (early vs best vs last)
- Different validation set
- Training didn't converge

**Fix:** Check the actual history file or training log for best R@1.

### Issue 3: Unsure Which Experiment is Ablation (B)

**Ablation (B) should be:**
- Multi-positive InfoNCE ✓
- No hard negatives ✗
- No curriculum ✗
- Batch size = 32
- Random sampling (not paired)

**Look for experiment with:**
```json
{
  "hard_neg_max_frac": 0.0,  // No hard negatives
  "batch_size": 32,
  "paired_sampling": false,
  "bidirectional": true     // For the re-run
}
```

---

## 🔧 Quick Verification Checklist

Run on remote desktop:

```bash
# 1. Check if verification script works
cd C:\Users\aya.alaswad\remote\MyReasearch
python verify_bidirectional_ablation.py

# 2. If script doesn't work, manually check experiment directories
cd D:\experiments
dir /s *bidirectional* 2>nul

# 3. Search experiment configs
findstr /s "bidirectional" *.json

# 4. Check specific experiment (if you know which one)
cd D:\experiments\exp2_paired  # or wherever ablation B is
type experiment_config.json | findstr "bidirectional"

# 5. Check training log for confirmation
type training.log | findstr /i "bidirectional"
```

---

## 📊 What Success Looks Like

**If ablation was done correctly, you should see:**

```
Experiment: exp2_paired_bidirectional
  Config: experiment_config.json
    Bidirectional: True
    Best R@1: 6.61%
  ✓ Matches paper claim (6.61%)

Experiment: exp2_paired_unidirectional
  Config: experiment_config.json
    Bidirectional: False
    Best R@1: 7.02%
  ✓ Matches paper claim (7.02%)
```

---

## 💡 Summary

**To verify bidirectional ablation:**

1. ✅ **Easiest:** Run `verify_bidirectional_ablation.py` on remote desktop
2. ✅ **Manual:** Check experiment config for `"bidirectional": true`
3. ✅ **Verify results:** R@1 should be ~6.61% (bidirectional) vs ~7.02% (unidirectional)
4. ✅ **Code check:** Implementation is correct in `train_sharp_raddino_v2.py`

**Red flags:**
- ⚠️ Can't find any experiment with `"bidirectional": true`
- ⚠️ R@1 results don't match paper (6.61% vs 7.02%)
- ⚠️ No training logs confirming bidirectional loss was used

---

## 📝 Next Steps

1. **Run verification script** on remote desktop
2. **If ablation NOT done:** Need to run it (takes ~2 days)
3. **If results don't match:** Check which checkpoint was used for the paper
4. **If everything matches:** ✓ Paper claims are verified!

Let me know what you find!
