"""
Extract and summarize Stage 2 results from all 4 experiments.
Outputs CheXbert F1, RadGraph F1, and other metrics for comparison.
"""

import re
import json
from pathlib import Path

def extract_metric(log_file, metric_name):
    """Extract a metric value from log file."""
    if not Path(log_file).exists():
        return None

    with open(log_file, 'r') as f:
        content = f.read()

    # Look for pattern like: "test_report_chexbert_f1_macro: 0.3032"
    pattern = rf"{metric_name}:\s*([\d.]+)"
    match = re.search(pattern, content)

    if match:
        return float(match.group(1))
    return None


def main():
    logs_dir = Path("logs")

    experiments = {
        'exp1_baseline': 'Baseline (bi, batch=32)',
        'exp2_paired': 'Paired Sampling (100% co-pos)',
        'exp3_full': 'Full SHARP (hard neg 60%)',
        'exp4_large': 'Large Batch (batch=512)',
    }

    metrics_to_extract = [
        'test_report_chexbert_f1_macro',
        'test_report_radgraph_f1',
        'test_report_cxr_bert',
        'test_report_nlg_bleu_1',
        'test_report_nlg_bleu_4',
        'test_report_nlg_rouge_l',
        'test_report_nlg_meteor',
        'test_report_bertscore_f1',
    ]

    results = {}

    print("=" * 80)
    print("STAGE 2 RESULTS SUMMARY")
    print("=" * 80)
    print()

    for exp_id, exp_name in experiments.items():
        log_file = logs_dir / f"{exp_id}_test.log"

        print(f"{exp_id}: {exp_name}")
        print("-" * 80)

        results[exp_id] = {}

        for metric in metrics_to_extract:
            value = extract_metric(log_file, metric)
            results[exp_id][metric] = value

            # Friendly name
            friendly_name = metric.replace('test_report_', '').replace('_', ' ').title()

            if value is not None:
                print(f"  {friendly_name}: {value:.4f}")
            else:
                print(f"  {friendly_name}: NOT FOUND")

        print()

    # Save to JSON
    with open('results_all_metrics.json', 'w') as f:
        json.dump(results, f, indent=2)

    print("=" * 80)
    print("COMPARISON TABLE")
    print("=" * 80)
    print()

    # Print comparison table for key metrics
    key_metrics = [
        ('test_report_chexbert_f1_macro', 'CheXbert F1'),
        ('test_report_radgraph_f1', 'RadGraph F1'),
        ('test_report_cxr_bert', 'CXR-BERT'),
        ('test_report_nlg_bleu_4', 'BLEU-4'),
        ('test_report_nlg_rouge_l', 'ROUGE-L'),
    ]

    header = f"{'Experiment':<25} | " + " | ".join([f"{name:>12}" for _, name in key_metrics])
    print(header)
    print("-" * len(header))

    for exp_id, exp_name in experiments.items():
        row = f"{exp_name:<25} | "
        values = []
        for metric_key, _ in key_metrics:
            val = results[exp_id].get(metric_key)
            if val is not None:
                values.append(f"{val:>12.4f}")
            else:
                values.append(f"{'N/A':>12}")
        row += " | ".join(values)
        print(row)

    print()

    # Calculate improvements over baseline
    baseline_id = 'exp1_baseline'
    baseline = results[baseline_id]

    print("=" * 80)
    print("IMPROVEMENT OVER BASELINE (exp1)")
    print("=" * 80)
    print()

    for exp_id, exp_name in experiments.items():
        if exp_id == baseline_id:
            continue

        print(f"{exp_name}:")
        print("-" * 80)

        for metric_key, metric_name in key_metrics:
            baseline_val = baseline.get(metric_key)
            exp_val = results[exp_id].get(metric_key)

            if baseline_val is not None and exp_val is not None:
                diff = exp_val - baseline_val
                rel_change = (diff / baseline_val) * 100 if baseline_val != 0 else 0

                sign = "+" if diff > 0 else ""
                print(f"  {metric_name:<15}: {sign}{diff:.4f} ({sign}{rel_change:.1f}%)")

        print()

    print("=" * 80)
    print("Results saved to:")
    print("  - results_all_metrics.json (full results)")
    print("=" * 80)
    print()
    print("Next steps:")
    print("  1. Run: python per_condition_analysis.py")
    print("  2. Run: python statistical_tests.py")
    print()


if __name__ == "__main__":
    main()
