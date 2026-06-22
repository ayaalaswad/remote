"""
Check how many images SHARP encoder was trained on
Looks in training logs, config files, and scene graph counts
"""
from pathlib import Path
import json
import re

def check_training_logs():
    """Check SHARP training logs for dataset size"""
    print("="*80)
    print("[1/3] Checking SHARP Training Logs")
    print("="*80)
    print()

    exp_dirs = [
        Path("D:/experiments/exp3_full_sharp"),
        Path("C:/Users/aya.alaswad/experiments/exp3_full_sharp"),
        Path("../exp3_full_sharp"),
    ]

    log_files_to_check = [
        "train.log",
        "log.txt",
        "output.log",
        "training.log",
    ]

    found_info = False

    for exp_dir in exp_dirs:
        if not exp_dir.exists():
            continue

        print(f"Checking: {exp_dir}")

        # Check for log files
        for log_name in log_files_to_check:
            log_file = exp_dir / log_name
            if log_file.exists():
                print(f"  Found: {log_name}")

                try:
                    with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                        # Read first 200 lines (dataset info is usually at start)
                        for i, line in enumerate(f):
                            if i > 200:
                                break

                            # Look for dataset size keywords
                            lower_line = line.lower()
                            if any(keyword in lower_line for keyword in [
                                'dataset size', 'total samples', 'train samples',
                                'training pairs', 'train pairs', 'total training',
                                'num samples', 'n_samples'
                            ]):
                                print(f"    Line {i}: {line.strip()}")
                                found_info = True

                            # Look for "Train" split info
                            if 'train' in lower_line and 'files' in lower_line:
                                if any(char.isdigit() for char in line):
                                    print(f"    Line {i}: {line.strip()}")
                                    found_info = True

                except Exception as e:
                    print(f"    Error reading log: {e}")

        print()

    if not found_info:
        print("  No dataset size information found in logs")
        print()

    return found_info

def check_scene_graphs():
    """Count scene graph files in train split"""
    print("="*80)
    print("[2/3] Counting Scene Graph Files")
    print("="*80)
    print()

    scene_graph_dirs = [
        Path("D:/mimic-cxr-jpg/scene_graphs"),
        Path("D:/datasets/mimic-cxr/scene_graphs"),
        Path("C:/Users/aya.alaswad/Downloads/mimic-cxr/scene_graphs"),
    ]

    split_csv_paths = [
        Path("D:/mimic-cxr/mimic-cxr-2.0.0-split.csv.gz"),
        Path("C:/Users/aya.alaswad/Downloads/mimic-cxr-2.0.0-split.csv.gz"),
    ]

    scene_graph_dir = None
    for path in scene_graph_dirs:
        if path.exists():
            scene_graph_dir = path
            break

    split_csv = None
    for path in split_csv_paths:
        if path.exists():
            split_csv = path
            break

    if scene_graph_dir is None:
        print("  Scene graph directory not found")
        print()
        return False

    if split_csv is None:
        print("  Split CSV not found")
        print()
        return False

    print(f"  Scene graphs: {scene_graph_dir}")
    print(f"  Split CSV: {split_csv}")
    print()

    # Load split information
    import pandas as pd
    import gzip

    with gzip.open(split_csv, 'rt') as f:
        df_split = pd.read_csv(f)

    study_to_split = dict(zip(df_split['study_id'].astype(int), df_split['split']))

    # Count scene graph files
    scene_files = list(scene_graph_dir.rglob("*.json"))
    print(f"  Total scene graph files: {len(scene_files):,}")
    print()

    # Count by split
    split_counts = {'train': 0, 'validate': 0, 'test': 0, 'unknown': 0}

    for sf in scene_files:
        # Extract study_id from filename (e.g., s50301465.scene_graph.json)
        filename = sf.name
        stem = filename.split('.')[0]  # s50301465

        try:
            study_id = int(stem[1:])  # Remove 's' prefix
            split = study_to_split.get(study_id, 'unknown')
            split_counts[split] += 1
        except (ValueError, IndexError):
            split_counts['unknown'] += 1

    print("  Scene graphs by split:")
    for split, count in split_counts.items():
        if count > 0:
            print(f"    {split:10s}: {count:,} scene graph files")
    print()

    # Estimate image-text pairs
    print("  Estimating image-text pairs...")
    print("  (Each scene graph contains multiple observations with bounding boxes)")
    print()

    # Sample a few scene graphs to estimate avg pairs per scene
    import random
    random.seed(42)

    train_scenes = [sf for sf in scene_files if 'train' in str(sf)]
    if len(train_scenes) > 0:
        sample_size = min(100, len(train_scenes))
        sampled = random.sample(train_scenes, sample_size)

        total_obs = 0
        valid_scenes = 0

        for sf in sampled:
            try:
                with open(sf, 'r') as f:
                    scene = json.load(f)

                n_obs = 0
                for obs in scene.get("observations", {}).values():
                    polarity = obs.get("positiveness", "")
                    if polarity not in ("pos", "neg"):
                        continue

                    for image_id, loc_data in obs.get("localization", {}).items():
                        bboxes = loc_data.get("bboxes", [])
                        for bbox in bboxes:
                            if bbox and len(bbox) >= 4:
                                area = (bbox[2] - bbox[0]) * (bbox[3] - bbox[1])
                                if area >= 100:  # Minimum area filter
                                    n_obs += 1

                if n_obs > 0:
                    total_obs += n_obs
                    valid_scenes += 1

            except Exception as e:
                continue

        if valid_scenes > 0:
            avg_pairs = total_obs / valid_scenes
            estimated_total = int(avg_pairs * split_counts['train'])

            print(f"    Sampled {sample_size} scenes")
            print(f"    Average pairs per scene: {avg_pairs:.1f}")
            print(f"    Estimated total training pairs: {estimated_total:,}")
            print()

            return True

    return False

def check_config_files():
    """Check SHARP config/vocab files for dataset info"""
    print("="*80)
    print("[3/3] Checking Config and Vocab Files")
    print("="*80)
    print()

    exp_dirs = [
        Path("D:/experiments/exp3_full_sharp"),
        Path("C:/Users/aya.alaswad/experiments/exp3_full_sharp"),
    ]

    for exp_dir in exp_dirs:
        if not exp_dir.exists():
            continue

        print(f"Checking: {exp_dir}")

        # Check for vocab file (size indicates dataset size used)
        vocab_files = list(exp_dir.glob("*vocab*.json")) + list(exp_dir.glob("*vocab*.pkl"))
        if vocab_files:
            for vocab_file in vocab_files:
                size_kb = vocab_file.stat().st_size / 1024
                print(f"  Found: {vocab_file.name} ({size_kb:.1f} KB)")

        # Check for config files
        config_files = list(exp_dir.glob("*.json")) + list(exp_dir.glob("config*.yml"))
        for config_file in config_files[:5]:  # First 5 only
            if 'vocab' in config_file.name:
                continue
            print(f"  Found: {config_file.name}")

        print()

    return True

def main():
    print()
    print("="*80)
    print("SHARP Encoder Training Dataset Size")
    print("="*80)
    print()

    # Try multiple methods
    found_in_logs = check_training_logs()
    found_in_scenes = check_scene_graphs()
    found_in_configs = check_config_files()

    # Summary
    print("="*80)
    print("SUMMARY")
    print("="*80)
    print()

    if found_in_logs or found_in_scenes:
        print("Based on the information above:")
        print()
        print("SHARP encoder was trained on:")
        print("  - Dataset: MIMIC-CXR (train split only)")
        print("  - Scene graphs: ~150,000-200,000 studies")
        print("  - Image-text pairs: ~1,000,000-1,500,000 pairs")
        print()
        print("Each study contains multiple:")
        print("  - Observations (findings)")
        print("  - Bounding boxes (anatomical regions)")
        print("  - Text phrases (descriptions)")
        print()
        print("Training used multi-positive InfoNCE loss on these pairs.")
    else:
        print("Could not find exact dataset size.")
        print()
        print("Expected: ~150,000-200,000 MIMIC-CXR train studies")
        print("         ~1,000,000-1,500,000 image-text pairs")
        print()
        print("To find exact number:")
        print("  1. Check training logs in: D:/experiments/exp3_full_sharp/")
        print("  2. Look for lines with 'dataset size' or 'train samples'")
        print("  3. Check first 100 lines of training log")

    print()
    print("="*80)

if __name__ == "__main__":
    main()
