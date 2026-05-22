"""
Phase 0 Diagnostic: Sanity-check the paired sampler.

Dump 10 random batches and verify:
- 32 unique items?
- Truly 100% co-positive (16 pairs)?
- No accidental duplicates?
"""

import sys
sys.path.insert(0, "C:/Users/ZA/lawer/MyReasearch")

import json
import random
from collections import Counter, defaultdict
from pathlib import Path
from train_sharp_large_batch import PairedBatchSampler, extract_pairs


def build_test_manifest(scene_dir, image_dir, num_files=1000):
    """Build a small manifest for testing."""
    scene_files = list(Path(scene_dir).rglob("*.scene.json"))
    sample_files = random.sample(scene_files, min(num_files, len(scene_files)))

    manifest = []
    rng = random.Random(42)

    for sf in sample_files:
        try:
            with open(sf) as fh:
                scene = json.load(fh)
        except Exception:
            continue

        pairs = extract_pairs(scene, image_dir, rng=rng, no_polarity=False)
        for pair in pairs:
            manifest.append({
                'crop': pair['image_path'],
                'concept_key': pair['concept_key'],
                'phrase': pair['phrase'],
                'bbox': pair['bbox'],
            })

    return manifest


def analyze_batch(batch_indices, manifest):
    """Analyze a single batch to check correctness."""
    batch_items = [manifest[idx] for idx in batch_indices]

    # Check 1: All indices unique?
    if len(batch_indices) != len(set(batch_indices)):
        duplicates = [idx for idx, count in Counter(batch_indices).items() if count > 1]
        return {
            'valid': False,
            'error': f'Duplicate indices found: {duplicates}',
            'batch_size': len(batch_indices),
        }

    # Check 2: Extract concept keys
    concept_keys = [item['concept_key'] for item in batch_items]

    # Check 3: Count co-positives
    key_counts = Counter(concept_keys)

    # For paired sampling, each key should appear exactly 2 times
    expected_pairs = len(batch_indices) // 2
    actual_keys_with_2_instances = sum(1 for count in key_counts.values() if count == 2)

    # Co-positive rate
    co_positive_pairs = sum(count - 1 for count in key_counts.values() if count >= 2)
    total_possible = len(batch_indices) - 1
    co_positive_rate = (co_positive_pairs / total_possible) * 100 if total_possible > 0 else 0

    return {
        'valid': True,
        'batch_size': len(batch_indices),
        'unique_keys': len(key_counts),
        'expected_pairs': expected_pairs,
        'actual_pairs': actual_keys_with_2_instances,
        'co_positive_rate': co_positive_rate,
        'key_distribution': dict(key_counts),
        'phrases': [item['phrase'] for item in batch_items],
    }


def sanity_check_sampler():
    """Main sanity check function."""

    print("="*80)
    print("PAIRED SAMPLER SANITY CHECK")
    print("="*80)

    # Use smaller test set for speed
    scene_dir = "D:/datasets/mimic-ext-cxr-qba/scene_graphs/scene_data"
    image_dir = "D:/datasets/mimic-cxr-jpg"

    if not Path(scene_dir).exists():
        print(f"ERROR: Scene directory not found: {scene_dir}")
        print("This script should be run on the remote desktop where data exists.")
        return

    print("\nBuilding test manifest (1000 files)...")
    manifest = build_test_manifest(scene_dir, image_dir, num_files=1000)
    print(f"  Built manifest: {len(manifest):,} pairs")

    # Create paired sampler
    print("\nCreating PairedBatchSampler...")
    sampler = PairedBatchSampler(
        crop_manifest=manifest,
        batch_size=32,
        shuffle=True,
        seed=42
    )

    # Sample 10 batches
    print("\nSampling 10 random batches for inspection...")
    print("="*80)

    batch_iterator = iter(sampler)
    all_valid = True

    for i in range(10):
        try:
            batch_indices = next(batch_iterator)
        except StopIteration:
            print(f"\nWARNING: Sampler exhausted after {i} batches")
            break

        print(f"\n--- Batch {i+1} ---")
        print(f"Indices: {batch_indices[:8]}... (showing first 8)")

        result = analyze_batch(batch_indices, manifest)

        if not result['valid']:
            print(f"✗ INVALID: {result['error']}")
            all_valid = False
            continue

        print(f"Batch size: {result['batch_size']}")
        print(f"Unique concept keys: {result['unique_keys']}")
        print(f"Expected pairs: {result['expected_pairs']}")
        print(f"Actual pairs (keys with 2 instances): {result['actual_pairs']}")
        print(f"Co-positive rate: {result['co_positive_rate']:.1f}%")

        # Show key distribution
        print(f"\nKey distribution:")
        for key, count in list(result['key_distribution'].items())[:5]:
            print(f"  {key}: {count} instances")
        if len(result['key_distribution']) > 5:
            print(f"  ... and {len(result['key_distribution']) - 5} more keys")

        # Verify correctness
        if result['actual_pairs'] == result['expected_pairs']:
            print(f"✓ CORRECT: All {result['expected_pairs']} pairs present")
        else:
            print(f"✗ INCORRECT: Expected {result['expected_pairs']} pairs, got {result['actual_pairs']}")
            all_valid = False

        if result['co_positive_rate'] >= 99.0:
            print(f"✓ CORRECT: Co-positive rate ~100%")
        else:
            print(f"✗ INCORRECT: Co-positive rate should be 100%, got {result['co_positive_rate']:.1f}%")
            all_valid = False

    print("\n" + "="*80)
    print("FINAL VERDICT")
    print("="*80)

    if all_valid:
        print("✓ PASSED: Paired sampler is working correctly")
        print("  - All batches have correct structure")
        print("  - 100% co-positive rate achieved")
        print("  - No duplicate indices")
        print("\nConclusion: Exp #2's failure is NOT due to sampler bugs.")
        print("The poor performance (R@1=0.81%) is a REAL finding.")
    else:
        print("✗ FAILED: Paired sampler has issues")
        print("\nConclusion: Exp #2's failure might be due to sampler bugs.")
        print("Fix the sampler before claiming paired sampling hurts performance.")

    print("="*80)


if __name__ == "__main__":
    sanity_check_sampler()
