# BenchX Data Download Instructions

## Overview
You need to download 4 datasets for BenchX evaluation. Download in this order (easiest to hardest).

**Total size:** ~150 GB
**Total download time:** 2-4 hours (depending on connection)

---

## 1. SIIM-ACR Pneumothorax (Easiest - Kaggle)
**Size:** ~12k images (~12 GB)
**Time:** ~30 minutes
**Difficulty:** Easy (Kaggle account only)

### Steps:
1. Go to: https://www.kaggle.com/c/siim-acr-pneumothorax-segmentation
2. Click "Download All" (requires Kaggle account + competition acceptance)
3. Extract to: `D:\datasets\siim-pneumothorax\`

### Kaggle CLI (Alternative):
```bash
pip install kaggle
kaggle competitions download -c siim-acr-pneumothorax-segmentation
unzip siim-acr-pneumothorax-segmentation.zip -d D:\datasets\siim-pneumothorax\
```

---

## 2. RSNA Pneumonia Detection (Easy - Kaggle)
**Size:** ~30k images (~30 GB)
**Time:** ~1 hour
**Difficulty:** Easy (Kaggle account only)

### Steps:
1. Go to: https://www.kaggle.com/c/rsna-pneumonia-detection-challenge
2. Click "Download All"
3. Extract to: `D:\datasets\rsna-pneumonia\`

### Kaggle CLI (Alternative):
```bash
kaggle competitions download -c rsna-pneumonia-detection-challenge
unzip rsna-pneumonia-detection-challenge.zip -d D:\datasets\rsna-pneumonia\
```

---

## 3. VinDr-CXR (Medium - PhysioNet Credentialed)
**Size:** ~18k images (~18 GB)
**Time:** ~30 minutes download + 1-2 days credential approval
**Difficulty:** Medium (requires PhysioNet credentialed access)

### Steps:

**A. Get PhysioNet Credentials (if you don't have):**
1. Go to: https://physionet.org/
2. Create account
3. Complete CITI training course (required for credentialed datasets)
4. Wait for approval (~1-2 business days)

**B. Request VinDr-CXR Access:**
1. Go to: https://physionet.org/content/vindr-cxr/1.0.0/
2. Click "Request Access"
3. Sign data use agreement
4. Wait for approval (~1-2 days)

**C. Download:**
```bash
# After approval, download using wget (provided by PhysioNet)
wget -r -N -c -np --user YOUR_USERNAME --ask-password https://physionet.org/files/vindr-cxr/1.0.0/

# Or use PhysioNet's download page directly
# Extract to: D:\datasets\vindr-cxr\
```

**Note:** You already have MIMIC-CXR credentialed access, so the CITI training is done. Just request VinDr-CXR specifically.

---

## 4. NIH ChestX-ray14 (Hardest - Large Download)
**Size:** ~112k images (~45 GB)
**Time:** ~2 hours download
**Difficulty:** Hard (large file, slow NIH servers)

### Option A: Official NIH (Slow but Free)
```bash
# Download from NIH Clinical Center
wget https://nihcc.app.box.com/s/vua1c08qnvhhcwpd8l2l/folder/36938765345

# Extract to: D:\datasets\nih-chestxray14\
```

### Option B: HuggingFace Mirror (Faster - Recommended)
```bash
pip install huggingface_hub

# Download using HF CLI
huggingface-cli download alkzar90/NIH-Chest-X-ray-dataset --repo-type dataset --local-dir D:\datasets\nih-chestxray14\
```

### Option C: Kaggle Mirror (Easiest)
```bash
kaggle datasets download -d nih-chest-xrays/data
unzip data.zip -d D:\datasets\nih-chestxray14\
```

---

## After Downloading All 4 Datasets

### Verify Directory Structure:
```
D:\datasets\
├── rsna-pneumonia\
│   ├── stage_2_train_images\
│   └── stage_2_train_labels.csv
├── siim-pneumothorax\
│   ├── train\
│   └── train-rle.csv
├── vindr-cxr\
│   ├── train\
│   ├── test\
│   └── annotations\
└── nih-chestxray14\
    ├── images\
    └── Data_Entry_2017.csv
```

### Run BenchX Preprocessing:
```bash
cd C:\Users\aya.alaswad\remote\BenchX

# Preprocess each dataset (creates train/val/test splits)
python preprocess/rsna_preprocess.py --data_root D:/datasets/rsna-pneumonia
python preprocess/siim_preprocess.py --data_root D:/datasets/siim-pneumothorax
python preprocess/vindr_preprocess.py --data_root D:/datasets/vindr-cxr
python preprocess/nih_preprocess.py --data_root D:/datasets/nih-chestxray14
```

**Important:** BenchX's preprocessing creates the exact train/val/test splits used by all 9 baselines. This ensures fair comparison.

---

## Quick Start Recommendation

**If you want to start FAST:**
1. Download **SIIM only** (~30 min) - smallest dataset
2. Run SHARP on SIIM to test integration
3. While results run, download RSNA, VinDr, NIH in parallel

**Full timeline:**
- SIIM: 30 min download + 30 min training = **1 hour to first result**
- RSNA: 1 hour download + 1 hour training = **2 hours**
- VinDr: 30 min download + 1 hour training = **1.5 hours** (+ credential wait)
- NIH: 2 hours download + 4 hours training = **6 hours**

**Total:** ~10 hours (most of it is download + GPU time, not hands-on)

---

## Troubleshooting

**Kaggle API not working:**
```bash
# Create ~/.kaggle/kaggle.json with your API token
{
  "username": "YOUR_USERNAME",
  "key": "YOUR_API_KEY"
}
```

**PhysioNet download fails:**
- Make sure you completed CITI training
- Check your credentialed status: https://physionet.org/settings/credentialing/
- VinDr-CXR requires separate approval even if you have MIMIC-CXR access

**NIH download too slow:**
- Use HuggingFace or Kaggle mirrors (much faster)
- Kaggle version is pre-split and easiest to use

---

## Next Step After Download

Once all datasets are downloaded and preprocessed:
```batch
cd C:\Users\aya.alaswad\remote\MyReasearch
benchx_run_all.bat
```

This will run SHARP on all 4 datasets sequentially.
