#!/usr/bin/env python3
"""
Check NVIDIA GPU Setup for SHARP Training

Verifies:
1. NVIDIA GPU detected
2. CUDA available in PyTorch
3. GPU memory available
4. cuDNN enabled
"""

import sys

print("="*80)
print("🔍 GPU SETUP CHECK")
print("="*80)

# ─── Step 1: Check PyTorch installation ───────────────────────────────────────
print("\n📦 Step 1: Checking PyTorch installation...")
try:
    import torch
    print(f"   ✅ PyTorch installed: {torch.__version__}")
except ImportError:
    print("   ❌ PyTorch not installed!")
    print("\n   Install with:")
    print("   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118")
    sys.exit(1)

# ─── Step 2: Check CUDA availability ──────────────────────────────────────────
print("\n🎮 Step 2: Checking CUDA availability...")
if torch.cuda.is_available():
    print(f"   ✅ CUDA available: {torch.version.cuda}")
    print(f"   ✅ cuDNN enabled: {torch.backends.cudnn.enabled}")
    print(f"   ✅ cuDNN version: {torch.backends.cudnn.version()}")
else:
    print("   ❌ CUDA NOT available!")
    print("\n   Possible issues:")
    print("   1. PyTorch CPU-only version installed (need GPU version)")
    print("   2. NVIDIA drivers not installed")
    print("   3. CUDA toolkit not installed")
    print("\n   Install GPU PyTorch:")
    print("   pip uninstall torch torchvision torchaudio")
    print("   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118")
    sys.exit(1)

# ─── Step 3: Check GPU devices ────────────────────────────────────────────────
print(f"\n🖥️  Step 3: Checking GPU devices...")
num_gpus = torch.cuda.device_count()
print(f"   ✅ Number of GPUs detected: {num_gpus}")

if num_gpus == 0:
    print("   ❌ No GPUs detected!")
    sys.exit(1)

for i in range(num_gpus):
    print(f"\n   GPU {i}:")
    print(f"      Name: {torch.cuda.get_device_name(i)}")

    # Get memory info
    props = torch.cuda.get_device_properties(i)
    total_memory = props.total_memory / (1024**3)  # Convert to GB
    print(f"      Total memory: {total_memory:.2f} GB")
    print(f"      Compute capability: {props.major}.{props.minor}")

    # Check current memory usage
    allocated = torch.cuda.memory_allocated(i) / (1024**3)
    reserved = torch.cuda.memory_reserved(i) / (1024**3)
    print(f"      Currently allocated: {allocated:.2f} GB")
    print(f"      Currently reserved: {reserved:.2f} GB")
    print(f"      Available: {total_memory - reserved:.2f} GB")

# ─── Step 4: Test GPU computation ─────────────────────────────────────────────
print(f"\n🧪 Step 4: Testing GPU computation...")
try:
    # Create a small tensor on GPU
    device = torch.device('cuda:0')
    x = torch.randn(1000, 1000, device=device)
    y = torch.randn(1000, 1000, device=device)
    z = torch.matmul(x, y)

    print(f"   ✅ GPU computation successful!")
    print(f"   ✅ Default GPU: {torch.cuda.current_device()}")
    print(f"   ✅ Device name: {torch.cuda.get_device_name(torch.cuda.current_device())}")

    del x, y, z
    torch.cuda.empty_cache()

except Exception as e:
    print(f"   ❌ GPU computation failed: {e}")
    sys.exit(1)

# ─── Step 5: Check for batch size 512 ─────────────────────────────────────────
print(f"\n💾 Step 5: Checking memory for batch_size=512...")

total_mem_gb = torch.cuda.get_device_properties(0).total_memory / (1024**3)

# Rough estimate: ViT-B/16 with batch 512 needs ~20-24 GB
if total_mem_gb >= 24:
    print(f"   ✅ {total_mem_gb:.1f} GB VRAM - Should handle batch_size=512")
    recommended_batch = 512
elif total_mem_gb >= 16:
    print(f"   ⚠️  {total_mem_gb:.1f} GB VRAM - Recommend batch_size=256 with grad_accum=2")
    recommended_batch = 256
elif total_mem_gb >= 12:
    print(f"   ⚠️  {total_mem_gb:.1f} GB VRAM - Recommend batch_size=128 with grad_accum=4")
    recommended_batch = 128
else:
    print(f"   ❌ {total_mem_gb:.1f} GB VRAM - Too small for large batch training")
    print(f"      Recommend batch_size=64 with grad_accum=8")
    recommended_batch = 64

# ─── Step 6: Environment check ────────────────────────────────────────────────
print(f"\n🔧 Step 6: Checking environment...")

import os
cuda_visible = os.environ.get('CUDA_VISIBLE_DEVICES', 'not set')
print(f"   CUDA_VISIBLE_DEVICES: {cuda_visible}")

if cuda_visible == 'not set':
    print(f"   ✅ All GPUs visible (default)")
else:
    print(f"   ℹ️  Only GPU(s) {cuda_visible} visible")

# ─── Final Summary ─────────────────────────────────────────────────────────────
print(f"\n{'='*80}")
print(f"✅ SUMMARY - GPU READY FOR TRAINING")
print(f"{'='*80}")
print(f"\nYour GPU: {torch.cuda.get_device_name(0)}")
print(f"VRAM: {total_mem_gb:.1f} GB")
print(f"Recommended batch size: {recommended_batch}")

if recommended_batch == 512:
    print(f"\n🚀 RECOMMENDED TRAINING COMMAND:")
    print(f"   python train_sharp_large_batch.py \\")
    print(f"     --scene_dir ./scene_data \\")
    print(f"     --image_dir ./mimic-cxr-jpg \\")
    print(f"     --split_csv ./mimic-cxr-2.0.0-split.csv.gz \\")
    print(f"     --output_dir ./sharp_experiments/batch_512 \\")
    print(f"     --batch_size 512")
else:
    print(f"\n🚀 RECOMMENDED TRAINING COMMAND:")
    print(f"   python train_sharp_large_batch.py \\")
    print(f"     --scene_dir ./scene_data \\")
    print(f"     --image_dir ./mimic-cxr-jpg \\")
    print(f"     --split_csv ./mimic-cxr-2.0.0-split.csv.gz \\")
    print(f"     --output_dir ./sharp_experiments/batch_{recommended_batch} \\")
    print(f"     --batch_size {recommended_batch} \\")
    print(f"     --grad_accum {512 // recommended_batch}")
    print(f"\n   (Effective batch = {recommended_batch} × {512 // recommended_batch} = 512)")

print(f"\n{'='*80}\n")

# ─── Extra: Check other dependencies ───────────────────────────────────────────
print(f"📚 Checking other dependencies...")

deps = {
    'transformers': 'Hugging Face Transformers',
    'pandas': 'Pandas',
    'PIL': 'Pillow (PIL)',
    'tqdm': 'tqdm',
}

missing = []
for module, name in deps.items():
    try:
        if module == 'PIL':
            from PIL import Image
        else:
            __import__(module)
        print(f"   ✅ {name}")
    except ImportError:
        print(f"   ❌ {name} - NOT INSTALLED")
        missing.append(module)

if missing:
    print(f"\n⚠️  Install missing dependencies:")
    install_cmd = "pip install " + " ".join(missing).replace('PIL', 'pillow')
    print(f"   {install_cmd}")
else:
    print(f"\n✅ All dependencies installed!")

print(f"\n{'='*80}")
print(f"🎯 READY TO TRAIN!")
print(f"{'='*80}\n")
