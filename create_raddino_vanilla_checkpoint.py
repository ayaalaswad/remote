#!/usr/bin/env python3
"""
Extract Vanilla RadDINO Checkpoint
===================================

Downloads microsoft/rad-dino from HuggingFace and saves it as a checkpoint
in the format that CXRMate Stage 2 expects.

This creates a "Stage 0" checkpoint - raw pretrained RadDINO without any
SHARP Stage 1 training.
"""

import torch
from pathlib import Path

def main():
    print("="*80)
    print("Creating Vanilla RadDINO Checkpoint")
    print("="*80)
    print()

    # Output path
    output_dir = Path("D:/experiments/raddino_vanilla")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "pretrained.pt"

    print(f"Output: {output_path}")
    print()

    # Check if already exists
    if output_path.exists():
        print("[WARNING] Checkpoint already exists!")
        print(f"          {output_path}")
        print()
        response = input("Overwrite? (y/n): ")
        if response.lower() != 'y':
            print("[SKIP] Using existing checkpoint")
            return
        print()

    print("Step 1: Loading microsoft/rad-dino from HuggingFace...")
    print("        (This may take a few minutes on first download)")
    print()

    try:
        # Load RadDINO model
        from transformers import AutoModel

        model = AutoModel.from_pretrained(
            "microsoft/rad-dino",
            trust_remote_code=True
        )

        print("[OK] RadDINO loaded successfully")
        print(f"     Model type: {type(model).__name__}")
        print()

    except Exception as e:
        print(f"[ERROR] Failed to load RadDINO: {e}")
        print()
        print("Please install required packages:")
        print("  pip install transformers")
        return

    print("Step 2: Extracting encoder state dict...")
    print()

    # Get the encoder (vision model)
    # RadDINO structure: model.encoder or model.vision_model
    if hasattr(model, 'encoder'):
        encoder = model.encoder
        print("     Found encoder at model.encoder")
    elif hasattr(model, 'vision_model'):
        encoder = model.vision_model
        print("     Found encoder at model.vision_model")
    else:
        # Fallback: use entire model
        encoder = model
        print("     Using entire model as encoder")

    state_dict = encoder.state_dict()
    print(f"     State dict keys: {len(state_dict)}")
    print(f"     Total parameters: {sum(p.numel() for p in state_dict.values()):,}")
    print()

    print("Step 3: Saving checkpoint...")
    print()

    # Save in the same format as Stage 1 checkpoints
    # CXRMate expects: {'encoder': state_dict, ...}
    checkpoint = {
        'encoder': state_dict,
        'step': 0,
        'epoch': 0,
        'source': 'microsoft/rad-dino',
        'note': 'Vanilla RadDINO without SHARP Stage 1 training',
    }

    torch.save(checkpoint, output_path)

    print(f"[OK] Checkpoint saved: {output_path}")
    print(f"     File size: {output_path.stat().st_size / 1024 / 1024:.1f} MB")
    print()

    print("="*80)
    print("✓ Vanilla RadDINO checkpoint created successfully!")
    print("="*80)
    print()
    print("Next steps:")
    print("  1. This checkpoint can be used for Stage 2 (Experiment 2)")
    print("  2. Config: stage2_training/configs/exp_raddino_vanilla.yaml")
    print("  3. Compare with RadDINO+SHARP Stage 1 (Experiment 1)")
    print()
    print(f"Checkpoint path: {output_path}")
    print()

if __name__ == "__main__":
    main()
