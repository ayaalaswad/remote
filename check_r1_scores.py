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
        
        # History is a list of epoch records
        if isinstance(history, list):
            # Find records with i2t_r1 (image-to-text R@1)
            i2t_r1_scores = []
            for record in history:
                if isinstance(record, dict) and 'i2t_r1' in record:
                    i2t_r1_scores.append(record['i2t_r1'])
            
            if i2t_r1_scores:
                best_r1 = max(i2t_r1_scores)
                final_r1 = i2t_r1_scores[-1]
                best_epoch = i2t_r1_scores.index(best_r1) + 1
                print(f"  ✓ Best i2t R@1: {best_r1:.2f}% (epoch {best_epoch})")
                print(f"  ✓ Final i2t R@1: {final_r1:.2f}% (final epoch)")
                
                # Show if this matches our target
                if abs(best_r1 - 6.61) < 0.1:
                    print(f"  >>> MATCH: Exp #1 Baseline (6.61%)")
                elif abs(best_r1 - 6.21) < 0.1:
                    print(f"  >>> MATCH: Exp #3 Full SHARP (6.21%)")
                elif abs(best_r1 - 8.77) < 0.1:
                    print(f"  >>> MATCH: Exp #4 v2a Best (8.77%) ⭐")
            else:
                print(f"  ⚠️ No i2t_r1 found in records")
    
    except Exception as e:
        print(f"  ❌ Error: {e}")

print("\n" + "="*80)
print("Summary:")
print("="*80)
print("\nTarget R@1 scores:")
print("  Exp #1 Baseline: 6.61%")
print("  Exp #3 Full SHARP: 6.21%")
print("  Exp #4 v2a (Best): 8.77%")
