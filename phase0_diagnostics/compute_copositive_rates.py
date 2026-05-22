"""
Phase 0 Diagnostic: Compute empirical co-positive frequency from all 4 training logs.

R3 explicitly asked for this. Currently we estimate:
- Exp #1: ~40%
- Exp #2: 100% (guaranteed by sampler)
- Exp #3: ~50%
- Exp #4: TBD

This script extracts the actual numbers from logs.
"""

import re
from pathlib import Path
from collections import defaultdict
import json


def extract_copositive_stats(log_file):
    """
    Extract MP-InfoNCE co-positive statistics from training log.

    Looks for lines like:
    [MP-InfoNCE stats] Direction: i<->t (bi), Batch size: 32, Avg co-positives: 0.69, Max: 2.0, % with co-pos: 50.0%
    """

    if not Path(log_file).exists():
        return None

    stats = {
        'avg_copos': [],
        'max_copos': [],
        'pct_with_copos': [],
        'steps': [],
    }

    with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
        for line_num, line in enumerate(f, 1):
            # Look for MP-InfoNCE stats pattern
            match = re.search(
                r'Avg co-positives:\s*([\d.]+),\s*Max:\s*([\d.]+),\s*%\s*with\s*co-pos:\s*([\d.]+)%',
                line
            )

            if match:
                avg_copos = float(match.group(1))
                max_copos = float(match.group(2))
                pct_copos = float(match.group(3))

                stats['avg_copos'].append(avg_copos)
                stats['max_copos'].append(max_copos)
                stats['pct_with_copos'].append(pct_copos)

                # Try to extract step number from same line or nearby
                step_match = re.search(r'step\s+(\d+)', line)
                if step_match:
                    stats['steps'].append(int(step_match.group(1)))
                else:
                    stats['steps'].append(None)

    return stats if len(stats['avg_copos']) > 0 else None


def compute_summary_stats(values):
    """Compute mean, min, max, final for a list of values."""
    if not values:
        return None

    return {
        'mean': sum(values) / len(values),
        'min': min(values),
        'max': max(values),
        'final': values[-1] if values else None,
        'count': len(values),
    }


def main():
    """Extract and compare co-positive rates from all experiments."""

    print("="*80)
    print("EMPIRICAL CO-POSITIVE RATE ANALYSIS")
    print("="*80)

    experiments = {
        'exp1_baseline': {
            'name': 'Baseline (bi, batch=32, random sampling)',
            'log': 'D:/experiments/exp1_baseline/training.log',
        },
        'exp2_paired': {
            'name': 'Paired Sampling (bi, batch=32, 100% co-pos)',
            'log': 'D:/experiments/exp2_paired_fixed/training.log',
        },
        'exp3_full': {
            'name': 'Full SHARP (bi, batch=32, hard neg 60%)',
            'log': 'D:/experiments/exp3_full_sharp/training.log',
        },
        'exp4_large': {
            'name': 'Large Batch (bi, batch=512, hard neg 60%)',
            'log': 'D:/experiments/exp4_large_batch/training.log',
        },
    }

    results = {}

    for exp_id, exp_info in experiments.items():
        log_path = Path(exp_info['log'])

        print(f"\n{exp_info['name']}")
        print("-" * 80)

        if not log_path.exists():
            print(f"  ✗ Log not found: {log_path}")
            results[exp_id] = None
            continue

        stats = extract_copositive_stats(log_path)

        if stats is None:
            print(f"  ✗ No MP-InfoNCE stats found in log")
            results[exp_id] = None
            continue

        # Compute summary statistics
        avg_summary = compute_summary_stats(stats['avg_copos'])
        max_summary = compute_summary_stats(stats['max_copos'])
        pct_summary = compute_summary_stats(stats['pct_with_copos'])

        print(f"  Found {avg_summary['count']} MP-InfoNCE stat entries")
        print(f"\n  Average Co-positives per Sample:")
        print(f"    Mean:  {avg_summary['mean']:.2f}")
        print(f"    Range: [{avg_summary['min']:.2f}, {avg_summary['max']:.2f}]")
        print(f"    Final: {avg_summary['final']:.2f}")

        print(f"\n  Max Co-positives in Batch:")
        print(f"    Mean:  {max_summary['mean']:.2f}")
        print(f"    Range: [{max_summary['min']:.2f}, {max_summary['max']:.2f}]")
        print(f"    Final: {max_summary['final']:.2f}")

        print(f"\n  % Batches with Co-positives:")
        print(f"    Mean:  {pct_summary['mean']:.1f}%")
        print(f"    Range: [{pct_summary['min']:.1f}%, {pct_summary['max']:.1f}%]")
        print(f"    Final: {pct_summary['final']:.1f}%")

        results[exp_id] = {
            'avg_copos': avg_summary,
            'max_copos': max_summary,
            'pct_with_copos': pct_summary,
        }

    # Create comparison table
    print("\n" + "="*80)
    print("COMPARISON TABLE")
    print("="*80)
    print()

    header = f"{'Experiment':<35} | {'Avg Co-pos':<12} | {'% with Co-pos':<15}"
    print(header)
    print("-" * len(header))

    for exp_id, exp_info in experiments.items():
        result = results.get(exp_id)

        if result is None:
            row = f"{exp_info['name']:<35} | {'N/A':<12} | {'N/A':<15}"
        else:
            avg_val = result['avg_copos']['mean']
            pct_val = result['pct_with_copos']['mean']
            row = f"{exp_info['name']:<35} | {avg_val:<12.2f} | {pct_val:<15.1f}%"

        print(row)

    print("\n" + "="*80)
    print("KEY FINDINGS FOR REVIEWERS")
    print("="*80)

    # R3 asked about this specifically
    exp1_result = results.get('exp1_baseline')
    exp2_result = results.get('exp2_paired')
    exp4_result = results.get('exp4_large')

    if exp1_result:
        print(f"\n1. Baseline (batch=32, random sampling):")
        print(f"   → {exp1_result['pct_with_copos']['mean']:.1f}% of batches have co-positives")
        print(f"   → Average {exp1_result['avg_copos']['mean']:.2f} co-positives per sample")
        print(f"   → This confirms R3's concern: insufficient co-positives at small batch size")

    if exp2_result:
        print(f"\n2. Paired sampling (batch=32, forced pairs):")
        print(f"   → {exp2_result['pct_with_copos']['mean']:.1f}% of batches have co-positives")
        if exp2_result['pct_with_copos']['mean'] >= 99.0:
            print(f"   → ✓ CONFIRMED: 100% co-positive rate achieved")
        else:
            print(f"   → ✗ WARNING: Not 100%! Sampler may have bugs")

    if exp4_result:
        print(f"\n3. Large batch (batch=512):")
        print(f"   → {exp4_result['pct_with_copos']['mean']:.1f}% of batches have co-positives")
        print(f"   → Average {exp4_result['avg_copos']['mean']:.2f} co-positives per sample")
        if exp1_result:
            improvement = exp4_result['avg_copos']['mean'] / exp1_result['avg_copos']['mean']
            print(f"   → {improvement:.1f}x more co-positives than batch=32")

    # Save results to JSON
    output = {
        exp_id: {
            'name': experiments[exp_id]['name'],
            'avg_copos_mean': results[exp_id]['avg_copos']['mean'] if results[exp_id] else None,
            'pct_with_copos_mean': results[exp_id]['pct_with_copos']['mean'] if results[exp_id] else None,
        }
        for exp_id in experiments.keys()
    }

    with open('copositive_rates_summary.json', 'w') as f:
        json.dump(output, f, indent=2)

    print("\n" + "="*80)
    print("Results saved to: copositive_rates_summary.json")
    print("="*80)


if __name__ == "__main__":
    main()
