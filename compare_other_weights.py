"""
Check if OTHER weights (not cls_token) differ between checkpoints
"""
import torch

checkpoints = [
    ('Exp #1', 'D:/experiments/exp1_baseline/p3_best.pt'),
    ('Exp #3', 'D:/experiments/exp3_full_sharp/p3_best.pt'),
    ('Exp #4 v2a', 'D:/experiments/exp4_v2a_matched_epochs/p3_best.pt')
]

print("="*80)
print("Comparing OTHER weights (not cls_token)")
print("="*80)

states = {}
for name, path in checkpoints:
    checkpoint = torch.load(path, map_location='cpu')
    states[name] = checkpoint['model_state_dict']
    print(f"\nLoaded {name}")

# Check several different weights
weight_keys = [
    'image_encoder.vit.embeddings.position_embeddings',
    'image_encoder.vit.encoder.layer.0.attention.query.weight',
    'image_encoder.vit.encoder.layer.0.attention.key.weight', 
    'image_encoder.vit.encoder.layer.11.output.dense.weight',
]

print(f"\n{'='*80}")
print("Comparing specific weights:")
print(f"{'='*80}")

for key in weight_keys:
    print(f"\n{key}:")
    
    weights = {}
    for name in states.keys():
        if key in states[name]:
            w = states[name][key].flatten()
            weights[name] = w
            print(f"  {name}: shape={w.shape}, mean={w.mean().item():.6f}, std={w.std().item():.6f}")
            print(f"    First 3 values: {w[:3].tolist()}")
    
    # Compare
    if len(weights) >= 2:
        names = list(weights.keys())
        diff_01 = torch.abs(weights[names[0]] - weights[names[1]]).sum().item()
        diff_02 = torch.abs(weights[names[0]] - weights[names[2]]).sum().item()
        
        print(f"\n  {names[0]} vs {names[1]}: L1 distance = {diff_01:.2f}")
        print(f"  {names[0]} vs {names[2]}: L1 distance = {diff_02:.2f}")
        
        if diff_01 < 1e-6 and diff_02 < 1e-6:
            print(f"  ⚠️ IDENTICAL")
        else:
            print(f"  ✓ DIFFERENT")

print(f"\n{'='*80}")
print("Summary:")
print(f"{'='*80}")
print("\nIf OTHER weights are different but cls_token is identical,")
print("this suggests cls_token was frozen or not trained properly.")
