# SHARP Large Batch Experiment

Batch size experiments for SHARP (Scene-graph Supervised Hierarchical Attention for Radiology Report Generation) training to validate multi-positive InfoNCE hypothesis.

## 🎯 Hypothesis

**Problem**: Multi-positive InfoNCE performed worse than symmetric InfoNCE baseline with batch_size=32.

**Root Cause**: Batch too small → few co-positives → MP-InfoNCE reduces to standard InfoNCE.

**Solution**: Test batch_size=512 → expect many co-positives → MP-InfoNCE advantage.

## 📁 Repository Contents

### Training Scripts
- **`train_sharp_large_batch.py`** - Main training script (batch=512 default)
- **`check_gpu.py`** - GPU verification script
- **`check_gpu.bat`** - Windows GPU check (double-click)
- **`explore_concept_keys.py`** - Data exploration tool

### Documentation
- **`START_TRAINING.md`** - Quick start guide
- **`GPU_SETUP_GUIDE.md`** - GPU troubleshooting
- **`SHARP_BATCH_EXPERIMENT_README.md`** - Full documentation
- **`BATCH_EXPERIMENT_QUICK_START.md`** - Quick reference
- **`CONCEPT_KEY_GUIDE.md`** - Understanding concept keys

### Configuration
- **`requirements.txt`** - Python dependencies
- **`.gitignore`** - Git ignore rules

## 🚀 Quick Start

### 1. Clone Repository
```bash
git clone https://github.com/YOUR_USERNAME/sharp-batch-experiments.git
cd sharp-batch-experiments
```

### 2. Install Dependencies
```bash
# Install PyTorch with CUDA support (GPU version)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Install other dependencies
pip install -r requirements.txt
```

### 3. Check GPU
```bash
python check_gpu.py
```

Expected output:
```
✅ SUMMARY - GPU READY FOR TRAINING
Your GPU: NVIDIA RTX A5000
VRAM: 24.0 GB
Recommended batch size: 512
```

### 4. Download Data

**MIMIC-CXR** (~400 GB):
- Register at https://physionet.org/
- Download: https://physionet.org/content/mimic-cxr-jpg/2.1.0/

**MIMIC-Ext Scene Graphs** (1.1 GB):
- Download: https://physionet.org/content/mimic-ext-cxr-qba/1.0.0/
- Extract `scene_data.zip`

### 5. Run Training

**Quick test (5 minutes)**:
```bash
python train_sharp_large_batch.py \
  --scene_dir ./scene_data \
  --image_dir ./mimic-cxr-jpg \
  --split_csv ./mimic-cxr-2.0.0-split.csv.gz \
  --output_dir ./test_run \
  --batch_size 512 \
  --total_steps 100 \
  --eval_every 50
```

**Full training (10-12 hours)**:
```bash
python train_sharp_large_batch.py \
  --scene_dir ./scene_data \
  --image_dir ./mimic-cxr-jpg \
  --split_csv ./mimic-cxr-2.0.0-split.csv.gz \
  --output_dir ./sharp_experiments/batch_512 \
  --batch_size 512
```

## 📊 Expected Results

### Multi-Positive InfoNCE Statistics
- **batch=32**: Avg 0.5 co-positives/anchor, ~20% with co-positives
- **batch=512**: Avg 3.5 co-positives/anchor, ~68% with co-positives ✅

### Validation Performance
- **batch=32 baseline**: I→T R@1 ~35-40%
- **batch=512 target**: I→T R@1 >45%

### Downstream Task
- **Target CheXbert F1**: >0.315 (beats RAD-DINO baseline 0.3136)

## 🔑 Key Innovation

**Concept Keys**: `(region, entity, polarity)`
- Example: `("right lung", "opacity", "pos")`
- Multi-positive: Same key → positives, different key → negatives
- Hard negatives: Same region/entity, opposite polarity

## 💻 Hardware Requirements

| Batch Size | VRAM Needed | Recommended GPU |
|------------|-------------|-----------------|
| 512 | ~22 GB | RTX A5000, A6000, 4090 |
| 256 × 2 | ~22 GB | Same (effective 512) |
| 128 × 4 | ~20 GB | RTX 3090, A5000 |
| 64 × 8 | ~16 GB | RTX 3080, 4080 |

## 📚 Documentation

- **[START_TRAINING.md](START_TRAINING.md)** - Step-by-step training guide
- **[GPU_SETUP_GUIDE.md](GPU_SETUP_GUIDE.md)** - GPU troubleshooting
- **[CONCEPT_KEY_GUIDE.md](CONCEPT_KEY_GUIDE.md)** - Understanding the data
- **[SHARP_BATCH_EXPERIMENT_README.md](SHARP_BATCH_EXPERIMENT_README.md)** - Full experiment details

## 🛠️ Troubleshooting

### CUDA Out of Memory
```bash
# Reduce batch size, increase grad accumulation
python train_sharp_large_batch.py --batch_size 256 --grad_accum 2
```

### Training on CPU (slow)
```bash
# Reinstall PyTorch GPU version
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118 --force-reinstall
```

### Scene files not found
```bash
# Use absolute paths
python train_sharp_large_batch.py --scene_dir /full/path/to/scene_data
```

## 📖 References

**Multi-Positive InfoNCE**:
- Khosla et al., "Supervised Contrastive Learning", NeurIPS 2020

**MIMIC-Ext Dataset**:
- https://physionet.org/content/mimic-ext-cxr-qba/1.0.0/

**Related Work**:
- SHARP (your MICCAI submission)
- RAD-DINO: Domain-pretrained ViT for radiology
- CXRMate: Report generation baseline

## 📝 Citation

If you use this code, please cite:

```bibtex
@article{sharp2024,
  title={SHARP: Scene-graph Supervised Hierarchical Attention for Radiology Report Generation},
  author={Your Name},
  year={2024}
}
```

## 📄 License

[Add your license here]

## 🙏 Acknowledgments

- MIMIC-CXR dataset from MIT-LCP
- MIMIC-Ext annotations
- PyTorch and Hugging Face teams

---

**Status**: Ready for training ✅

**Expected completion time**: 10-12 hours on RTX A5000

**Target**: Validate MP-InfoNCE hypothesis with large batches
