#!/usr/bin/env python3
"""
Verify Bidirectional Ablation Study
====================================

This script checks:
1. Which experiments used bidirectional loss
2. What R@1 results they achieved
3. If the paper claims match the actual experiments

Run this on the REMOTE DESKTOP where experiments are stored.
"""

import json
from pathlib import Path

def check_experiment(exp_dir):
    """Check if experiment used bidirectional and get R@1"""
    exp_path = Path(exp_dir)

    if not exp_path.exists():
        return None

    print(f"\nChecking: {exp_path.name}")
    print("-" * 80)

    # Look for config/history files
    config_files = list(exp_path.glob("*.json"))
    history_files = list(exp_path.glob("*history*.json"))

    bidirectional = None
    best_r1 = None

    # Check config files
    for config_file in config_files:
        try:
            with open(config_file) as f:
                data = json.load(f)

                # Check for bidirectional flag
                if isinstance(data, dict):
                    if 'bidirectional' in data:
                        bidirectional = data['bidirectional']
                    elif 'args' in data and 'bidirectional' in data['args']:
                        bidirectional = data['args']['bidirectional']

                    # Check for R@1 results
                    if 'best_r1' in data:
                        best_r1 = data['best_r1']
                    elif 'val_r1' in data:
                        best_r1 = data['val_r1']

            print(f"  Config: {config_file.name}")
            if bidirectional is not None:
                print(f"    Bidirectional: {bidirectional}")
            if best_r1 is not None:
                print(f"    Best R@1: {best_r1:.2%}")

        except Exception as e:
            print(f"  Error reading {config_file.name}: {e}")

    # Check history files
    for history_file in history_files:
        try:
            with open(history_file) as f:
                data = json.load(f)

                # History is usually a list of dicts with step/metrics
                if isinstance(data, list) and data:
                    # Find best R@1
                    r1_values = [entry.get('val_r1', 0) for entry in data if 'val_r1' in entry]
                    if r1_values:
                        best_r1 = max(r1_values)
                        print(f"  History: {history_file.name}")
                        print(f"    Best R@1: {best_r1:.2%}")

        except Exception as e:
            print(f"  Error reading {history_file.name}: {e}")

    # Check checkpoint filenames (sometimes encode R@1)
    checkpoints = list(exp_path.glob("p3_best*.pt")) + list(exp_path.glob("p3_best*.pth"))
    for ckpt in checkpoints:
        # Format: 0.0702_23_42.pt (r1_epoch_step.pt)
        parts = ckpt.stem.split('_')
        if len(parts) >= 1:
            try:
                r1_from_name = float(parts[0])
                if 0 < r1_from_name < 1:  # Reasonable R@1 range
                    print(f"  Checkpoint: {ckpt.name}")
                    print(f"    R@1 (from filename): {r1_from_name:.2%}")
                    if best_r1 is None:
                        best_r1 = r1_from_name
            except:
                pass

    return {
        'name': exp_path.name,
        'bidirectional': bidirectional,
        'best_r1': best_r1
    }

def main():
    print("="*80)
    print("Bidirectional Ablation Verification")
    print("="*80)
    print()

    # Define experiments to check
    experiments = [
        "D:/experiments/exp1_baseline",
        "D:/experiments/exp2_paired",
        "D:/experiments/exp3_hardneg",
        "D:/experiments/exp3_full_sharp",
        "D:/experiments/exp4_large_batch",
        "D:/experiments/exp_raddino_hardneg",
        # Add more experiment paths as needed
    ]

    results = []

    for exp in experiments:
        result = check_experiment(exp)
        if result:
            results.append(result)

    # Summary
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    print()

    print("| Experiment | Bidirectional | Best R@1 | Matches Paper? |")
    print("|------------|---------------|----------|----------------|")

    for r in results:
        bidir_str = "✓ Yes" if r['bidirectional'] else "✗ No" if r['bidirectional'] is False else "?"
        r1_str = f"{r['best_r1']:.2%}" if r['best_r1'] else "?"

        # Check against paper claims
        matches = ""
        if r['bidirectional'] and r['best_r1']:
            # Paper says: ablation (B) bidirectional got R@1 = 6.61%
            if abs(r['best_r1'] - 0.0661) < 0.002:  # Within 0.2%
                matches = "✓ Yes (6.61%)"
            else:
                matches = f"? ({r1_str} vs 6.61%)"

        print(f"| {r['name'][:30]:<30} | {bidir_str:^13} | {r1_str:^8} | {matches:^14} |")

    print()
    print("="*80)
    print()

    print("PAPER CLAIMS (Section 4.2, lines 564-576):")
    print("-" * 80)
    print("  Ablation (B) with bidirectional loss: R@1 = 6.61%")
    print("  Ablation (B) with unidirectional loss: R@1 = 7.02%")
    print()
    print("  Interpretation: Bidirectional loss got LOWER R@1 (6.61% vs 7.02%)")
    print()

    # Verify findings
    bidirectional_exps = [r for r in results if r['bidirectional']]

    if bidirectional_exps:
        print("✓ Found experiments with bidirectional=true:")
        for r in bidirectional_exps:
            r1_str = f"R@1={r['best_r1']:.2%}" if r['best_r1'] else "R@1=?"
            print(f"    - {r['name']}: {r1_str}")
    else:
        print("⚠ WARNING: No experiments found with bidirectional=true!")
        print("           You may need to check experiment directories manually.")

    print()
    print("="*80)
    print()

if __name__ == "__main__":
    main()
