#!/usr/bin/env python3
"""
Verify RadDINO setup before running experiments.

Checks:
1. RadDINO model is downloaded and accessible
2. Dependencies are installed
3. Script syntax is valid
4. Can initialize model without errors
"""

import sys
import torch

def check_raddino_available():
    """Check if RadDINO model is accessible."""
    try:
        from transformers import AutoModel
        print("[OK] transformers installed")

        # Try to load RadDINO config (doesn't download weights if already cached)
        print("\nChecking RadDINO model...")
        model = AutoModel.from_pretrained(
            "microsoft/rad-dino",
            trust_remote_code=True
        )
        print("[OK] RadDINO model accessible")

        # Check output dimensions
        dummy_input = torch.randn(1, 3, 224, 224)
        with torch.no_grad():
            out = model(pixel_values=dummy_input)
            cls_dim = out.last_hidden_state[:, 0].shape[-1]

        print(f"[OK] CLS token output: {cls_dim}d (expected: 768)")

        if cls_dim != 768:
            print(f"⚠ WARNING: Expected 768d output, got {cls_dim}d")
            print("  May need to modify projection head in train_sharp_raddino.py")
            return False

        return True

    except ImportError as e:
        print(f"[ERROR] Missing dependency: {e}")
        print("\nInstall with:")
        print("  pip install transformers>=4.30.0")
        return False

    except Exception as e:
        print(f"[ERROR] RadDINO not accessible: {e}")
        print("\nDownload with:")
        print("  huggingface-cli download microsoft/rad-dino")
        return False


def check_script_syntax():
    """Check if train_sharp_raddino_v2.py has valid syntax."""
    try:
        import py_compile
        py_compile.compile('train_sharp_raddino_v2.py', doraise=True)
        print("[OK] train_sharp_raddino_v2.py syntax valid")
        return True
    except py_compile.PyCompileError as e:
        print(f"[ERROR] Syntax error in train_sharp_raddino_v2.py:")
        print(f"  {e}")
        return False
    except FileNotFoundError:
        print("[ERROR] train_sharp_raddino_v2.py not found")
        print("  Run this script from the MyReasearch directory")
        return False


def check_dependencies():
    """Check all required dependencies."""
    required = [
        ('torch', 'PyTorch'),
        ('transformers', 'HuggingFace Transformers'),
        ('PIL', 'Pillow'),
        ('tqdm', 'tqdm'),
    ]

    all_ok = True
    for module, name in required:
        try:
            __import__(module)
            print(f"[OK] {name}")
        except ImportError:
            print(f"[ERROR] {name} not installed")
            all_ok = False

    # Just check pandas exists without importing (avoid numpy version issues on local)
    try:
        import importlib.util
        spec = importlib.util.find_spec("pandas")
        if spec is not None:
            print(f"[OK] Pandas")
        else:
            print(f"[ERROR] Pandas not installed")
            all_ok = False
    except Exception:
        print(f"[ERROR] Pandas not installed")
        all_ok = False

    return all_ok


def main():
    print("=" * 60)
    print("  RadDINO Setup Verification")
    print("=" * 60)
    print()

    print("[1/3] Checking dependencies...")
    deps_ok = check_dependencies()
    print()

    print("[2/3] Checking script syntax...")
    syntax_ok = check_script_syntax()
    print()

    print("[3/3] Checking RadDINO model...")
    raddino_ok = check_raddino_available()
    print()

    print("=" * 60)
    if deps_ok and syntax_ok and raddino_ok:
        print("[OK] All checks passed!")
        print()
        print("Ready to run:")
        print("  1. Smoke test:     run_raddino_smoketest.bat")
        print("  2. Full training:  run_raddino_exp3_hardneg.bat")
    else:
        print("[ERROR] Setup incomplete - fix errors above")
        sys.exit(1)
    print("=" * 60)


if __name__ == "__main__":
    main()
