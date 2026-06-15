"""
Calculate F1 scores for SIIM experiments from saved predictions
"""
import json
from pathlib import Path
from sklearn.metrics import precision_recall_fscore_support, classification_report
import numpy as np

def load_predictions(hyps_file, refs_file):
    """Load predictions and references from files"""
    with open(hyps_file, 'r') as f:
        hyps_lines = f.readlines()

    with open(refs_file, 'r') as f:
        refs_lines = f.readlines()

    # Parse JSON lines
    predictions = []
    references = []

    for hyp_line, ref_line in zip(hyps_lines, refs_lines):
        hyp_line = hyp_line.strip()
        ref_line = ref_line.strip()

        if hyp_line and ref_line:
            try:
                hyp_data = json.loads(hyp_line)
                ref_data = json.loads(ref_line)

                # Extract predictions (class with highest probability)
                if 'predictions' in hyp_data:
                    pred = hyp_data['predictions']
                    predictions.append(int(np.argmax(pred)))

                # Extract references
                if 'labels' in ref_data:
                    references.append(int(ref_data['labels']))
            except:
                continue

    return np.array(predictions), np.array(references)

def calculate_metrics(predictions, references):
    """Calculate precision, recall, F1"""
    precision, recall, f1, support = precision_recall_fscore_support(
        references, predictions, average='binary', zero_division=0
    )

    # Also get per-class metrics
    report = classification_report(references, predictions,
                                   target_names=['Negative', 'Positive'],
                                   output_dict=True, zero_division=0)

    return {
        'precision': precision * 100,
        'recall': recall * 100,
        'f1': f1 * 100,
        'support': support,
        'report': report
    }

def main():
    print("="*80)
    print("SIIM F1 Score Calculation")
    print("="*80)
    print()

    benchx_root = Path("C:/Users/aya.alaswad/remote/BenchX/experiments/classification/siim")

    experiments = {
        "SIIM 1%": "SHARP_1pct/SHARP_1pct",
        "SIIM 10%": "SHARP_10pct/SHARP_10pct",
        "SIIM 100%": "SHARP_100pct/SHARP_100pct"
    }

    all_results = {}

    for name, exp_path in experiments.items():
        print(f"\n{name}:")
        print("-" * 40)

        exp_dir = benchx_root / exp_path

        if not exp_dir.exists():
            print(f"  ✗ Directory not found: {exp_dir}")
            continue

        # Find prediction files
        hyps_file = exp_dir / "val_42_hyps.txt"
        refs_file = exp_dir / "val_42_refs.txt"

        if not hyps_file.exists() or not refs_file.exists():
            print(f"  ✗ Prediction files not found")
            print(f"    Expected: {hyps_file}")
            continue

        try:
            predictions, references = load_predictions(hyps_file, refs_file)

            if len(predictions) == 0:
                print(f"  ✗ No predictions loaded")
                continue

            metrics = calculate_metrics(predictions, references)

            all_results[name] = metrics

            print(f"  Total samples: {len(predictions)}")
            print(f"  Precision: {metrics['precision']:.2f}%")
            print(f"  Recall: {metrics['recall']:.2f}%")
            print(f"  F1 Score: {metrics['f1']:.2f}%")
            print(f"  Support (Positive class): {metrics['support']}")

            # Show class distribution
            n_pos = np.sum(references == 1)
            n_neg = np.sum(references == 0)
            print(f"  Class distribution: {n_neg} negative, {n_pos} positive ({n_pos/(n_pos+n_neg)*100:.1f}% positive)")

        except Exception as e:
            print(f"  ✗ Error: {e}")
            import traceback
            traceback.print_exc()

    # Print summary table
    if all_results:
        print("\n" + "="*80)
        print("SIIM F1 Summary Table")
        print("="*80)
        print()
        print(f"{'Experiment':<15} {'Precision':<12} {'Recall':<12} {'F1 Score':<12}")
        print("-" * 55)

        for name, metrics in all_results.items():
            print(f"{name:<15} {metrics['precision']:>10.2f}% {metrics['recall']:>10.2f}% {metrics['f1']:>10.2f}%")

        # Save to file
        with open("siim_f1_results.txt", "w") as f:
            f.write("="*80 + "\n")
            f.write("SIIM F1 Score Results\n")
            f.write("="*80 + "\n\n")

            f.write(f"{'Experiment':<15} {'Precision':<12} {'Recall':<12} {'F1 Score':<12}\n")
            f.write("-" * 55 + "\n")

            for name, metrics in all_results.items():
                f.write(f"{name:<15} {metrics['precision']:>10.2f}% {metrics['recall']:>10.2f}% {metrics['f1']:>10.2f}%\n")

            f.write("\n" + "="*80 + "\n")
            f.write("Detailed Reports\n")
            f.write("="*80 + "\n\n")

            for name, metrics in all_results.items():
                f.write(f"\n{name}:\n")
                f.write("-" * 40 + "\n")
                f.write(f"Precision: {metrics['precision']:.2f}%\n")
                f.write(f"Recall: {metrics['recall']:.2f}%\n")
                f.write(f"F1 Score: {metrics['f1']:.2f}%\n")
                f.write(f"Support: {metrics['support']}\n")

        print(f"\n✓ Results saved to: siim_f1_results.txt")
    else:
        print("\n⚠️ No results calculated")

    print()

if __name__ == "__main__":
    main()
