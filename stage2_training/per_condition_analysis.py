"""
Extract per-condition CheXbert F1 scores for the 14 conditions.
Focuses on conditions mentioned by reviewers: Fracture, Lung Lesion, Consolidation.
"""

import re
import pandas as pd
from pathlib import Path

# 14 CheXbert conditions
CHEXBERT_CONDITIONS = [
    'Enlarged Cardiomediastinum',
    'Cardiomegaly',
    'Lung Opacity',
    'Lung Lesion',
    'Edema',
    'Consolidation',
    'Pneumonia',
    'Atelectasis',
    'Pneumothorax',
    'Pleural Effusion',
    'Pleural Other',
    'Fracture',
    'Support Devices',
    'No Finding',
]

# Conditions specifically mentioned by reviewers
REVIEWER_CONDITIONS = ['Fracture', 'Lung Lesion', 'Consolidation']


def extract_condition_scores(log_file):
    """
    Extract per-condition F1 scores from test log.

    Pattern to look for:
    test_report_chexbert_f1_Fracture: 0.2345
    test_report_chexbert_f1_Lung_Lesion: 0.3456
    etc.
    """
    if not Path(log_file).exists():
        return {}

    with open(log_file, 'r') as f:
        content = f.read()

    scores = {}

    for condition in CHEXBERT_CONDITIONS:
        # Replace spaces with underscores for metric name
        metric_name = condition.replace(' ', '_')
        pattern = rf"test_report_chexbert_f1_{metric_name}:\s*([\d.]+)"

        match = re.search(pattern, content)
        if match:
            scores[condition] = float(match.group(1))
        else:
            scores[condition] = None

    return scores


def main():
    logs_dir = Path("logs")

    experiments = {
        'exp1_baseline': 'Baseline (bi, batch=32)',
        'exp2_paired': 'Paired Sampling (100% co-pos)',
        'exp3_full': 'Full SHARP (hard neg 60%)',
        'exp4_large': 'Large Batch (batch=512)',
    }

    print("=" * 80)
    print("PER-CONDITION CHEXBERT F1 ANALYSIS")
    print("=" * 80)
    print()

    # Extract scores for all experiments
    all_results = {}

    for exp_id, exp_name in experiments.items():
        log_file = logs_dir / f"{exp_id}_test.log"
        scores = extract_condition_scores(log_file)
        all_results[exp_id] = scores

    # Create DataFrame for easy comparison
    df_data = []

    for condition in CHEXBERT_CONDITIONS:
        row = {'Condition': condition}
        for exp_id in experiments.keys():
            row[exp_id] = all_results[exp_id].get(condition)
        df_data.append(row)

    df = pd.DataFrame(df_data)

    # Calculate improvements over baseline
    baseline_col = 'exp1_baseline'
    for exp_id in experiments.keys():
        if exp_id != baseline_col:
            diff_col = f'{exp_id}_diff'
            df[diff_col] = df[exp_id] - df[baseline_col]

    # Save full results
    df.to_csv('results_per_condition.csv', index=False)
    print("Full per-condition results saved to: results_per_condition.csv")
    print()

    # Print summary for reviewer-mentioned conditions
    print("=" * 80)
    print("REVIEWER-MENTIONED CONDITIONS (Fracture, Lung Lesion, Consolidation)")
    print("=" * 80)
    print()

    reviewer_df = df[df['Condition'].isin(REVIEWER_CONDITIONS)]

    for _, row in reviewer_df.iterrows():
        condition = row['Condition']
        print(f"{condition}:")
        print("-" * 80)

        for exp_id, exp_name in experiments.items():
            value = row[exp_id]

            if value is not None:
                if exp_id == baseline_col:
                    print(f"  {exp_name:<35}: {value:.4f} (baseline)")
                else:
                    diff = row[f'{exp_id}_diff']
                    sign = "+" if diff > 0 else ""
                    rel_change = (diff / row[baseline_col]) * 100 if row[baseline_col] != 0 else 0
                    print(f"  {exp_name:<35}: {value:.4f} ({sign}{diff:.4f}, {sign}{rel_change:>6.1f}%)")
            else:
                print(f"  {exp_name:<35}: N/A")

        print()

    # Print full condition table
    print("=" * 80)
    print("ALL 14 CONDITIONS - COMPARISON TABLE")
    print("=" * 80)
    print()

    # Format as table
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', None)
    pd.set_option('display.float_format', lambda x: f'{x:.4f}' if pd.notnull(x) else 'N/A')

    print(df[['Condition', 'exp1_baseline', 'exp2_paired', 'exp3_full', 'exp4_large']].to_string(index=False))
    print()

    # Summary statistics
    print("=" * 80)
    print("SUMMARY STATISTICS")
    print("=" * 80)
    print()

    for exp_id, exp_name in experiments.items():
        values = df[exp_id].dropna()
        if len(values) > 0:
            mean_f1 = values.mean()
            std_f1 = values.std()
            min_f1 = values.min()
            max_f1 = values.max()

            print(f"{exp_name}:")
            print(f"  Mean F1:   {mean_f1:.4f} (+/- {std_f1:.4f})")
            print(f"  Min F1:    {min_f1:.4f}")
            print(f"  Max F1:    {max_f1:.4f}")
            print()

    print("=" * 80)
    print("Files generated:")
    print("  - results_per_condition.csv")
    print("=" * 80)
    print()


if __name__ == "__main__":
    main()
