# Integrate SHARP into BenchX - Direct Approach

## Goal
Load SHARP's ViT encoder directly and run on BenchX tasks to compare with published baselines.

## Quick Setup (3 steps)

### Step 1: Add SHARP Model to BenchX

On remote desktop:

```cmd
cd C:\Users\aya.alaswad\remote
git pull origin main

# Copy SHARP loader to BenchX models directory
copy load_sharp_in_benchx.py BenchX\models\sharp_encoder.py
```

### Step 2: Register SHARP in BenchX Model Registry

Edit `BenchX\models\__init__.py` and add:

```python
from .sharp_encoder import SHARPEncoder

# Add to model registry (find the dict with model names)
MODEL_REGISTRY = {
    # ... existing models ...
    'sharp_vit': SHARPEncoder,
}
```

**OR** if there's no registry, just ensure the import works.

### Step 3: Test SHARP Encoder Loads

```cmd
cd C:\Users\aya.alaswad\remote
python load_sharp_in_benchx.py
```

Expected output:
```
Loading SHARP encoder from: D:\experiments\exp3_full_sharp\p3_best.pt
Found XXX ViT parameters in SHARP checkpoint
✓ SHARP encoder loaded successfully (step XXXXX)
Testing forward pass...
Input shape: (2, 3, 224, 224)
Output shape: (2, 768)
✓ SUCCESS! SHARP encoder working correctly
```

## Alternative: Simpler Approach (If BenchX Integration is Complex)

If modifying BenchX is too complicated, use this **standalone approach**:

### Create Custom Training Script

```python
# train_sharp_on_siim.py

import torch
from load_sharp_in_benchx import SHARPEncoder
from BenchX.data.datasets import SIIM_Pneumothorax_Dataset
from BenchX.data.transforms import NIHTransforms

# 1. Load SHARP encoder
encoder = SHARPEncoder('D:/experiments/exp3_full_sharp/p3_best.pt')

# 2. Add classification head
classifier = torch.nn.Linear(768, 2)  # 2 classes for SIIM

# 3. Create model
model = torch.nn.Sequential(encoder, classifier)

# 4. Load SIIM dataset
dataset = SIIM_Pneumothorax_Dataset(
    data_path='BenchX/datasets/SIIM',
    csvpath='BenchX/datasets/SIIM/siim_labels.csv',
    split='train_1',
    extension='.png'
)

# 5. Train with standard PyTorch loop
# ... (standard training code)
```

This bypasses BenchX's config system entirely.

## Expected Results

After training on SIIM (22 samples, train_1 split):

**Baseline comparisons from BenchX paper:**
- ConVIRT: SIIM AUROC = ???
- MGCA: SIIM AUROC = ???
- MRM: SIIM AUROC = ???

**Your result:**
- SHARP: SIIM AUROC = ???

If SHARP > baselines → Success! 🎉

## What to Run on Remote

**Option A: Quick Test**

```cmd
cd C:\Users\aya.alaswad\remote
git pull
python load_sharp_in_benchx.py
```

This just tests if SHARP loads correctly.

**Option B: Full Integration** (after test works)

Modify BenchX's model registry, then:

```cmd
cd BenchX
python bin/train.py configs/classification/SIIM/sharp.yml
```

**Option C: Standalone Script** (if BenchX integration fails)

Create custom training script that uses SHARP directly.

---

## Which Option Do You Prefer?

1. **Modify BenchX** (proper integration, uses BenchX's training loop)
2. **Standalone script** (simpler, full control, but need to write training loop)

Let me know and I'll create the exact code you need!
