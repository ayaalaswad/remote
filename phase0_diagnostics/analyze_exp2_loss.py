"""
Phase 0 Diagnostic: Analyze Exp #2 loss curve to diagnose training failure.

If loss diverged or plateaued → broken training
If loss decreased smoothly but R@1 collapsed → real and weird
"""

import re
import matplotlib.pyplot as plt
from pathlib import Path

def extract_loss_from_log(log_file):
    """Extract step and loss from training log."""
    steps = []
    losses = []

    with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            # Look for pattern: [step XXXXX] loss=X.XXXX
            match = re.search(r'\[step\s+(\d+)\]\s+loss=([\d.]+)', line)
            if match:
                step = int(match.group(1))
                loss = float(match.group(2))
                steps.append(step)
                losses.append(loss)

    return steps, losses


def extract_r_at_1_from_log(log_file):
    """Extract step and R@1 from training log."""
    steps = []
    r_at_1 = []

    with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            # Look for pattern: [step XXXXX] ... I->T R@1=X.XX%
            match = re.search(r'\[step\s+(\d+)\].*I->T R@1=([\d.]+)%', line)
            if match:
                step = int(match.group(1))
                r1 = float(match.group(2))
                steps.append(step)
                r_at_1.append(r1)

    return steps, r_at_1


def plot_exp2_diagnostics():
    """Plot Exp #2 loss and R@1 curves to diagnose failure."""

    # Paths to logs (on remote desktop these would be D:\experiments\...)
    exp2_log = Path("D:/experiments/exp2_paired_fixed/training.log")
    exp1_log = Path("D:/experiments/exp1_baseline/training.log")

    if not exp2_log.exists():
        print(f"ERROR: Exp #2 log not found at {exp2_log}")
        print("This script should be run on the remote desktop where training ran.")
        return

    print("Extracting Exp #2 training metrics...")
    exp2_steps, exp2_losses = extract_loss_from_log(exp2_log)
    exp2_r1_steps, exp2_r1 = extract_r_at_1_from_log(exp2_log)

    print(f"  Found {len(exp2_losses)} loss values")
    print(f"  Found {len(exp2_r1)} R@1 evaluations")

    # Also extract Exp #1 for comparison
    exp1_steps, exp1_losses = [], []
    exp1_r1_steps, exp1_r1 = [], []

    if exp1_log.exists():
        print("\nExtracting Exp #1 (baseline) for comparison...")
        exp1_steps, exp1_losses = extract_loss_from_log(exp1_log)
        exp1_r1_steps, exp1_r1 = extract_r_at_1_from_log(exp1_log)
        print(f"  Found {len(exp1_losses)} loss values")
        print(f"  Found {len(exp1_r1)} R@1 evaluations")

    # Create diagnostic plots
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('Exp #2 Diagnostic: Paired Sampling Failure Analysis', fontsize=16, fontweight='bold')

    # Plot 1: Loss curve
    ax1 = axes[0, 0]
    ax1.plot(exp2_steps, exp2_losses, label='Exp #2 (Paired)', alpha=0.7)
    if exp1_steps:
        ax1.plot(exp1_steps, exp1_losses, label='Exp #1 (Baseline)', alpha=0.7)
    ax1.set_xlabel('Step')
    ax1.set_ylabel('Loss')
    ax1.set_title('Training Loss Curve')
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    # Plot 2: R@1 curve
    ax2 = axes[0, 1]
    ax2.plot(exp2_r1_steps, exp2_r1, 'o-', label='Exp #2 (Paired)', markersize=4)
    if exp1_r1_steps:
        ax2.plot(exp1_r1_steps, exp1_r1, 'o-', label='Exp #1 (Baseline)', markersize=4)
    ax2.axhline(y=6.61, color='g', linestyle='--', label='Exp #1 Final (6.61%)', alpha=0.5)
    ax2.axhline(y=0.81, color='r', linestyle='--', label='Exp #2 Final (0.81%)', alpha=0.5)
    ax2.set_xlabel('Step')
    ax2.set_ylabel('R@1 (%)')
    ax2.set_title('Validation R@1')
    ax2.legend()
    ax2.grid(True, alpha=0.3)

    # Plot 3: Loss (first 10k steps only - to see if divergence happened early)
    ax3 = axes[1, 0]
    exp2_early_steps = [s for s in exp2_steps if s <= 10000]
    exp2_early_losses = [l for s, l in zip(exp2_steps, exp2_losses) if s <= 10000]
    ax3.plot(exp2_early_steps, exp2_early_losses, label='Exp #2 (Paired)', alpha=0.7)
    if exp1_steps:
        exp1_early_steps = [s for s in exp1_steps if s <= 10000]
        exp1_early_losses = [l for s, l in zip(exp1_steps, exp1_losses) if s <= 10000]
        ax3.plot(exp1_early_steps, exp1_early_losses, label='Exp #1 (Baseline)', alpha=0.7)
    ax3.set_xlabel('Step')
    ax3.set_ylabel('Loss')
    ax3.set_title('Training Loss (First 10k Steps)')
    ax3.legend()
    ax3.grid(True, alpha=0.3)

    # Plot 4: Loss gradient (rate of change)
    ax4 = axes[1, 1]
    if len(exp2_losses) > 1:
        exp2_loss_grad = [exp2_losses[i+1] - exp2_losses[i] for i in range(len(exp2_losses)-1)]
        ax4.plot(exp2_steps[1:], exp2_loss_grad, label='Exp #2 gradient', alpha=0.7)
    if len(exp1_losses) > 1:
        exp1_loss_grad = [exp1_losses[i+1] - exp1_losses[i] for i in range(len(exp1_losses)-1)]
        ax4.plot(exp1_steps[1:], exp1_loss_grad, label='Exp #1 gradient', alpha=0.7)
    ax4.axhline(y=0, color='k', linestyle='-', alpha=0.3)
    ax4.set_xlabel('Step')
    ax4.set_ylabel('Δ Loss')
    ax4.set_title('Loss Gradient (rate of change)')
    ax4.legend()
    ax4.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('exp2_diagnostic_plots.png', dpi=150, bbox_inches='tight')
    print(f"\n✓ Saved diagnostic plots to: exp2_diagnostic_plots.png")

    # Print diagnostic summary
    print("\n" + "="*80)
    print("DIAGNOSTIC SUMMARY")
    print("="*80)

    if len(exp2_losses) > 0:
        print(f"\nExp #2 Loss:")
        print(f"  Initial: {exp2_losses[0]:.4f}")
        print(f"  Final:   {exp2_losses[-1]:.4f}")
        print(f"  Change:  {exp2_losses[-1] - exp2_losses[0]:.4f}")

        # Check if loss decreased smoothly
        if exp2_losses[-1] < exp2_losses[0]:
            print(f"  ✓ Loss decreased (training progressed)")
        else:
            print(f"  ✗ Loss increased or stayed flat (possible training collapse)")

    if len(exp2_r1) > 0:
        print(f"\nExp #2 R@1:")
        print(f"  Best:  {max(exp2_r1):.2f}%")
        print(f"  Final: {exp2_r1[-1]:.2f}%")

        if max(exp2_r1) < 2.0:
            print(f"  ✗ R@1 never exceeded 2% (severe failure)")
        elif exp2_r1[-1] < 2.0:
            print(f"  ✗ R@1 collapsed below 2% (early stopping kicked in too late)")

    print("\n" + "="*80)
    print("DIAGNOSIS:")
    print("="*80)

    if len(exp2_losses) > 0 and exp2_losses[-1] < exp2_losses[0]:
        print("Loss decreased smoothly → Training ran successfully")
        print("But R@1 collapsed → This is REAL and WEIRD")
        print("\nPossible causes:")
        print("  1. Paired sampling creates trivial task (model memorizes pairs)")
        print("  2. Limited diversity (20k files vs 60k+ baseline)")
        print("  3. Model overfits to paired structure, loses generalization")
        print("\n✓ This is a FINDING: forced co-positives harm performance")
    else:
        print("Loss did NOT decrease properly → Training was BROKEN")
        print("\nPossible causes:")
        print("  1. Bug in paired sampler (creates invalid batches)")
        print("  2. Dataset corruption (manifest has bad entries)")
        print("  3. Hyperparameter issue (LR too high, etc.)")
        print("\n✗ This is a BUG: fix before making claims")

    print("="*80)


if __name__ == "__main__":
    plot_exp2_diagnostics()
