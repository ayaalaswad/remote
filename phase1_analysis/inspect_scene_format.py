"""
Inspect actual scene graph format to find correct field names
"""

import json
from pathlib import Path

scene_file = list(Path("D:/datasets/mimic-ext-cxr-qba/scene_graphs/scene_data").rglob("*.scene_graph.json"))[0]

print("Inspecting scene file:", scene_file.name)
print("="*80)

with open(scene_file) as f:
    scene = json.load(f)

print("\nTop-level keys:")
for key in scene.keys():
    print(f"  - {key}")

print("\n" + "="*80)
print("Full JSON structure (first scene):")
print(json.dumps(scene, indent=2)[:2000])  # First 2000 chars
