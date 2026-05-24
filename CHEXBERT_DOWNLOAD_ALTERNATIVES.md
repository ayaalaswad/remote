# CheXbert Download - Alternative Methods for Restricted Countries

**Issue**: Google Drive is blocked in some countries (China, Iran, etc.)

**File needed**: `chexbert.pth` (438 MB)

**Destination**: `C:\Users\aya.alaswad\remote\checkpoints\stanford\chexbert\chexbert.pth`

---

## Method 1: Direct Download from PhysioNet (RECOMMENDED)

CheXbert is hosted on PhysioNet (medical research repository):

```cmd
REM Install wget if you don't have it
wget https://physionet.org/files/chest-imagenome/1.0.0/silver_dataset/scene_tabular/chexbert.pth -O checkpoints\stanford\chexbert\chexbert.pth
```

---

## Method 2: Use Hugging Face (Mirror)

Hugging Face often works in restricted countries:

```cmd
wget https://huggingface.co/datasets/StanfordAIMI/chest-imagenome/resolve/main/chexbert.pth -O checkpoints\stanford\chexbert\chexbert.pth
```

---

## Method 3: Use VPN + Google Drive

1. Connect to a VPN (US/Europe server)
2. Run the gdown command:
   ```cmd
   gdown 1DS6NYirOXQf8qYieSVMvqNwuOlgAbM_E -O checkpoints\stanford\chexbert\chexbert.pth
   ```

---

## Method 4: Browser Download (Manual)

If automated downloads fail:

1. **Open this URL in browser** (try with VPN if blocked):
   https://drive.google.com/file/d/1DS6NYirOXQf8qYieSVMvqNwuOlgAbM_E/view

2. **Or try PhysioNet**:
   https://physionet.org/content/chest-imagenome/1.0.0/

3. **Download the file** (438 MB)

4. **Move to the correct location**:
   ```cmd
   move Downloads\chexbert.pth C:\Users\aya.alaswad\remote\checkpoints\stanford\chexbert\
   ```

---

## Method 5: Request from Colleague/Friend

If all else fails:
1. Ask a colleague in unrestricted country to download it
2. Transfer via:
   - Dropbox
   - OneDrive
   - WeTransfer
   - SSH/SFTP
   - USB drive

---

## Verify Download

After download, verify the file:

```cmd
python -c "from pathlib import Path; p = Path('checkpoints/stanford/chexbert/chexbert.pth'); print(f'✓ Downloaded: {p.stat().st_size / (1024**2):.1f} MB') if p.exists() and p.stat().st_size > 400*1024*1024 else print('✗ File missing or too small')"
```

**Expected**: `✓ Downloaded: 438.2 MB`

---

## If All Methods Fail

**Option A**: Skip CheXbert evaluation temporarily
- Complete Stage 1 analysis (Phase 1 t-SNE/UMAP)
- Write rebuttal with Stage 1 results only
- Promise Stage 2 results in camera-ready

**Option B**: Use alternative evaluation
- BLEU/ROUGE/METEOR scores (don't need CheXbert)
- RadGraph F1 (alternative clinical metric)
- Human evaluation

**Option C**: Contact Stanford directly
- Email: stanfordmlgroup@cs.stanford.edu
- Explain you're in restricted country
- Request alternative download link

---

## Recommended Order

Try in this order:
1. **Method 2** (Hugging Face) - Most likely to work
2. **Method 4** (Browser + VPN) - Manual but reliable
3. **Method 5** (Colleague) - Last resort

---

**Which country are you in?** This helps me recommend the best method.
