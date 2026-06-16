"""
Calculate F1 scores from pushed results in rsna_results_latest and siim_results_latest
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
        print(f"  >> CONSERVATIVE")

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
    print("F1 Score Calculation - From Pushed Results")
    print("="*80)

    base_dir = Path(".")

    # Map experiments to their result files
    # Try local pushed results first, then BenchX directory on remote
    experiments = {
        "RSNA 1%": [
            "rsna_results_latest/SHARP_1pct/SHARP_1pct",
            "BenchX/experiments/classification/rsna/SHARP_1pct/SHARP_1pct"
        ],
        "RSNA 10%": [
            "rsna_results_latest/SHARP_10pct/SHARP_10pct",
            "BenchX/experiments/classification/rsna/SHARP_10pct/SHARP_10pct"
        ],
        "RSNA 100%": [
            "rsna_results_latest/SHARP_100pct/SHARP_100pct",
            "BenchX/experiments/classification/rsna/SHARP_100pct/SHARP_100pct"
        ],
        "RSNA Linear Probe (10%)": [
            "rsna_lp_results",
            "BenchX/experiments/classification/rsna/SHARP_LP/SHARP_LinearProbe"
        ],
        "SIIM 1%": [
            "siim_results_latest/SHARP_1pct/SHARP_1pct",
            "BenchX/experiments/classification/siim/SHARP_1pct/SHARP_1pct"
        ],
        "SIIM 10%": [
            "siim_results_latest/SHARP_10pct/SHARP_10pct",
            "BenchX/experiments/classification/siim/SHARP_10pct/SHARP_10pct"
        ],
        "SIIM 100%": [
            "siim_results_latest/SHARP_100pct/SHARP_100pct",
            "BenchX/experiments/classification/siim/SHARP_100pct/SHARP_100pct"
        ],
    }

    all_results = {}

    for name, result_paths in experiments.items():
        print(f"\n{'='*80}")
        print(f"{name}")
        print('='*80)

        # Try each path until we find one that exists
        exp_dir = None
        if isinstance(result_paths, str):
            result_paths = [result_paths]

        for result_path in result_paths:
            test_dir = base_dir / result_path
            if test_dir.exists():
                exp_dir = test_dir
                break

        if exp_dir is None:
            print(f"  X Directory not found")
            continue

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
            import traceback
            traceback.print_exc()

    # Summary table
    if all_results:
        print("\n" + "="*80)
        print("SUMMARY - All F1 Scores")
        print("="*80)
        print()
        print(f"{'Experiment':<30} {'F1':<10} {'Precision':<12} {'Recall':<10} {'Specificity':<12}")
        print("-" * 80)

        for name, m in all_results.items():
            print(f"{name:<30} {m['f1']:>8.2f}% {m['precision']:>10.2f}% {m['recall']:>8.2f}% {m['specificity']:>10.2f}%")

        # RSNA Data Scaling
        print("\n" + "="*80)
        print("RSNA Pneumonia - F1 Data Scaling")
        print("="*80)
        rsna_splits = ["RSNA 1%", "RSNA 10%", "RSNA 100%"]
        print(f"\n{'Split':<15} {'F1':<10} {'Precision':<12} {'Recall':<10} {'Specificity':<12}")
        print("-" * 65)
        for split in rsna_splits:
            if split in all_results:
                m = all_results[split]
                print(f"{split:<15} {m['f1']:>8.2f}% {m['precision']:>10.2f}% {m['recall']:>8.2f}% {m['specificity']:>10.2f}%")

        # Compare with AUROC
        print("\n" + "="*80)
        print("RSNA: AUROC vs F1 Comparison")
        print("="*80)
        print()
        print(f"{'Split':<15} {'AUROC':<12} {'F1 Score':<12}")
        print("-" * 40)
        print(f"{'RSNA 1%':<15} {0.6900:<12.4f} {all_results.get('RSNA 1%', {}).get('f1', 0):>10.2f}%")
        print(f"{'RSNA 10%':<15} {0.7514:<12.4f} {all_results.get('RSNA 10%', {}).get('f1', 0):>10.2f}%")
        print(f"{'RSNA 100%':<15} {0.7923:<12.4f} {all_results.get('RSNA 100%', {}).get('f1', 0):>10.2f}%")

        # Linear probe comparison
        if "RSNA Linear Probe (10%)" in all_results and "RSNA 10%" in all_results:
            print("\n" + "="*80)
            print("Fine-tuning vs Linear Probe (RSNA 10%)")
            print("="*80)
            lp = all_results["RSNA Linear Probe (10%)"]
            ft = all_results["RSNA 10%"]
            print()
            print(f"{'Metric':<20} {'Fine-tuning':<15} {'Linear Probe':<15} {'Gap':<15}")
            print("-" * 70)
            print(f"{'AUROC':<20} {0.7514:<15.4f} {0.7317:<15.4f} {-0.0197:<15.4f}")
            print(f"{'F1 Score':<20} {ft['f1']:<15.2f} {lp['f1']:<15.2f} {ft['f1'] - lp['f1']:<15.2f}")
            print(f"{'Recall':<20} {ft['recall']:<15.2f} {lp['recall']:<15.2f} {ft['recall'] - lp['recall']:<15.2f}")

        # SIIM Data Scaling
        siim_splits = ["SIIM 1%", "SIIM 10%", "SIIM 100%"]
        if any(s in all_results for s in siim_splits):
            print("\n" + "="*80)
            print("SIIM Pneumothorax - F1 Data Scaling")
            print("="*80)
            print(f"\n{'Split':<15} {'F1':<10} {'Precision':<12} {'Recall':<10} {'Specificity':<12}")
            print("-" * 65)
            for split in siim_splits:
                if split in all_results:
                    m = all_results[split]
                    print(f"{split:<15} {m['f1']:>8.2f}% {m['precision']:>10.2f}% {m['recall']:>8.2f}% {m['specificity']:>10.2f}%")

            # Compare with AUROC
            print("\n" + "="*80)
            print("SIIM: AUROC vs F1 Comparison")
            print("="*80)
            print()
            print(f"{'Split':<15} {'AUROC':<12} {'F1 Score':<12}")
            print("-" * 40)
            siim_aurocs = {"SIIM 1%": 0.6037, "SIIM 10%": 0.6244, "SIIM 100%": 0.6675}
            for split in siim_splits:
                if split in all_results:
                    auroc = siim_aurocs.get(split, 0)
                    f1 = all_results[split]['f1']
                    print(f"{split:<15} {auroc:<12.4f} {f1:>10.2f}%")

        # Save to file
        with open("all_f1_results.txt", "w") as f:
            f.write("="*80 + "\n")
            f.write("F1 Score Results - All SHARP Experiments\n")
            f.write("="*80 + "\n\n")

            f.write(f"{'Experiment':<30} {'F1':<10} {'Precision':<12} {'Recall':<10} {'Specificity':<12}\n")
            f.write("-" * 80 + "\n")

            for name, m in all_results.items():
                f.write(f"{name:<30} {m['f1']:>8.2f}% {m['precision']:>10.2f}% {m['recall']:>8.2f}% {m['specificity']:>10.2f}%\n")

            f.write("\n\nRSNA Data Scaling:\n")
            f.write(f"{'Split':<15} {'AUROC':<12} {'F1 Score':<12}\n")
            f.write("-" * 40 + "\n")
            f.write(f"{'RSNA 1%':<15} {0.6900:<12.4f} {all_results.get('RSNA 1%', {}).get('f1', 0):>10.2f}%\n")
            f.write(f"{'RSNA 10%':<15} {0.7514:<12.4f} {all_results.get('RSNA 10%', {}).get('f1', 0):>10.2f}%\n")
            f.write(f"{'RSNA 100%':<15} {0.7923:<12.4f} {all_results.get('RSNA 100%', {}).get('f1', 0):>10.2f}%\n")

        print(f"\nOK Results saved to: all_f1_results.txt")

    else:
        print("\nWARNING: No results calculated")

    print()

if __name__ == "__main__":
    main()
