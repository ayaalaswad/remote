"""
Run this on the remote machine to verify checkpoints are actually loading
"""
import torch

print("="*80)
print("Verifying Checkpoint Loading - Comparing cls_token values")
print("="*80)

checkpoints = [
    ('Exp #1 Baseline', 'D:/experiments/exp1_baseline/p3_best_timm.pt'),
    ('Exp #3 Full SHARP', 'D:/experiments/exp3_full_sharp/p3_best_timm.pt'),
    ('Exp #4 v2a (Best R@1)', 'D:/experiments/exp4_v2a_matched_epochs/p3_best_timm.pt')
]

cls_tokens = {}

for name, ckpt_path in checkpoints:
    print(f"\n{name}:")
    print(f"  Loading: {ckpt_path}")
    
    try:
        state_dict = torch.load(ckpt_path, map_location='cpu')
        
        # Check if it's a nested structure
        if 'state_dict' in state_dict:
            state_dict = state_dict['state_dict']
        elif 'model' in state_dict:
            state_dict = state_dict['model']
        
        # Find cls_token
        if 'cls_token' in state_dict:
            cls_token = state_dict['cls_token']
        else:
            # Search for any key containing cls_token
            cls_token_keys = [k for k in state_dict.keys() if 'cls_token' in k]
            if cls_token_keys:
                print(f"  Found cls_token key: {cls_token_keys[0]}")
                cls_token = state_dict[cls_token_keys[0]]
            else:
                print(f"  ERROR: No cls_token found!")
                print(f"  First 20 keys: {list(state_dict.keys())[:20]}")
                continue
        
        cls_token = cls_token.flatten()
        cls_tokens[name] = cls_token
        
        print(f"  cls_token shape: {cls_token.shape}")
        print(f"  First 5 values: {cls_token[:5].tolist()}")
        print(f"  Mean: {cls_token.mean().item():.6f}, Std: {cls_token.std().item():.6f}")
        
    except Exception as e:
        print(f"  ERROR: {e}")

# Compare
print(f"\n{'='*80}")
print("Comparison:")
print(f"{'='*80}")

if len(cls_tokens) >= 2:
    names = list(cls_tokens.keys())
    
    for i in range(len(names)):
        for j in range(i+1, len(names)):
            print(f"\n{names[i]} vs {names[j]}:")
            diff = torch.abs(cls_tokens[names[i]] - cls_tokens[names[j]]).sum().item()
            print(f"  L1 Distance: {diff:.6f}")
            if diff < 1e-6:
                print(f"  *** WARNING: IDENTICAL! ***")
            else:
                print(f"  Different (OK)")

print(f"\n{'='*80}")
print("Conclusion:")
print(f"{'='*80}")

if len(cls_tokens) >= 3:
    names = list(cls_tokens.keys())
    all_same = all(
        torch.abs(cls_tokens[names[i]] - cls_tokens[names[j]]).sum().item() < 1e-6
        for i in range(len(names))
        for j in range(i+1, len(names))
    )
    
    if all_same:
        print("\n*** CRITICAL BUG FOUND! ***")
        print("All checkpoints have IDENTICAL weights!")
        print("BenchX is NOT loading SHARP checkpoints.")
        print("It's likely falling back to ImageNet ViT pretrained weights for all three.")
        print("\nThis explains why F1 = 43.07% for all checkpoints!")
    else:
        print("\nCheckpoints have different weights - loading works correctly.")
        print("The identical F1 scores (43.07%) must have another explanation.")
elif len(cls_tokens) >= 2:
    print("\nPartial verification - need all 3 checkpoints to confirm")
else:
    print("\nCould not load checkpoints for verification")
