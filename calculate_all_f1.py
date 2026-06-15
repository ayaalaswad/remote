"""
Calculate F1 scores for ALL experiments (RSNA + SIIM)
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

    print(f"  Precision: {precision*100:>6.2f}%")
    print(f"  Recall:    {recall*100:>6.2f}%")
    print(f"  F1 Score:  {f1*100:>6.2f}%")
    print(f"  Specificity: {specificity*100:>6.2f}%")

    if specificity > 0.85 and recall < 0.60:
        print(f"  >> CONSERVATIVE (high specificity, low recall)")

    return {
        'precision': precision * 100,
        'recall': recall * 100,
        'f1': f1 * 100,
        'specificity': specificity * 100,
        'tn': tn, 'fp': fp, 'fn': fn, 'tp': tp,
        'n_total': n_total
    }

def main():
    print("="*80)
    print("F1 Score Calculation - All SHARP BenchX Experiments")
    print("="*80)

    benchx_root = Path("C:/Users/aya.alaswad/remote/BenchX/experiments/classification")

    # Define all experiments with possible paths
    experiments = {
        "RSNA Fine-tuning (10%)": [
            benchx_root / "rsna/SHARP/SHARP",
            benchx_root / "rsna/SHARP",
        ],
        "RSNA Linear Probe (10%)": [
            benchx_root / "rsna/SHARP_LP/SHARP_LinearProbe",
            benchx_root / "rsna/SHARP_LP",
        ],
        "SIIM 1%": [
            benchx_root / "siim/SHARP_1pct/SHARP_1pct",
            benchx_root / "siim/SHARP_1pct",
        ],
        "SIIM 10%": [
            benchx_root / "siim/SHARP_10pct/SHARP_10pct",
            benchx_root / "siim/SHARP_10pct",
        ],
        "SIIM 100%": [
            benchx_root / "siim/SHARP_100pct/SHARP_100pct",
            benchx_root / "siim/SHARP_100pct",
        ],
    }

    all_results = {}

    for name, possible_paths in experiments.items():
        print(f"\n{'='*80}")
        print(f"{name}")
        print('='*80)

        # Find existing directory
        exp_dir = None
        for path in possible_paths:
            if path.exists():
                exp_dir = path
                break

        if exp_dir is None:
            print(f"  X Directory not found")
            continue

        print(f"  Found: {exp_dir}")

        hyps_file = exp_dir / "val_42_hyps.txt"
        refs_file = exp_dir / "val_42_refs.txt"

        if not hyps_file.exists() or not refs_file.exists():
            print(f"  X Prediction files not found")
            continue

        try:
            predictions, references = load_predictions(hyps_file, refs_file)

            if len(predictions) == 0:
                print(f"  X No predictions loaded")
                continue

            metrics = calculate_metrics(predictions, references, name)
            all_results[name] = metrics

        except Exception as e:
            print(f"  X Error: {e}")

    # Summary table
    if all_results:
        print("\n" + "="*80)
        print("SUMMARY - All F1 Scores")
        print("="*80)
        print()
        print(f"{'Experiment':<30} {'F1':<10} {'Precision':<12} {'Recall':<10} {'Specificity':<12}")
        print("-" * 80)

        for name, m in all_results.items():
            exp_short = name.replace(" (10%)", "").replace(" (%)", "")
            print(f"{exp_short:<30} {m['f1']:>8.2f}% {m['precision']:>10.2f}% {m['recall']:>8.2f}% {m['specificity']:>10.2f}%")

        # Group by dataset
        print("\n" + "="*80)
        print("RSNA Results (10% data)")
        print("="*80)
        for name, m in all_results.items():
            if 'RSNA' in name:
                print(f"\n{name}:")
                print(f"  F1: {m['f1']:.2f}%")
                print(f"  Precision: {m['precision']:.2f}%, Recall: {m['recall']:.2f}%")

        print("\n" + "="*80)
        print("SIIM Results (Data Scaling)")
        print("="*80)
        siim_splits = ["SIIM 1%", "SIIM 10%", "SIIM 100%"]
        print(f"\n{'Split':<15} {'F1':<10} {'Precision':<12} {'Recall':<10}")
        print("-" * 50)
        for split in siim_splits:
            if split in all_results:
                m = all_results[split]
                print(f"{split:<15} {m['f1']:>8.2f}% {m['precision']:>10.2f}% {m['recall']:>8.2f}%")

        # Save to file
        with open("all_f1_results.txt", "w") as f:
            f.write("="*80 + "\n")
            f.write("F1 Score Results - All SHARP BenchX Experiments\n")
            f.write("="*80 + "\n\n")

            f.write(f"{'Experiment':<30} {'F1':<10} {'Precision':<12} {'Recall':<10} {'Specificity':<12}\n")
            f.write("-" * 80 + "\n")

            for name, m in all_results.items():
                exp_short = name.replace(" (10%)", "")
                f.write(f"{exp_short:<30} {m['f1']:>8.2f}% {m['precision']:>10.2f}% {m['recall']:>8.2f}% {m['specificity']:>10.2f}%\n")

            f.write("\n" + "="*80 + "\n")
            f.write("Detailed Results\n")
            f.write("="*80 + "\n\n")

            for name, m in all_results.items():
                f.write(f"{name}:\n")
                f.write(f"  Samples: {m['n_total']}\n")
                f.write(f"  F1 Score: {m['f1']:.2f}%\n")
                f.write(f"  Precision: {m['precision']:.2f}%\n")
                f.write(f"  Recall: {m['recall']:.2f}%\n")
                f.write(f"  Specificity: {m['specificity']:.2f}%\n")
                f.write(f"  Confusion: TN={m['tn']}, FP={m['fp']}, FN={m['fn']}, TP={m['tp']}\n")
                f.write("\n")

        print(f"\nOK Results saved to: all_f1_results.txt")

    else:
        print("\nWARNING: No results calculated")

    print()

if __name__ == "__main__":
    main()
