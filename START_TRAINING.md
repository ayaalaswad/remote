# 🚀 Start SHARP Training - Quick Guide

## ⚡ Quick Start (3 Steps)

### Step 1: Check GPU (30 seconds)

**Double-click**: `check_gpu.bat`

OR run:
```bash
python check_gpu.py
```

**Expected output**:
```
✅ SUMMARY - GPU READY FOR TRAINING

Your GPU: NVIDIA RTX A5000
VRAM: 24.0 GB
Recommended batch size: 512
```

If you see ✅ → Continue to Step 2

If you see ❌ → Read `GPU_SETUP_GUIDE.md` for fixes

---

### Step 2: Verify Data Available

Check you have:
- ✅ MIMIC-CXR images (~400 GB)
- ✅ MIMIC-Ext scene graphs (1.1 GB)
- ✅ Split CSV file

**Quick check**:
```bash
# Windows - check these paths exist
dir scene_data\p10\p10000032\
dir mimic-cxr-jpg\files\p10\
dir mimic-cxr-2.0.0-split.csv.gz
```

All should show files (not "File Not Found")

---

### Step 3: Run Training

**Option A: Full training (10-12 hours)**
```bash
python train_sharp_large_batch.py ^
  --scene_dir ./scene_data ^
  --image_dir ./mimic-cxr-jpg ^
  --split_csv ./mimic-cxr-2.0.0-split.csv.gz ^
  --output_dir ./sharp_experiments/batch_512 ^
  --batch_size 512
```

**Option B: Quick test first (5 minutes)**
```bash
python train_sharp_large_batch.py ^
  --scene_dir ./scene_data ^
  --image_dir ./mimic-cxr-jpg ^
  --split_csv ./mimic-cxr-2.0.0-split.csv.gz ^
  --output_dir ./test_run ^
  --batch_size 512 ^
  --total_steps 100 ^
  --eval_every 50 ^
  --val_gallery_size 200
```

If test passes → Run full training!

---

## 📊 During Training - What to Watch

### Expected Output

```
SHARP LARGE BATCH EXPERIMENT
Testing multi-positive InfoNCE hypothesis
================================================================================
Device       : cuda
Batch size   : 512  |  Grad accum: 1  |  Effective batch: 512

Loading official MIMIC-CXR split...
───────────────────────────────────────────────────────────
  Official MIMIC-CXR split
  Train     : 121,374 files   64,588 subjects
  Validate  :  18,447 files    9,765 subjects
  Test      :  23,156 files   11,219 subjects
  Subject-id disjointness: VERIFIED across all splits
───────────────────────────────────────────────────────────

Building vocabulary from train files...
   Vocab size: 10,000  → sharp_experiments/batch_512/p3_vocab.json

Building hard-negative index (20k train files sample)...
   HN index: 82,347 pairs  |  42 regions  |  423 (region,entity) groups

Train: 121,374 files  |  237 batches/epoch  |  Val: 18,447 files

Creating model (ImageNet ViT-B/16)...
   ViT frozen: 85,800,192 params
   Trainable (proj + text encoder): 2,854,144 params

Building validation gallery...
   Gallery: 2,000 pairs from 1,245 subjects

Starting Phase 3 training...
  100,000 steps  |  eval every 2,000  |  patience 10

SHARP-LargeBatch:   0%|          | 0/100000 [00:00<?, ?step/s]
```

### Monitor MP-InfoNCE Stats (Every 100 Batches)

```
[MP-InfoNCE stats] Batch size: 512, Avg co-positives: 3.47, Max: 12, % with co-pos: 68.2%
```

**Good**: Avg co-positives > 2.0, % with co-pos > 50%

### Monitor Training Progress

```
[step   2000]  loss=2.8456  I→T R@1=28.45%  R@5=56.32%  T→I R@1=27.89%  hard_frac=0.15  lr=1.00e-04
   🎉 New best  I→T R@1=28.45%  → sharp_experiments/batch_512/p3_best.pt

[step   4000]  loss=2.1234  I→T R@1=35.67%  R@5=64.21%  T→I R@1=34.12%  hard_frac=0.30  lr=9.87e-05
   🎉 New best  I→T R@1=35.67%  → sharp_experiments/batch_512/p3_best.pt
```

**Progress**: R@1 should increase over time

---

## 🖥️ Monitor GPU

### Windows Task Manager
1. `Ctrl + Shift + Esc`
2. Performance tab → GPU
3. Should show: 80-100% utilization, ~20-22 GB memory

### Command Line
```bash
# In separate terminal/command prompt
nvidia-smi -l 1
```

**Expected**:
```
|   0  NVIDIA RTX A5000    Off  |   70W / 230W |  21500MiB / 24564MiB |  98% |
```

---

## ⏱️ Timeline

| Event | Time | What to expect |
|-------|------|----------------|
| Start | 0 min | Data loading, vocab building |
| Step 100 | ~1 min | First MP-InfoNCE stats printed |
| Step 2000 | ~20 min | First evaluation, R@1 ~20-30% |
| Step 5000 | ~50 min | ViT blocks unfreeze, LR adjustment |
| Step 10000 | ~2 hours | R@1 ~35-40%, loss decreasing |
| Step 50000 | ~8 hours | R@1 ~45-50%, may early stop |
| Step 100000 | ~12 hours | Training complete (or early stop) |

---

## 🚨 Common Issues

### "CUDA out of memory"
```bash
# Reduce batch size
python train_sharp_large_batch.py --batch_size 256 --grad_accum 2 ...
```

### Training on CPU (very slow)
```bash
# Check PyTorch CUDA
python -c "import torch; print(torch.cuda.is_available())"

# If False, reinstall GPU version
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118 --force-reinstall
```

### "Scene files not found"
```bash
# Check paths
dir scene_data\p10\

# Should show directories like p10000032, p10000980, etc.
```

### Slow progress (< 5 batches/second)
- Check GPU utilization (should be >80%)
- If 0%, training using CPU → Fix PyTorch CUDA install
- If >80%, normal speed for large batch

---

## 📁 Output Files

Training creates:
```
sharp_experiments/batch_512/
├── experiment_config.json     # Experiment settings
├── p3_vocab.json             # Vocabulary (10k tokens)
├── p3_best.pt                # Best checkpoint (use this!)
├── p3_last.pt                # Latest checkpoint
├── p3_history.json           # Training metrics
├── p3_gallery_imgs.pt        # Validation cache
└── p3_gallery_txts.pt
```

**Most important**: `p3_best.pt` (best model based on R@1)

---

## ✅ Success Criteria

Training successful if:
- ✅ Completes without OOM errors
- ✅ Final I→T R@1 > 40% (baseline ~35%)
- ✅ MP-InfoNCE shows avg co-positives > 2.0
- ✅ Best checkpoint saved

**Next step**: Fine-tune decoder with `p3_best.pt` → Final CheXbert F1

---

## 🎯 Expected Results

### Hypothesis Validation

**If batch=512 R@1 > batch=32 R@1**:
- ✅ Hypothesis confirmed
- ✅ MP-InfoNCE works with large batches
- ✅ Paper can claim: "Batch size critical for multi-positive InfoNCE"

**Target downstream F1**: > 0.315 (beats RAD-DINO's 0.3136)

---

## 📞 Quick Commands Reference

```bash
# Check GPU
python check_gpu.py

# Quick test (5 min)
python train_sharp_large_batch.py --total_steps 100 --eval_every 50 --batch_size 512

# Full training (12 hours)
python train_sharp_large_batch.py --batch_size 512

# Monitor GPU
nvidia-smi -l 1

# Check progress
type sharp_experiments\batch_512\p3_history.json
```

---

## 🎬 Ready to Start?

1. ✅ Run `python check_gpu.py`
2. ✅ Verify GPU detected with enough VRAM
3. ✅ Check data paths exist
4. ✅ Start with quick test (100 steps)
5. ✅ If test passes → Full training!

---

**Need help?** Check:
- `GPU_SETUP_GUIDE.md` - GPU troubleshooting
- `SHARP_BATCH_EXPERIMENT_README.md` - Full documentation
- `CONCEPT_KEY_GUIDE.md` - Understanding the data

**Ready to run!** 🚀
