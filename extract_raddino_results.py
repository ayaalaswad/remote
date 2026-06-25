#!/usr/bin/env python3
"""
Extract RadDINO Stage 2 Results
================================

Reads the CXRMate test results and extracts key metrics.
"""

import json
import os
from pathlib import Path

def find_raddino_results():
    """Find RadDINO experiment directory in CXRMate"""
    cxrmate_dir = Path("C:/Users/aya.alaswad/remote/cxrmate")
    exp_dir = cxrmate_dir / "experiments"

    if not exp_dir.exists():
        print(f"[ERROR] Experiments directory not found: {exp_dir}")
        return None

    # Look for most recent experiment
    experiments = sorted(exp_dir.glob("*"), key=lambda x: x.stat().st_mtime, reverse=True)

    if not experiments:
        print(f"[ERROR] No experiments found in {exp_dir}")
        return None

    # Show all experiments and ask user to pick
    print("\n" + "="*80)
    print("Found experiments (sorted by most recent):")
    print("="*80)
    for i, exp in enumerate(experiments[:10]):  # Show top 10
        mtime = exp.stat().st_mtime
        print(f"  [{i+1}] {exp.name} (modified: {mtime})")

    # For automatic mode, just use the most recent
    latest = experiments[0]
    print(f"\n[INFO] Using most recent experiment: {latest.name}")

    return latest

def extract_metrics(exp_dir):
    """Extract metrics from lightning logs"""
    metrics_file = exp_dir / "lightning_logs" / "version_0" / "test_results.json"

    if not metrics_file.exists():
        print(f"[ERROR] Results file not found: {metrics_file}")
        print("\nTrying alternative location...")

        # Try metrics.csv
        csv_file = exp_dir / "lightning_logs" / "version_0" / "metrics.csv"
        if csv_file.exists():
            print(f"[INFO] Found metrics.csv, parsing...")
            return parse_metrics_csv(csv_file)

        return None

    with open(metrics_file) as f:
        results = json.load(f)

    return results

def parse_metrics_csv(csv_file):
    """Parse metrics from CSV file"""
    import csv

    test_metrics = {}
    with open(csv_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Look for test metrics (last row with test_ prefix)
            for key, val in row.items():
                if key.startswith('test_') and val:
                    test_metrics[key] = float(val)

    return test_metrics

def main():
    print("="*80)
    print("RadDINO Stage 2 Results Extraction")
    print("="*80)

    # Find experiment
    exp_dir = find_raddino_results()
    if not exp_dir:
        return

    # Extract metrics
    results = extract_metrics(exp_dir)
    if not results:
        print("\n[ERROR] Could not extract metrics")
        return

    # Display key metrics
    print("\n" + "="*80)
    print("RadDINO Stage 2 Results")
    print("="*80)
    print()

    # Main metric: CheXbert F1
    chexbert_key = None
    for key in results.keys():
        if 'chexbert' in key.lower() and 'f1' in key.lower() and 'macro' in key.lower():
            chexbert_key = key
            break

    if chexbert_key:
        chexbert_f1 = results[chexbert_key]
        print(f"  CheXbert F1 (macro): {chexbert_f1:.4f}")
        print()
    else:
        print("  [WARNING] CheXbert F1 not found in results")
        print()

    # Other metrics
    print("  Other metrics:")
    for key, val in sorted(results.items()):
        if key != chexbert_key:
            print(f"    {key}: {val:.4f}")

    print()
    print("="*80)
    print("Comparison with Main SHARP")
    print("="*80)
    print()
    print("  Main SHARP (Exp #3):  CheXbert F1 = 0.3032")
    if chexbert_key:
        print(f"  RadDINO (Stage 2):    CheXbert F1 = {chexbert_f1:.4f}")
        print()

        diff = chexbert_f1 - 0.3032
        pct_diff = (diff / 0.3032) * 100

        if diff > 0:
            print(f"  Δ = +{diff:.4f} ({pct_diff:+.1f}%) - RadDINO is BETTER ✓")
        elif diff < 0:
            print(f"  Δ = {diff:.4f} ({pct_diff:+.1f}%) - RadDINO is WORSE")
        else:
            print(f"  Δ = 0.0000 (0.0%) - Same performance")

    print()
    print("="*80)
    print()

    # Save results
    output_file = Path("raddino_results") / "stage2_results.json"
    output_file.parent.mkdir(exist_ok=True)

    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"[OK] Results saved to: {output_file}")
    print()

if __name__ == "__main__":
    main()
