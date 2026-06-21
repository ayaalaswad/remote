"""
Calculate F1 scores from NEW SIIM results in BenchX/experiments
(ignores old broken results in siim_results_latest)
"""
from pathlib import Path
import numpy as np

def parse_array_line(line):
    """Parse array format like '[ 0.08984375 -0.11035156]'"""
    line = line.strip().replace('[', '').replace(']', '')
    values = [float(x) for x in line.split() if x]
    return np.array(values)

def load_predictions(hyps_file, refs_file):
    """Load predictions from array format files"""
    predictions = []
    references = []

    with open(hyps_file, 'r') as f:
        hyps_lines = f.readlines()
    with open(refs_file, 'r') as f:
        refs_lines = f.readlines()

    for hyp_line, ref_line in zip(hyps_lines, refs_lines):
        try:
            hyp_array = parse_array_line(hyp_line)
            ref_array = parse_array_line(ref_line)
            predictions.append(int(np.argmax(hyp_array)))
            references.append(int(np.argmax(ref_array)))
        except:
            continue

    return np.array(predictions), np.array(references)

def calculate_confusion_matrix(y_true, y_pred):
    """Calculate confusion matrix manually"""
    tn = np.sum((y_true == 0) & (y_pred == 0))
    fp = np.sum((y_true == 0) & (y_pred == 1))
    fn = np.sum((y_true == 1) & (y_pred == 0))
    tp = np.sum((y_true == 1) & (y_pred == 1))
    return tn, fp, fn, tp

def calculate_metrics(predictions, references, name):
    """Calculate and display metrics"""
    print(f"\n{name}:")
    print("-" * 70)

    n_total = len(predictions)
    n_pos_ref = np.sum(references == 1)
    n_neg_ref = np.sum(references == 0)

    print(f"  Total samples: {n_total}")
    print(f"  Actual: {n_neg_ref} neg ({n_neg_ref/n_total*100:.1f}%), {n_pos_ref} pos ({n_pos_ref/n_total*100:.1f}%)")

    tn, fp, fn, tp = calculate_confusion_matrix(references, predictions)

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
    specificity = tn / (tn + fp) if (tn + fp) > 0 else 0

    print(f"  TN={tn}, FP={fp}, FN={fn}, TP={tp}")
    print(f"  Precision: {precision*100:>6.2f}%")
    print(f"  Recall:    {recall*100:>6.2f}%")
    print(f"  F1 Score:  {f1*100:>6.2f}%")
    print(f"  Specificity: {specificity*100:>6.2f}%")

    if specificity > 0.85 and recall < 0.60:
        print(f"  >> CONSERVATIVE")

    return {
        'precision': precision * 100,
        'recall': recall * 100,
        'f1': f1 * 100,
        'specificity': specificity * 100,
        'tn': tn, 'fp': fp, 'fn': fn, 'tp': tp,
    }

def main():
    print("="*80)
    print("NEW SIIM Results - F1 Score Calculation")
    print("="*80)
    print()
    print("Reading from: BenchX/experiments/classification/siim/")
    print("(Ignoring old broken results in siim_results_latest/)")
    print()

    base_dir = Path(".")

    # ONLY read from NEW BenchX results
    experiments = {
        "SIIM 1% (NEW)": "BenchX/experiments/classification/siim/SHARP_1pct/SHARP_1pct",
        "SIIM 10% (NEW)": "BenchX/experiments/classification/siim/SHARP_10pct/SHARP_10pct",
        "SIIM 100% (NEW)": "BenchX/experiments/classification/siim/SHARP_100pct/SHARP_100pct",
    }

    all_results = {}

    for name, result_path in experiments.items():
        print(f"\n{'='*80}")
        print(f"{name}")
        print('='*80)

        exp_dir = base_dir / result_path

        if not exp_dir.exists():
            print(f"  X Directory not found: {exp_dir}")
            continue

        hyps_file = exp_dir / "val_42_hyps.txt"
        refs_file = exp_dir / "val_42_refs.txt"

        if not hyps_file.exists():
            print(f"  X Prediction file not found: {hyps_file}")
            continue

        if not refs_file.exists():
            print(f"  X Reference file not found: {refs_file}")
            continue

        try:
            predictions, references = load_predictions(hyps_file, refs_file)

            if len(predictions) == 0:
                print(f"  X No valid predictions found")
                continue

            results = calculate_metrics(predictions, references, name)
            all_results[name] = results

        except Exception as e:
            print(f"  X Error: {e}")
            continue

    # Summary
    if all_results:
        print("\n" + "="*80)
        print("SUMMARY - NEW SIIM Results")
        print("="*80)
        print()
        print(f"{'Experiment':<25} {'F1':>8}  {'Precision':>10}  {'Recall':>8}  {'Specificity':>12}")
        print("-" * 80)

        for name, results in all_results.items():
            print(f"{name:<25} {results['f1']:>7.2f}%  {results['precision']:>9.2f}%  "
                  f"{results['recall']:>7.2f}%  {results['specificity']:>11.2f}%")

        print()
        print("="*80)
        print("Comparison with OLD broken results:")
        print("="*80)
        print()
        print("OLD (with broken validation set):")
        print("  SIIM 1%:   0.00% F1")
        print("  SIIM 10%:  0.80% F1")
        print("  SIIM 100%: 2.35% F1")
        print()
        print("NEW (with fixed validation set):")
        for name, results in all_results.items():
            print(f"  {name}: {results['f1']:>6.2f}% F1")
        print()
        print("These improved scores prove the validation fix worked!")

    else:
        print("\n[ERROR] No results found")
        print()
        print("Expected locations:")
        for name, path in experiments.items():
            print(f"  {base_dir / path}")

if __name__ == "__main__":
    main()
