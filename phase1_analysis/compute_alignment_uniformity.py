"""
Compute alignment and uniformity metrics (Wang & Isola 2020).

Paper: "Understanding Contrastive Representation Learning through Alignment and Uniformity on the Hypersphere"
https://arxiv.org/abs/2005.10242

Two key metrics for contrastive learning quality:

1. Alignment: How close are positive pairs?
   - Lower is better (closer alignment)
   - Measures: E[(f(x) - f(x+))^2] for positive pairs

2. Uniformity: How evenly distributed are representations on hypersphere?
   - Lower is better (more uniform distribution)
   - Measures: log E[e^(-2||f(x) - f(x')||^2)] for random pairs

These metrics are:
- Quantitative (two numbers per experiment)
- Theoretically grounded
- Directly interpretable
- Reviewer-friendly (established in literature)
"""

import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from tqdm import tqdm

def l2_normalize(x):
    """Normalize vectors to unit length."""
    return x / (np.linalg.norm(x, axis=1, keepdims=True) + 1e-8)

def compute_alignment(image_embs, text_embs, n_samples=1000):
    """
    Compute alignment metric: E[(f(x) - f(x+))^2]

    Lower is better - measures how close positive pairs are.

    Args:
        image_embs: Image embeddings (N, D)
        text_embs: Text embeddings (N, D)
        n_samples: Number of samples to use

    Returns:
        alignment: Scalar alignment metric
    """
    # Normalize to unit hypersphere
    image_embs = l2_normalize(image_embs)
    text_embs = l2_normalize(text_embs)

    # Subsample
    n = min(n_samples, len(image_embs))
    indices = np.random.RandomState(42).choice(len(image_embs), n, replace=False)

    image_embs = image_embs[indices]
    text_embs = text_embs[indices]

    # Compute squared L2 distance for positive pairs
    squared_dists = np.sum((image_embs - text_embs) ** 2, axis=1)

    # Return mean
    alignment = squared_dists.mean()

    return alignment

def compute_uniformity(embeddings, t=2.0, n_samples=1000):
    """
    Compute uniformity metric: log E[e^(-t||f(x) - f(x')||^2)]

    Lower is better - measures how uniformly distributed embeddings are.

    Args:
        embeddings: Combined embeddings (N, D)
        t: Temperature parameter (default 2.0 from paper)
        n_samples: Number of samples to use

    Returns:
        uniformity: Scalar uniformity metric
    """
    # Normalize to unit hypersphere
    embeddings = l2_normalize(embeddings)

    # Subsample
    n = min(n_samples, len(embeddings))
    indices = np.random.RandomState(42).choice(len(embeddings), n, replace=False)
    embeddings = embeddings[indices]

    # Compute pairwise squared distances
    # For efficiency, use random pairs instead of all pairs
    n_pairs = min(n * 100, n * (n-1) // 2)  # 100 random pairs per sample

    pair_dists = []
    for _ in tqdm(range(n_pairs), desc="Computing uniformity"):
        i, j = np.random.choice(n, 2, replace=False)
        sq_dist = np.sum((embeddings[i] - embeddings[j]) ** 2)
        pair_dists.append(np.exp(-t * sq_dist))

    # Compute log of mean
    uniformity = np.log(np.mean(pair_dists))

    return uniformity

def compute_metrics_for_experiment(embeddings_file, n_samples=1000):
    """
    Compute alignment and uniformity for one experiment.

    Args:
        embeddings_file: Path to .npz file
        n_samples: Number of samples

    Returns:
        alignment: Alignment metric
        uniformity: Uniformity metric
    """
    print(f"Loading {embeddings_file.name}...")
    data = np.load(embeddings_file)

    image_embs = data['image_embs']
    text_embs = data['text_embs']

    print(f"  Loaded {len(image_embs)} samples")

    # Compute alignment (how close are positive pairs?)
    print("  Computing alignment...")
    alignment = compute_alignment(image_embs, text_embs, n_samples)

    # Compute uniformity (how spread out are embeddings?)
    print("  Computing uniformity...")
    combined_embs = np.vstack([image_embs, text_embs])
    uniformity = compute_uniformity(combined_embs, n_samples=n_samples)

    print(f"  Alignment:   {alignment:.4f} (lower = better)")
    print(f"  Uniformity:  {uniformity:.4f} (lower = better)")

    return alignment, uniformity

def plot_metrics(experiments_metrics, output_path):
    """
    Create scatter plot of alignment vs uniformity.

    Args:
        experiments_metrics: Dict mapping exp_id -> (alignment, uniformity, r1)
        output_path: Where to save the figure
    """
    fig, ax = plt.subplots(1, 1, figsize=(10, 8))

    exp_info = {
        'exp1': ('Baseline', 'blue', 'o', 6.61),
        'exp2': ('Paired Sampling', 'red', 's', 0.81),
        'exp3': ('Hard Negatives', 'green', '^', 6.21),
        'exp4': ('Large Batch', 'purple', 'D', 6.99)
    }

    for exp_id, (label, color, marker, r1) in exp_info.items():
        if exp_id not in experiments_metrics:
            continue

        alignment, uniformity = experiments_metrics[exp_id]

        ax.scatter(alignment, uniformity, s=200, c=color, marker=marker,
                  label=f'{label} (R@1={r1:.2f}%)', edgecolors='black', linewidth=2)

        # Add annotation
        ax.annotate(f'{exp_id.upper()}', (alignment, uniformity),
                   xytext=(10, 10), textcoords='offset points',
                   fontsize=10, fontweight='bold')

    ax.set_xlabel('Alignment (lower = better)', fontsize=13, fontweight='bold')
    ax.set_ylabel('Uniformity (lower = better)', fontsize=13, fontweight='bold')
    ax.set_title('Alignment vs Uniformity (Wang & Isola 2020)\nIdeal: Lower-left corner',
                fontsize=14, fontweight='bold')

    # Add ideal region annotation
    ax.annotate('← Ideal region', xy=(0.05, 0.05), xycoords='axes fraction',
               fontsize=11, color='gray', style='italic')

    ax.legend(fontsize=11, loc='upper right')
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
    print("Phase 1 Analysis: Alignment & Uniformity (Wang & Isola 2020)")
    print("="*70)
    print("\nComputing two metrics for contrastive learning quality:")
    print("  1. Alignment:   How close are positive pairs? (lower = better)")
    print("  2. Uniformity:  How spread out are embeddings? (lower = better)")
    print()

    experiments = ['exp1', 'exp2', 'exp3', 'exp4']
    experiments_metrics = {}

    for exp_id in experiments:
        emb_file = emb_dir / f'{exp_id}_embeddings.npz'
        if not emb_file.exists():
            print(f"WARNING: {emb_file} not found, skipping...")
            print()
            continue

        alignment, uniformity = compute_metrics_for_experiment(emb_file, n_samples=1000)
        experiments_metrics[exp_id] = (alignment, uniformity)
        print()

    # Create scatter plot
    output_path = output_dir / 'alignment_uniformity.png'
    plot_metrics(experiments_metrics, output_path)

    # Save metrics to file
    metrics_path = output_dir / 'alignment_uniformity_metrics.txt'
    with open(metrics_path, 'w') as f:
        f.write("Alignment & Uniformity Metrics (Wang & Isola 2020)\n")
        f.write("="*70 + "\n\n")
        f.write("Lower is better for both metrics.\n\n")

        f.write(f"{'Experiment':<20} {'Alignment':<12} {'Uniformity':<12} {'R@1':<10}\n")
        f.write("-"*70 + "\n")

        exp_r1 = {'exp1': 6.61, 'exp2': 0.81, 'exp3': 6.21, 'exp4': 6.99}

        for exp_id in ['exp1', 'exp2', 'exp3', 'exp4']:
            if exp_id not in experiments_metrics:
                continue

            alignment, uniformity = experiments_metrics[exp_id]
            r1 = exp_r1[exp_id]

            f.write(f"{exp_id.upper():<20} {alignment:<12.4f} {uniformity:<12.4f} {r1:<10.2f}%\n")

        f.write("\n\nInterpretation:\n")
        f.write("-"*70 + "\n")
        f.write("- Alignment measures positive pair closeness\n")
        f.write("- Uniformity measures embedding spread on hypersphere\n")
        f.write("- Good contrastive learning needs BOTH low alignment AND low uniformity\n")
        f.write("- Exp #2 (paired) likely has poor alignment (explains collapse)\n")
        f.write("- Exp #4 (large batch) should have better metrics than baseline\n")

    print(f"Saved metrics: {metrics_path}")

    print("\n" + "="*70)
    print("Analysis Complete!")
    print("="*70)
    print("\nThese metrics are:")
    print("  ✓ Quantitative (two numbers per experiment)")
    print("  ✓ Theoretically grounded (Wang & Isola 2020)")
    print("  ✓ Directly interpretable")
    print("  ✓ Reviewer-friendly (established metric)")
    print("\nUse these instead of UMAP 'tight clusters' claims!")

if __name__ == '__main__':
    main()
