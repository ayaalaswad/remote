"""
Phase 1: Compute "concept consistency @ top-5" metric

For each text embedding, retrieve top-5 most similar text embeddings.
Measure what % of top-5 have the same concept key (region, entity, polarity).

High consistency = encoder learned to group same concepts together.
Low consistency = encoder confused, similar embeddings don't share concept.
"""

import numpy as np
from pathlib import Path
import argparse
from tqdm import tqdm
import json


def compute_similarity_matrix(embeddings):
    """
    Compute cosine similarity matrix.

    Args:
        embeddings: (N, D) array

    Returns:
        sim_matrix: (N, N) array where sim_matrix[i, j] = cos(emb_i, emb_j)
    """
    # Normalize embeddings
    norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
    normalized = embeddings / (norms + 1e-8)

    # Compute cosine similarity
    sim_matrix = normalized @ normalized.T

    return sim_matrix


def concept_consistency_at_k(embeddings, concept_keys, k=5):
    """
    For each sample, retrieve top-k most similar samples.
    Measure what % have the same concept key.

    Args:
        embeddings: (N, D) array
        concept_keys: list of (region, entity, polarity) tuples
        k: number of top retrievals to check

    Returns:
        consistency: scalar, average % of top-k with same concept
        per_sample_consistency: (N,) array
    """
    print(f"\nComputing concept consistency @ top-{k}...")

    # Convert concept keys to array
    concept_keys = np.array(concept_keys)

    # Compute similarity matrix
    sim_matrix = compute_similarity_matrix(embeddings)

    # For each sample, get top-k most similar (excluding self)
    per_sample_consistency = []

    for i in tqdm(range(len(embeddings)), desc="Computing consistency"):
        # Get similarities (excluding self)
        sims = sim_matrix[i].copy()
        sims[i] = -np.inf  # Exclude self

        # Get top-k indices
        topk_indices = np.argsort(sims)[-k:]

        # Check how many have same concept key
        query_key = tuple(concept_keys[i])
        topk_keys = [tuple(concept_keys[j]) for j in topk_indices]

        matches = sum(1 for key in topk_keys if key == query_key)
        consistency_score = matches / k

        per_sample_consistency.append(consistency_score)

    per_sample_consistency = np.array(per_sample_consistency)
    avg_consistency = np.mean(per_sample_consistency)

    return avg_consistency, per_sample_consistency


def analyze_by_entity(embeddings, concept_keys, entities, k=5):
    """
    Break down consistency by entity type.

    Returns dict mapping entity -> consistency score.
    """
    print(f"\nAnalyzing consistency by entity...")

    from collections import defaultdict

    # Compute similarity matrix
    sim_matrix = compute_similarity_matrix(embeddings)

    entity_to_consistencies = defaultdict(list)

    for i in tqdm(range(len(embeddings)), desc="By entity"):
        entity = entities[i]

        # Get similarities (excluding self)
        sims = sim_matrix[i].copy()
        sims[i] = -np.inf

        # Get top-k
        topk_indices = np.argsort(sims)[-k:]

        # Check matches
        query_key = tuple(concept_keys[i])
        topk_keys = [tuple(concept_keys[j]) for j in topk_indices]

        matches = sum(1 for key in topk_keys if key == query_key)
        consistency_score = matches / k

        entity_to_consistencies[entity].append(consistency_score)

    # Average by entity
    entity_to_avg = {
        entity: np.mean(scores)
        for entity, scores in entity_to_consistencies.items()
    }

    return entity_to_avg


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--embedding_dir", type=str, default="phase1_analysis/embeddings")
    parser.add_argument("--output_dir", type=str, default="phase1_analysis/consistency")
    parser.add_argument("--k", type=int, default=5, help="Top-k for consistency metric")
    args = parser.parse_args()

    embedding_dir = Path(args.embedding_dir)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Load all embeddings
    exp_names = ["exp1_baseline", "exp2_paired", "exp3_full_sharp", "exp4_large_batch"]

    results = {}

    for exp_name in exp_names:
        emb_path = embedding_dir / f"{exp_name}_embeddings.npz"
        if not emb_path.exists():
            print(f"⚠️  Not found: {emb_path}")
            continue

        print(f"\n{'='*80}")
        print(f"Analyzing {exp_name}")
        print(f"{'='*80}")

        # Load
        data = np.load(emb_path, allow_pickle=True)
        text_embs = data["text_embs"]
        concept_keys = data["concept_keys"]
        entities = data["entities"]

        print(f"Loaded {len(text_embs):,} text embeddings")

        # Compute overall consistency
        avg_consistency, per_sample = concept_consistency_at_k(text_embs, concept_keys, k=args.k)

        # Compute by entity
        entity_consistency = analyze_by_entity(text_embs, concept_keys, entities, k=args.k)

        # Sort entities by consistency
        sorted_entities = sorted(entity_consistency.items(), key=lambda x: x[1], reverse=True)

        print(f"\n{'='*60}")
        print(f"Results for {exp_name}:")
        print(f"{'='*60}")
        print(f"Overall Concept Consistency @ top-{args.k}: {avg_consistency:.2%}")
        print(f"\nTop 10 entities by consistency:")
        for entity, cons in sorted_entities[:10]:
            print(f"  {entity:30s}: {cons:.2%}")

        print(f"\nBottom 10 entities by consistency:")
        for entity, cons in sorted_entities[-10:]:
            print(f"  {entity:30s}: {cons:.2%}")

        # Store results
        results[exp_name] = {
            "overall_consistency": float(avg_consistency),
            "entity_consistency": {e: float(c) for e, c in entity_consistency.items()},
            "top_entities": [(e, float(c)) for e, c in sorted_entities[:10]],
            "bottom_entities": [(e, float(c)) for e, c in sorted_entities[-10:]],
        }

    # Save results
    output_path = output_dir / f"concept_consistency_k{args.k}.json"
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)

    print(f"\n✓ Saved results to {output_path}")

    # Create summary comparison
    print(f"\n{'='*80}")
    print(f"SUMMARY: Concept Consistency @ top-{args.k}")
    print(f"{'='*80}")

    for exp_name in exp_names:
        if exp_name in results:
            cons = results[exp_name]["overall_consistency"]
            print(f"{exp_name:20s}: {cons:.2%}")

    print("\n" + "="*80)
    print("Phase 1 Step 3: Concept consistency analysis complete!")
    print("="*80)


if __name__ == "__main__":
    main()
