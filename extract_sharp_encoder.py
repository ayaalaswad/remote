"""
Extract SHARP's ViT encoder for BenchX compatibility

This script extracts just the ViT encoder weights from SHARP's checkpoint,
removing the projection head and text encoder, so BenchX can load it.
"""

import torch
import os

def extract_sharp_vit_encoder(sharp_checkpoint_path, output_path):
    """
    Extract ViT encoder from SHARP checkpoint

    Args:
        sharp_checkpoint_path: Path to SHARP's p3_best.pt
        output_path: Where to save extracted encoder
    """
    print("="*80)
    print("Extracting SHARP ViT Encoder for BenchX")
    print("="*80)
    print()

    # Load SHARP checkpoint
    print(f"Loading SHARP checkpoint: {sharp_checkpoint_path}")
    ckpt = torch.load(sharp_checkpoint_path, map_location='cpu')

    print(f"Checkpoint keys: {list(ckpt.keys())}")
    print()

    if 'model_state_dict' not in ckpt:
        print("ERROR: No 'model_state_dict' in checkpoint")
        return False

    state_dict = ckpt['model_state_dict']

    # Find all image encoder keys
    img_encoder_keys = [k for k in state_dict.keys() if 'image_encoder' in k or 'img_encoder' in k]
    print(f"Found {len(img_encoder_keys)} image encoder parameters")
    print()

    # Show sample keys
    print("Sample image encoder keys:")
    for i, key in enumerate(img_encoder_keys[:10]):
        print(f"  {i+1}. {key}")
    print()

    # Extract only ViT weights (exclude projection head)
    vit_state_dict = {}
    projection_keys = []

    for key in img_encoder_keys:
        # Remove prefix
        clean_key = key.replace('image_encoder.', '').replace('img_encoder.', '')

        # Check if it's ViT backbone or projection head
        if 'projection' in clean_key:
            projection_keys.append(key)
        else:
            vit_state_dict[clean_key] = state_dict[key]

    print(f"Extracted {len(vit_state_dict)} ViT parameters")
    print(f"Excluded {len(projection_keys)} projection head parameters")
    print()

    # Save extracted weights
    output_dict = {
        'model': vit_state_dict,
        'source': 'SHARP',
        'architecture': 'ViT-B/16',
        'embedding_dim': 768,  # ViT-B/16 output before projection
        'original_checkpoint': os.path.basename(sharp_checkpoint_path),
        'step': ckpt.get('step', 'unknown'),
    }

    print(f"Saving extracted encoder to: {output_path}")
    torch.save(output_dict, output_path)

    # Verify saved file
    file_size = os.path.getsize(output_path) / (1024 * 1024)
    print(f"✓ Saved successfully ({file_size:.1f} MB)")
    print()

    # Show what we extracted
    print("Extracted ViT structure:")
    vit_modules = set([k.split('.')[0] for k in vit_state_dict.keys()])
    for module in sorted(vit_modules):
        module_params = [k for k in vit_state_dict.keys() if k.startswith(module)]
        print(f"  - {module}: {len(module_params)} parameters")
    print()

    print("="*80)
    print("SUCCESS! Extracted encoder ready for BenchX")
    print()
    print("Next steps:")
    print("1. Use this extracted encoder in BenchX config")
    print("2. Or load it in a custom model class")
    print("="*80)

    return True


if __name__ == "__main__":
    # Paths
    sharp_checkpoint = r"D:\experiments\exp3_full_sharp\p3_best.pt"
    output_path = r"D:\experiments\sharp_vit_encoder.pt"

    # Extract
    success = extract_sharp_vit_encoder(sharp_checkpoint, output_path)

    if success:
        print()
        print(f"Extracted encoder saved to: {output_path}")
        print("Use this in BenchX config as pretrained checkpoint")
    else:
        print()
        print("Failed to extract encoder - check error messages above")
