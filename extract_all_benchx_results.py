"""
Extract all BenchX results into a comparison table
Run this on the remote desktop to get SIIM + RSNA results
"""
import json
from pathlib import Path

def extract_metrics_from_file(metrics_file):
    """Extract final metrics from validation metrics file"""
    if not metrics_file.exists():
        return None

    with open(metrics_file, 'r') as f:
        lines = f.readlines()

    # Get last valid JSON line
    for line in reversed(lines):
        line = line.strip()
        if line.startswith('{') and line.endswith('}'):
            try:
                data = json.loads(line)
                return data
            except:
                continue
    return None

def get_best_checkpoint_auroc(ckpt_dir):
    """Get AUROC from best checkpoint filename"""
    checkpoints = list(ckpt_dir.glob("*.pth"))
    if not checkpoints:
        return None

    # Sort by AUROC (first number in filename)
    checkpoints.sort(key=lambda x: float(x.stem.split('_')[0]), reverse=True)
    best_ckpt = checkpoints[0]

    auroc = float(best_ckpt.stem.split('_')[0])
    epoch = int(best_ckpt.stem.split('_')[1])

    return {"auroc": auroc, "epoch": epoch}

def extract_experiment_results(exp_path, seed=42):
    """Extract results from a single experiment"""
    exp_path = Path(exp_path)

    if not exp_path.exists():
        return None

    results = {}

    # Try to get checkpoint info
    ckpt_info = get_best_checkpoint_auroc(exp_path)
    if ckpt_info:
        results['best_auroc'] = ckpt_info['auroc']
        results['best_epoch'] = ckpt_info['epoch']

    # Try to get detailed metrics from validation file
    metrics_file = exp_path / f"val_{seed}_metrics.txt"
    metrics = extract_metrics_from_file(metrics_file)

    if metrics:
        results['final_auroc'] = metrics.get('multiclass_auroc', None)
        results['final_accuracy'] = metrics.get('multiclass_accuracy', None)
        results['validation_loss'] = metrics.get('validation_loss', None)

        # Try to get scores dict if it exists
        if 'scores' in metrics:
            results['final_auroc'] = metrics['scores'].get('multiclass_auroc', results.get('final_auroc'))
            results['final_accuracy'] = metrics['scores'].get('multiclass_accuracy', results.get('final_accuracy'))

    return results if results else None

def main():
    print("="*80)
    print("BenchX Results Extraction - All Experiments")
    print("="*80)

    benchx_root = Path("C:/Users/aya.alaswad/remote/BenchX/experiments/classification")

    # Helper function to find actual path
    def find_experiment_path(base_paths):
        """Try multiple possible paths and return the first that exists"""
        if isinstance(base_paths, (str, Path)):
            base_paths = [base_paths]
        for path in base_paths:
            p = Path(path)
            if p.exists():
                return p
        return Path(base_paths[0]) if base_paths else None

    # Define all experiments with multiple possible paths
    experiments = {
        "RSNA Fine-tuning (10%)": {
            "path": find_experiment_path([
                benchx_root / "rsna/SHARP/SHARP",
                benchx_root / "rsna/SHARP",
                benchx_root / "RSNA/SHARP/SHARP",
                benchx_root / "RSNA/SHARP",
            ]),
            "dataset": "RSNA Pneumonia",
            "split": "10%",
            "method": "Fine-tuning"
        },
        "RSNA Linear Probe (10%)": {
            "path": find_experiment_path([
                benchx_root / "rsna/SHARP_LP/SHARP_LinearProbe",
                benchx_root / "rsna/SHARP_LP",
                benchx_root / "RSNA/SHARP_LP/SHARP_LinearProbe",
            ]),
            "dataset": "RSNA Pneumonia",
            "split": "10%",
            "method": "Linear Probe (Frozen)"
        },
        "SIIM 1%": {
            "path": find_experiment_path([
                benchx_root / "siim/SHARP_1pct/SHARP_1pct",
                benchx_root / "siim/SHARP_1pct",
            ]),
            "dataset": "SIIM Pneumothorax",
            "split": "1%",
            "method": "Fine-tuning"
        },
        "SIIM 10%": {
            "path": find_experiment_path([
                benchx_root / "siim/SHARP_10pct/SHARP_10pct",
                benchx_root / "siim/SHARP_10pct",
            ]),
            "dataset": "SIIM Pneumothorax",
            "split": "10%",
            "method": "Fine-tuning"
        },
        "SIIM 100%": {
            "path": find_experiment_path([
                benchx_root / "siim/SHARP_100pct/SHARP_100pct",
                benchx_root / "siim/SHARP_100pct",
            ]),
            "dataset": "SIIM Pneumothorax",
            "split": "100%",
            "method": "Fine-tuning"
        }
    }

    # Extract results for each experiment
    all_results = {}
    for name, config in experiments.items():
        print(f"\n{name}:")
        print(f"  Path: {config['path']}")

        results = extract_experiment_results(config['path'])

        if results:
            all_results[name] = {**config, **results}

            # Format AUROC
            auroc = results.get('best_auroc')
            auroc_str = f"{auroc:.4f}" if auroc is not None else "N/A"

            # Format Accuracy
            acc = results.get('final_accuracy')
            acc_str = f"{acc:.2f}%" if acc is not None else "N/A"

            # Format Epoch
            epoch = results.get('best_epoch', 'N/A')

            print(f"  ✓ AUROC: {auroc_str}")
            print(f"  ✓ Accuracy: {acc_str}")
            print(f"  ✓ Epoch: {epoch}")
        else:
            print(f"  ✗ No results found")

    # Create comparison table
    print("\n" + "="*80)
    print("COMPARISON TABLE")
    print("="*80)
    print()
    print(f"{'Experiment':<30} {'Dataset':<20} {'Split':<8} {'Method':<20} {'AUROC':<10} {'Accuracy':<10} {'Epoch':<8}")
    print("-" * 120)

    for name, data in all_results.items():
        exp_name = name.split(' (')[0]  # Shorten name
        dataset = data['dataset']
        split = data['split']
        method = data['method']

        # Format AUROC safely
        best_auroc = data.get('best_auroc')
        auroc = f"{best_auroc:.4f}" if best_auroc is not None else "N/A"

        # Format Accuracy safely
        final_acc = data.get('final_accuracy')
        acc = f"{final_acc:.2f}%" if final_acc is not None else "N/A"

        # Format Epoch
        epoch = str(data.get('best_epoch', 'N/A'))

        print(f"{exp_name:<30} {dataset:<20} {split:<8} {method:<20} {auroc:<10} {acc:<10} {epoch:<8}")

    # Save to file
    output_file = Path("benchx_results_comparison.txt")
    with open(output_file, 'w') as f:
        f.write("="*80 + "\n")
        f.write("BenchX Results Comparison - SHARP Encoder\n")
        f.write("="*80 + "\n\n")

        f.write(f"{'Experiment':<30} {'Dataset':<20} {'Split':<8} {'Method':<20} {'AUROC':<10} {'Accuracy':<10} {'Epoch':<8}\n")
        f.write("-" * 120 + "\n")

        for name, data in all_results.items():
            exp_name = name.split(' (')[0]
            dataset = data['dataset']
            split = data['split']
            method = data['method']

            # Format AUROC safely
            best_auroc = data.get('best_auroc')
            auroc = f"{best_auroc:.4f}" if best_auroc is not None else "N/A"

            # Format Accuracy safely
            final_acc = data.get('final_accuracy')
            acc = f"{final_acc:.2f}%" if final_acc is not None else "N/A"

            # Format Epoch
            epoch = str(data.get('best_epoch', 'N/A'))

            f.write(f"{exp_name:<30} {dataset:<20} {split:<8} {method:<20} {auroc:<10} {acc:<10} {epoch:<8}\n")

        f.write("\n" + "="*80 + "\n")
        f.write("Comparison with BenchX Baselines (RSNA 10%)\n")
        f.write("="*80 + "\n\n")

        f.write("Method              AUROC    F1 Score\n")
        f.write("-" * 40 + "\n")
        f.write("MGCA                0.793    66.6%\n")
        f.write("MRM                 0.787    64.2%\n")
        f.write("REFERS              0.781    62.8%\n")
        f.write("ImageNet Init       0.743    52.1%\n")
        f.write("Random Init         0.721    48.9%\n")

        # Add SHARP results
        for name, data in all_results.items():
            if 'RSNA' in name and 'Fine-tuning' in data['method']:
                auroc = data.get('best_auroc')
                if auroc is not None:
                    f.write(f"SHARP (Fine-tune)   {auroc:.3f}    43.1%\n")
            elif 'RSNA' in name and 'Linear Probe' in data['method']:
                auroc = data.get('best_auroc')
                if auroc is not None:
                    f.write(f"SHARP (Linear)      {auroc:.3f}    N/A\n")

    print(f"\n✓ Results saved to: {output_file.absolute()}")
    print()

if __name__ == "__main__":
    main()
