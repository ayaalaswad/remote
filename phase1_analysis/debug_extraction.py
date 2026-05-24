"""
Debug extraction on first 10 samples with DETAILED logging
Shows exactly where extraction fails
"""

import json
import torch
from pathlib import Path
from PIL import Image
from torchvision import transforms

scene_dir = Path("D:/datasets/mimic-ext-cxr-qba/scene_graphs/scene_data")
image_dir = Path("D:/datasets/mimic-cxr-jpg")

# Get first 10 validation scene files
import pandas as pd
df = pd.read_csv("D:/datasets/mimic-cxr-jpg/mimic-cxr-2.0.0-split.csv.gz", compression='gzip')
val_studies = df[df['split'] == 'validate']['study_id'].head(10).tolist()

print("Testing first 10 validation samples")
print("="*80)

success_count = 0
fail_reasons = {}

for i, study_id in enumerate(val_studies, 1):
    study_id_str = f"s{study_id}"
    print(f"\n[{i}/10] Study: {study_id_str}")

    # Find scene file
    scene_files = list(scene_dir.rglob(f"{study_id_str}.scene_graph.json"))
    if not scene_files:
        fail_reasons['scene_not_found'] = fail_reasons.get('scene_not_found', 0) + 1
        print(f"  FAIL: Scene file not found")
        continue

    scene_file = scene_files[0]
    print(f"  Scene: {scene_file.name}")

    try:
        # Load scene
        with open(scene_file) as f:
            scene = json.load(f)

        patient_id = scene.get('patient_id', '')
        study_id_scene = scene.get('study_id', '')
        print(f"  patient_id: {patient_id}")
        print(f"  study_id: {study_id_scene}")

        if not patient_id:
            fail_reasons['no_patient_id'] = fail_reasons.get('no_patient_id', 0) + 1
            print(f"  FAIL: No patient_id")
            continue

        # Find image
        p_prefix = f"p{patient_id[1:3]}"
        study_dir = image_dir / p_prefix / patient_id / study_id_scene
        print(f"  Looking for images in: {study_dir}")
        print(f"  Directory exists: {study_dir.exists()}")

        if not study_dir.exists():
            fail_reasons['study_dir_not_found'] = fail_reasons.get('study_dir_not_found', 0) + 1
            print(f"  FAIL: Study directory not found")
            continue

        images = list(study_dir.glob("*.jpg"))
        print(f"  Images found: {len(images)}")
        if not images:
            fail_reasons['no_images'] = fail_reasons.get('no_images', 0) + 1
            print(f"  FAIL: No images in directory")
            continue

        print(f"  Using image: {images[0].name}")

        # Check observations
        observations = scene.get('observations', {})
        print(f"  Observations: {len(observations)}")
        if not observations:
            fail_reasons['no_observations'] = fail_reasons.get('no_observations', 0) + 1
            print(f"  FAIL: No observations")
            continue

        # Check observation format
        valid_obs = 0
        for obs_id, obs in observations.items():
            polarity = obs.get('positiveness', '')
            if polarity in ['pos', 'neg']:
                valid_obs += 1

        print(f"  Valid observations (pos/neg): {valid_obs}")
        if valid_obs == 0:
            fail_reasons['no_valid_observations'] = fail_reasons.get('no_valid_observations', 0) + 1
            print(f"  FAIL: No valid observations")
            continue

        # Try loading image
        try:
            img = Image.open(images[0]).convert('RGB')
            print(f"  Image loaded: {img.size}")
        except Exception as e:
            fail_reasons['image_load_error'] = fail_reasons.get('image_load_error', 0) + 1
            print(f"  FAIL: Image load error: {e}")
            continue

        print(f"  SUCCESS: Would extract {valid_obs} embeddings")
        success_count += 1

    except Exception as e:
        fail_reasons['exception'] = fail_reasons.get('exception', 0) + 1
        print(f"  FAIL: Exception: {e}")

print("\n" + "="*80)
print("SUMMARY")
print("="*80)
print(f"Successful: {success_count}/10")
print("\nFailure reasons:")
for reason, count in sorted(fail_reasons.items(), key=lambda x: -x[1]):
    print(f"  {reason}: {count}")
