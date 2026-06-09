"""
Verify the SOURCE checkpoints (p3_best.pt) have different weights BEFORE conversion
"""
import torch

checkpoints = [
    ('Exp #1 Baseline', 'D:/experiments/exp1_baseline/p3_best.pt'),
    ('Exp #3 Full SHARP', 'D:/experiments/exp3_full_sharp/p3_best.pt'),
    ('Exp #4 v2a (Best R@1)', 'D:/experiments/exp4_v2a_matched_epochs/p3_best.pt')
]

print("="*80)
print("Verifying SOURCE Checkpoints (p3_best.pt) - BEFORE Conversion")
print("="*80)

cls_tokens = {}

for name, path in checkpoints:
    print(f"\n{name}:")
    print(f"  Loading: {path}")
    
    checkpoint = torch.load(path, map_location='cpu')
    
    if 'model_state_dict' in checkpoint:
        state_dict = checkpoint['model_state_dict']
    else:
        state_dict = checkpoint
    
    # Get cls_token from HuggingFace format
    cls_token = state_dict['image_encoder.vit.embeddings.cls_token'].flatten()
    cls_tokens[name] = cls_token
    
    print(f"  cls_token shape: {cls_token.shape}")
    print(f"  First 5 values: {cls_token[:5].tolist()}")
    print(f"  Mean: {cls_token.mean().item():.6f}, Std: {cls_token.std().item():.6f}")

# Compare
print(f"\n{'='*80}")
print("Comparison:")
print(f"{'='*80}")

names = list(cls_tokens.keys())
for i in range(len(names)):
    for j in range(i+1, len(names)):
        print(f"\n{names[i]} vs {names[j]}:")
        diff = torch.abs(cls_tokens[names[i]] - cls_tokens[names[j]]).sum().item()
        print(f"  L1 Distance: {diff:.6f}")
        if diff < 1e-6:
            print(f"  *** SOURCE CHECKPOINTS ARE IDENTICAL! ***")
        else:
            print(f"  Different (OK)")

print(f"\n{'='*80}")
print("Conclusion:")
print(f"{'='*80}")

all_same = all(
    torch.abs(cls_tokens[names[i]] - cls_tokens[names[j]]).sum().item() < 1e-6
    for i in range(len(names))
    for j in range(i+1, len(names))
)

if all_same:
    print("\n*** PROBLEM: SOURCE checkpoints (p3_best.pt) are IDENTICAL! ***")
    print("The original training checkpoints are the same.")
    print("This means Exp #1, Exp #3, and Exp #4 v2a all saved the same model!")
else:
    print("\n✓ SOURCE checkpoints are different")
    print("The bug is in the conversion script - it's producing identical output")
