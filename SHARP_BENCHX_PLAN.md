# SHARP → BenchX Integration Plan

## The Goal

Evaluate **SHARP's pretrained ViT-B/16 encoder** on BenchX classification tasks (SIIM, RSNA) to see how it compares to other medical imaging encoders.

## The Architecture Issue

**SHARP uses:**
- Encoder: ViT-B/16 (768-dim features)
- Projection: 768 → 512 → 256
- Final embedding: 256-dim (for contrastive learning)

**BenchX expects:**
- Encoder: ResNet50 or ViT (768-dim features from ViT)
- Classifier: Linear layer on top (768 → num_classes)

## The Problem

Your current config uses:
```yaml
includes:
  - configs/_base_/models/convirt.yml  # Probably specifies ResNet50
```

This imports ConVIRT's config, which likely uses **ResNet50**, not ViT.

## Two Approaches

### Approach 1: Test Architecture Pipeline First ✅ **START HERE**

**Goal:** Verify BenchX works with ViT-B/16 architecture

**Config:** `sharp_siim_vit.yml` (I just created this)
- Uses ViT-B/16 (same architecture as SHARP)
- Loads ImageNet pretrained weights (not SHARP)
- This is just to verify the pipeline works

**Run on remote:**
```cmd
cd C:\Users\aya.alaswad\remote
git pull
copy sharp_siim_vit.yml BenchX\configs\classification\SIIM\sharp.yml /Y
cd BenchX
python bin/train.py configs/classification/SIIM/sharp.yml
```

**Expected result:**
- Trains successfully with ViT-B/16
- Gets some baseline AUROC (maybe 0.6-0.7)
- Proves BenchX can handle ViT architecture

### Approach 2: Load SHARP Checkpoint Properly 🎯 **AFTER APPROACH 1 WORKS**

Once we confirm ViT works, we load SHARP's weights.

**Option A: Extract encoder to compatible format**

Run on remote:
```cmd
python extract_sharp_encoder.py
```

This creates `D:\experiments\sharp_vit_encoder.pt` with just the ViT weights (no projection head).

Then modify config:
```yaml
cnn:
  proto: vit_base_patch16_224
  pretrained: D:/experiments/sharp_vit_encoder.pt
```

**Option B: Custom model class (more complex)**

Create a custom PyTorch model that:
1. Loads SHARP's full checkpoint
2. Uses only the ViT encoder part
3. Adds classification head

This requires modifying BenchX's model code.

## Why This Two-Step Approach?

**Step 1 (ViT + ImageNet):**
- ✅ Verifies BenchX works
- ✅ Verifies dataset loading fixed
- ✅ Gives you a baseline to beat
- ✅ Fast to test (no custom loading logic)

**Step 2 (ViT + SHARP weights):**
- 🎯 What you actually want
- 🎯 Tests SHARP's learned representations
- 🎯 Compares to ImageNet baseline

## Comparison Matrix

After both steps, you'll have:

| Encoder | SIIM AUROC | RSNA AUROC | Notes |
|---------|------------|------------|-------|
| ViT-B/16 (ImageNet) | ??? | ??? | Baseline |
| ViT-B/16 (SHARP) | ??? | ??? | Your method |
| ConVIRT (from paper) | ??? | ??? | Published |
| MGCA (from paper) | ??? | ??? | Published |

This shows if SHARP's contrastive learning improves over ImageNet initialization.

## What I Recommend Right Now

1. **Push the new files to GitHub:**
   ```cmd
   # On local
   git add extract_sharp_encoder.py sharp_siim_vit.yml SHARP_BENCHX_PLAN.md
   git commit -m "Add SHARP ViT encoder extraction and proper config"
   git push
   ```

2. **On remote, test ViT baseline:**
   ```cmd
   git pull
   copy sharp_siim_vit.yml BenchX\configs\classification\SIIM\sharp.yml /Y
   cd BenchX
   python bin/train.py configs/classification/SIIM/sharp.yml
   ```

3. **If that works, extract SHARP encoder:**
   ```cmd
   python extract_sharp_encoder.py
   ```

4. **Then test SHARP encoder:**
   Update config to use extracted checkpoint and re-run.

## Expected Outcomes

**ViT + ImageNet baseline:** AUROC ~0.65-0.75
**ViT + SHARP:** AUROC should be **higher** (that's the whole point!)

If SHARP < ImageNet, that means:
- Either SHARP's pretraining didn't help
- Or there's a domain mismatch (MIMIC-CXR → SIIM/RSNA)

If SHARP > ImageNet, that's your result! "SHARP's contrastive pretraining improves downstream classification by X%"

---

**Ready to try Approach 1 (ViT baseline)?** This will tell us if the architecture works before we worry about loading SHARP's checkpoint.
