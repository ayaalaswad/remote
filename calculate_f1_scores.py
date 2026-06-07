"""
Calculate F1 scores from SHARP predictions to compare with BenchX baselines
"""
import numpy as np
import json

def calculate_f1_manual(predictions, references, pos_label=1):
    """Calculate F1 score manually without sklearn"""
    # Calculate TP, FP, FN
    tp = np.sum((predictions == pos_label) & (references == pos_label))
    fp = np.sum((predictions == pos_label) & (references != pos_label))
    fn = np.sum((predictions != pos_label) & (references == pos_label))

    # Calculate precision and recall
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0

    # Calculate F1
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0

    return f1 * 100  # Convert to percentage

def calculate_f1_from_logits(hyps_file, refs_file):
    """Calculate F1 score from logits and references"""
    # Load logits (shape: [N, 2] for binary classification)
    with open(hyps_file, 'r') as f:
        logits = []
        for line in f:
            # Parse numpy array format: [ 0.40771484 -0.42016602]
            values = line.strip().strip('[]').split()
            logits.append([float(values[0]), float(values[1])])
    logits = np.array(logits)

    # Convert logits to predictions (argmax)
    predictions = np.argmax(logits, axis=1)

    # Load ground truth labels (one-hot format: [1. 0.] or [0. 1.])
    with open(refs_file, 'r') as f:
        references = []
        for line in f:
            # Parse one-hot: [1. 0.] means class 0, [0. 1.] means class 1
            values = line.strip().strip('[]').split()
            one_hot = [float(values[0]), float(values[1])]
            references.append(np.argmax(one_hot))  # Convert to class index
    references = np.array(references)

    # Calculate F1 score
    f1 = calculate_f1_manual(predictions, references, pos_label=1)

    return f1, predictions, references

# Calculate F1 for all 3 splits
splits = {
    '1pct': {
        'hyps': r'C:\Users\ZA\lawer\MyReasearch\rsnaresults\rsna1pct\val_42_hyps.txt',
        'refs': r'C:\Users\ZA\lawer\MyReasearch\rsnaresults\rsna1pct\val_42_refs.txt'
    },
    '10pct': {
        'hyps': r'C:\Users\ZA\lawer\MyReasearch\rsnaresults\rsna10pct\val_42_hyps (3).txt',
        'refs': r'C:\Users\ZA\lawer\MyReasearch\rsnaresults\rsna10pct\val_42_refs (3).txt'
    },
    '100pct': {
        'hyps': r'C:\Users\ZA\lawer\MyReasearch\rsnaresults\rsna100pct\val_42_hyps (4).txt',
        'refs': r'C:\Users\ZA\lawer\MyReasearch\rsnaresults\rsna100pct\val_42_refs (4).txt'
    }
}

results = {}
for split_name, files in splits.items():
    f1, preds, refs = calculate_f1_from_logits(files['hyps'], files['refs'])
    results[split_name] = {
        'f1': float(f1),
        'total_samples': int(len(refs)),
        'positive_samples': int(np.sum(refs == 1)),
        'negative_samples': int(np.sum(refs == 0)),
        'correct_predictions': int(np.sum(preds == refs))
    }
    print(f"\n{split_name.upper()}:")
    print(f"  F1 Score: {f1:.1f}")
    print(f"  Samples: {len(refs)} (Pos: {np.sum(refs == 1)}, Neg: {np.sum(refs == 0)})")
    print(f"  Correct: {np.sum(preds == refs)} ({100*np.sum(preds == refs)/len(refs):.1f}%)")

# Print comparison table
print("\n" + "="*60)
print("SHARP vs BenchX Baselines - RSNA Pneumonia F1 Scores")
print("="*60)
print(f"\n{'Method':<15} {'1%':<8} {'10%':<8} {'100%':<8}")
print("-" * 60)
print(f"{'SHARP':<15} {results['1pct']['f1']:<8.1f} {results['10pct']['f1']:<8.1f} {results['100pct']['f1']:<8.1f}")
print("-" * 60)
print(f"{'MRM':<15} {'62.6':<8} {'66.6':<8} {'66.5':<8}")
print(f"{'MGCA-ViT':<15} {'61.0':<8} {'64.3':<8} {'66.9':<8}")
print(f"{'REFERS':<15} {'61.7':<8} {'63.8':<8} {'67.2':<8}")
print(f"{'MedCLIP-ViT':<15} {'63.5':<8} {'65.3':<8} {'66.2':<8}")

# Save results
with open(r'C:\Users\ZA\lawer\MyReasearch\sharp_f1_results.json', 'w') as f:
    json.dump(results, f, indent=2)

print("\nResults saved to: sharp_f1_results.json")
