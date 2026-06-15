"""
Calculate F1 scores WITHOUT sklearn dependency
"""
from pathlib import Path
import numpy as np

def parse_array_line(line):
    """Parse a line like '[ 0.08984375 -0.11035156]' into numpy array"""
    line = line.strip()
    line = line.replace('[', '').replace(']', '')
    values = [float(x) for x in line.split() if x]
    return np.array(values)

def load_predictions(hyps_file, refs_file):
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

            pred_class = int(np.argmax(hyp_array))
            ref_class = int(np.argmax(ref_array))

            predictions.append(pred_class)
            references.append(ref_class)
        except Exception as e:
            continue

    return np.array(predictions), np.array(references)

def calculate_confusion_matrix(y_true, y_pred):
    """Manually calculate confusion matrix"""
    tn = np.sum((y_true == 0) & (y_pred == 0))
    fp = np.sum((y_true == 0) & (y_pred == 1))
    fn = np.sum((y_true == 1) & (y_pred == 0))
    tp = np.sum((y_true == 1) & (y_pred == 1))
    return tn, fp, fn, tp

def calculate_metrics(predictions, references, name):
    """Calculate metrics manually"""
    print(f"\n{name}:")
    print("-" * 70)

    n_total = len(predictions)
    n_pos_ref = np.sum(references == 1)
    n_neg_ref = np.sum(references == 0)
    n_pos_pred = np.sum(predictions == 1)
    n_neg_pred = np.sum(predictions == 0)

    print(f"Total samples: {n_total}")
    print(f"Actual: {n_neg_ref} neg ({n_neg_ref/n_total*100:.1f}%), "
          f"{n_pos_ref} pos ({n_pos_ref/n_total*100:.1f}%)")
    print(f"Predicted: {n_neg_pred} neg ({n_neg_pred/n_total*100:.1f}%), "
          f"{n_pos_pred} pos ({n_pos_pred/n_total*100:.1f}%)")

    # Calculate confusion matrix
    tn, fp, fn, tp = calculate_confusion_matrix(references, predictions)

    print(f"\nConfusion Matrix:")
    print(f"                Predicted Neg  Predicted Pos")
    print(f"  Actual Neg         {tn:>6}         {fp:>6}")
    print(f"  Actual Pos         {fn:>6}         {tp:>6}")

    # Calculate metrics
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
    specificity = tn / (tn + fp) if (tn + fp) > 0 else 0
    accuracy = (tp + tn) / n_total if n_total > 0 else 0

    print(f"\nMetrics:")
    print(f"  Precision:    {precision*100:>6.2f}%  (Of positive predictions, % correct)")
    print(f"  Recall:       {recall*100:>6.2f}%  (Of actual positives, % found)")
    print(f"  F1 Score:     {f1*100:>6.2f}%  (Harmonic mean)")
    print(f"  Specificity:  {specificity*100:>6.2f}%  (Of actual negatives, % correct)")
    print(f"  Accuracy:     {accuracy*100:>6.2f}%  (Overall correctness)")

    # Diagnosis
    print(f"\nDiagnosis:")
    if specificity > 0.85 and recall < 0.60:
        print("   WARNING: CONSERVATIVE - Predicts negative too often!")
        print("   - High specificity (few false positives)")
        print("   - Low recall (many false negatives)")
        print("   - Missing true positive cases")
        print("\n   Solution: Adjust classification threshold or use class weights")
    elif recall > 0.85 and specificity < 0.60:
        print("   WARNING: AGGRESSIVE - Predicts positive too often!")
    else:
        print("   OK: Relatively balanced predictions")

    return {
        'precision': precision * 100,
        'recall': recall * 100,
        'f1': f1 * 100,
        'specificity': specificity * 100,
        'accuracy': accuracy * 100,
        'tn': tn, 'fp': fp, 'fn': fn, 'tp': tp
    }

def main():
    print("="*80)
    print("F1 Score Calculation - SHARP BenchX (No sklearn)")
    print("="*80)
    print()

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
            print(f"  X File not found: {files['hyps']}")
            continue

        if not files['refs'].exists():
            print(f"  X File not found: {files['refs']}")
            continue

        try:
            predictions, references = load_predictions(files['hyps'], files['refs'])

            if len(predictions) == 0:
                print(f"  X No predictions loaded")
                continue

            metrics = calculate_metrics(predictions, references, name)
            all_results[name] = metrics

        except Exception as e:
            print(f"  X Error: {e}")
            import traceback
            traceback.print_exc()

    if all_results:
        print("\n" + "="*80)
        print("FINAL RESULTS")
        print("="*80)
        print()

        for name, m in all_results.items():
            print(f"{name}:")
            print(f"  F1 Score:     {m['f1']:.2f}%")
            print(f"  Precision:    {m['precision']:.2f}%")
            print(f"  Recall:       {m['recall']:.2f}%")
            print(f"  Specificity:  {m['specificity']:.2f}%")
            print(f"  Accuracy:     {m['accuracy']:.2f}%")
            print()

        # Save to file
        with open("f1_results_detailed.txt", "w") as f:
            f.write("="*80 + "\n")
            f.write("F1 Score Results - SHARP BenchX\n")
            f.write("="*80 + "\n\n")

            for name, m in all_results.items():
                f.write(f"{name}:\n")
                f.write(f"  F1 Score:     {m['f1']:.2f}%\n")
                f.write(f"  Precision:    {m['precision']:.2f}%\n")
                f.write(f"  Recall:       {m['recall']:.2f}%\n")
                f.write(f"  Specificity:  {m['specificity']:.2f}%\n")
                f.write(f"  Accuracy:     {m['accuracy']:.2f}%\n")
                f.write(f"\n  Confusion Matrix:\n")
                f.write(f"    TN: {m['tn']}, FP: {m['fp']}\n")
                f.write(f"    FN: {m['fn']}, TP: {m['tp']}\n")
                f.write("\n")

        print(f"OK Results saved to: f1_results_detailed.txt")

    else:
        print("\nWARNING: No results calculated")

    print()

if __name__ == "__main__":
    main()
