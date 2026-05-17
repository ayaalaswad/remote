# 🎮 GPU Setup Guide for SHARP Training

## ⚡ Quick Check - Is GPU Ready?

Run this command:
```bash
python check_gpu.py
```

**Expected output**:
```
✅ SUMMARY - GPU READY FOR TRAINING

Your GPU: NVIDIA RTX A5000
VRAM: 24.0 GB
Recommended batch size: 512

🚀 RECOMMENDED TRAINING COMMAND:
   python train_sharp_large_batch.py --batch_size 512 ...
```

If you see this → GPU is ready! Skip to "Running Training" section below.

---

## 🔧 Detailed Setup (If GPU Not Working)

### Step 1: Check Windows GPU Status

**Method 1: Task Manager**
1. Press `Ctrl + Shift + Esc` to open Task Manager
2. Click "Performance" tab
3. Look for "GPU 0" or "GPU 1" in the left panel
4. Should show your NVIDIA GPU name (e.g., "RTX A5000")

**Method 2: NVIDIA Control Panel**
1. Right-click desktop → "NVIDIA Control Panel"
2. Click "System Information" (bottom left)
3. Should show GPU name and driver version

**Method 3: Command line**
```bash
nvidia-smi
```

**Expected output**:
```
+-----------------------------------------------------------------------------+
| NVIDIA-SMI 535.xx       Driver Version: 535.xx       CUDA Version: 12.x   |
|-------------------------------+----------------------+----------------------+
| GPU  Name        Persistence-M| Bus-Id        Disp.A | Volatile Uncorr. ECC |
|   0  NVIDIA RTX A5000    Off  | 00000000:01:00.0 Off |                  Off |
| 30%   45C    P0    70W / 230W |      0MiB / 24564MiB |      0%      Default |
+-------------------------------+----------------------+----------------------+
```

If this works → NVIDIA driver installed ✅

If you get "nvidia-smi is not recognized" → Install NVIDIA drivers ❌

---

### Step 2: Install/Update NVIDIA Drivers

**If nvidia-smi not working**:

1. Go to https://www.nvidia.com/Download/index.aspx
2. Select your GPU model
3. Download and install latest driver
4. Restart computer
5. Run `nvidia-smi` again to verify

---

### Step 3: Check PyTorch GPU Support

```bash
python -c "import torch; print('CUDA available:', torch.cuda.is_available()); print('GPU:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'None')"
```

**Expected output**:
```
CUDA available: True
GPU: NVIDIA RTX A5000
```

**If says "CUDA available: False"**:

You have PyTorch CPU-only version. Install GPU version:

```bash
# Uninstall CPU version
pip uninstall torch torchvision torchaudio

# Install GPU version (CUDA 11.8)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

After install, run check again:
```bash
python check_gpu.py
```

---

## 🚀 Running Training with GPU

### Basic Command (Automatic GPU Detection)

```bash
python train_sharp_large_batch.py \
  --scene_dir ./scene_data \
  --image_dir ./mimic-cxr-jpg \
  --split_csv ./mimic-cxr-2.0.0-split.csv.gz \
  --output_dir ./sharp_experiments/batch_512 \
  --batch_size 512
```

**The script automatically uses GPU if available** (no extra flags needed!)

---

### Force Specific GPU (If Multiple GPUs)

If you have multiple GPUs and want to use GPU 1:

**Windows Command Prompt**:
```cmd
set CUDA_VISIBLE_DEVICES=1
python train_sharp_large_batch.py --batch_size 512 ...
```

**Windows PowerShell**:
```powershell
$env:CUDA_VISIBLE_DEVICES="1"
python train_sharp_large_batch.py --batch_size 512 ...
```

**Linux/Mac**:
```bash
CUDA_VISIBLE_DEVICES=1 python train_sharp_large_batch.py --batch_size 512 ...
```

---

## 📊 Monitor GPU During Training

### Method 1: Task Manager (Windows)

1. Open Task Manager (`Ctrl + Shift + Esc`)
2. Go to "Performance" tab
3. Select "GPU 0" in left panel
4. Watch GPU utilization

**While training**:
- GPU utilization: Should be 80-100%
- GPU memory: Should use ~20-22 GB (for batch=512)

### Method 2: nvidia-smi (Command Line)

**Continuous monitoring**:
```bash
# Updates every 1 second
nvidia-smi -l 1
```

**Watch memory usage**:
```bash
# Updates every 2 seconds, shows only memory
nvidia-smi --query-gpu=timestamp,name,memory.used,memory.total,utilization.gpu --format=csv -l 2
```

**Expected output during training**:
```
timestamp, name, memory.used [MiB], memory.total [MiB], utilization.gpu [%]
2026-05-17 10:30:00.000, NVIDIA RTX A5000, 21500 MiB, 24564 MiB, 98 %
```

### Method 3: Within Training Script

The training script prints device info at start:
```
Device       : cuda
Batch size   : 512  |  Grad accum: 1  |  Effective batch: 512
```

Look for `Device: cuda` (not `cpu`)!

---

## 🚨 Troubleshooting

### Issue 1: "CUDA out of memory"

**Error message**:
```
RuntimeError: CUDA out of memory. Tried to allocate X.XX GiB
```

**Solutions**:

**Option A**: Reduce batch size, increase gradient accumulation
```bash
# Instead of batch=512, use batch=256 × accum=2
python train_sharp_large_batch.py --batch_size 256 --grad_accum 2 ...

# Or batch=128 × accum=4
python train_sharp_large_batch.py --batch_size 128 --grad_accum 4 ...
```

**Option B**: Use smaller images
```bash
python train_sharp_large_batch.py --image_size 192 --batch_size 512 ...
```

**Option C**: Close other GPU programs
- Check Task Manager → GPU column
- Close any programs using GPU (games, video editors, etc.)

---

### Issue 2: Training using CPU instead of GPU

**Symptoms**:
- Training very slow (1-2 seconds per batch vs 0.1s)
- GPU utilization = 0% in Task Manager
- Script prints "Device: cpu"

**Fixes**:

1. Check PyTorch CUDA:
```bash
python -c "import torch; print(torch.cuda.is_available())"
```

2. If False, reinstall PyTorch GPU version:
```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118 --force-reinstall
```

3. Verify again:
```bash
python check_gpu.py
```

---

### Issue 3: "nvidia-smi not found"

**Fix**: Install/update NVIDIA drivers
1. Download from: https://www.nvidia.com/Download/index.aspx
2. Install and restart
3. Verify: `nvidia-smi`

---

### Issue 4: Multiple GPUs, want to use specific one

**List all GPUs**:
```bash
nvidia-smi -L
```

Output:
```
GPU 0: NVIDIA RTX 3090
GPU 1: NVIDIA RTX A5000
```

**Use GPU 1 only**:
```bash
set CUDA_VISIBLE_DEVICES=1
python train_sharp_large_batch.py ...
```

---

## 📋 Pre-Training Checklist

Run before starting long training:

```bash
# 1. Check GPU
python check_gpu.py

# 2. Quick test (100 steps, ~2 minutes)
python train_sharp_large_batch.py \
  --scene_dir ./scene_data \
  --image_dir ./mimic-cxr-jpg \
  --split_csv ./mimic-cxr-2.0.0-split.csv.gz \
  --output_dir ./test_gpu \
  --batch_size 512 \
  --total_steps 100 \
  --eval_every 50

# 3. Watch GPU usage during test
nvidia-smi -l 1
```

**Good signs**:
- ✅ Script starts without errors
- ✅ GPU utilization 80-100%
- ✅ Memory usage ~20-22 GB
- ✅ ~10-20 batches per second

**Bad signs**:
- ❌ "CUDA out of memory" → Reduce batch size
- ❌ GPU utilization 0% → Check PyTorch CUDA install
- ❌ Very slow (1-2 batches/sec) → Check using CPU not GPU

---

## 💾 Memory Requirements by Batch Size

| Batch Size | VRAM Needed | Recommended GPU | Command |
|------------|-------------|-----------------|---------|
| 512 | ~22 GB | RTX A5000, A6000, 4090 | `--batch_size 512` |
| 256 × 2 | ~22 GB | Same (effective 512) | `--batch_size 256 --grad_accum 2` |
| 128 × 4 | ~20 GB | RTX 3090, A5000 | `--batch_size 128 --grad_accum 4` |
| 64 × 8 | ~16 GB | RTX 3080, 4080 | `--batch_size 64 --grad_accum 8` |
| 32 × 16 | ~12 GB | RTX 3060 Ti | `--batch_size 32 --grad_accum 16` |

**Note**: All achieve effective batch = 512, but larger physical batch is better for multi-positive InfoNCE!

---

## 🎯 Optimal Settings for Common GPUs

### NVIDIA RTX A5000 (24 GB)
```bash
python train_sharp_large_batch.py --batch_size 512
```
Perfect for full batch!

### NVIDIA RTX 3090 (24 GB)
```bash
python train_sharp_large_batch.py --batch_size 512
```
Should work, may need `--batch_size 384` if OOM

### NVIDIA RTX 4090 (24 GB)
```bash
python train_sharp_large_batch.py --batch_size 512
```
Fast training!

### NVIDIA RTX 3080 (10-12 GB)
```bash
python train_sharp_large_batch.py --batch_size 128 --grad_accum 4
```
Effective batch = 512

### NVIDIA RTX 4060 Ti (16 GB)
```bash
python train_sharp_large_batch.py --batch_size 192 --grad_accum 3
```
Effective batch = 576 (close enough)

---

## ✅ Final Verification

Before 10-hour training run, do quick test:

```bash
# 5-minute test
python train_sharp_large_batch.py \
  --scene_dir ./scene_data \
  --image_dir ./mimic-cxr-jpg \
  --split_csv ./mimic-cxr-2.0.0-split.csv.gz \
  --output_dir ./test_run \
  --batch_size 512 \
  --total_steps 200 \
  --eval_every 100 \
  --val_gallery_size 200

# Monitor in another terminal
nvidia-smi -l 1
```

If completes successfully → Start full training!

---

## 🚀 Full Training Command

Once GPU verified:

```bash
python train_sharp_large_batch.py \
  --scene_dir ./scene_data \
  --image_dir ./mimic-cxr-jpg \
  --split_csv ./mimic-cxr-2.0.0-split.csv.gz \
  --output_dir ./sharp_experiments/batch_512 \
  --batch_size 512 \
  --total_steps 100000 \
  --eval_every 2000
```

Expected duration: ~10-12 hours on RTX A5000

---

## 📞 Quick Reference

| Command | Purpose |
|---------|---------|
| `python check_gpu.py` | Check GPU setup |
| `nvidia-smi` | Check GPU status |
| `nvidia-smi -l 1` | Monitor GPU (updates every 1s) |
| `set CUDA_VISIBLE_DEVICES=0` | Use GPU 0 only (Windows) |
| Task Manager → Performance → GPU | Windows GPU monitor |

---

**Ready?** Run `python check_gpu.py` and follow the recommendations! 🚀
