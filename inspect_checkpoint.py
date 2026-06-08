"""
Inspect checkpoint structure to find correct key names
"""
import torch

checkpoint_path = 'D:/experiments/exp1_baseline/p3_best.pt'

print("="*80)
print(f"Inspecting checkpoint: {checkpoint_path}")
print("="*80)

state_dict = torch.load(checkpoint_path, map_location='cpu')

print(f"\nTop-level type: {type(state_dict)}")

if isinstance(state_dict, dict):
    print(f"Top-level keys: {list(state_dict.keys())[:20]}")
    
    # Check if it's a nested structure
    for key in ['state_dict', 'model', 'image_encoder']:
        if key in state_dict:
            print(f"\nFound nested key: '{key}'")
            nested = state_dict[key]
            if isinstance(nested, dict):
                print(f"  Nested keys (first 20): {list(nested.keys())[:20]}")

# Search for cls_token
print("\n" + "="*80)
print("Searching for cls_token...")
print("="*80)

def search_keys(d, prefix=""):
    """Recursively search for keys containing 'cls_token'"""
    if isinstance(d, dict):
        for key, value in d.items():
            full_key = f"{prefix}.{key}" if prefix else key
            if 'cls_token' in key.lower():
                print(f"  FOUND: {full_key}")
                if hasattr(value, 'shape'):
                    print(f"    Shape: {value.shape}")
            if isinstance(value, dict):
                search_keys(value, full_key)

search_keys(state_dict)

# Show all keys (first 50)
print("\n" + "="*80)
print("All keys (first 50):")
print("="*80)

def get_all_keys(d, prefix=""):
    """Get all keys recursively"""
    keys = []
    if isinstance(d, dict):
        for key, value in d.items():
            full_key = f"{prefix}.{key}" if prefix else key
            keys.append(full_key)
            if isinstance(value, dict):
                keys.extend(get_all_keys(value, full_key))
    return keys

all_keys = get_all_keys(state_dict)
for i, key in enumerate(all_keys[:50]):
    print(f"  {i+1}. {key}")

if len(all_keys) > 50:
    print(f"  ... and {len(all_keys) - 50} more keys")

print(f"\nTotal keys: {len(all_keys)}")
