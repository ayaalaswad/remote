# 🔄 Resumable Training Guide

## ✅ Training is Now Fully Resumable!

The training script now has **automatic checkpoint saving and resume** to handle interruptions gracefully.

---

## 🚀 Features

### 1. **Auto-Resume** ⚡
If training is interrupted (crash, power loss, etc.), just run the same command again:

```bash
python train_sharp_large_batch.py \
  --scene_dir D:\datasets\mimic-ext-cxr-qba\scene_graphs \
  --image_dir D:\datasets\mimic-cxr-jpg\files \
  --split_csv D:\datasets\mimic-cxr-jpg\mimic-cxr-2.0.0-split.csv.gz \
  --output_dir D:\experiments\exp2_paired \
  --batch_size 32 \
  --bidirectional \
  --paired_sampling
```

**The script will automatically**:
- ✅ Detect existing checkpoint (`p3_last.pt`)
- ✅ Resume from last saved step
- ✅ Restore model, optimizer, and training state
- ✅ Continue training seamlessly

You'll see:
```
⚡ Auto-resuming from: D:\experiments\exp2_paired\p3_last.pt
   ✅ Restored GradScaler state
   Resumed at step 15,000 (will train to 100,000)
   Restored history: 7 evals, best R@1=28.45%
```

---

### 2. **Frequent Checkpointing** 💾

Training saves checkpoints at multiple points:

| Checkpoint | When Saved | Purpose |
|-----------|------------|---------|
| `p3_last.pt` | Every 1,000 steps (default) | Crash recovery - auto-resumes from here |
| `p3_last.pt` | Every eval (2,000 steps) | Full checkpoint with metrics |
| `p3_best.pt` | When validation improves | Best performing model |

**Configure save frequency**:
```bash
# Save every 500 steps (more frequent, safer)
--save_every 500

# Save every 2000 steps (less frequent, faster)
--save_every 2000
```

---

### 3. **Complete State Restoration** 🔧

When resuming, the script restores:
- ✅ Model weights (image encoder, text encoder, temperature)
- ✅ Optimizer state (Adam momentum, learning rate)
- ✅ GradScaler state (mixed precision training)
- ✅ Training step counter
- ✅ Best validation score
- ✅ Evaluation history
- ✅ ViT unfreeze status (if past step 5k)

**This means**:
- Training continues exactly as if never interrupted
- No performance degradation
- No need to retrain from scratch

---

### 4. **Manual Resume** (Optional) 📂

You can also manually specify a checkpoint:

```bash
# Resume from specific checkpoint
python train_sharp_large_batch.py \
  --resume_from D:\experiments\exp2_paired\p3_best.pt \
  [... other args ...]

# Resume from a different experiment
python train_sharp_large_batch.py \
  --resume_from D:\experiments\exp1_baseline\p3_last.pt \
  --output_dir D:\experiments\exp1_continued \
  [... other args ...]
```

---

## 📊 Monitoring Progress

### Check Current Training State

```bash
# View training history
type D:\experiments\exp2_paired\p3_history.json

# Check latest checkpoint info
python -c "import torch; ckpt=torch.load('D:/experiments/exp2_paired/p3_last.pt', map_location='cpu'); print(f'Step: {ckpt[\"step\"]:,}'); print(f'Best R@1: {ckpt.get(\"i2t_r1\", 0)*100:.2f}%')"
```

### Watch Training Log

```bash
# On Windows (Command Prompt)
powershell Get-Content D:\experiments\exp2_paired\training.log -Wait -Tail 20

# On Git Bash / WSL
tail -f /d/experiments/exp2_paired/training.log
```

---

## 🛡️ Handling Different Scenarios

### Scenario 1: Power Outage / System Crash

**What happens**: Training stops unexpectedly at step 23,456

**Solution**: Just run the same command again
```bash
python train_sharp_large_batch.py [same args as before]
```

**Result**: Training resumes from step 23,000 (last saved checkpoint)

---

### Scenario 2: Out of Memory (OOM)

**What happens**: CUDA OOM error at step 5,432

**Solution**: Reduce batch size and resume
```bash
python train_sharp_large_batch.py \
  --batch_size 16 \
  --grad_accum 2 \
  --resume_from D:\experiments\exp2_paired\p3_last.pt \
  [... other args ...]
```

**Note**: Effective batch size stays the same (16 × 2 = 32)

---

### Scenario 3: Want to Continue Training Longer

**What happens**: Training stopped at 100k steps, but you want to train to 150k

**Solution**: Resume with higher total_steps
```bash
python train_sharp_large_batch.py \
  --total_steps 150000 \
  --resume_from D:\experiments\exp2_paired\p3_last.pt \
  [... other args ...]
```

**Result**: Training continues from 100k to 150k

---

### Scenario 4: Manually Killed Training (Ctrl+C)

**What happens**: You stopped training at step 42,000

**Solution**: Just restart with same command
```bash
python train_sharp_large_batch.py [same args]
```

**Result**: Resumes from step 42,000 or last checkpoint before that

---

## 🎯 Best Practices

### 1. **Save Checkpoint Frequency**
```bash
# For 12-hour experiments (default)
--save_every 1000   # ~every 10-15 minutes, max 15 min lost if crash

# For critical experiments
--save_every 500    # ~every 5-7 minutes, max 7 min lost

# For stable long runs
--save_every 2000   # ~every 20-30 minutes
```

### 2. **Keep Multiple Backup Copies**
Before starting a new experiment:
```bash
# Backup previous checkpoints
mkdir D:\experiments\exp2_paired_backup
copy D:\experiments\exp2_paired\*.pt D:\experiments\exp2_paired_backup\
```

### 3. **Check Disk Space**
Checkpoints are ~1.5 GB each. Make sure you have enough space:
```bash
# Windows: Check free space
dir D:\experiments
```

For 100k step experiment:
- `p3_last.pt`: 1.5 GB (overwritten every 1k steps)
- `p3_best.pt`: 1.5 GB (saved when improving)
- Total: ~3 GB per experiment

### 4. **Monitor GPU Temperature**
Long training runs can overheat:
```bash
# Check GPU temp periodically
nvidia-smi
```

If temp > 85°C, consider:
- Improve case airflow
- Reduce batch size slightly
- Lower room temperature

---

## 🧪 Testing Resume Functionality

### Quick Test (5 minutes)

```bash
# Start short training
python train_sharp_large_batch.py \
  --scene_dir D:\datasets\mimic-ext-cxr-qba\scene_graphs \
  --image_dir D:\datasets\mimic-cxr-jpg\files \
  --split_csv D:\datasets\mimic-cxr-jpg\mimic-cxr-2.0.0-split.csv.gz \
  --output_dir D:\test_resume \
  --batch_size 32 \
  --total_steps 3000 \
  --eval_every 1000 \
  --save_every 500

# After it reaches step 1500, press Ctrl+C to stop

# Resume (should start from step 1500)
python train_sharp_large_batch.py \
  --scene_dir D:\datasets\mimic-ext-cxr-qba\scene_graphs \
  --image_dir D:\datasets\mimic-cxr-jpg\files \
  --split_csv D:\datasets\mimic-cxr-jpg\mimic-cxr-2.0.0-split.csv.gz \
  --output_dir D:\test_resume \
  --batch_size 32 \
  --total_steps 3000 \
  --eval_every 1000 \
  --save_every 500
```

You should see:
```
⚡ Auto-resuming from: D:\test_resume\p3_last.pt
   Resumed at step 1,500 (will train to 3,000)
```

---

## ❓ FAQ

### Q: Will resuming change my results?
**A**: No. The model continues training exactly as if never interrupted.

### Q: Can I resume with different hyperparameters?
**A**: Partially. You can change:
- ✅ `total_steps` (train longer)
- ✅ `eval_every` (evaluate more/less often)
- ✅ `save_every` (save more/less often)
- ⚠️ Changing batch_size, lr, or architecture requires retraining from scratch

### Q: What if checkpoint is corrupted?
**A**: Use `p3_best.pt` or train from scratch. Always keep backups!

### Q: Can I resume on a different machine?
**A**: Yes! Just copy the entire experiment folder to the new machine. Make sure data paths match.

### Q: How much disk space do I need?
**A**: ~3 GB per experiment (2 checkpoints × 1.5 GB each)

### Q: Can I delete old checkpoints?
**A**: Yes, but keep at least `p3_best.pt`. Delete `p3_last.pt` only if experiment is complete.

---

## 🎉 Summary

**Training is now bulletproof**:
- ✅ Auto-resumes after crashes
- ✅ Saves every 1,000 steps
- ✅ Keeps best model
- ✅ Preserves complete training state
- ✅ No need to babysit 12-hour experiments

**Just run your experiment and forget about it!** 🚀

If anything goes wrong, simply run the same command again.
