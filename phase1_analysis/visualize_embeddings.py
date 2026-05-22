"""
Phase 1: Visualize Stage 1 embeddings with t-SNE and UMAP

Creates 2×2 panel figure comparing all 4 experiments.
Colors points by concept keys (region, entity, polarity).
"""

import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import argparse
from tqdm import tqdm


def load_embeddings(embedding_path):
    """Load embeddings from npz file."""
    data = np.load(embedding_path, allow_pickle=True)
    return {
        "image_embs": data["image_embs"],
        "text_embs": data["text_embs"],
        "concept_keys": data["concept_keys"],
        "regions": data["regions"],
        "entities": data["entities"],
        "polarities": data["polarities"],
    }


def run_tsne(embeddings, n_components=2, perplexity=30, random_state=42):
    """Run t-SNE on embeddings."""
    from sklearn.manifold import TSNE

    print(f"Running t-SNE (perplexity={perplexity})...")
    tsne = TSNE(n_components=n_components, perplexity=perplexity, random_state=random_state, n_jobs=-1)
    reduced = tsne.fit_transform(embeddings)
    return reduced


def run_umap(embeddings, n_components=2, n_neighbors=15, min_dist=0.1, random_state=42):
    """Run UMAP on embeddings."""
    import umap

    print(f"Running UMAP (n_neighbors={n_neighbors})...")
    reducer = umap.UMAP(n_components=n_components, n_neighbors=n_neighbors, min_dist=min_dist, random_state=random_state)
    reduced = reducer.fit_transform(embeddings)
    return reduced


def get_color_mapping(labels):
    """
    Create color mapping for labels.
    Uses distinct colors for most common labels, gray for rare ones.
    """
    from collections import Counter

    # Count frequencies
    label_counts = Counter(labels)
    most_common = label_counts.most_common(10)  # Top 10 labels

    # Assign colors
    import matplotlib.cm as cm
    colors = cm.tab10(np.linspace(0, 1, 10))

    label_to_color = {}
    for i, (label, count) in enumerate(most_common):
        label_to_color[label] = colors[i]

    # Assign gray to rare labels
    gray = np.array([0.7, 0.7, 0.7, 1.0])
    for label in label_counts:
        if label not in label_to_color:
            label_to_color[label] = gray

    return label_to_color, most_common


def visualize_experiment(ax, reduced_coords, labels, title, show_legend=False):
    """
    Visualize reduced embeddings on a single subplot.

    Args:
        ax: matplotlib axis
        reduced_coords: (N, 2) array
        labels: (N,) array of labels
        title: plot title
        show_legend: whether to show legend
    """
    label_to_color, most_common = get_color_mapping(labels)

    # Plot each label
    for label in set(labels):
        mask = labels == label
        color = label_to_color[label]
        ax.scatter(
            reduced_coords[mask, 0],
            reduced_coords[mask, 1],
            c=[color],
            s=5,
            alpha=0.5,
            label=label if label in [l for l, _ in most_common[:5]] else None,
        )

    ax.set_title(title, fontsize=12, fontweight="bold")
    ax.set_xticks([])
    ax.set_yticks([])

    if show_legend:
        ax.legend(loc="upper right", fontsize=8, markerscale=2)


def create_comparison_figure(embeddings_dict, method="tsne", color_by="entity"):
    """
    Create 2×2 comparison figure for all 4 experiments.

    Args:
        embeddings_dict: dict mapping exp_name -> embeddings
        method: "tsne" or "umap"
        color_by: "region", "entity", "polarity", or "concept_key"
    """
    fig, axes = plt.subplots(2, 2, figsize=(16, 14))
    fig.suptitle(f"Stage 1 Encoder Representations ({method.upper()}, colored by {color_by})",
                 fontsize=16, fontweight="bold")

    exp_names = ["exp1_baseline", "exp2_paired", "exp3_full_sharp", "exp4_large_batch"]
    titles = [
        "Exp #1: Baseline",
        "Exp #2: Paired Sampling (R@1=0.81%)",
        "Exp #3: Full SHARP (Hard Negatives)",
        "Exp #4: Large Batch (batch=512)",
    ]

    for idx, (exp_name, title) in enumerate(zip(exp_names, titles)):
        row = idx // 2
        col = idx % 2
        ax = axes[row, col]

        if exp_name not in embeddings_dict:
            ax.text(0.5, 0.5, f"No data for {exp_name}", ha="center", va="center", fontsize=12)
            ax.set_xticks([])
            ax.set_yticks([])
            continue

        emb_data = embeddings_dict[exp_name]

        # Use text embeddings (more interpretable)
        embeddings = emb_data["text_embs"]

        # Get labels based on color_by
        if color_by == "region":
            labels = emb_data["regions"]
        elif color_by == "entity":
            labels = emb_data["entities"]
        elif color_by == "polarity":
            labels = emb_data["polarities"]
        elif color_by == "concept_key":
            labels = np.array([f"{r}|{e}|{p}" for r, e, p in emb_data["concept_keys"]])
        else:
            raise ValueError(f"Unknown color_by: {color_by}")

        # Run dimensionality reduction
        if method == "tsne":
            reduced = run_tsne(embeddings)
        elif method == "umap":
            reduced = run_umap(embeddings)
        else:
            raise ValueError(f"Unknown method: {method}")

        # Visualize
        visualize_experiment(ax, reduced, labels, title, show_legend=(idx == 0))

    plt.tight_layout()
    return fig


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--embedding_dir", type=str, default="phase1_analysis/embeddings")
    parser.add_argument("--output_dir", type=str, default="phase1_analysis/figures")
    parser.add_argument("--method", type=str, default="tsne", choices=["tsne", "umap", "both"])
    parser.add_argument("--color_by", type=str, default="entity", choices=["region", "entity", "polarity", "concept_key"])
    args = parser.parse_args()

    embedding_dir = Path(args.embedding_dir)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Load all embeddings
    exp_names = ["exp1_baseline", "exp2_paired", "exp3_full_sharp", "exp4_large_batch"]
    embeddings_dict = {}

    for exp_name in exp_names:
        emb_path = embedding_dir / f"{exp_name}_embeddings.npz"
        if emb_path.exists():
            print(f"Loading {exp_name}...")
            embeddings_dict[exp_name] = load_embeddings(emb_path)
        else:
            print(f"⚠️  Not found: {emb_path}")

    if not embeddings_dict:
        print("No embeddings found! Run extract_embeddings.py first.")
        return

    # Create visualizations
    methods = ["tsne", "umap"] if args.method == "both" else [args.method]

    for method in methods:
        print(f"\n{'='*80}")
        print(f"Creating {method.upper()} visualization...")
        print(f"{'='*80}")

        fig = create_comparison_figure(embeddings_dict, method=method, color_by=args.color_by)

        output_path = output_dir / f"stage1_comparison_{method}_{args.color_by}.png"
        fig.savefig(output_path, dpi=300, bbox_inches="tight")
        print(f"✓ Saved to {output_path}")

        plt.close(fig)

    print("\n" + "="*80)
    print("Phase 1 Step 2: Visualization complete!")
    print("="*80)


if __name__ == "__main__":
    main()
