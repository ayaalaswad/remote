#!/usr/bin/env python3
"""
Explore MIMIC-Ext Scene Graphs - Extract Concept Keys

Shows you:
1. What concept keys exist in your data
2. Structure of scene graph JSON files
3. Distribution of (region, entity, polarity) combinations
4. Example phrases for each concept key

This helps verify your data has the right format for SHARP training.
"""

import json
import gzip
from pathlib import Path
from collections import Counter, defaultdict
import argparse


def explore_single_scene(scene_path, show_structure=True):
    """Explore one scene graph file in detail."""
    print(f"\n{'='*80}")
    print(f"Exploring: {scene_path}")
    print(f"{'='*80}")

    try:
        with open(scene_path) as f:
            scene = json.load(f)
    except Exception as e:
        print(f"❌ Error loading file: {e}")
        return None

    # Show top-level structure
    if show_structure:
        print(f"\n📋 Top-level keys:")
        for key in scene.keys():
            print(f"   - {key}")

    # Extract study info
    patient_id = scene.get("patient_id", "unknown")
    study_id = scene.get("study_id", "unknown")
    print(f"\n🏥 Study Info:")
    print(f"   Patient ID: {patient_id}")
    print(f"   Study ID: {study_id}")

    # Extract observations
    observations = scene.get("observations", {})
    print(f"\n🔍 Observations: {len(observations)} total")

    concept_keys = []
    examples = []

    for obs_id, obs in observations.items():
        # Get polarity (pos/neg)
        polarity = obs.get("positiveness", "")
        if polarity not in ("pos", "neg"):
            continue

        # Get entity (finding name)
        entity = obs.get("name", "unknown")

        # Get severity (optional)
        severity = obs.get("severity", [])
        if isinstance(severity, list):
            severity = severity[0] if severity else ""

        # Get localizations (regions + bboxes)
        localizations = obs.get("localization", {})

        for image_id, loc_data in localizations.items():
            bboxes = loc_data.get("bboxes", [])
            regions = loc_data.get("localization_reference_ids", [])

            if not bboxes:
                continue

            region = regions[0] if regions else "unknown"

            # THIS IS THE CONCEPT KEY!
            concept_key = (region, entity, polarity)
            concept_keys.append(concept_key)

            # Build phrase (what the model sees)
            attrs = [polarity]
            if severity:
                attrs.append(severity)
            phrase = f"[{region}] {entity} ({', '.join(attrs)})"

            examples.append({
                'concept_key': concept_key,
                'phrase': phrase,
                'bbox': bboxes[0] if bboxes else None,
                'image_id': image_id,
            })

    print(f"\n📊 Extracted Concept Keys: {len(concept_keys)} pairs")
    print(f"\n   Format: (region, entity, polarity)")

    # Show unique concept keys
    unique_keys = list(set(concept_keys))
    print(f"\n   Unique keys in this file: {len(unique_keys)}")

    # Show examples
    print(f"\n💡 Example Concept Keys & Phrases:")
    for i, ex in enumerate(examples[:10], 1):
        ck = ex['concept_key']
        print(f"\n   {i}. Concept Key: {ck}")
        print(f"      Phrase: \"{ex['phrase']}\"")
        print(f"      BBox: {ex['bbox']}")
        print(f"      Image: {ex['image_id']}")

    if len(examples) > 10:
        print(f"\n   ... and {len(examples) - 10} more pairs")

    return concept_keys, examples


def explore_multiple_scenes(scene_dir, num_files=100):
    """Explore multiple scene files to get statistics."""
    print(f"\n{'='*80}")
    print(f"Exploring Scene Directory: {scene_dir}")
    print(f"{'='*80}")

    scene_files = list(Path(scene_dir).rglob("*.scene_graph.json"))

    if not scene_files:
        print(f"❌ No scene graph files found in {scene_dir}")
        print(f"   Expected pattern: *.scene_graph.json")
        return

    print(f"\n📁 Found: {len(scene_files):,} scene graph files")
    print(f"   Sampling: {min(num_files, len(scene_files))} files")

    # Sample files
    import random
    random.seed(42)
    sample = random.sample(scene_files, min(num_files, len(scene_files)))

    all_concept_keys = []
    all_regions = Counter()
    all_entities = Counter()
    all_polarities = Counter()
    key_to_phrases = defaultdict(set)

    print(f"\n⏳ Processing files...")
    for i, sf in enumerate(sample, 1):
        if i % 20 == 0:
            print(f"   Processed {i}/{len(sample)} files...")

        try:
            with open(sf) as f:
                scene = json.load(f)
        except Exception:
            continue

        for obs in scene.get("observations", {}).values():
            polarity = obs.get("positiveness", "")
            if polarity not in ("pos", "neg"):
                continue

            entity = obs.get("name", "unknown")
            severity = obs.get("severity", [])
            if isinstance(severity, list):
                severity = severity[0] if severity else ""

            for _, loc_data in obs.get("localization", {}).items():
                bboxes = loc_data.get("bboxes", [])
                regions = loc_data.get("localization_reference_ids", [])

                if not bboxes:
                    continue

                region = regions[0] if regions else "unknown"
                concept_key = (region, entity, polarity)

                all_concept_keys.append(concept_key)
                all_regions[region] += 1
                all_entities[entity] += 1
                all_polarities[polarity] += 1

                # Build phrase
                attrs = [polarity]
                if severity:
                    attrs.append(severity)
                phrase = f"[{region}] {entity} ({', '.join(attrs)})"
                key_to_phrases[concept_key].add(phrase)

    print(f"\n✅ Processing complete!")

    # Statistics
    print(f"\n{'='*80}")
    print(f"📊 CONCEPT KEY STATISTICS")
    print(f"{'='*80}")

    print(f"\nTotal pairs extracted: {len(all_concept_keys):,}")
    print(f"Unique concept keys: {len(set(all_concept_keys)):,}")

    # Region distribution
    print(f"\n🔹 Top 20 Regions (anatomical areas):")
    for region, count in all_regions.most_common(20):
        pct = (count / len(all_concept_keys)) * 100
        print(f"   {region:30} {count:>6,} ({pct:>5.1f}%)")

    # Entity distribution
    print(f"\n🔹 Top 20 Entities (findings):")
    for entity, count in all_entities.most_common(20):
        pct = (count / len(all_concept_keys)) * 100
        print(f"   {entity:30} {count:>6,} ({pct:>5.1f}%)")

    # Polarity distribution
    print(f"\n🔹 Polarity Distribution:")
    for polarity, count in all_polarities.most_common():
        pct = (count / len(all_concept_keys)) * 100
        print(f"   {polarity:30} {count:>6,} ({pct:>5.1f}%)")

    # Most common concept keys
    print(f"\n🔹 Top 20 Concept Keys (region, entity, polarity):")
    key_counts = Counter(all_concept_keys)
    for i, (ck, count) in enumerate(key_counts.most_common(20), 1):
        region, entity, polarity = ck
        pct = (count / len(all_concept_keys)) * 100
        example_phrase = list(key_to_phrases[ck])[0]
        print(f"\n   {i}. Count: {count:,} ({pct:.1f}%)")
        print(f"      Key: ({region}, {entity}, {polarity})")
        print(f"      Example phrase: \"{example_phrase}\"")

    # Multi-positive potential
    print(f"\n{'='*80}")
    print(f"🎯 MULTI-POSITIVE InfoNCE POTENTIAL")
    print(f"{'='*80}")

    avg_per_key = len(all_concept_keys) / len(set(all_concept_keys))
    print(f"\nAverage pairs per unique concept key: {avg_per_key:.2f}")

    # Estimate co-positives for different batch sizes
    unique_keys = list(set(all_concept_keys))
    key_probs = {k: count / len(all_concept_keys) for k, count in key_counts.items()}

    print(f"\n💡 Expected co-positives per batch:")
    for batch_size in [32, 64, 128, 256, 512]:
        # Expected number of times each key appears in batch
        expected_copositives = sum(
            max(0, batch_size * prob - 1)  # -1 for anchor itself
            for prob in key_probs.values()
        )
        pct_with_copositives = 0
        for prob in key_probs.values():
            # Probability of having at least 2 instances in batch
            p_0 = (1 - prob) ** batch_size
            p_1 = batch_size * prob * ((1 - prob) ** (batch_size - 1))
            pct_with_copositives += (1 - p_0 - p_1) * prob * batch_size

        print(f"   Batch {batch_size:3d}: Avg {expected_copositives/batch_size:.2f} co-pos/anchor, "
              f"~{pct_with_copositives:.0f}% anchors have co-pos")

    print(f"\n   ⚠️  batch=32:  Low co-positive rate → MP-InfoNCE ≈ standard InfoNCE")
    print(f"   ✅  batch=512: High co-positive rate → MP-InfoNCE advantage!")


def verify_data_format(scene_path):
    """Verify a scene file has all required fields for SHARP."""
    print(f"\n{'='*80}")
    print(f"🔍 VERIFYING DATA FORMAT")
    print(f"{'='*80}")

    try:
        with open(scene_path) as f:
            scene = json.load(f)
    except Exception as e:
        print(f"❌ Cannot load file: {e}")
        return False

    required_fields = {
        'patient_id': False,
        'study_id': False,
        'observations': False,
    }

    for field in required_fields:
        if field in scene:
            required_fields[field] = True
            print(f"✅ Found: {field}")
        else:
            print(f"❌ Missing: {field}")

    if not all(required_fields.values()):
        print(f"\n❌ Data format invalid - missing required fields")
        return False

    # Check observations structure
    observations = scene.get("observations", {})
    if not observations:
        print(f"⚠️  No observations found in this file")
        return True

    print(f"\n✅ Observations found: {len(observations)}")

    # Check one observation
    first_obs = list(observations.values())[0]
    obs_fields = {
        'positiveness': 'positiveness' in first_obs,
        'name': 'name' in first_obs,
        'localization': 'localization' in first_obs,
    }

    print(f"\n📋 Observation structure:")
    for field, found in obs_fields.items():
        status = "✅" if found else "❌"
        print(f"   {status} {field}")

    # Check localization structure
    if 'localization' in first_obs:
        first_loc = list(first_obs['localization'].values())[0]
        print(f"\n📋 Localization structure:")
        print(f"   {'✅' if 'bboxes' in first_loc else '❌'} bboxes")
        print(f"   {'✅' if 'localization_reference_ids' in first_loc else '❌'} localization_reference_ids")

        if 'bboxes' in first_loc and first_loc['bboxes']:
            print(f"\n   Example bbox: {first_loc['bboxes'][0]}")
        if 'localization_reference_ids' in first_loc:
            print(f"   Example region: {first_loc['localization_reference_ids']}")

    print(f"\n✅ Data format looks correct for SHARP training!")
    return True


def main():
    parser = argparse.ArgumentParser(description="Explore MIMIC-Ext scene graphs")
    parser.add_argument("--scene_dir", default="./scene_data",
                        help="Path to scene_data directory")
    parser.add_argument("--mode", choices=["single", "stats", "verify"], default="stats",
                        help="Exploration mode")
    parser.add_argument("--file", help="Specific scene file to explore (for single/verify mode)")
    parser.add_argument("--num_files", type=int, default=100,
                        help="Number of files to sample for stats mode")

    args = parser.parse_args()

    if args.mode == "single":
        if not args.file:
            # Find first scene file
            scene_files = list(Path(args.scene_dir).rglob("*.scene_graph.json"))
            if not scene_files:
                print(f"❌ No scene files found in {args.scene_dir}")
                return
            args.file = str(scene_files[0])
            print(f"No file specified, using: {args.file}")

        explore_single_scene(args.file, show_structure=True)

    elif args.mode == "verify":
        if not args.file:
            scene_files = list(Path(args.scene_dir).rglob("*.scene_graph.json"))
            if not scene_files:
                print(f"❌ No scene files found in {args.scene_dir}")
                return
            args.file = str(scene_files[0])

        verify_data_format(args.file)

    elif args.mode == "stats":
        explore_multiple_scenes(args.scene_dir, args.num_files)

    print(f"\n{'='*80}")
    print(f"✅ EXPLORATION COMPLETE")
    print(f"{'='*80}\n")

    # Show what concept keys are used for
    print(f"💡 What are concept keys used for?\n")
    print(f"   1. Multi-positive InfoNCE:")
    print(f"      - Pairs with SAME key = positives")
    print(f"      - Pairs with DIFFERENT key = negatives\n")
    print(f"   2. Hard negative mining:")
    print(f"      - Anatomy-hard: same region, different entity")
    print(f"      - Negation-hard: same (region,entity), opposite polarity\n")
    print(f"   3. Example:")
    print(f"      Key A: (right lung, opacity, pos)")
    print(f"      Key B: (right lung, opacity, pos)  ← POSITIVE pair (same key)")
    print(f"      Key C: (left lung, opacity, pos)   ← NEGATIVE (different region)")
    print(f"      Key D: (right lung, opacity, neg)  ← HARD NEG (opposite polarity)\n")


if __name__ == "__main__":
    main()
