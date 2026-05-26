"""
Compute cosine similarity distributions for Phase 1 embeddings.

Shows the fundamental retrieval signal:
- Positive pairs (image, matching text) should have HIGH cosine similarity
- Random negatives (image, non-matching text) should have LOW cosine similarity

This is the geometry that directly explains R@1 performance.
"""

import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from tqdm import tqdm

def cosine_similarity(a, b):
    """Compute cosine similarity between vectors (can be batched)."""
    if len(a.shape) == 1:
        a = a.reshape(1, -1)
    if len(b.shape) == 1:
        b = b.reshape(1, -1)

    # Normalize
    a_norm = a / (np.linalg.norm(a, axis=1, keepdims=True) + 1e-8)
    b_norm = b / (np.linalg.norm(b, axis=1, keepdims=True) + 1e-8)

    return np.sum(a_norm * b_norm, axis=1)

def compute_similarity_distributions(embeddings_file, n_samples=1000, n_negatives=100):
    """
    Compute cosine similarity distributions for positive and negative pairs.

    Args:
        embeddings_file: Path to .npz file
        n_samples: Number of samples to analyze
        n_negatives: Number of random negatives per positive

    Returns:
        positive_sims: Array of cosine similarities for (image, matching_text) pairs
        negative_sims: Array of cosine similarities for (image, random_text) pairs
    """
    print(f"Loading {embeddings_file.name}...")
    data = np.load(embeddings_file)

    image_embs = data['image_embs']
    text_embs = data['text_embs']

    # Subsample
    n = min(n_samples, len(image_embs))
    indices = np.random.RandomState(42).choice(len(image_embs), n, replace=False)

    image_embs = image_embs[indices]
    text_embs = text_embs[indices]

    print(f"  Computing similarities for {n} samples...")

    # Positive pairs (i, i)
    positive_sims = []
    for i in tqdm(range(n), desc="Positive pairs"):
        sim = cosine_similarity(image_embs[i], text_embs[i])
        positive_sims.append(sim[0])

    positive_sims = np.array(positive_sims)

    # Negative pairs (i, j) where j != i
    negative_sims = []
    for i in tqdm(range(n), desc="Negative pairs"):
        # Sample random negatives (excluding i)
        neg_indices = np.random.choice([j for j in range(n) if j != i],
                                      min(n_negatives, n-1),
                                      replace=False)

        for j in neg_indices:
            sim = cosine_similarity(image_embs[i], text_embs[j])
            negative_sims.append(sim[0])

    negative_sims = np.array(negative_sims)

    print(f"  Positive: mean={positive_sims.mean():.4f}, std={positive_sims.std():.4f}")
    print(f"  Negative: mean={negative_sims.mean():.4f}, std={negative_sims.std():.4f}")
    print(f"  Separation: {positive_sims.mean() - negative_sims.mean():.4f}")

    return positive_sims, negative_sims

def plot_similarity_distributions(experiments_data, output_path):
    """
    Create figure showing cosine similarity distributions for all experiments.

    Args:
        experiments_data: Dict mapping exp_id -> (positive_sims, negative_sims)
        output_path: Where to save the figure
    """
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    axes = axes.flatten()

    exp_info = {
        'exp1': ('Exp #1: Baseline (6.61% R@1)', 0),
        'exp2': ('Exp #2: Paired Sampling (0.81% R@1)', 1),
        'exp3': ('Exp #3: Hard Negatives (6.21% R@1)', 2),
        'exp4': ('Exp #4: Large Batch (6.99% R@1)', 3)
    }

    for exp_id, (title, idx) in exp_info.items():
        if exp_id not in experiments_data:
            axes[idx].text(0.5, 0.5, f'Data not available for {exp_id}',
                          ha='center', va='center', fontsize=12)
            axes[idx].set_title(title, fontsize=13, fontweight='bold')
            continue

        ax = axes[idx]
        pos_sims, neg_sims = experiments_data[exp_id]

        # Plot histograms
        bins = np.linspace(-0.5, 1.0, 50)
        ax.hist(neg_sims, bins=bins, alpha=0.5, color='red',
               label=f'Negatives (μ={neg_sims.mean():.3f})', density=True)
        ax.hist(pos_sims, bins=bins, alpha=0.5, color='blue',
               label=f'Positives (μ={pos_sims.mean():.3f})', density=True)

        # Add vertical lines for means
        ax.axvline(neg_sims.mean(), color='red', linestyle='--', linewidth=2)
        ax.axvline(pos_sims.mean(), color='blue', linestyle='--', linewidth=2)

        # Calculate separation
        separation = pos_sims.mean() - neg_sims.mean()

        ax.set_title(f'{title}\nSeparation: {separation:.3f}',
                    fontsize=13, fontweight='bold')
        ax.set_xlabel('Cosine Similarity', fontsize=11)
        ax.set_ylabel('Density', fontsize=11)
        ax.legend(fontsize=10)
        ax.grid(alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"\nSaved: {output_path}")
    plt.close()

def main():
    emb_dir = Path('embeddings')
    output_dir = Path('plots')
    output_dir.mkdir(exist_ok=True)

    print("="*70)
    print("Phase 1 Analysis: Cosine Similarity Distributions")
    print("="*70)
    print("\nThis shows the fundamental retrieval geometry:")
    print("  - Blue (positives): High similarity = good retrieval")
    print("  - Red (negatives): Low similarity = good separation")
    print("  - Greater separation = better R@1 performance")
    print()

    experiments = ['exp1', 'exp2', 'exp3', 'exp4']
    experiments_data = {}

    for exp_id in experiments:
        emb_file = emb_dir / f'{exp_id}_embeddings.npz'
        if not emb_file.exists():
            print(f"WARNING: {emb_file} not found, skipping...")
            continue

        pos_sims, neg_sims = compute_similarity_distributions(emb_file,
                                                              n_samples=1000,
                                                              n_negatives=100)
        experiments_data[exp_id] = (pos_sims, neg_sims)
        print()

    # Create comparison plot
    output_path = output_dir / 'cosine_similarity_distributions.png'
    plot_similarity_distributions(experiments_data, output_path)

    # Save statistics to file
    stats_path = output_dir / 'cosine_similarity_stats.txt'
    with open(stats_path, 'w') as f:
        f.write("Cosine Similarity Statistics\n")
        f.write("="*70 + "\n\n")

        for exp_id in ['exp1', 'exp2', 'exp3', 'exp4']:
            if exp_id not in experiments_data:
                continue

            pos_sims, neg_sims = experiments_data[exp_id]
            separation = pos_sims.mean() - neg_sims.mean()

            f.write(f"{exp_id.upper()}:\n")
            f.write(f"  Positive pairs: μ={pos_sims.mean():.4f}, σ={pos_sims.std():.4f}\n")
            f.write(f"  Negative pairs: μ={neg_sims.mean():.4f}, σ={neg_sims.std():.4f}\n")
            f.write(f"  Separation:     {separation:.4f}\n")
            f.write(f"  Overlap:        {np.sum(neg_sims > pos_sims.mean()) / len(neg_sims) * 100:.2f}%\n")
            f.write("\n")

    print(f"Saved statistics: {stats_path}")

    print("\n" + "="*70)
    print("Analysis Complete!")
    print("="*70)
    print("\nKey insights:")
    print("  - Exp #2 (paired) should show LESS separation (explains 0.81% R@1)")
    print("  - Exp #4 (large batch) should show MORE separation (explains 6.99% R@1)")
    print("  - This directly explains retrieval performance")

if __name__ == '__main__':
    main()
