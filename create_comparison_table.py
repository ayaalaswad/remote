"""
Create comparison table from known results
"""

def main():
    print("="*120)
    print("SHARP BenchX Results - Complete Comparison Table")
    print("="*120)
    print()

    # All results
    results = {
        "RSNA Fine-tuning (10%)": {
            "dataset": "RSNA Pneumonia",
            "split": "10%",
            "method": "Fine-tuning",
            "auroc": 0.7514,
            "accuracy": 77.0,
            "f1": 43.1,
            "status": "Complete"
        },
        "RSNA Linear Probe (10%)": {
            "dataset": "RSNA Pneumonia",
            "split": "10%",
            "method": "Frozen encoder",
            "auroc": 0.7333,
            "accuracy": 76.87,
            "f1": None,
            "status": "Complete"
        },
        "SIIM 1%": {
            "dataset": "SIIM Pneumothorax",
            "split": "1%",
            "method": "Fine-tuning",
            "auroc": 0.6037,
            "accuracy": None,
            "f1": None,
            "status": "Complete"
        },
        "SIIM 10%": {
            "dataset": "SIIM Pneumothorax",
            "split": "10%",
            "method": "Fine-tuning",
            "auroc": 0.6244,
            "accuracy": None,
            "f1": None,
            "status": "Complete"
        },
        "SIIM 100%": {
            "dataset": "SIIM Pneumothorax",
            "split": "100%",
            "method": "Fine-tuning",
            "auroc": 0.6675,
            "accuracy": None,
            "f1": None,
            "status": "Complete"
        }
    }

    # Print table
    print(f"{'Experiment':<30} {'Dataset':<20} {'Split':<8} {'Method':<18} {'AUROC':<10} {'Accuracy':<10} {'F1':<10}")
    print("-" * 120)

    for name, data in results.items():
        exp_name = name
        dataset = data['dataset']
        split = data['split']
        method = data['method']
        auroc = f"{data['auroc']:.4f}" if data['auroc'] else "N/A"
        acc = f"{data['accuracy']:.2f}%" if data['accuracy'] else "N/A"
        f1 = f"{data['f1']:.1f}%" if data['f1'] else "N/A"

        print(f"{exp_name:<30} {dataset:<20} {split:<8} {method:<18} {auroc:<10} {acc:<10} {f1:<10}")

    print()
    print("="*120)
    print("Comparison with BenchX Baselines (RSNA Pneumonia 10%)")
    print("="*120)
    print()

    baselines = [
        ("MGCA (Best)", 0.793, 66.6),
        ("MRM", 0.787, 64.2),
        ("REFERS", 0.781, 62.8),
        ("SHARP Fine-tuning", 0.7514, 43.1),
        ("ImageNet Init", 0.743, 52.1),
        ("SHARP Linear Probe", 0.7333, None),
        ("Random Init", 0.721, 48.9),
    ]

    print(f"{'Method':<25} {'AUROC':<12} {'F1 Score':<12} {'Gap from Best':<15}")
    print("-" * 70)

    best_auroc = baselines[0][1]
    for method, auroc, f1 in baselines:
        gap = auroc - best_auroc
        gap_str = f"{gap:+.4f}" if gap != 0 else "-"
        f1_str = f"{f1:.1f}%" if f1 else "N/A"
        print(f"{method:<25} {auroc:<12.4f} {f1_str:<12} {gap_str:<15}")

    print()
    print("="*120)
    print("Key Findings")
    print("="*120)
    print()
    print("✅ SHARP Performance:")
    print("   - Beats random init (+3.0% AUROC) and ImageNet (+0.8% AUROC)")
    print("   - Linear probe only 2.4% worse than fine-tuning → good feature learning")
    print()
    print("⚠️  Areas for Improvement:")
    print("   - Underperforms MGCA by 5.3% AUROC")
    print("   - F1 score significantly lower (43.1% vs 66.6%)")
    print("   - Conservative predictions (high specificity, low sensitivity)")
    print()
    print("📊 SIIM Pneumothorax Results:")
    print("   - 1% data:   AUROC 0.6037")
    print("   - 10% data:  AUROC 0.6244")
    print("   - 100% data: AUROC 0.6675")
    print("   - Clear improvement with more data (+10.5% from 1% to 100%)")
    print()
    print("🔬 RadDINO Hard Negatives:")
    print("   - Training completed: 87,000 steps")
    print("   - Checkpoint available for evaluation")
    print()

    # Save to file
    with open("FINAL_RESULTS_TABLE.txt", "w") as f:
        f.write("="*120 + "\n")
        f.write("SHARP BenchX Results - Complete Comparison Table\n")
        f.write("="*120 + "\n\n")

        f.write(f"{'Experiment':<30} {'Dataset':<20} {'Split':<8} {'Method':<18} {'AUROC':<10} {'Accuracy':<10} {'F1':<10}\n")
        f.write("-" * 120 + "\n")

        for name, data in results.items():
            exp_name = name
            dataset = data['dataset']
            split = data['split']
            method = data['method']
            auroc = f"{data['auroc']:.4f}" if data['auroc'] else "N/A"
            acc = f"{data['accuracy']:.2f}%" if data['accuracy'] else "N/A"
            f1 = f"{data['f1']:.1f}%" if data['f1'] else "N/A"

            f.write(f"{exp_name:<30} {dataset:<20} {split:<8} {method:<18} {auroc:<10} {acc:<10} {f1:<10}\n")

        f.write("\n" + "="*120 + "\n")
        f.write("Comparison with BenchX Baselines (RSNA Pneumonia 10%)\n")
        f.write("="*120 + "\n\n")

        f.write(f"{'Method':<25} {'AUROC':<12} {'F1 Score':<12} {'Gap from Best':<15}\n")
        f.write("-" * 70 + "\n")

        for method, auroc, f1 in baselines:
            gap = auroc - best_auroc
            gap_str = f"{gap:+.4f}" if gap != 0 else "-"
            f1_str = f"{f1:.1f}%" if f1 else "N/A"
            f.write(f"{method:<25} {auroc:<12.4f} {f1_str:<12} {gap_str:<15}\n")

        f.write("\n" + "="*120 + "\n")
        f.write("SIIM Pneumothorax - Data Scaling Analysis\n")
        f.write("="*120 + "\n\n")
        f.write("Split    AUROC    Improvement\n")
        f.write("-" * 40 + "\n")
        f.write("1%       0.6037   -\n")
        f.write("10%      0.6244   +0.0207 (+3.4%)\n")
        f.write("100%     0.6675   +0.0431 (+6.9% from 10%)\n")
        f.write("\n")
        f.write("Total improvement from 1% to 100%: +0.0638 (+10.6%)\n")

    print(f"✓ Results saved to: FINAL_RESULTS_TABLE.txt")
    print()

if __name__ == "__main__":
    main()
