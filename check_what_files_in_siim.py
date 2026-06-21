"""
Check what files are actually in the SIIM result directories
"""
from pathlib import Path

def list_files(directory):
    """List all files in directory and subdirectories"""
    if not directory.exists():
        print(f"  Directory does not exist: {directory}")
        return

    print(f"\nDirectory: {directory}")
    print("-" * 80)

    # List immediate files
    files = list(directory.glob("*"))
    if not files:
        print("  (empty)")
        return

    for item in sorted(files):
        if item.is_file():
            size_kb = item.stat().st_size / 1024
            print(f"  FILE: {item.name} ({size_kb:.1f} KB)")
        elif item.is_dir():
            print(f"  DIR:  {item.name}/")
            # List files in subdirectory
            subfiles = list(item.glob("*"))
            for subfile in sorted(subfiles):
                if subfile.is_file():
                    size_kb = subfile.stat().st_size / 1024
                    print(f"        {subfile.name} ({size_kb:.1f} KB)")

def main():
    print("="*80)
    print("SIIM Result Files Checker")
    print("="*80)

    base = Path("C:/Users/aya.alaswad/remote/BenchX/experiments/classification/siim")

    for exp in ["SHARP_1pct", "SHARP_10pct", "SHARP_100pct"]:
        exp_dir = base / exp
        list_files(exp_dir)

    print("\n" + "="*80)

if __name__ == "__main__":
    main()
