"""
Check R@1 scores from p3_history.json files to identify which exp4 is the best
"""
import json
import os

experiments = [
    ('Exp #1 Baseline', 'D:/experiments/exp1_baseline/p3_history.json'),
    ('Exp #3 Full SHARP', 'D:/experiments/exp3_full_sharp/p3_history.json'),
    ('Exp #4 large_batch_FAIR', 'D:/experiments/exp4_large_batch_FAIR/p3_history.json'),
    ('Exp #4 v2a_matched_epochs', 'D:/experiments/exp4_v2a_matched_epochs/p3_history.json'),
    ('Exp #4 v2_large_batch_PROPER', 'D:/experiments/exp4_v2_large_batch_PROPER/p3_history.json'),
]

print("="*80)
print("R@1 Scores from p3_history.json")
print("="*80)

for name, path in experiments:
    print(f"\n{name}:")
    print(f"  Path: {path}")
    
    if not os.path.exists(path):
        print(f"  ❌ File not found")
        continue
    
    try:
        with open(path, 'r') as f:
            history = json.load(f)
        
        # Find best val_r1 score
        if 'val_r1' in history:
            val_r1_scores = history['val_r1']
            if isinstance(val_r1_scores, list) and len(val_r1_scores) > 0:
                best_r1 = max(val_r1_scores)
                final_r1 = val_r1_scores[-1]
                print(f"  ✓ Best R@1: {best_r1:.4f}% (epoch {val_r1_scores.index(best_r1) + 1})")
                print(f"  ✓ Final R@1: {final_r1:.4f}% (epoch {len(val_r1_scores)})")
            else:
                print(f"  ⚠️ val_r1 found but empty or not a list")
        else:
            # Check if it's in a different format
            print(f"  Available keys: {list(history.keys())[:10]}")
    
    except Exception as e:
        print(f"  ❌ Error: {e}")

print("\n" + "="*80)
print("Summary:")
print("="*80)
print("\nTarget R@1 scores:")
print("  Exp #1 Baseline: 6.61%")
print("  Exp #3 Full SHARP: 6.21%")
print("  Exp #4 v2a (Best): 8.77%")
print("\nWhich directory matches 8.77%?")
