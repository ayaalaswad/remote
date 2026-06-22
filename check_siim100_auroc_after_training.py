"""
Post-training analysis for SIIM 100% with avg pooling
Compares NEW AUROC (avg) vs OLD AUROC (token) and recommends next steps
"""
from pathlib import Path
import re

def find_checkpoint_auroc(exp_dir):
    """Find AUROC from checkpoint filename"""
    checkpoint_files = list(exp_dir.glob("*.pth")) + list(exp_dir.glob("*.pt"))

    if not checkpoint_files:
        return None, None

    # Find the checkpoint with highest AUROC (best model)
    best_auroc = None
    best_file = None

    for ckpt in checkpoint_files:
        # Parse filename like: 0.668147_50_42.pth
        match = re.match(r'(\d+\.\d+)_(\d+)_(\d+)\.(pth|pt)', ckpt.name)
        if match:
            auroc = float(match.group(1))
            if best_auroc is None or auroc > best_auroc:
                best_auroc = auroc
                best_file = ckpt.name

    return best_auroc, best_file

def main():
    print("="*80)
    print("SIIM 100% Post-Training Analysis")
    print("="*80)
    print()
    print("Comparing: token pooling (OLD) vs avg pooling (NEW)")
    print()

    base_path = Path("BenchX/experiments/classification/siim/SHARP_100pct/SHARP_100pct")

    if not base_path.exists():
        print(f"[ERROR] Directory not found: {base_path}")
        print()
        print("Make sure training completed and results are in:")
        print(f"  {base_path.absolute()}")
        return

    print(f"[1/3] Finding NEW checkpoint (avg pooling)...")
    print(f"      Directory: {base_path}")
    print()

    auroc_new, ckpt_new = find_checkpoint_auroc(base_path)

    if auroc_new is None:
        print("[ERROR] No checkpoint found!")
        print()
        print("Possible issues:")
        print("  1. Training hasn't finished yet")
        print("  2. Training failed (check logs)")
        print("  3. Checkpoint is in a different location")
        print()
        return

    print(f"      NEW checkpoint: {ckpt_new}")
    print(f"      NEW AUROC (avg): {auroc_new:.4f}")
    print()

    # OLD AUROC from previous run with token pooling
    auroc_old = 0.6681
    print(f"[2/3] OLD AUROC (token): {auroc_old:.4f}")
    print()

    # Compare
    print("="*80)
    print("[3/3] COMPARISON")
    print("="*80)
    print()

    diff = auroc_new - auroc_old
    diff_pct = (diff / auroc_old) * 100

    print(f"  OLD (token):  {auroc_old:.4f}")
    print(f"  NEW (avg):    {auroc_new:.4f}")
    print(f"  Difference:   {diff:+.4f} ({diff_pct:+.2f}%)")
    print()

    # Decision logic
    print("="*80)
    print("DECISION")
    print("="*80)
    print()

    if diff > 0.02:  # Clearly improved (>2% absolute)
        print("[RESULT] AUROC CLEARLY WENT UP")
        print()
        print(f"  avg pooling improves AUROC by {diff:.4f} ({diff_pct:+.2f}%)")
        print()
        print("NEXT STEPS:")
        print("  1. Change ALL remaining token configs to avg:")
        print("     - sharp_rsna_1pct.yml")
        print("     - sharp_rsna_100pct.yml")
        print("     - sharp_siim_1pct.yml (already done)")
        print("     - sharp_siim_10pct.yml (already done)")
        print()
        print("  2. Retrain all experiments with avg pooling")
        print()
        print("  3. For the paper:")
        print("     - Lead with AUROC as primary metric")
        print("     - Report F1 as secondary with calibration caveat")
        print()

    elif diff < -0.02:  # Got worse
        print("[RESULT] AUROC WENT DOWN")
        print()
        print(f"  avg pooling HURTS AUROC by {abs(diff):.4f} ({abs(diff_pct):.2f}%)")
        print()
        print("NEXT STEPS:")
        print("  1. REVERT sharp_siim_100pct.yml back to token")
        print("  2. Keep token pooling for all configs")
        print("  3. The low F1 is a calibration issue, not pooling")
        print()

    else:  # Flat (within ±2%)
        print("[RESULT] AUROC IS FLAT / NO CHANGE")
        print()
        print(f"  Difference is only {diff:.4f} ({diff_pct:+.2f}%) - not meaningful")
        print()
        print("NEXT STEPS:")
        print("  1. Pooling method doesn't matter for SHARP on SIIM")
        print()
        print("  2. For consistency, make all configs use avg:")
        print("     - Ensures 1%/10%/100% curves are comparable")
        print("     - Standard practice in papers")
        print()
        print("  3. For the paper:")
        print("     - Lead with AUROC (0.66-0.68 is reasonable for SIIM)")
        print("     - Note F1 is low due to calibration on imbalanced data")
        print("     - Don't chase F1 - it's a threshold artifact")
        print()

    print("="*80)
    print("OPTIONAL: Check F1 Score (for curiosity only)")
    print("="*80)
    print()
    print("If you want to see the NEW F1 score (don't chase it!):")
    print("  python calculate_siim_new_f1.py")
    print()
    print("But remember: AUROC is what matters for the paper.")
    print()

    # Save result for record
    print("="*80)
    print("SUMMARY FOR RECORD")
    print("="*80)
    print()
    print(f"Experiment: SIIM 100%")
    print(f"OLD (token):  AUROC = {auroc_old:.4f}")
    print(f"NEW (avg):    AUROC = {auroc_new:.4f}, Checkpoint = {ckpt_new}")
    print(f"Difference:   {diff:+.4f} ({diff_pct:+.2f}%)")
    print()

if __name__ == "__main__":
    main()
