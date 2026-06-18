"""
Count exact number of images/pairs used in SHARP training
by analyzing scene graph files
"""
import json
import gzip
from pathlib import Path
from collections import defaultdict

def count_scene_graphs():
    """Count scene graph JSON files"""

    print("="*80)
    print("SHARP Training Data Counter")
    print("="*80)
    print()

    # Common scene graph locations
    scene_graph_paths = [
        Path("D:/mimic-cxr-jpg/scene_graphs"),
        Path("D:/datasets/mimic-cxr/scene_graphs"),
        Path("C:/Users/aya.alaswad/Downloads/mimic-cxr/scene_graphs"),
        Path("C:/Users/aya.alaswad/Downloads/scene_graphs"),
        Path("D:/scene_graphs"),
    ]

    scene_graph_dir = None
    for path in scene_graph_paths:
        if path.exists():
            scene_graph_dir = path
            break

    if scene_graph_dir is None:
        print("[NOT FOUND] Scene graph directory not found")
        print("Tried:")
        for p in scene_graph_paths:
            print(f"  - {p}")
        print()
        print("Scene graphs are typically in: mimic-cxr-jpg/scene_graphs/")
        return None

    print(f"[1/3] Found scene graphs: {scene_graph_dir}")
    print()

    # Count scene graph files
    scene_files = list(scene_graph_dir.rglob("*.json"))
    print(f"[2/3] Counting scene graph files...")
    print(f"      Total scene graph files: {len(scene_files):,}")
    print()

    return scene_graph_dir, scene_files

def load_split_info():
    """Load MIMIC-CXR split information"""

    print(f"[3/3] Loading MIMIC-CXR split information...")

    split_paths = [
        Path("C:/Users/aya.alaswad/Downloads/physionet.org/files/mimic-cxr/2.0.0/mimic-cxr-2.0.0-split.csv.gz"),
        Path("C:/Users/aya.alaswad/Downloads/mimic-cxr-2.0.0-split.csv.gz"),
        Path("D:/mimic-cxr/mimic-cxr-2.0.0-split.csv.gz"),
        Path("D:/datasets/mimic-cxr/mimic-cxr-2.0.0-split.csv.gz"),
    ]

    split_file = None
    for path in split_paths:
        if path.exists():
            split_file = path
            break

    if split_file is None:
        print("      Split file not found")
        return None, None

    print(f"      Found: {split_file}")

    import pandas as pd
    with gzip.open(split_file, 'rt') as f:
        df = pd.read_csv(f)

    study_to_split = dict(zip(df['study_id'].astype(int), df['split']))
    study_to_subject = dict(zip(df['study_id'].astype(int), df['subject_id'].astype(int)))

    print(f"      Loaded {len(study_to_split):,} studies")
    print()

    return study_to_split, study_to_subject

def count_by_split(scene_files, study_to_split):
    """Count scene graphs by split"""

    print("="*80)
    print("Scene Graphs by Split")
    print("="*80)
    print()

    by_split = defaultdict(int)
    skipped = 0

    for sf in scene_files:
        # Extract study_id from filename (e.g., s50301465.scene_graph.json -> 50301465)
        filename = sf.name
        stem = filename.split('.')[0]  # s50301465

        try:
            study_id = int(stem[1:])  # Remove 's' prefix
        except (ValueError, IndexError):
            skipped += 1
            continue

        split = study_to_split.get(study_id)
        if split:
            by_split[split] += 1
        else:
            skipped += 1

    total = sum(by_split.values())

    for split in ['train', 'validate', 'test']:
        count = by_split[split]
        pct = (count / total * 100) if total > 0 else 0
        print(f"{split:10s}: {count:8,} scene graphs ({pct:5.1f}%)")

    print(f"{'TOTAL':10s}: {total:8,} scene graphs")
    print(f"{'Skipped':10s}: {skipped:8,} (study_id not in split file)")
    print()

    return by_split

def count_pairs_in_scenes(scene_files, study_to_split, max_sample=1000):
    """Sample scene graphs to estimate total image-text pairs"""

    print("="*80)
    print("Estimating Image-Text Pairs")
    print("="*80)
    print()

    import random
    random.seed(42)

    # Sample scene graphs from train split
    train_scenes = []
    for sf in scene_files:
        filename = sf.name
        stem = filename.split('.')[0]
        try:
            study_id = int(stem[1:])
        except (ValueError, IndexError):
            continue

        split = study_to_split.get(study_id)
        if split == 'train':
            train_scenes.append(sf)

    if len(train_scenes) == 0:
        print("No train scene graphs found")
        return

    # Sample up to max_sample files
    sample_size = min(max_sample, len(train_scenes))
    sampled = random.sample(train_scenes, sample_size)

    print(f"Sampling {sample_size:,} scene graphs from train split...")
    print()

    total_pairs = 0
    valid_scenes = 0

    for sf in sampled:
        try:
            with open(sf, 'r') as f:
                scene = json.load(f)

            # Count observations (similar to extract_pairs logic)
            n_obs = 0
            for obs in scene.get("observations", {}).values():
                polarity = obs.get("positiveness", "")
                if polarity not in ("pos", "neg"):
                    continue

                # Count localizations with valid bboxes
                for image_id, loc_data in obs.get("localization", {}).items():
                    bboxes = loc_data.get("bboxes", [])
                    for bbox in bboxes:
                        if bbox and len(bbox) >= 4:
                            # Check minimum area (100 pixels, as in SHARP code)
                            area = (bbox[2] - bbox[0]) * (bbox[3] - bbox[1])
                            if area >= 100:
                                n_obs += 1

            if n_obs > 0:
                total_pairs += n_obs
                valid_scenes += 1

        except Exception as e:
            continue

    if valid_scenes == 0:
        print("No valid scenes found in sample")
        return

    avg_pairs = total_pairs / valid_scenes
    total_train_scenes = len(train_scenes)
    estimated_total = int(avg_pairs * total_train_scenes)

    print(f"Sample statistics:")
    print(f"  Valid scenes:     {valid_scenes:,} / {sample_size:,}")
    print(f"  Total pairs:      {total_pairs:,}")
    print(f"  Avg pairs/scene:  {avg_pairs:.1f}")
    print()
    print(f"Extrapolation to full train set:")
    print(f"  Train scenes:     {total_train_scenes:,}")
    print(f"  Estimated pairs:  {estimated_total:,}")
    print()
    print("="*80)
    print(f"SHARP TRAINING DATA SIZE: ~{estimated_total:,} image-text pairs")
    print("="*80)
    print()

    return estimated_total

def check_training_logs():
    """Check actual training logs for exact dataset size"""

    print()
    print("="*80)
    print("Checking Training Logs for Exact Count")
    print("="*80)
    print()

    exp_dirs = [
        Path("D:/experiments/exp3_full_sharp"),
        Path("D:/experiments/exp1_baseline"),
        Path("C:/Users/aya.alaswad/remote/exp3_full_sharp"),
    ]

    log_found = False

    for exp_dir in exp_dirs:
        if not exp_dir.exists():
            continue

        log_files = list(exp_dir.glob("*.log")) + list(exp_dir.glob("**/log.txt"))

        for log_file in log_files:
            print(f"Checking: {log_file}")

            try:
                with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                    for i, line in enumerate(f):
                        if i > 100:  # Only check first 100 lines
                            break

                        # Look for dataset size mentions
                        if any(keyword in line.lower() for keyword in
                              ['dataset size', 'total samples', 'train pairs', 'training examples']):
                            print(f"  Line {i}: {line.strip()}")
                            log_found = True

            except Exception as e:
                continue

    if not log_found:
        print("No dataset size information found in logs")
        print()
        print("To get exact count, look for these lines in training logs:")
        print("  - 'Dataset size: XXXXX'")
        print("  - 'Total training samples: XXXXX'")
        print("  - 'Train pairs: XXXXX'")

def main():
    print()

    # Count scene graphs
    result = count_scene_graphs()
    if result is None:
        print()
        print("Cannot count scene graphs without access to scene graph directory")
        print()
        print("Expected structure:")
        print("  mimic-cxr-jpg/")
        print("    scene_graphs/")
        print("      s12345.scene_graph.json")
        print("      s12346.scene_graph.json")
        print("      ...")
        return

    scene_graph_dir, scene_files = result

    # Load split info
    study_to_split, study_to_subject = load_split_info()

    if study_to_split is None:
        print("Cannot proceed without split information")
        return

    # Count by split
    by_split = count_by_split(scene_files, study_to_split)

    # Estimate pairs
    print()
    count_pairs_in_scenes(scene_files, study_to_split, max_sample=1000)

    # Check logs
    check_training_logs()

    print()
    print("="*80)
    print("Summary")
    print("="*80)
    print()
    print("The exact number of image-text pairs used in SHARP training is:")
    print(f"  {by_split['train']:,} scene graphs (train split)")
    print()
    print("Each scene graph contains multiple observations with bounding boxes,")
    print("so the total number of (image_crop, text_phrase) pairs is higher.")
    print()
    print("To get the EXACT number, check the training logs for lines like:")
    print("  'Dataset size: XXXXX' or 'Total training samples: XXXXX'")

if __name__ == "__main__":
    main()
