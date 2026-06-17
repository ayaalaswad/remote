"""
Check SIIM training status by examining logs and checkpoints
"""
import os
from pathlib import Path

def check_experiment_status(exp_name, exp_dir):
    """Check if an experiment finished training"""
    print(f"\n{'='*80}")
    print(f"{exp_name}")
    print(f"{'='*80}")

    if not exp_dir.exists():
        print(f"[NOT FOUND] Directory does not exist: {exp_dir}")
        return False

    print(f"Directory: {exp_dir}")

    # Check for log file
    log_file = exp_dir / "log.txt"
    if not log_file.exists():
        print(f"[NOT FOUND] No log.txt file found")
        return False

    print(f"[FOUND] log.txt exists")

    # Read last 50 lines of log
    with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()

    if len(lines) == 0:
        print(f"[ERROR] Log file is empty")
        return False

    print(f"[INFO] Log has {len(lines)} lines")

    # Check last lines for completion indicators
    last_lines = lines[-50:] if len(lines) > 50 else lines
    last_text = ''.join(last_lines).lower()

    # Look for signs of completion
    finished = False
    if 'training complete' in last_text or 'finished training' in last_text:
        print("[SUCCESS] Training completed!")
        finished = True
    elif 'best model' in last_text or 'saving best' in last_text:
        print("[LIKELY] Training likely completed (found 'best model' in logs)")
        finished = True
    elif 'epoch' in last_text:
        # Find the last epoch mentioned
        for line in reversed(last_lines):
            if 'epoch' in line.lower():
                print(f"[INFO] Last log entry: {line.strip()}")
                break

    # Check for checkpoints
    ckpt_files = list(exp_dir.glob("*.pt")) + list(exp_dir.glob("*.pth"))
    if ckpt_files:
        print(f"[FOUND] {len(ckpt_files)} checkpoint file(s):")
        for ckpt in ckpt_files:
            size_mb = ckpt.stat().st_size / (1024*1024)
            print(f"  - {ckpt.name} ({size_mb:.1f} MB)")
    else:
        print(f"[NOT FOUND] No checkpoint files (.pt or .pth)")

    # Check for metrics
    metrics_file = exp_dir / "metrics.json"
    if metrics_file.exists():
        print(f"[FOUND] metrics.json exists")
        finished = True

    # Check for val_42 prediction files
    val_files = list(exp_dir.glob("val_42_*.txt"))
    if val_files:
        print(f"[FOUND] {len(val_files)} validation prediction files")
        for vf in val_files:
            print(f"  - {vf.name}")
        finished = True

    print()
    if finished:
        print("[RESULT] Training appears to be COMPLETE")
    else:
        print("[RESULT] Training appears to be INCOMPLETE or FAILED")

    return finished

def main():
    print("="*80)
    print("SIIM Training Status Checker")
    print("="*80)

    # Base path
    base_path = Path("C:/Users/aya.alaswad/remote/BenchX/experiments/classification/siim")

    experiments = {
        "SIIM 1%": base_path / "SHARP_1pct" / "SHARP_1pct",
        "SIIM 10%": base_path / "SHARP_10pct" / "SHARP_10pct",
        "SIIM 100%": base_path / "SHARP_100pct" / "SHARP_100pct",
    }

    results = {}
    for name, path in experiments.items():
        results[name] = check_experiment_status(name, path)

    # Summary
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    for name, finished in results.items():
        status = "COMPLETE" if finished else "INCOMPLETE"
        print(f"{name:15s}: {status}")

    all_done = all(results.values())
    print()
    if all_done:
        print("[ALL DONE] All SIIM experiments completed!")
        print()
        print("Next steps:")
        print("  1. Run: python calculate_f1_from_pushed_results.py")
        print("  2. Run: push_siim_results.bat")
    else:
        print("[NOT DONE] Some experiments are incomplete")
        print()
        print("To resume training:")
        print("  fix_and_retrain_siim.bat")

if __name__ == "__main__":
    main()
