# SHARP Experiments → Training Script Mapping

## 🚨 CRITICAL FINDING

**ALL EXPERIMENTS USE BIDIRECTIONAL LOSS!**

From `experiments.md` line 21:
> **Bidirectional loss: Yes (all experiments)**

**This means:**
- ❌ Your paper Section 2.2 says "unidirectional" - **WRONG**
- ✓ Your paper Section 4.2 says you tested bidirectional as ablation - **MISLEADING**
- ✅ **REALITY:** ALL experiments (baseline + ablations) used bidirectional from the start

---

## 📋 Complete Experiment Mapping

### Stage 1: Contrastive Pretraining

| Exp | Name | Training Script | Launch Script | Bidirectional? | Output Dir |
|-----|------|----------------|---------------|----------------|------------|
| **#1** | Baseline | `train_sharp_raddino_v2.py` | *(need to find)* | ✓ **YES** | `D:/experiments/exp1_baseline/` |
| **#2** | Paired Sampling | `train_sharp_raddino_v2.py` | *(need to find)* | ✓ **YES** | `D:/experiments/exp2_paired/` |
| **#2b** | 20k Random Control | `train_sharp_raddino_v2.py` | `run_exp2b_20k_random.bat` | ✓ **YES** | `D:/experiments/exp2b_20k_random/` |
| **#3** | Hard Negatives (SHARP) | `train_sharp_raddino_v2.py` | *(need to find)* | ✓ **YES** | `D:/experiments/exp3_full_sharp/` |
| **#4 v2a** | Large Batch — Fair | `train_sharp_large_batch.py` | `run_exp4_v2a_FAIR.bat` | ✓ **YES** | `D:/experiments/exp4_v2a_matched_epochs/` |
| **#4 v2b** | Large Batch — Ceiling | `train_sharp_large_batch.py` | `run_exp4_v2_PROPER.bat` | ✓ **YES** | `D:/experiments/exp4_v2_large_batch_PROPER/` |

---

## 🔍 Detailed Config for Each Experiment

### Exp #1: Baseline
```bash
python train_sharp_raddino_v2.py \
  --batch_size 32 \
  --lr 0.0001 \
  --total_steps 100000 \
  --hard_neg_max_frac 0.0 \          # NO hard negatives
  --bidirectional \                  # ✓ BIDIRECTIONAL
  --output_dir D:\experiments\exp1_baseline
```

**Config to verify:** Look for `experiment_config.json` or training logs in:
```
D:\experiments\exp1_baseline\
```

---

### Exp #2: Paired Sampling
```bash
python train_sharp_raddino_v2.py \
  --batch_size 32 \
  --lr 0.0001 \
  --total_steps ~100000 \
  --hard_neg_max_frac 0.0 \          # NO hard negatives
  --paired_sampling \                # ✓ 100% paired
  --bidirectional \                  # ✓ BIDIRECTIONAL
  --output_dir D:\experiments\exp2_paired
```

**Config to verify:**
```
D:\experiments\exp2_paired\
```

---

### Exp #2b: 20k Random Control
```bash
python train_sharp_raddino_v2.py \
  --batch_size 32 \
  --lr 0.0001 \
  --total_steps 38000 \
  --hard_neg_max_frac 0.0 \          # NO hard negatives
  --max_train_files 20000 \          # Only 20k files
  --bidirectional \                  # ✓ BIDIRECTIONAL
  --output_dir D:\experiments\exp2b_20k_random
```

**Launch script:** `run_exp2b_20k_random.bat`
**Config to verify:**
```
D:\experiments\exp2b_20k_random\
```

---

### Exp #3: Hard Negatives (SHARP - Main Method)
```bash
python train_sharp_raddino_v2.py \
  --batch_size 32 \
  --lr 0.0001 \
  --total_steps 46000 \
  --hard_neg_max_frac 0.6 \          # ✓ 60% hard negatives
  --hard_neg_ramp_end 30000 \        # Curriculum: 5k→30k
  --warmup_steps 5000 \
  --bidirectional \                  # ✓ BIDIRECTIONAL
  --output_dir D:\experiments\exp3_full_sharp
```

**Config to verify:**
```
D:\experiments\exp3_full_sharp\
```

---

### Exp #4 v2a: Large Batch — Fair
```bash
python train_sharp_large_batch.py \
  --batch_size 512 \                 # ✓ Large batch
  --lr 0.0016 \                      # Scaled LR (16x)
  --total_steps 6250 \               # Matched samples
  --hard_neg_max_frac 0.6 \          # ✓ 60% hard negatives
  --hard_neg_ramp_end 1875 \         # Curriculum scaled
  --warmup_steps 312 \               # 5% warmup
  --bidirectional \                  # ✓ BIDIRECTIONAL
  --output_dir D:\experiments\exp4_v2a_matched_epochs
```

**Launch script:** `run_exp4_v2a_FAIR.bat` (line 58: `--bidirectional`)
**Config to verify:**
```
D:\experiments\exp4_v2a_matched_epochs\
```

---

### Exp #4 v2b: Large Batch — Ceiling
```bash
python train_sharp_large_batch.py \
  --batch_size 512 \                 # ✓ Large batch
  --lr 0.0016 \                      # Scaled LR (16x)
  --total_steps 100000 \             # Full 100k steps
  --hard_neg_max_frac 0.6 \          # ✓ 60% hard negatives
  --hard_neg_ramp_end 30000 \        # Full curriculum
  --warmup_steps 5000 \
  --bidirectional \                  # ✓ BIDIRECTIONAL
  --output_dir D:\experiments\exp4_v2_large_batch_PROPER
```

**Launch script:** `run_exp4_v2_PROPER.bat`
**Config to verify:**
```
D:\experiments\exp4_v2_large_batch_PROPER\
```

---

## ✅ How to Verify Each Experiment

**On remote desktop:**

```bash
# Exp #1 Baseline
cd D:\experiments\exp1_baseline
type experiment_config.json | findstr "bidirectional"
type training.log | findstr /i "bidirectional"

# Exp #2 Paired
cd D:\experiments\exp2_paired
type experiment_config.json | findstr "bidirectional"

# Exp #2b 20k Random
cd D:\experiments\exp2b_20k_random
type experiment_config.json | findstr "bidirectional"

# Exp #3 SHARP (Main)
cd D:\experiments\exp3_full_sharp
type experiment_config.json | findstr "bidirectional"

# Exp #4 v2a Large Batch Fair
cd D:\experiments\exp4_v2a_matched_epochs
type experiment_config.json | findstr "bidirectional"

# Exp #4 v2b Large Batch Ceiling
cd D:\experiments\exp4_v2_large_batch_PROPER
type experiment_config.json | findstr "bidirectional"
```

**Expected output for ALL:**
```json
"bidirectional": true
```

---

## 🔧 Training Script Implementation

Both training scripts implement bidirectional the same way:

### In `train_sharp_raddino_v2.py` (line 163-206):

```python
def multi_positive_infonce(img_embs, txt_embs, concept_keys, temperature, bidirectional=False):
    # ... compute i→t loss ...
    loss_i2t = (-sim_pos_avg_i2t + log_denom_i2t).mean()

    if bidirectional:
        # TEXT → IMAGE direction
        n_pos_t2i = pos_mask.sum(dim=0)
        sim_pos_avg_t2i = (sim.T * pos_mask.T).sum(dim=1) / n_pos_t2i
        log_denom_t2i = torch.logsumexp(sim.T, dim=1)
        loss_t2i = (-sim_pos_avg_t2i + log_denom_t2i).mean()

        return (loss_i2t + loss_t2i) / 2  # Average both directions
    else:
        return loss_i2t  # Unidirectional only
```

**When `--bidirectional` flag is passed:**
- Computes both image→text AND text→image losses
- Averages them: `(L_i2t + L_t2i) / 2`

**When flag is NOT passed:**
- Only computes image→text loss

---

## ⚠️ CRITICAL PAPER CORRECTION NEEDED

### Current Paper (Section 2.2, lines 220-222):

> "The loss is **unidirectional** (image anchors only)"

### What Actually Happened:

**ALL experiments used BIDIRECTIONAL loss!**

### What You Should Write:

**Option 1 (if you want to keep using bidirectional):**
```latex
The loss is bidirectional, computing both image→text and text→image
directions and averaging them, similar to CLIP. We denote the combined
loss as L = (L_{i→t} + L_{t→i}) / 2.
```

**Option 2 (if you want to match what you originally intended):**
```latex
The loss is unidirectional (image anchors only); same-concept crops...
```

**BUT THEN YOU MUST:**
- Remove `--bidirectional` from ALL experiment launch scripts
- Re-run ALL experiments without bidirectional
- Update all R@1 results in the paper

---

## 📊 Summary Table

| Experiment | Script | Bidirectional? | Hard Neg | Paired | Batch | R@1 |
|------------|--------|----------------|----------|--------|-------|-----|
| #1 Baseline | train_sharp_raddino_v2.py | ✓ YES | 0% | No | 32 | 6.61% |
| #2 Paired | train_sharp_raddino_v2.py | ✓ YES | 0% | 100% | 32 | 0.81% |
| #2b 20k Control | train_sharp_raddino_v2.py | ✓ YES | 0% | No | 32 | 4.99% |
| #3 SHARP | train_sharp_raddino_v2.py | ✓ YES | 60% | No | 32 | 6.21% |
| #4 v2a Fair | train_sharp_large_batch.py | ✓ YES | 60% | No | 512 | 8.77% |
| #4 v2b Ceiling | train_sharp_large_batch.py | ✓ YES | 60% | No | 512 | 8.9% |

**ALL use bidirectional!**

---

## 🎯 What You Need to Do

1. **Verify on remote desktop:**
   ```bash
   cd D:\experiments\exp3_full_sharp
   type experiment_config.json
   ```

2. **Check if `"bidirectional": true`** appears in config

3. **If YES (expected):**
   - Update paper Section 2.2 to say "bidirectional"
   - Remove the ablation study claim about testing bidirectional (Section 4.2, lines 564-576)
   - Or reframe it as "all our experiments use bidirectional by default"

4. **If NO:**
   - Something is wrong with the documentation
   - Check training logs for confirmation

---

## 📝 Quick Verification Command

**Run on remote desktop:**

```bash
cd C:\Users\aya.alaswad\remote\MyReasearch
python verify_bidirectional_ablation.py
```

This will check ALL experiment directories and show which ones used bidirectional.

---

**Last updated:** Based on your screenshot and experiments.md
**Key finding:** ALL experiments use bidirectional, not just an ablation!
