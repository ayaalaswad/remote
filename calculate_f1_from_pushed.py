"""
Calculate F1 scores from already-pushed results
"""
import json
from pathlib import Path
from sklearn.metrics import precision_recall_fscore_support, confusion_matrix
import numpy as np

def load_predictions_from_pushed(hyps_file, refs_file):
    """Load predictions and references from pushed results files"""
    predictions = []
    references = []

    print(f"  Reading: {hyps_file}")
    print(f"  Reading: {refs_file}")

    with open(hyps_file, 'r') as f:
        hyps_lines = f.readlines()

    with open(refs_file, 'r') as f:
        refs_lines = f.readlines()

    print(f"  Found {len(hyps_lines)} hypothesis lines")
    print(f"  Found {len(refs_lines)} reference lines")

    for hyp_line, ref_line in zip(hyps_lines, refs_lines):
        hyp_line = hyp_line.strip()
        ref_line = ref_line.strip()

        if hyp_line and ref_line:
            try:
                hyp_data = json.loads(hyp_line)
                ref_data = json.loads(ref_line)

                # Extract predictions
                if 'predictions' in hyp_data:
                    pred = hyp_data['predictions']
                    predictions.append(int(np.argmax(pred)))

                # Extract references
                if 'labels' in ref_data:
                    references.append(int(ref_data['labels']))
            except Exception as e:
                print(f"  Warning: Could not parse line: {e}")
                continue

    return np.array(predictions), np.array(references)

def calculate_metrics(predictions, references, name):
    """Calculate and display metrics"""
    print(f"\n{name}:")
    print("-" * 60)

    # Basic counts
    n_total = len(predictions)
    n_pos_ref = np.sum(references == 1)
    n_neg_ref = np.sum(references == 0)
    n_pos_pred = np.sum(predictions == 1)
    n_neg_pred = np.sum(predictions == 0)

    print(f"Total samples: {n_total}")
    print(f"Actual: {n_neg_ref} negative ({n_neg_ref/n_total*100:.1f}%), {n_pos_ref} positive ({n_pos_ref/n_total*100:.1f}%)")
    print(f"Predicted: {n_neg_pred} negative ({n_neg_pred/n_total*100:.1f}%), {n_pos_pred} positive ({n_pos_pred/n_total*100:.1f}%)")

    # Confusion matrix
    cm = confusion_matrix(references, predictions)
    tn, fp, fn, tp = cm.ravel()

    print(f"\nConfusion Matrix:")
    print(f"              Predicted Neg  Predicted Pos")
    print(f"  Actual Neg       {tn:>6}         {fp:>6}")
    print(f"  Actual Pos       {fn:>6}         {tp:>6}")

    # Calculate metrics
    precision, recall, f1, _ = precision_recall_fscore_support(
        references, predictions, average='binary', zero_division=0
    )

    specificity = tn / (tn + fp) * 100 if (tn + fp) > 0 else 0
    sensitivity = tp / (tp + fn) * 100 if (tp + fn) > 0 else 0

    print(f"\nMetrics:")
    print(f"  Precision: {precision*100:.2f}%")
    print(f"  Recall (Sensitivity): {recall*100:.2f}%")
    print(f"  F1 Score: {f1*100:.2f}%")
    print(f"  Specificity: {specificity:.2f}%")

    return {
        'precision': precision * 100,
        'recall': recall * 100,
        'f1': f1 * 100,
        'specificity': specificity,
        'sensitivity': sensitivity,
        'cm': cm
    }

def main():
    print("="*80)
    print("F1 Score Calculation from Pushed Results")
    print("="*80)
    print()

    results_dir = Path("C:/Users/aya.alaswad/remote")

    experiments = {
        "RSNA Linear Probe (10%)": {
            "hyps": results_dir / "rsna_lp_results/val_42_hyps.txt",
            "refs": results_dir / "rsna_lp_results/val_42_refs.txt"
        }
    }

    all_results = {}

    for name, files in experiments.items():
        print(f"\n{'='*80}")
        print(f"Processing: {name}")
        print('='*80)

        if not files['hyps'].exists():
            print(f"  ✗ File not found: {files['hyps']}")
            continue

        if not files['refs'].exists():
            print(f"  ✗ File not found: {files['refs']}")
            continue

        try:
            predictions, references = load_predictions_from_pushed(files['hyps'], files['refs'])

            if len(predictions) == 0:
                print(f"  ✗ No predictions loaded")
                continue

            metrics = calculate_metrics(predictions, references, name)
            all_results[name] = metrics

        except Exception as e:
            print(f"  ✗ Error: {e}")
            import traceback
            traceback.print_exc()

    # Print summary
    if all_results:
        print("\n" + "="*80)
        print("SUMMARY")
        print("="*80)
        print()
        print(f"{'Experiment':<30} {'Precision':<12} {'Recall':<12} {'F1 Score':<12} {'Specificity':<12}")
        print("-" * 80)

        for name, metrics in all_results.items():
            exp_name = name.replace(" (10%)", "")
            print(f"{exp_name:<30} {metrics['precision']:>10.2f}% {metrics['recall']:>10.2f}% {metrics['f1']:>10.2f}% {metrics['specificity']:>10.2f}%")

        # Save to file
        with open("f1_results.txt", "w") as f:
            f.write("="*80 + "\n")
            f.write("F1 Score Results\n")
            f.write("="*80 + "\n\n")

            for name, metrics in all_results.items():
                f.write(f"{name}:\n")
                f.write(f"  Precision: {metrics['precision']:.2f}%\n")
                f.write(f"  Recall: {metrics['recall']:.2f}%\n")
                f.write(f"  F1 Score: {metrics['f1']:.2f}%\n")
                f.write(f"  Specificity: {metrics['specificity']:.2f}%\n")
                f.write(f"  Sensitivity: {metrics['sensitivity']:.2f}%\n")
                f.write("\n")

        print(f"\n✓ Results saved to: f1_results.txt")
    else:
        print("\n⚠️ No results calculated")

    print()

if __name__ == "__main__":
    main()
