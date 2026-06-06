# BenchX Troubleshooting Guide

## Common Issues and Fixes

### Issue 1: Dataset Loading Returns 0 Samples

**Symptoms:**
```
RuntimeError: Dataset has 0 samples
```

**Cause:** Mismatch between CSV filenames and split file entries

**Fix:**
```cmd
cd C:\Users\aya.alaswad\remote
python debug_siim_data.py
```

If you see "No matches found", run:
```cmd
python rebuild_siim_csv.py
```

Expected output: "SUCCESS! Dataset will have 22 samples"

---

### Issue 2: SHARP Model Not Found

**Symptoms:**
```
ModuleNotFoundError: No module named 'models.sharp'
```

**Cause:** BenchX doesn't have the SHARP model wrapper

**Fix:**
1. Copy SHARP model to BenchX:
```cmd
cd C:\Users\aya.alaswad\remote
copy sharp_benchx_model.py BenchX\models\sharp.py
```

2. Verify it's there:
```cmd
dir BenchX\models\sharp.py
```

---

### Issue 3: Checkpoint Loading Error

**Symptoms:**
```
FileNotFoundError: D:/experiments/exp3_full_sharp/p3_best.pt
```

**Cause:** Checkpoint path is incorrect

**Fix:**
1. Verify checkpoint exists:
```cmd
dir D:\experiments\exp3_full_sharp\p3_best.pt
```

2. If missing, check other experiment folders:
```cmd
dir /s /b D:\experiments\*p3_best.pt
```

3. Update configs with correct path:
- Edit `sharp_siim_final.yml` line 25
- Edit `sharp_rsna_final.yml` line 25

---

### Issue 4: Config Base File Missing

**Symptoms:**
```
FileNotFoundError: configs/_base_/models/convirt.yml
```

**Cause:** BenchX config structure issue

**Fix:**
1. Check if BenchX has the base config:
```cmd
dir BenchX\configs\_base_\models\convirt.yml
```

2. If missing, you have two options:

**Option A (Recommended):** Remove the `includes:` line from configs
```yaml
# Remove this line:
includes:
  - configs/_base_/models/convirt.yml

# And add these directly:
model:
  proto: ImageClassifier
  cnn:
    proto: resnet50  # or vit_base for SHARP
    output_layer: avgpool
```

**Option B:** Use an existing working config as template
```cmd
cd BenchX\configs\classification\SIIM
copy mgca.yml sharp.yml
# Then edit sharp.yml to point to SHARP checkpoint
```

---

### Issue 5: Image Transform Not Found

**Symptoms:**
```
KeyError: 'NIHTransforms'
```

**Cause:** Transform name doesn't exist in BenchX

**Fix:**
Check available transforms:
```cmd
cd BenchX
python -c "from data.transforms import AVAILABLE_TRANSFORMS; print(AVAILABLE_TRANSFORMS)"
```

Use one of:
- `RSNATransforms` (for RSNA)
- `SIIMTransforms` (if available)
- `ChestXrayTransforms` (generic chest X-ray)
- Remove `transforms:` section to use defaults

---

### Issue 6: CUDA Out of Memory

**Symptoms:**
```
RuntimeError: CUDA out of memory
```

**Fix:**
Reduce batch size in configs:
```yaml
trainer:
  batch_size: 16  # or 8 if still failing
```

Or use gradient accumulation:
```yaml
trainer:
  batch_size: 16
  accumulate_grad_batches: 2  # effective batch = 32
```

---

### Issue 7: SHARP Encoder Architecture Mismatch

**Symptoms:**
```
RuntimeError: Error(s) in loading state_dict
```

**Cause:** SHARP's checkpoint structure doesn't match expected format

**Fix:**

Modify `BenchX/models/sharp.py`:

```python
# Add more flexible checkpoint loading:

def load_sharp_checkpoint(checkpoint_path):
    ckpt = torch.load(checkpoint_path, map_location='cpu')

    # Try different state dict keys
    if 'model_state_dict' in ckpt:
        state_dict = ckpt['model_state_dict']
    elif 'state_dict' in ckpt:
        state_dict = ckpt['state_dict']
    else:
        state_dict = ckpt

    # Try different encoder prefixes
    for prefix in ['image_encoder.', 'img_encoder.', 'encoder.', '']:
        encoder_state = {
            k.replace(prefix, ''): v
            for k, v in state_dict.items()
            if k.startswith(prefix)
        }
        if encoder_state:
            return encoder_state

    raise ValueError("Could not find image encoder in checkpoint")
```

---

## Diagnostic Commands

### Test 1: Verify BenchX Installation
```cmd
cd C:\Users\aya.alaswad\remote\BenchX
python -c "import torch; print('PyTorch:', torch.__version__)"
python -c "from data.datasets import RSNA_Pneumonia_Dataset; print('✓ Datasets OK')"
python -c "from models import ImageClassifier; print('✓ Models OK')"
```

### Test 2: Test SHARP Model Loading (Standalone)
```cmd
cd C:\Users\aya.alaswad\remote
python sharp_benchx_model.py
```

Expected: "✓ SHARP model test passed!"

### Test 3: Verify Dataset Preprocessing
```cmd
# SIIM
python debug_siim_data.py

# RSNA (if preprocessed)
dir C:\Users\aya.alaswad\remote\BenchX\datasets\RSNA\*.csv
dir C:\Users\aya.alaswad\remote\BenchX\datasets\RSNA\images\*.png
```

### Test 4: Test with a Known Working Model
```cmd
cd C:\Users\aya.alaswad\remote\BenchX

# Try ConVIRT (should work out-of-box)
python bin/train.py configs/classification/SIIM/convirt.yml
```

If ConVIRT works but SHARP doesn't, the issue is SHARP-specific.

---

## Step-by-Step Fresh Setup

If nothing works, start from scratch:

### 1. Clone/Update BenchX
```cmd
cd C:\Users\aya.alaswad\remote
git clone https://github.com/yangzhou12/BenchX.git
# or if already exists:
cd BenchX
git pull
```

### 2. Install Dependencies
```cmd
conda activate benchx  # or your env name
pip install -r requirements.txt
```

### 3. Verify Checkpoint
```cmd
python -c "import torch; ckpt = torch.load('D:/experiments/exp3_full_sharp/p3_best.pt'); print(ckpt.keys())"
```

### 4. Add SHARP Model
```cmd
copy C:\Users\aya.alaswad\remote\sharp_benchx_model.py BenchX\models\sharp.py
```

### 5. Prepare SIIM Dataset
```cmd
cd C:\Users\aya.alaswad\remote
python rebuild_siim_csv.py
```

### 6. Create Minimal Config

Save as `BenchX/configs/classification/SIIM/sharp_minimal.yml`:

```yaml
name: SHARP_SIIM
use_amp: True
seed: 42

dataset:
  proto: SIIM_Pneumothorax_Dataset
  data_path: C:\Users\aya.alaswad\remote\BenchX\datasets\SIIM
  csvpath: C:\Users\aya.alaswad\remote\BenchX\datasets\SIIM\siim_labels.csv
  extension: ".png"
  split: "train_1"
  num_workers: 2

model:
  proto: ImageClassifier
  cnn:
    proto: resnet50
    pretrained: D:/experiments/exp3_full_sharp/p3_best.pt
    freeze: False
  classifier:
    proto: Classifier
    num_classes: 2

trainer:
  optimizer: AdamW
  optim_params:
    lr: 1e-4
  batch_size: 16
  epochs: 10
  early_stop: 5

validator:
  batch_size: 32
  metrics: [binary_accuracy, binary_auroc]
```

### 7. Test Minimal Config
```cmd
cd BenchX
python bin/train.py configs/classification/SIIM/sharp_minimal.yml
```

---

## Quick Diagnostics Checklist

Run these commands and send me the output:

```cmd
# 1. Check PyTorch and CUDA
python -c "import torch; print(f'PyTorch: {torch.__version__}'); print(f'CUDA: {torch.cuda.is_available()}')"

# 2. Check checkpoint
dir D:\experiments\exp3_full_sharp\p3_best.pt

# 3. Check dataset
dir C:\Users\aya.alaswad\remote\BenchX\datasets\SIIM\images\*.png | find /c ".png"

# 4. Check BenchX structure
dir C:\Users\aya.alaswad\remote\BenchX\bin\train.py
dir C:\Users\aya.alaswad\remote\BenchX\models\
dir C:\Users\aya.alaswad\remote\BenchX\data\datasets.py
```

---

## Expected Output vs Errors

### Success Looks Like:
```
Epoch 1/30: 100%|██████████| 10/10 [00:15<00:00]
Train Loss: 0.6234
Val AUROC: 0.7234
Saving checkpoint to experiments/classification/siim/...
```

### Common Error Messages:

1. **"Dataset has 0 samples"** → Fix CSV/split mismatch (see Issue 1)
2. **"ModuleNotFoundError: models.sharp"** → Add SHARP model (see Issue 2)
3. **"Checkpoint not found"** → Wrong path (see Issue 3)
4. **"Missing key in state_dict"** → Checkpoint structure mismatch (see Issue 7)
5. **"CUDA out of memory"** → Reduce batch size (see Issue 6)

---

## Need More Help?

Send me:
1. The exact error message (full traceback)
2. Output of diagnostic commands above
3. Which step in `run_benchx_siim_rsna.bat` is failing
