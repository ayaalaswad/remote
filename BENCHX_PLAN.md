# BenchX Evaluation Plan - After RadDINO

**Purpose:** Benchmark SHARP's pretrained encoder against 9 baselines on 4 downstream classification datasets (RSNA, SIIM, NIH, VinDr-CXR).

**Why:** Supervisor wants to see where SHARP stands on image representation benchmarks beyond report generation.

**Timeline:** Start after RadDINO training completes (~Week 1 Day 5-7 or Week 2).

---

## What BenchX Tests

**4 Classification Datasets:**
1. RSNA Pneumonia Detection (~30k images, Kaggle)
2. SIIM-ACR Pneumothorax (~12k images, Kaggle)
3. VinDr-CXR (18k images, PhysioNet - credentialed)
4. NIH ChestX-ray14 (~112k images - heaviest)

**9 Baseline Methods (AUROC from BenchX paper):**
- ConVIRT, GLoRIA (CheXpert pretraining)
- MGCA, MRM, MedKLIP, M-FLAG, REFERS, MedCLIP, PTUnifier (MIMIC-CXR pretraining)

**Output:** AUROC for SHARP vs baselines on identical protocol

---

## Setup Required (Before Running)

### 1. Environment Setup
```bash
cd C:\Users\aya.alaswad\remote
git clone https://github.com/yangzhou12/BenchX.git
cd BenchX
conda create -n benchx python=3.10 -y
conda activate benchx
pip install -r requirements.txt
```

### 2. Data Download & Preprocessing

**Easy (Kaggle):**
- RSNA Pneumonia: https://www.kaggle.com/c/rsna-pneumonia-detection-challenge
- SIIM-ACR Pneumothorax: https://www.kaggle.com/c/siim-acr-pneumothorax-segmentation

**Requires PhysioNet Credentials:**
- VinDr-CXR: https://physionet.org/content/vindr-cxr/1.0.0/
- Already have MIMIC-CXR access

**NIH ChestX-ray14:**
- Download from NIH or HuggingFace mirror
- Largest dataset (~112k images)

**Critical:** Use BenchX's preprocessing scripts to ensure exact train/val/test splits match baselines.

### 3. Register SHARP in BenchX

**Add SHARP model wrapper:**
```python
# BenchX/models/sharp.py (new file)
class SHARP(nn.Module):
    def __init__(self, checkpoint_path):
        super().__init__()
        # Load SHARP's pretrained encoder
        ckpt = torch.load(checkpoint_path)
        self.encoder = ImageEncoderViT(embedding_dim=256)  # or your encoder
        self.encoder.load_state_dict(ckpt['model_state_dict'])

    def forward(self, x):
        # Return features for classification head
        return self.encoder(x)  # Shape: (batch, embed_dim)
```

**Which SHARP checkpoint to use:**
- Best option: **Exp #3** (D:\experiments\exp3_hardneg\p3_best.pt) - 37.4% F1, best downstream
- Alternative: **Exp #4 v2a** (D:\experiments\exp4_v2a_matched_epochs\p3_best.pt) - 8.77% R@1, best retrieval
- After RadDINO: **RadDINO Exp #3** for encoder robustness comparison

### 4. Create SHARP Config Files

```bash
cd BenchX/configs/classification

# Copy MGCA configs (closest baseline - MIMIC-CXR pretrained)
cp rsna/mgca.yml rsna/sharp.yml
cp siim/mgca.yml siim/sharp.yml
cp nih/mgca.yml nih/sharp.yml
cp vindr/mgca.yml vindr/sharp.yml
```

**In each sharp.yml, change only:**
```yaml
model:
  name: sharp
  checkpoint: D:/experiments/exp3_hardneg/p3_best.pt
  backbone: vit_base  # or resnet50 - match baselines
```

**Keep identical:**
- Image size: 224 (or whatever MGCA uses)
- Optimizer: AdamW
- Learning rate schedule
- Augmentation
- Label fraction (test 1%, 10%, 100%)
- Batch size

---

## Execution Plan

### Phase 1: Quick Test (SIIM - smallest dataset)
**Why:** Verify SHARP integration works before running all 4 datasets

```bash
conda activate benchx
cd C:\Users\aya.alaswad\remote\BenchX

# Test SHARP on SIIM (12k images, fastest)
python bin/train.py configs/classification/siim/sharp.yml --label_fraction 1.0
```

**Expected runtime:** ~30-60 minutes (1 GPU)
**Success criteria:** Training completes, AUROC logged

### Phase 2: Full Evaluation (All 4 Datasets)

**Order by size (fast → slow):**
```bash
# 1. SIIM (~30-60 min)
python bin/train.py configs/classification/siim/sharp.yml --label_fraction 1.0

# 2. RSNA (~1-2 hours)
python bin/train.py configs/classification/rsna/sharp.yml --label_fraction 1.0

# 3. VinDr (~1-2 hours)
python bin/train.py configs/classification/vindr/sharp.yml --label_fraction 1.0

# 4. NIH (~4-6 hours - largest)
python bin/train.py configs/classification/nih/sharp.yml --label_fraction 1.0
```

**Total GPU time:** ~8-12 hours for all 4 datasets (100% labels)

### Phase 3: Label Efficiency Curve (Optional)

**If time permits, test low-data regime:**
```bash
# 1% labels
python bin/train.py configs/classification/rsna/sharp.yml --label_fraction 0.01

# 10% labels
python bin/train.py configs/classification/rsna/sharp.yml --label_fraction 0.10

# 100% labels (already done in Phase 2)
```

**Why:** Shows SHARP's sample efficiency vs baselines

---

## Expected Results Format

**Extract AUROC from each run:**
```
RSNA:  SHARP AUROC = ___%  vs  MGCA AUROC = ___%  (from BenchX paper)
SIIM:  SHARP AUROC = ___%  vs  MGCA AUROC = ___%
NIH:   SHARP AUROC = ___%  vs  MGCA AUROC = ___%
VinDr: SHARP AUROC = ___%  vs  MGCA AUROC = ___%
```

**Baseline numbers from BenchX paper (Table X):**
- Don't re-run baselines - use published BenchX results
- Cite: Zhou et al., "BenchX: A Unified Benchmark for Medical Vision-Language Pretraining", NeurIPS 2024

**Add to experiments.md:**
```markdown
## BenchX Downstream Classification

| Dataset | SHARP | MGCA | MRM | MedKLIP | Best Baseline |
|---------|-------|------|-----|---------|---------------|
| RSNA    | ___%  | ___%  | ___%  | ___%  | ___%  |
| SIIM    | ___%  | ___%  | ___%  | ___%  | ___%  |
| NIH     | ___%  | ___%  | ___%  | ___%  | ___%  |
| VinDr   | ___%  | ___%  | ___%  | ___%  | ___%  |

*Baseline numbers from BenchX (Zhou et al., NeurIPS 2024)*
```

---

## Compute Requirements

**Hardware:**
- 1 GPU with ≥16 GB VRAM (your RTX 4090 is perfect)
- No multi-GPU needed (downstream eval, not pretraining)

**Time Breakdown:**
- Data download & preprocessing: 2-4 hours (one-time)
- SHARP integration: 1-2 hours (coding)
- Phase 1 (SIIM test): 1 hour
- Phase 2 (all 4 datasets): 8-12 hours GPU time
- Phase 3 (label efficiency): +4-6 hours per dataset (optional)

**Total:** 1-2 days wall time (mostly GPU runs in background)

---

## Success Criteria

**Minimum (for paper):**
- ✓ SHARP runs on all 4 BenchX datasets
- ✓ AUROC numbers comparable to baselines
- ✓ Same protocol (BenchX splits, no extra tuning)

**Strong result:**
- SHARP matches or beats MGCA/MRM (MIMIC-CXR baselines)
- Competitive with best baseline (within 1-2 AUROC points)

**Excellent result:**
- SHARP beats all MIMIC-CXR baselines
- Shows label efficiency (good at 1%, 10%)

**Paper contribution:**
- Validates SHARP's image representations generalize beyond report generation
- Direct comparison to 9 published methods on standard benchmarks
- Addresses supervisor's concern about representation quality

---

## Integration with Current Work

**After RadDINO completes, you'll have:**
1. **Stage 1 experiments:** R@1 retrieval metrics
2. **Stage 2 experiments:** CheXbert F1 (clinical report quality)
3. **BenchX evaluation:** AUROC on classification (image representation quality)

**This gives 3 complementary evaluation angles:**
- Retrieval: How well does SHARP match images to reports?
- Report generation: How clinically accurate are generated reports?
- Classification: How good are SHARP's learned image features?

**Paper structure:**
```
Abstract: Multi-positive InfoNCE + hard negatives for medical VLP
Stage 1 Results: Retrieval metrics (R@1)
Stage 2 Results: Report generation (CheXbert F1) - MAIN RESULT
BenchX Results: Classification (AUROC) - ROBUSTNESS CHECK
Ablations: Exp #2/2b (co-positive frequency), RadDINO (encoder choice)
```

---

## Risks & Mitigation

**Risk 1: Data access delays**
- VinDr requires PhysioNet credentialing (~1-2 days approval)
- Mitigation: Start with RSNA/SIIM (Kaggle, instant)

**Risk 2: SHARP integration issues**
- BenchX expects specific encoder output format
- Mitigation: Test on SIIM first (Phase 1), debug before running all

**Risk 3: Poor results**
- SHARP might underperform on classification (optimized for report generation)
- Mitigation: Frame as "complementary evaluation" not "main result"

**Risk 4: Time pressure**
- Workshop deadline 2026-07-07 (5 weeks away)
- Mitigation: BenchX is Week 2 work, after critical experiments done

---

## Next Steps (After RadDINO)

**Week 1 Day 5-7 (While analyzing RadDINO results):**
1. Clone BenchX repo
2. Set up conda environment
3. Start data downloads (RSNA, SIIM, VinDr)

**Week 2 Day 1-2:**
1. Finish data preprocessing
2. Integrate SHARP into BenchX
3. Run Phase 1 test (SIIM)

**Week 2 Day 3-5:**
1. Run Phase 2 (all 4 datasets)
2. Extract AUROC results
3. Add to experiments.md

**Week 2 Day 6-7 (Optional):**
1. Label efficiency curves (1%, 10%, 100%)
2. Multiple seeds for error bars

**Week 3:**
- Focus on paper writing
- BenchX results go in Section X (robustness evaluation)

---

## File Checklist

**Before running:**
- [ ] BenchX repo cloned
- [ ] Conda environment set up
- [ ] RSNA dataset downloaded + preprocessed
- [ ] SIIM dataset downloaded + preprocessed
- [ ] VinDr dataset downloaded + preprocessed
- [ ] NIH dataset downloaded + preprocessed
- [ ] SHARP model wrapper added to BenchX
- [ ] 4 config files created (sharp.yml for each dataset)
- [ ] Checkpoint path verified (Exp #3 p3_best.pt)

**After running:**
- [ ] RSNA AUROC extracted
- [ ] SIIM AUROC extracted
- [ ] NIH AUROC extracted
- [ ] VinDr AUROC extracted
- [ ] Baseline numbers copied from BenchX paper
- [ ] Results added to experiments.md
- [ ] Comparison table created

---

## Contact Info for Issues

**BenchX repo:** https://github.com/yangzhou12/BenchX
**BenchX paper:** Zhou et al., NeurIPS 2024
**Issues:** Check repo's GitHub Issues or contact authors

**SHARP side:**
- Use Exp #3 checkpoint: `D:\experiments\exp3_hardneg\p3_best.pt`
- Encoder: ViT-B/16 (ImageNet pretrained, fine-tuned with SHARP)
- Output dim: 256d (after projection head)

---

**Status:** PLANNED - Execute after RadDINO training completes
**Priority:** HIGH (supervisor request)
**Estimated start:** Week 1 Day 5-7 or Week 2 Day 1
