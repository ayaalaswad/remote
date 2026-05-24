"""
Debug script to test single sample extraction
This will show EXACTLY where the extraction is failing
"""

import json
from pathlib import Path

# Pick first validation file
val_files = list(Path("D:/datasets/mimic-ext-cxr-qba/scene_graphs/scene_data").rglob("*.scene_graph.json"))[:5]

print("Testing first 5 scene files:")
for i, scene_file in enumerate(val_files[:5], 1):
    print(f"\n{'='*80}")
    print(f"Sample {i}: {scene_file.name}")

    try:
        with open(scene_file) as f:
            scene = json.load(f)

        # Check dicom_id
        dicom_id = scene.get('dicom_id', '')
        print(f"  dicom_id: '{dicom_id}'")
        if not dicom_id:
            print("  ERROR: dicom_id is empty!")
            continue

        # Check observations
        observations = scene.get('observations', {})
        print(f"  observations: {len(observations)} found")
        if not observations:
            print("  ERROR: No observations!")
            continue

        # Check observation format
        for obs_id, obs in list(observations.items())[:3]:
            entity = obs.get('name', 'finding')
            polarity = obs.get('positiveness', 'pos')
            print(f"    {obs_id}: entity='{entity}', polarity='{polarity}'")

            if polarity not in ['pos', 'neg']:
                print(f"      WARNING: Invalid polarity '{polarity}'")

        # Try image path construction
        parts = dicom_id.split('_')
        if len(parts) >= 3:
            subject_id = parts[0]  # pXXXXXXX
            study_id = parts[1]    # sXXXXXXXX
            img_file = parts[2]    # XXXXXXXX
            p_prefix = f"p{subject_id[1:3]}"
            img_path = Path("D:/datasets/mimic-cxr-jpg") / p_prefix / subject_id / study_id / f"{img_file}.jpg"
            print(f"  Image path: {img_path}")
            print(f"  Image exists: {img_path.exists()}")
        else:
            print(f"  ERROR: Cannot parse dicom_id '{dicom_id}' (expected format: pXXX_sXXX_XXX)")

        print("  WOULD EXTRACT: YES" if dicom_id and observations else "  WOULD EXTRACT: NO")

    except Exception as e:
        print(f"  ERROR: {e}")

print("\n" + "="*80)
print("Summary: Check above for what's failing")
