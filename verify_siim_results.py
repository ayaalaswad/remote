"""
Three verification checks for SIIM results:
1. Check if predictions are fresh (not stale from pre-fix)
2. Verify global_pool setting is 'avg' not 'token'
3. Plot positive-class probability histogram
"""
import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt

def parse_array_line(line):
    """Parse array format like '[ 0.08984375 -0.11035156]'"""
    line = line.strip().replace('[', '').replace(']', '')
    values = [float(x) for x in line.split() if x]
    return np.array(values)

def check_1_timestamps():
    """Check 1: Verify prediction files are fresh (from today's training)"""
    print("="*80)
    print("CHECK 1: Prediction File Timestamps")
    print("="*80)
    print()

    import os
    import datetime

    base = Path("BenchX/experiments/classification/siim")

    for exp in ["SHARP_1pct", "SHARP_10pct", "SHARP_100pct"]:
        hyps_file = base / exp / exp / "val_42_hyps.txt"

        if hyps_file.exists():
            timestamp = os.path.getctime(hyps_file)
            dt = datetime.datetime.fromtimestamp(timestamp)
            print(f"{exp}:")
            print(f"  Created: {dt.strftime('%Y-%m-%d %H:%M:%S')}")

            # Check if from today
            today = datetime.date.today()
            if dt.date() == today:
                print(f"  Status: FRESH (created today)")
            else:
                print(f"  Status: STALE (created {(today - dt.date()).days} days ago)")
        else:
            print(f"{exp}: FILE NOT FOUND")
        print()

def check_2_global_pool():
    """Check 2: Verify global_pool setting in configs"""
    print("="*80)
    print("CHECK 2: Global Pool Setting")
    print("="*80)
    print()

    import yaml

    configs = {
        "SIIM 1%": "sharp_siim_1pct.yml",
        "SIIM 10%": "sharp_siim_10pct.yml",
        "SIIM 100%": "sharp_siim_100pct.yml",
    }

    for name, config_file in configs.items():
        config_path = Path(config_file)

        if not config_path.exists():
            print(f"{name}: Config file not found: {config_file}")
            continue

        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)

        global_pool = config.get('model', {}).get('cnn', {}).get('global_pool', 'NOT SET')

        print(f"{name}:")
        print(f"  Config: {config_file}")
        print(f"  global_pool: {global_pool}")

        if global_pool == 'avg':
            print(f"  Status: CORRECT (avg)")
        elif global_pool == 'token':
            print(f"  Status: WRONG - Should be 'avg' not 'token'!")
        else:
            print(f"  Status: NOT SET")
        print()

def check_3_probability_histogram():
    """Check 3: Plot positive-class probability histogram"""
    print("="*80)
    print("CHECK 3: Positive-Class Probability Histogram")
    print("="*80)
    print()

    base = Path("BenchX/experiments/classification/siim")

    fig, axes = plt.subplots(1, 3, figsize=(15, 4))

    experiments = [
        ("SIIM 1%", "SHARP_1pct"),
        ("SIIM 10%", "SHARP_10pct"),
        ("SIIM 100%", "SHARP_100pct"),
    ]

    for idx, (name, exp_dir) in enumerate(experiments):
        hyps_file = base / exp_dir / exp_dir / "val_42_hyps.txt"
        refs_file = base / exp_dir / exp_dir / "val_42_refs.txt"

        if not hyps_file.exists():
            print(f"{name}: Prediction file not found")
            continue

        # Load predictions (logits)
        pos_probs = []
        true_labels = []

        with open(hyps_file, 'r') as f:
            hyps_lines = f.readlines()
        with open(refs_file, 'r') as f:
            refs_lines = f.readlines()

        for hyp_line, ref_line in zip(hyps_lines, refs_lines):
            try:
                logits = parse_array_line(hyp_line)
                ref_array = parse_array_line(ref_line)

                # Convert logits to probabilities using softmax
                exp_logits = np.exp(logits - np.max(logits))  # numerical stability
                probs = exp_logits / np.sum(exp_logits)

                pos_prob = probs[1]  # Probability of positive class
                true_label = int(np.argmax(ref_array))

                pos_probs.append(pos_prob)
                true_labels.append(true_label)
            except:
                continue

        pos_probs = np.array(pos_probs)
        true_labels = np.array(true_labels)

        # Plot histogram
        ax = axes[idx]

        # Separate by true label
        pos_probs_negative = pos_probs[true_labels == 0]
        pos_probs_positive = pos_probs[true_labels == 1]

        ax.hist(pos_probs_negative, bins=50, alpha=0.5, label='True Negative', color='blue')
        ax.hist(pos_probs_positive, bins=50, alpha=0.5, label='True Positive', color='red')
        ax.axvline(0.5, color='black', linestyle='--', linewidth=2, label='Threshold (0.5)')

        ax.set_xlabel('Positive Class Probability')
        ax.set_ylabel('Count')
        ax.set_title(f'{name}\nAUROC in filename')
        ax.legend()
        ax.grid(True, alpha=0.3)

        # Statistics
        print(f"{name}:")
        print(f"  Total samples: {len(pos_probs)}")
        print(f"  True positives: {np.sum(true_labels == 1)}")
        print(f"  Positive probs for TRUE POSITIVES:")
        print(f"    Mean: {pos_probs_positive.mean():.3f}")
        print(f"    Median: {np.median(pos_probs_positive):.3f}")
        print(f"    % above 0.5: {(pos_probs_positive > 0.5).sum() / len(pos_probs_positive) * 100:.1f}%")
        print(f"  Positive probs for TRUE NEGATIVES:")
        print(f"    Mean: {pos_probs_negative.mean():.3f}")
        print(f"    Median: {np.median(pos_probs_negative):.3f}")
        print()

    plt.tight_layout()
    plt.savefig('siim_probability_histograms.png', dpi=150, bbox_inches='tight')
    print(f"Histogram saved to: siim_probability_histograms.png")
    print()

    # Interpretation
    print("="*80)
    print("INTERPRETATION")
    print("="*80)
    print()
    print("If positive-class probabilities for TRUE POSITIVES bunch at 0.1-0.4:")
    print("  -> Calibration issue confirmed (AUROC good, threshold bad)")
    print("  -> Expected behavior with unweighted CE on imbalanced data")
    print()
    print("If positive-class probabilities for TRUE POSITIVES are >0.5:")
    print("  -> Something else is wrong (predictions might be stale)")

def main():
    print()
    print("="*80)
    print("SIIM Results Verification - 3 Checks")
    print("="*80)
    print()

    # Check 1: Timestamps
    check_1_timestamps()

    # Check 2: Global pool
    try:
        check_2_global_pool()
    except Exception as e:
        print(f"Check 2 failed: {e}")
        print("(Needs PyYAML: pip install pyyaml)")
        print()

    # Check 3: Probability histogram
    try:
        check_3_probability_histogram()
    except Exception as e:
        print(f"Check 3 failed: {e}")
        print()

    print("="*80)
    print("NEXT STEP: Run MGCA baseline on SIIM to prove low F1 is expected")
    print("="*80)

if __name__ == "__main__":
    main()
