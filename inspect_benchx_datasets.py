"""
Inspect BenchX dataset classes to understand their requirements
"""
import sys
sys.path.insert(0, r'C:\Users\aya.alaswad\remote\BenchX')

from unifier.datasets import datasets
import inspect

print("="*80)
print("BENCHX DATASET CLASS INSPECTION")
print("="*80)
print()

# Find all dataset classes
all_classes = [name for name in dir(datasets) if 'Dataset' in name and not name.startswith('_')]
print(f"Found {len(all_classes)} dataset classes:")
for cls_name in sorted(all_classes):
    print(f"  - {cls_name}")
print()

# Inspect SIIM dataset
print("="*80)
print("SIIM_Pneumothorax_Dataset")
print("="*80)
if hasattr(datasets, 'SIIM_Pneumothorax_Dataset'):
    cls = getattr(datasets, 'SIIM_Pneumothorax_Dataset')
    print("\n__init__ signature:")
    print(inspect.signature(cls.__init__))
    print("\n__init__ source code:")
    try:
        source = inspect.getsource(cls.__init__)
        # Print first 50 lines
        for i, line in enumerate(source.split('\n')[:50]):
            print(f"{i+1:3d}: {line}")
    except:
        print("  [Could not get source]")
else:
    print("  [Class not found]")

print()
print("="*80)
print("RSNA_Pneumonia_Dataset")
print("="*80)
if hasattr(datasets, 'RSNA_Pneumonia_Dataset'):
    cls = getattr(datasets, 'RSNA_Pneumonia_Dataset')
    print("\n__init__ signature:")
    print(inspect.signature(cls.__init__))
    print("\n__init__ source code:")
    try:
        source = inspect.getsource(cls.__init__)
        # Print first 50 lines
        for i, line in enumerate(source.split('\n')[:50]):
            print(f"{i+1:3d}: {line}")
    except:
        print("  [Could not get source]")
else:
    print("  [Class not found]")

# Also check transforms
print()
print("="*80)
print("AVAILABLE TRANSFORMS")
print("="*80)
from unifier.datasets import transforms
transform_classes = [name for name in dir(transforms) if 'Transform' in name and not name.startswith('_')]
print(f"Found {len(transform_classes)} transform classes:")
for t_name in sorted(transform_classes):
    print(f"  - {t_name}")
