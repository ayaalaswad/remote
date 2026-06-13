"""
Quick check of RSNA Linear Probe results
"""
import json
from pathlib import Path

lp_dir = Path("C:/Users/aya.alaswad/remote/BenchX/experiments/classification/rsna/SHARP_LP/SHARP_LP")

print("="*80)
print("RSNA Linear Probe Status")
print("="*80)

if not lp_dir.exists():
    print("\n[NOT STARTED] Linear Probe directory doesn't exist")
    exit(1)

# Check log file
log_file = lp_dir / "42.log"
if log_file.exists():
    with open(log_file, 'r') as f:
        lines = f.readlines()

    # Check completion
    if any("Early stopping" in line for line in lines):
        print("\n[COMPLETE] Training finished with early stopping")
    elif any("Epoch 30" in line for line in lines):
        print("\n[COMPLETE] Training finished (max epochs)")
    else:
        # Find last epoch
        for line in reversed(lines):
            if "Epoch" in line and "/" in line:
                print(f"\n[IN PROGRESS] {line.strip()}")
                break
else:
    print("\n[NOT STARTED] No log file found")

# Find best checkpoint
checkpoints = list(lp_dir.glob("*.pth"))
if checkpoints:
    checkpoints.sort(key=lambda x: float(x.stem.split('_')[0]), reverse=True)
    best_ckpt = checkpoints[0]

    auroc = float(best_ckpt.stem.split('_')[0])
    epoch = int(best_ckpt.stem.split('_')[1])

    print(f"\nBest AUROC: {auroc:.4f} (epoch {epoch})")

    # Try to read metrics
    metrics_file = lp_dir / "val_42_metrics.txt"
    if metrics_file.exists():
        with open(metrics_file, 'r') as f:
            lines = f.readlines()
            for line in reversed(lines):
                if '"multiclass_accuracy"' in line:
                    try:
                        data = json.loads(line)
                        acc = data['scores']['multiclass_accuracy']
                        print(f"Accuracy: {acc:.2f}%")
                        break
                    except:
                        pass

    # Comparison with fine-tuning
    print("\n" + "="*80)
    print("Comparison")
    print("="*80)
    print(f"Fine-Tuning AUROC: 0.7514 (from previous run)")
    print(f"Linear Probe AUROC: {auroc:.4f}")
    diff = 0.7514 - auroc
    print(f"Difference: {diff:.4f} ({'fine-tuning helps' if diff > 0 else 'linear probe better!'})")

else:
    print("\nNo checkpoints found yet")

print("\n" + "="*80)
