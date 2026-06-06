"""
Quick BenchX diagnostic script
Run this to identify what's blocking your SHARP training
"""

import os
import sys

def check(condition, success_msg, fail_msg):
    """Print check result"""
    if condition:
        print(f"✓ {success_msg}")
        return True
    else:
        print(f"✗ {fail_msg}")
        return False

def main():
    print("="*80)
    print("BenchX SHARP Diagnostic (Remote Desktop)")
    print("="*80)
    print()

    # Auto-detect if we're on remote or local
    if os.path.exists(r"C:\Users\aya.alaswad"):
        base_path = r"C:\Users\aya.alaswad\remote"
        print("Detected: REMOTE DESKTOP")
    else:
        # Assume local development machine
        base_path = os.getcwd()
        print("Detected: LOCAL MACHINE")
        print("NOTE: This diagnostic should be run on the REMOTE DESKTOP where BenchX is installed")
        print()

    print(f"Base path: {base_path}")
    print()

    issues = []

    # 1. Python environment
    print("1. Python Environment")
    try:
        import torch
        print(f"   ✓ PyTorch {torch.__version__}")
        print(f"   ✓ CUDA available: {torch.cuda.is_available()}")
        if torch.cuda.is_available():
            print(f"   ✓ GPU: {torch.cuda.get_device_name(0)}")
    except ImportError:
        print("   ✗ PyTorch not installed")
        issues.append("Install PyTorch: pip install torch torchvision")
    print()

    # 2. BenchX installation
    print("2. BenchX Installation")
    benchx_path = os.path.join(base_path, "BenchX")
    if os.path.exists(benchx_path):
        print(f"   ✓ BenchX directory exists: {benchx_path}")

        # Check key files
        train_script = os.path.join(benchx_path, "bin", "train.py")
        if os.path.exists(train_script):
            print(f"   ✓ Training script found")
        else:
            print(f"   ✗ Training script missing: {train_script}")
            issues.append("BenchX not properly cloned")

        # Check if SHARP model exists
        sharp_model = os.path.join(benchx_path, "models", "sharp.py")
        if os.path.exists(sharp_model):
            print(f"   ✓ SHARP model integrated: {sharp_model}")
        else:
            print(f"   ✗ SHARP model missing: {sharp_model}")
            issues.append("Copy sharp_benchx_model.py to BenchX/models/sharp.py")
    else:
        print(f"   ✗ BenchX not found at: {benchx_path}")
        issues.append("Clone BenchX: git clone https://github.com/yangzhou12/BenchX.git")
    print()

    # 3. SHARP checkpoint
    print("3. SHARP Checkpoint")
    checkpoint_path = r"D:\experiments\exp3_full_sharp\p3_best.pt"
    if os.path.exists(checkpoint_path):
        print(f"   ✓ Checkpoint exists: {checkpoint_path}")
        try:
            import torch
            ckpt = torch.load(checkpoint_path, map_location='cpu')
            print(f"   ✓ Checkpoint loads successfully")
            print(f"   ✓ Keys in checkpoint: {list(ckpt.keys())}")
            if 'model_state_dict' in ckpt:
                state_dict = ckpt['model_state_dict']
                img_encoder_keys = [k for k in state_dict.keys() if 'image_encoder' in k or 'img_encoder' in k]
                if img_encoder_keys:
                    print(f"   ✓ Found {len(img_encoder_keys)} image encoder parameters")
                else:
                    print(f"   ✗ No image_encoder keys found in state_dict")
                    issues.append("Checkpoint may not have image encoder weights")
        except Exception as e:
            print(f"   ✗ Error loading checkpoint: {e}")
            issues.append(f"Checkpoint loading error: {e}")
    else:
        print(f"   ✗ Checkpoint not found: {checkpoint_path}")
        issues.append("Verify checkpoint path in configs")
    print()

    # 4. SIIM dataset
    print("4. SIIM Dataset")
    siim_path = os.path.join(base_path, "BenchX", "datasets", "SIIM")
    if os.path.exists(siim_path):
        print(f"   ✓ SIIM directory exists: {siim_path}")

        # Check images
        images_dir = os.path.join(siim_path, "images")
        if os.path.exists(images_dir):
            import glob
            images = glob.glob(os.path.join(images_dir, "*.png"))
            print(f"   ✓ Images directory: {len(images)} PNG files")
        else:
            print(f"   ✗ Images directory not found: {images_dir}")
            issues.append("SIIM images not preprocessed")

        # Check CSV
        csv_path = os.path.join(siim_path, "siim_labels.csv")
        if os.path.exists(csv_path):
            print(f"   ✓ Labels CSV exists")
            try:
                import pandas as pd
                df = pd.read_csv(csv_path)
                print(f"   ✓ CSV has {len(df)} rows")
                if 'new_filename' in df.columns and 'has_pneumo' in df.columns:
                    print(f"   ✓ CSV has required columns")
                else:
                    print(f"   ✗ CSV missing required columns")
                    print(f"      Found: {df.columns.tolist()}")
                    issues.append("Run rebuild_siim_csv.py to fix CSV format")
            except Exception as e:
                print(f"   ✗ Error reading CSV: {e}")
        else:
            print(f"   ✗ Labels CSV not found: {csv_path}")
            issues.append("Run rebuild_siim_csv.py to create CSV")

        # Check split file
        split_path = os.path.join(siim_path, "train_1.txt")
        if os.path.exists(split_path):
            with open(split_path, 'r') as f:
                split_entries = [line.strip() for line in f]
            print(f"   ✓ Split file exists: {len(split_entries)} entries")
        else:
            print(f"   ✗ Split file not found: {split_path}")
            issues.append("SIIM split files missing")
    else:
        print(f"   ✗ SIIM directory not found: {siim_path}")
        issues.append("SIIM dataset not preprocessed")
    print()

    # 5. Config files
    print("5. Config Files")
    configs = [
        os.path.join(base_path, "sharp_siim_final.yml"),
        os.path.join(base_path, "sharp_rsna_final.yml"),
    ]
    for cfg in configs:
        if os.path.exists(cfg):
            print(f"   ✓ {os.path.basename(cfg)}")
        else:
            print(f"   ✗ {os.path.basename(cfg)} not found")
    print()

    # Summary
    print("="*80)
    if issues:
        print("ISSUES FOUND:")
        print()
        for i, issue in enumerate(issues, 1):
            print(f"{i}. {issue}")
        print()
        print("Fix these issues before running BenchX training.")
    else:
        print("✓ ALL CHECKS PASSED!")
        print()
        print("You're ready to run:")
        print(f"  cd {base_path}")
        print("  run_benchx_siim_rsna.bat")
    print("="*80)

if __name__ == "__main__":
    main()
