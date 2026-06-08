import numpy as np
import ast

def calculate_f1(predictions, references, pos_label=1):
    """Calculate F1 score manually"""
    tp = np.sum((predictions == pos_label) & (references == pos_label))
    fp = np.sum((predictions == pos_label) & (references != pos_label))
    fn = np.sum((predictions != pos_label) & (references == pos_label))
    tn = np.sum((predictions != pos_label) & (references != pos_label))

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0

    return {
        'f1': f1 * 100,
        'precision': precision * 100,
        'recall': recall * 100,
        'tp': int(tp),
        'fp': int(fp),
        'fn': int(fn),
        'tn': int(tn)
    }

def process_split(hyps_file, refs_file, split_name):
    """Process one data split"""
    print(f"\n{'='*60}")
    print(f"Processing {split_name}")
    print(f"{'='*60}")

    # Read predictions (logits) - they're in numpy array string format
    logits = []
    with open(hyps_file, 'r') as f:
        for line in f:
            line = line.strip()
            # Remove brackets and split by whitespace
            line = line.replace('[', '').replace(']', '')
            values = [float(x) for x in line.split()]
            logits.append(values)
    logits = np.array(logits)

    # Convert logits to predictions (argmax)
    predictions = np.argmax(logits, axis=1)

    # Read references (one-hot encoded)
    refs = []
    with open(refs_file, 'r') as f:
        for line in f:
            line = line.strip()
            # Remove brackets and split by whitespace
            line = line.replace('[', '').replace(']', '')
            values = [float(x) for x in line.split()]
            refs.append(values)
    refs = np.array(refs)
    # Convert one-hot to class labels (argmax)
    references = np.argmax(refs, axis=1)

    # Class distribution
    print(f"\nClass distribution:")
    print(f"  References - Class 0: {np.sum(references == 0)} ({np.sum(references == 0)/len(references)*100:.1f}%)")
    print(f"  References - Class 1: {np.sum(references == 1)} ({np.sum(references == 1)/len(references)*100:.1f}%)")
    print(f"  Predictions - Class 0: {np.sum(predictions == 0)} ({np.sum(predictions == 0)/len(predictions)*100:.1f}%)")
    print(f"  Predictions - Class 1: {np.sum(predictions == 1)} ({np.sum(predictions == 1)/len(predictions)*100:.1f}%)")

    # Calculate F1 for both classes
    results = {}
    for label in [0, 1]:
        label_name = "no_pneumonia" if label == 0 else "pneumonia"
        results[label_name] = calculate_f1(predictions, references, pos_label=label)

    return results, predictions, references

# Process all three splits
splits = [
    ('rsnaresults/rsna1pct/val_42_hyps.txt', 'rsnaresults/rsna1pct/val_42_refs.txt', 'RSNA 1%'),
    ('rsnaresults/rsna10pct/val_42_hyps (3).txt', 'rsnaresults/rsna10pct/val_42_refs (3).txt', 'RSNA 10%'),
    ('rsnaresults/rsna100pct/val_42_hyps (4).txt', 'rsnaresults/rsna100pct/val_42_refs (4).txt', 'RSNA 100%')
]

all_results = {}

for hyps_file, refs_file, split_name in splits:
    results, preds, refs = process_split(hyps_file, refs_file, split_name)
    all_results[split_name] = results

    print(f"\n{split_name} Results:")
    print(f"  No Pneumonia (Class 0) - F1: {results['no_pneumonia']['f1']:.2f}%")
    print(f"    Precision: {results['no_pneumonia']['precision']:.2f}%, Recall: {results['no_pneumonia']['recall']:.2f}%")
    print(f"    TP: {results['no_pneumonia']['tp']}, FP: {results['no_pneumonia']['fp']}, FN: {results['no_pneumonia']['fn']}, TN: {results['no_pneumonia']['tn']}")

    print(f"\n  Pneumonia (Class 1) - F1: {results['pneumonia']['f1']:.2f}%")
    print(f"    Precision: {results['pneumonia']['precision']:.2f}%, Recall: {results['pneumonia']['recall']:.2f}%")
    print(f"    TP: {results['pneumonia']['tp']}, FP: {results['pneumonia']['fp']}, FN: {results['pneumonia']['fn']}, TN: {results['pneumonia']['tn']}")

# Summary comparison
print(f"\n\n{'='*60}")
print("SUMMARY: SHARP vs BenchX Baselines (RSNA Pneumonia Detection)")
print(f"{'='*60}")
print("\nF1 Scores (Pneumonia Class):")
print(f"  SHARP 1%:   {all_results['RSNA 1%']['pneumonia']['f1']:.2f}%")
print(f"  SHARP 10%:  {all_results['RSNA 10%']['pneumonia']['f1']:.2f}%")
print(f"  SHARP 100%: {all_results['RSNA 100%']['pneumonia']['f1']:.2f}%")

print("\nBenchX Baselines (from paper, 100% data):")
print("  MGCA:      67.2%")
print("  GLoRIA:    63.8%")
print("  BioViL:    62.9%")
print("  MRM:       66.0%")
print("  ConVIRT:   60.9%")

print(f"\nGap from best baseline (MGCA 67.2%):")
print(f"  SHARP 100%: {all_results['RSNA 100%']['pneumonia']['f1'] - 67.2:.1f} points")

# Save to JSON
import json
with open('sharp_rsna_f1_final.json', 'w') as f:
    json.dump(all_results, f, indent=2)

print("\n\nResults saved to sharp_rsna_f1_final.json")
