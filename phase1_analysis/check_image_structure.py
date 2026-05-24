"""
Check actual MIMIC-CXR-JPG directory structure
"""

from pathlib import Path
import random

image_dir = Path("D:/datasets/mimic-cxr-jpg")

print("Checking MIMIC-CXR-JPG structure")
print("="*80)

# Check top level
print("\nTop level directories:")
top_dirs = sorted([d for d in image_dir.iterdir() if d.is_dir()])[:10]
for d in top_dirs:
    print(f"  {d.name}")

# Pick first p-directory and explore
if top_dirs:
    p_dir = top_dirs[0]
    print(f"\nInside {p_dir.name}:")

    # Check patients
    patients = sorted([d for d in p_dir.iterdir() if d.is_dir()])[:5]
    for patient in patients:
        print(f"  {patient.name}/")

        # Check studies
        studies = sorted([d for d in patient.iterdir() if d.is_dir()])[:3]
        for study in studies:
            print(f"    {study.name}/")

            # Check images
            images = list(study.glob("*.jpg"))[:3]
            for img in images:
                print(f"      {img.name}")

print("\n" + "="*80)
print("Expected structure: pXX/pXXXXXXX/sXXXXXXXX/*.jpg")
print("Check if actual structure matches this")
