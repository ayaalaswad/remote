"""
Calculate F1 scores from pushed results (simple array format)
"""
from pathlib import Path
from sklearn.metrics import precision_recall_fscore_support, confusion_matrix
import numpy as np
import re

def parse_array_line(line):
    """Parse a line like '[ 0.08984375 -0.11035156]' into numpy array"""
    line = line.strip()
    # Remove brackets and split by whitespace
    line = line.replace('[', '').replace(']', '')
    values = [float(x) for x in line.split() if x]
    return np.array(values)

def load_predictions_simple(hyps_file, refs_file):
    """Load predictions from simple array format"""
    predictions = []
    references = []

    with open(hyps_file, 'r') as f:
        hyps_lines = f.readlines()

    with open(refs_file, 'r') as f:
        refs_lines = f.readlines()

    print(f"  Found {len(hyps_lines)} prediction lines")
    print(f"  Found {len(refs_lines)} reference lines")

    for hyp_line, ref_line in zip(hyps_lines, refs_lines):
        try:
            hyp_array = parse_array_line(hyp_line)
            ref_array = parse_array_line(ref_line)

            # Get predicted class (argmax of scores)
            pred_class = int(np.argmax(hyp_array))
            # Get reference class (argmax of one-hot)
            ref_class = int(np.argmax(ref_array))

            predictions.append(pred_class)
            references.append(ref_class)
        except Exception as e:
            print(f"  Warning: Could not parse line: {e}")
            continue

    return np.array(predictions), np.array(references)

def calculate_metrics(predictions, references, name):
    """Calculate and display metrics"""
    print(f"\n{name}:")
    print("-" * 70)

    # Basic counts
    n_total = len(predictions)
    n_pos_ref = np.sum(references == 1)
    n_neg_ref = np.sum(references == 0)
    n_pos_pred = np.sum(predictions == 1)
    n_neg_pred = np.sum(predictions == 0)

    print(f"Total samples: {n_total}")
    print(f"Actual distribution: {n_neg_ref} negative ({n_neg_ref/n_total*100:.1f}%), "
          f"{n_pos_ref} positive ({n_pos_ref/n_total*100:.1f}%)")
    print(f"Predicted distribution: {n_neg_pred} negative ({n_neg_pred/n_total*100:.1f}%), "
          f"{n_pos_pred} positive ({n_pos_pred/n_total*100:.1f}%)")

    # Confusion matrix
    cm = confusion_matrix(references, predictions)
    tn, fp, fn, tp = cm.ravel()

    print(f"\nConfusion Matrix:")
    print(f"                Predicted Neg  Predicted Pos")
    print(f"  Actual Neg         {tn:>6}         {fp:>6}")
    print(f"  Actual Pos         {fn:>6}         {tp:>6}")

    # Calculate metrics
    precision, recall, f1, _ = precision_recall_fscore_support(
        references, predictions, average='binary', zero_division=0
    )

    specificity = tn / (tn + fp) * 100 if (tn + fp) > 0 else 0
    sensitivity = tp / (tp + fn) * 100 if (tp + fn) > 0 else 0

    print(f"\n{'Metric':<20} {'Value':<15} {'Interpretation'}")
    print("-" * 70)
    print(f"{'Precision':<20} {precision*100:>13.2f}%   Of positive predictions, how many correct?")
    print(f"{'Recall/Sensitivity':<20} {recall*100:>13.2f}%   Of actual positives, how many found?")
    print(f"{'F1 Score':<20} {f1*100:>13.2f}%   Harmonic mean of precision & recall")
    print(f"{'Specificity':<20} {specificity:>13.2f}%   Of actual negatives, how many correct?")

    # Diagnosis
    print(f"\n🔍 Analysis:")
    if specificity > 85 and sensitivity < 60:
        print("   ⚠️  CONSERVATIVE model - predicts negative too often")
        print("   - High specificity (few false positives)")
        print("   - Low recall (many false negatives)")
        print("   - Missing many true positive cases")
    elif sensitivity > 85 and specificity < 60:
        print("   ⚠️  AGGRESSIVE model - predicts positive too often")
        print("   - High recall (few false negatives)")
        print("   - Low specificity (many false positives)")
    else:
        print("   ✓ Balanced model")

    return {
        'precision': precision * 100,
        'recall': recall * 100,
        'f1': f1 * 100,
        'specificity': specificity,
        'sensitivity': sensitivity,
        'cm': cm,
        'n_samples': n_total
    }

def main():
    print("="*80)
    print("F1 Score Calculation - SHARP BenchX Results")
    print("="*80)
    print()

    # Use current directory if running from remote, otherwise navigate
    base_dir = Path(".")
    if not (base_dir / "rsna_lp_results").exists():
        base_dir = Path("C:/Users/aya.alaswad/remote")

    experiments = {
        "RSNA Linear Probe (10%)": {
            "hyps": base_dir / "rsna_lp_results/val_42_hyps.txt",
            "refs": base_dir / "rsna_lp_results/val_42_refs.txt"
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
            predictions, references = load_predictions_simple(files['hyps'], files['refs'])

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
        print("SUMMARY TABLE")
        print("="*80)
        print()
        print(f"{'Experiment':<30} {'Precision':<12} {'Recall':<12} {'F1 Score':<12} {'Specificity':<12}")
        print("-" * 80)

        for name, metrics in all_results.items():
            exp_name = name.replace(" (10%)", "")
            print(f"{exp_name:<30} {metrics['precision']:>10.2f}% {metrics['recall']:>10.2f}% "
                  f"{metrics['f1']:>10.2f}% {metrics['specificity']:>10.2f}%")

        # Save to file
        with open("f1_results_detailed.txt", "w") as f:
            f.write("="*80 + "\n")
            f.write("F1 Score Results - SHARP BenchX\n")
            f.write("="*80 + "\n\n")

            for name, metrics in all_results.items():
                f.write(f"{name}:\n")
                f.write(f"  Samples: {metrics['n_samples']}\n")
                f.write(f"  Precision: {metrics['precision']:.2f}%\n")
                f.write(f"  Recall (Sensitivity): {metrics['recall']:.2f}%\n")
                f.write(f"  F1 Score: {metrics['f1']:.2f}%\n")
                f.write(f"  Specificity: {metrics['specificity']:.2f}%\n")

                cm = metrics['cm']
                tn, fp, fn, tp = cm.ravel()
                f.write(f"\n  Confusion Matrix:\n")
                f.write(f"                Predicted Neg  Predicted Pos\n")
                f.write(f"    Actual Neg       {tn:>6}         {fp:>6}\n")
                f.write(f"    Actual Pos       {fn:>6}         {tp:>6}\n")
                f.write("\n")

        print(f"\n✓ Results saved to: f1_results_detailed.txt")

        print("\n" + "="*80)
        print("📊 Key Takeaway")
        print("="*80)
        print()
        for name, metrics in all_results.items():
            print(f"{name}:")
            print(f"  F1 Score: {metrics['f1']:.2f}%")
            print(f"  Specificity vs Sensitivity: {metrics['specificity']:.1f}% vs {metrics['sensitivity']:.1f}%")

            if metrics['specificity'] > 85 and metrics['sensitivity'] < 60:
                print(f"  → Model is CONSERVATIVE (predicts negative too often)")
                print(f"  → This explains the F1 gap compared to MGCA (66.6%)")

    else:
        print("\n⚠️ No results calculated")

    print()

if __name__ == "__main__":
    main()
