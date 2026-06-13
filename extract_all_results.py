"""
Extract results from all completed training experiments
"""
import os
import json
import torch
from pathlib import Path

def extract_siim_results():
    """Extract SIIM results from all splits"""
    print("="*80)
    print("SIIM Results")
    print("="*80)

    base_dir = Path("C:/Users/aya.alaswad/remote/BenchX/experiments/classification/siim")

    results = {}

    for split_name in ["SHARP_1pct", "SHARP_10pct", "SHARP_100pct"]:
        split_dir = base_dir / split_name / split_name

        if not split_dir.exists():
            print(f"\n{split_name}: NOT FOUND")
            continue

        print(f"\n{split_name}:")

        # Find best checkpoint
        checkpoints = list(split_dir.glob("*.pth"))
        if checkpoints:
            # Sort by AUROC (filename format: 0.XXXX_epoch_seed.pth)
            checkpoints.sort(key=lambda x: float(x.stem.split('_')[0]), reverse=True)
            best_ckpt = checkpoints[0]

            auroc = float(best_ckpt.stem.split('_')[0])
            epoch = int(best_ckpt.stem.split('_')[1])

            print(f"  Best AUROC: {auroc:.4f} (epoch {epoch})")
            results[split_name] = {"auroc": auroc, "epoch": epoch}

            # Try to read metrics file
            metrics_file = split_dir / "val_42_metrics.txt"
            if metrics_file.exists():
                with open(metrics_file, 'r') as f:
                    lines = f.readlines()
                    # Find last epoch's metrics
                    for line in reversed(lines):
                        if '"multiclass_accuracy"' in line:
                            try:
                                data = json.loads(line)
                                acc = data['scores']['multiclass_accuracy']
                                print(f"  Accuracy: {acc:.2f}%")
                                results[split_name]['accuracy'] = acc
                                break
                            except:
                                pass
        else:
            print(f"  No checkpoints found")

    return results

def extract_rsna_lp_results():
    """Extract RSNA Linear Probe results"""
    print("\n" + "="*80)
    print("RSNA Linear Probe Results")
    print("="*80)

    lp_dir = Path("C:/Users/aya.alaswad/remote/BenchX/experiments/classification/rsna/SHARP_LP/SHARP_LP")

    if not lp_dir.exists():
        print("\nLinear Probe: NOT STARTED")
        return None

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

        return {"auroc": auroc, "epoch": epoch}
    else:
        print("\nNo checkpoints found")
        return None

def extract_raddino_results():
    """Extract RadDINO results"""
    print("\n" + "="*80)
    print("RadDINO Results")
    print("="*80)

    raddino_dir = Path("D:/experiments/exp_raddino_hardneg")

    if not raddino_dir.exists():
        print("\nRadDINO: NOT STARTED")
        return None

    best_ckpt = raddino_dir / "p3_best.pt"
    last_ckpt = raddino_dir / "p3_last.pt"

    results = {}

    if best_ckpt.exists():
        ckpt = torch.load(best_ckpt, map_location='cpu')
        print(f"\nBest checkpoint:")
        print(f"  Step: {ckpt['step']:,}")
        print(f"  Best R@1: {ckpt.get('best_r1', 'N/A')}")
        results['best'] = {
            'step': ckpt['step'],
            'r1': ckpt.get('best_r1', None)
        }

    if last_ckpt.exists():
        ckpt = torch.load(last_ckpt, map_location='cpu')
        print(f"\nLast checkpoint:")
        print(f"  Step: {ckpt['step']:,}")
        print(f"  Current R@1: {ckpt.get('r1', 'N/A')}")
        results['last'] = {
            'step': ckpt['step'],
            'r1': ckpt.get('r1', None)
        }

    # Check if training completed
    log_file = raddino_dir / "training.log"
    if log_file.exists():
        with open(log_file, 'r') as f:
            last_lines = f.readlines()[-10:]
            if any('Training complete' in line for line in last_lines):
                print("\n[COMPLETE] Training finished")
            else:
                print("\n[IN PROGRESS or STOPPED]")

    return results

def compare_results():
    """Compare key results"""
    print("\n" + "="*80)
    print("Comparison Summary")
    print("="*80)

    print("\nSIIM (10% data):")
    siim_10pct_dir = Path("C:/Users/aya.alaswad/remote/BenchX/experiments/classification/siim/SHARP_10pct/SHARP_10pct")
    checkpoints = list(siim_10pct_dir.glob("*.pth"))
    if checkpoints:
        checkpoints.sort(key=lambda x: float(x.stem.split('_')[0]), reverse=True)
        print(f"  AUROC: {float(checkpoints[0].stem.split('_')[0]):.4f}")

    print("\nRSNA (10% data):")
    print("  Fine-Tuning AUROC: 0.7514 (from previous run)")

    rsna_lp_dir = Path("C:/Users/aya.alaswad/remote/BenchX/experiments/classification/rsna/SHARP_LP/SHARP_LP")
    checkpoints = list(rsna_lp_dir.glob("*.pth"))
    if checkpoints:
        checkpoints.sort(key=lambda x: float(x.stem.split('_')[0]), reverse=True)
        ft_auroc = 0.7514
        lp_auroc = float(checkpoints[0].stem.split('_')[0])
        print(f"  Linear Probe AUROC: {lp_auroc:.4f}")
        print(f"  Difference: {(ft_auroc - lp_auroc):.4f} ({'fine-tuning helps' if ft_auroc > lp_auroc else 'linear probe equal/better'})")
    else:
        print("  Linear Probe: Not completed yet")

if __name__ == "__main__":
    try:
        siim_results = extract_siim_results()
        rsna_lp_results = extract_rsna_lp_results()
        raddino_results = extract_raddino_results()
        compare_results()

        print("\n" + "="*80)
        print("Done!")
        print("="*80)

    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
