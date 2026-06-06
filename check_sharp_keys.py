"""
Check SHARP checkpoint keys to find correct prefix
"""
import torch

checkpoint_path = r"D:\experiments\exp3_full_sharp\p3_best.pt"

print("="*80)
print("SHARP Checkpoint Key Inspector")
print("="*80)
print()

print(f"Loading: {checkpoint_path}")
ckpt = torch.load(checkpoint_path, map_location='cpu')

print(f"Top-level keys in checkpoint: {list(ckpt.keys())}")
print()

# Get the state dict
if 'model_state_dict' in ckpt:
    state_dict = ckpt['model_state_dict']
    print("Using 'model_state_dict' key")
elif 'state_dict' in ckpt:
    state_dict = ckpt['state_dict']
    print("Using 'state_dict' key")
else:
    state_dict = ckpt
    print("Using checkpoint directly as state_dict")

print()
print("="*80)
print("Looking for ViT keys (cls_token, patch_embed, etc.)")
print("="*80)

keys = list(state_dict.keys())
vit_keys = [k for k in keys if 'cls_token' in k or 'patch_embed' in k or 'pos_embed' in k]

if vit_keys:
    print(f"\nFound {len(vit_keys)} ViT-related keys:")
    for k in vit_keys[:10]:  # Show first 10
        print(f"  {k}")

    # Determine prefix
    if vit_keys:
        first_key = vit_keys[0]
        if 'cls_token' in first_key:
            prefix = first_key.replace('cls_token', '')
        elif 'patch_embed' in first_key:
            prefix = first_key.split('patch_embed')[0]
        elif 'pos_embed' in first_key:
            prefix = first_key.replace('pos_embed', '')
        else:
            prefix = ""

        print()
        print("="*80)
        print("RECOMMENDED PREFIX")
        print("="*80)
        print(f"\nprefix: {prefix}")
        print()
        print("Add this to your BenchX config:")
        print(f"  cnn:")
        print(f"    pretrained: D:/experiments/exp3_full_sharp/p3_best.pt")
        print(f"    prefix: {prefix}")
else:
    print("\n❌ No ViT keys found!")
    print("\nAll keys in state_dict:")
    for k in keys[:20]:
        print(f"  {k}")

print()
print("="*80)
