"""
Calculate F1 scores for RSNA experiments from saved predictions
"""
import json
from pathlib import Path
from sklearn.metrics import precision_recall_fscore_support, classification_report, confusion_matrix
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

    # Confusion matrix
    cm = confusion_matrix(references, predictions)

    return {
        'precision': precision * 100,
        'recall': recall * 100,
        'f1': f1 * 100,
        'support': support,
        'report': report,
        'confusion_matrix': cm
    }

def main():
    print("="*80)
    print("RSNA F1 Score Calculation")
    print("="*80)
    print()

    benchx_root = Path("C:/Users/aya.alaswad/remote/BenchX/experiments/classification/rsna")

    experiments = {
        "RSNA Fine-tuning (10%)": [
            "SHARP/SHARP",
            "SHARP",
        ],
        "RSNA Linear Probe (10%)": [
            "SHARP_LP/SHARP_LinearProbe",
            "SHARP_LP",
        ]
    }

    all_results = {}

    for name, possible_paths in experiments.items():
        print(f"\n{name}:")
        print("-" * 40)

        exp_dir = None
        for path in possible_paths:
            test_dir = benchx_root / path
            if test_dir.exists():
                exp_dir = test_dir
                break

        if exp_dir is None:
            print(f"  ✗ Directory not found. Tried:")
            for path in possible_paths:
                print(f"    - {benchx_root / path}")
            continue

        print(f"  Found: {exp_dir}")

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
            print(f"  Class distribution: {n_neg} negative ({n_neg/(n_pos+n_neg)*100:.1f}%), {n_pos} positive ({n_pos/(n_pos+n_neg)*100:.1f}%)")

            # Show confusion matrix
            cm = metrics['confusion_matrix']
            print(f"\n  Confusion Matrix:")
            print(f"                Predicted Neg  Predicted Pos")
            print(f"    Actual Neg       {cm[0][0]:>6}         {cm[0][1]:>6}")
            print(f"    Actual Pos       {cm[1][0]:>6}         {cm[1][1]:>6}")

            # Calculate specificity and sensitivity
            tn, fp, fn, tp = cm.ravel()
            specificity = tn / (tn + fp) * 100 if (tn + fp) > 0 else 0
            sensitivity = tp / (tp + fn) * 100 if (tp + fn) > 0 else 0
            print(f"\n  Specificity (True Negative Rate): {specificity:.2f}%")
            print(f"  Sensitivity (Recall): {sensitivity:.2f}%")

        except Exception as e:
            print(f"  ✗ Error: {e}")
            import traceback
            traceback.print_exc()

    # Print summary table
    if all_results:
        print("\n" + "="*80)
        print("RSNA F1 Summary Table")
        print("="*80)
        print()
        print(f"{'Experiment':<30} {'Precision':<12} {'Recall':<12} {'F1 Score':<12} {'Specificity':<12}")
        print("-" * 80)

        for name, metrics in all_results.items():
            cm = metrics['confusion_matrix']
            tn, fp, fn, tp = cm.ravel()
            specificity = tn / (tn + fp) * 100 if (tn + fp) > 0 else 0

            exp_name = name.replace(" (10%)", "")
            print(f"{exp_name:<30} {metrics['precision']:>10.2f}% {metrics['recall']:>10.2f}% {metrics['f1']:>10.2f}% {specificity:>10.2f}%")

        # Compare fine-tuning vs linear probe
        if len(all_results) == 2:
            ft_key = "RSNA Fine-tuning (10%)"
            lp_key = "RSNA Linear Probe (10%)"

            if ft_key in all_results and lp_key in all_results:
                print("\n" + "="*80)
                print("Fine-tuning vs Linear Probe Comparison")
                print("="*80)
                print()

                ft_f1 = all_results[ft_key]['f1']
                lp_f1 = all_results[lp_key]['f1']
                f1_diff = ft_f1 - lp_f1

                print(f"Fine-tuning F1: {ft_f1:.2f}%")
                print(f"Linear Probe F1: {lp_f1:.2f}%")
                print(f"Difference: {f1_diff:+.2f}% ({f1_diff/ft_f1*100:+.1f}% relative)")

        # Save to file
        with open("rsna_f1_results.txt", "w") as f:
            f.write("="*80 + "\n")
            f.write("RSNA F1 Score Results\n")
            f.write("="*80 + "\n\n")

            f.write(f"{'Experiment':<30} {'Precision':<12} {'Recall':<12} {'F1 Score':<12} {'Specificity':<12}\n")
            f.write("-" * 80 + "\n")

            for name, metrics in all_results.items():
                cm = metrics['confusion_matrix']
                tn, fp, fn, tp = cm.ravel()
                specificity = tn / (tn + fp) * 100 if (tn + fp) > 0 else 0

                exp_name = name.replace(" (10%)", "")
                f.write(f"{exp_name:<30} {metrics['precision']:>10.2f}% {metrics['recall']:>10.2f}% {metrics['f1']:>10.2f}% {specificity:>10.2f}%\n")

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

                cm = metrics['confusion_matrix']
                tn, fp, fn, tp = cm.ravel()
                specificity = tn / (tn + fp) * 100 if (tn + fp) > 0 else 0
                sensitivity = tp / (tp + fn) * 100 if (tp + fn) > 0 else 0

                f.write(f"\nConfusion Matrix:\n")
                f.write(f"              Predicted Neg  Predicted Pos\n")
                f.write(f"  Actual Neg       {cm[0][0]:>6}         {cm[0][1]:>6}\n")
                f.write(f"  Actual Pos       {cm[1][0]:>6}         {cm[1][1]:>6}\n")
                f.write(f"\nSpecificity: {specificity:.2f}%\n")
                f.write(f"Sensitivity: {sensitivity:.2f}%\n")

            # Add comparison if both exist
            if len(all_results) == 2:
                ft_key = "RSNA Fine-tuning (10%)"
                lp_key = "RSNA Linear Probe (10%)"

                if ft_key in all_results and lp_key in all_results:
                    f.write("\n" + "="*80 + "\n")
                    f.write("Fine-tuning vs Linear Probe Comparison\n")
                    f.write("="*80 + "\n\n")

                    ft_f1 = all_results[ft_key]['f1']
                    lp_f1 = all_results[lp_key]['f1']
                    f1_diff = ft_f1 - lp_f1

                    f.write(f"Fine-tuning F1: {ft_f1:.2f}%\n")
                    f.write(f"Linear Probe F1: {lp_f1:.2f}%\n")
                    f.write(f"Difference: {f1_diff:+.2f}% ({f1_diff/ft_f1*100:+.1f}% relative)\n")

        print(f"\n✓ Results saved to: rsna_f1_results.txt")
    else:
        print("\n⚠️ No results calculated")

    print()

if __name__ == "__main__":
    main()
