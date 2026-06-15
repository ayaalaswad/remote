"""
Extract AUROC from all pushed results
"""
from pathlib import Path
import json

def extract_auroc_from_metrics(metrics_file):
    """Extract final AUROC from metrics file"""
    with open(metrics_file, 'r') as f:
        lines = f.readlines()

    for line in reversed(lines):
        line = line.strip()
        if '"multiclass_auroc"' in line:
            try:
                # Extract just the number
                auroc_str = line.split(':')[1].strip().rstrip(',')
                return float(auroc_str)
            except:
                continue
    return None

def main():
    print("="*80)
    print("AUROC Extraction - All SHARP BenchX Experiments")
    print("="*80)
    print()

    base_dir = Path(".")

    experiments = {
        "RSNA 1%": "rsna_results_latest/SHARP_1pct/SHARP_1pct/val_42_metrics.txt",
        "RSNA 10%": "rsna_results_latest/SHARP_10pct/SHARP_10pct/val_42_metrics.txt",
        "RSNA 100%": "rsna_results_latest/SHARP_100pct/SHARP_100pct/val_42_metrics.txt",
        "RSNA Linear Probe (10%)": "rsna_lp_results/val_42_metrics.txt",
        "SIIM 1%": "siim_results_latest/SHARP_1pct/SHARP_1pct/val_42_metrics.txt",
        "SIIM 10%": "siim_results_latest/SHARP_10pct/SHARP_10pct/val_42_metrics.txt",
        "SIIM 100%": "siim_results_latest/SHARP_100pct/SHARP_100pct/val_42_metrics.txt",
    }

    all_results = {}

    for name, metrics_path in experiments.items():
        metrics_file = base_dir / metrics_path

        if not metrics_file.exists():
            print(f"{name:<30} - NOT FOUND")
            continue

        try:
            auroc = extract_auroc_from_metrics(metrics_file)
            if auroc:
                all_results[name] = auroc
                print(f"{name:<30} AUROC: {auroc:.4f}")
            else:
                print(f"{name:<30} - Could not extract AUROC")
        except Exception as e:
            print(f"{name:<30} - Error: {e}")

    # Summary tables
    if all_results:
        print("\n" + "="*80)
        print("RSNA Pneumonia - Data Scaling")
        print("="*80)
        print()

        rsna_splits = ["RSNA 1%", "RSNA 10%", "RSNA 100%"]
        print(f"{'Split':<15} {'AUROC':<10} {'Improvement':<20}")
        print("-" * 50)

        prev_auroc = None
        for split in rsna_splits:
            if split in all_results:
                auroc = all_results[split]
                if prev_auroc:
                    improvement = auroc - prev_auroc
                    pct_improvement = (improvement / prev_auroc) * 100
                    print(f"{split:<15} {auroc:.4f}     +{improvement:.4f} (+{pct_improvement:.1f}%)")
                else:
                    print(f"{split:<15} {auroc:.4f}     -")
                prev_auroc = auroc

        # Comparison with baselines
        if "RSNA 100%" in all_results:
            print("\n" + "="*80)
            print("RSNA 100% vs BenchX Baselines")
            print("="*80)
            print()

            sharp_100 = all_results["RSNA 100%"]
            baselines = {
                "MGCA (Best)": 0.793,
                "MRM": 0.787,
                "REFERS": 0.781,
                "SHARP 100%": sharp_100,
                "SHARP 10%": all_results.get("RSNA 10%", 0),
                "ImageNet": 0.743,
                "Random": 0.721
            }

            print(f"{'Method':<25} {'AUROC':<12} {'vs MGCA':<15}")
            print("-" * 55)

            mgca_auroc = 0.793
            for method, auroc in baselines.items():
                if auroc > 0:
                    gap = auroc - mgca_auroc
                    gap_str = f"{gap:+.4f}" if gap != 0 else "-"
                    marker = " <-- SHARP!" if "SHARP" in method else ""
                    print(f"{method:<25} {auroc:.4f}        {gap_str:<15}{marker}")

        print("\n" + "="*80)
        print("SIIM Pneumothorax - Data Scaling")
        print("="*80)
        print()

        siim_splits = ["SIIM 1%", "SIIM 10%", "SIIM 100%"]
        print(f"{'Split':<15} {'AUROC':<10} {'Improvement':<20}")
        print("-" * 50)

        prev_auroc = None
        for split in siim_splits:
            if split in all_results:
                auroc = all_results[split]
                if prev_auroc:
                    improvement = auroc - prev_auroc
                    pct_improvement = (improvement / prev_auroc) * 100
                    print(f"{split:<15} {auroc:.4f}     +{improvement:.4f} (+{pct_improvement:.1f}%)")
                else:
                    print(f"{split:<15} {auroc:.4f}     -")
                prev_auroc = auroc

        # Linear probe comparison
        if "RSNA Linear Probe (10%)" in all_results and "RSNA 10%" in all_results:
            print("\n" + "="*80)
            print("Fine-tuning vs Linear Probe (RSNA 10%)")
            print("="*80)
            print()

            ft = all_results["RSNA 10%"]
            lp = all_results["RSNA Linear Probe (10%)"]
            gap = ft - lp

            print(f"Fine-tuning:  {ft:.4f}")
            print(f"Linear Probe: {lp:.4f}")
            print(f"Gap:          {gap:.4f} ({gap/ft*100:.1f}%)")

    print()

if __name__ == "__main__":
    main()
