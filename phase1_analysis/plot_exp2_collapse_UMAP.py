"""
UMAP visualization ONLY for Exp #2 collapse evidence.

This is the ONLY legitimate use of UMAP in our analysis:
- Exp #2 (paired sampling) shows poor image-text separation
- This visually demonstrates the representation collapse

DO NOT use UMAP to claim "tighter clusters = better R@1" for other experiments.
That's overinterpreting UMAP artifacts.

For Exp #1, #3, #4: Use cosine similarity distributions and alignment/uniformity instead.
"""

import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import umap

def plot_exp2_collapse(embeddings_file, output_path):
    """
    Create UMAP plot showing Exp #2's representation collapse.

    Args:
        embeddings_file: Path to exp2_embeddings.npz
        output_path: Where to save the figure
    """
    print(f"Loading {embeddings_file.name}...")
    data = np.load(embeddings_file)

    image_embs = data['image_embs']
    text_embs = data['text_embs']

    # Subsample to 1000 points
    n = min(1000, len(image_embs))
    idx = np.random.RandomState(42).choice(len(image_embs), n, replace=False)

    image_embs = image_embs[idx]
    text_embs = text_embs[idx]

    print(f"  Loaded {n} samples")
    print("  Running UMAP...")

    # Combine for UMAP
    combined = np.vstack([image_embs, text_embs])

    # Run UMAP
    reducer = umap.UMAP(n_neighbors=15, min_dist=0.1, random_state=42)
    embedded = reducer.fit_transform(combined)

    # Split back
    n_img = len(image_embs)
    embedded_img = embedded[:n_img]
    embedded_txt = embedded[n_img:]

    # Create figure
    fig, ax = plt.subplots(1, 1, figsize=(10, 8))

    # Plot
    ax.scatter(embedded_img[:, 0], embedded_img[:, 1],
              c='blue', alpha=0.4, s=25, label='Image', edgecolors='none')
    ax.scatter(embedded_txt[:, 0], embedded_txt[:, 1],
              c='red', alpha=0.4, s=25, label='Text', edgecolors='none')

    ax.set_title('Exp #2: Paired Sampling Collapse (R@1=0.81%)\nPoor Image-Text Separation',
                fontsize=14, fontweight='bold')
    ax.legend(fontsize=12)
    ax.set_xlabel('UMAP Dimension 1', fontsize=12)
    ax.set_ylabel('UMAP Dimension 2', fontsize=12)
    ax.grid(alpha=0.2)

    # Add explanation text
    explanation = (
        "Forced 100% co-positive pairing causes:\n"
        "• Poor separation between modalities\n"
        "• Representation collapse\n"
        "• Explains 0.81% R@1 performance"
    )
    ax.text(0.02, 0.98, explanation,
           transform=ax.transAxes,
           fontsize=10,
           verticalalignment='top',
           bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Saved: {output_path}")
    plt.close()

def main():
    emb_dir = Path('embeddings')
    output_dir = Path('plots')
    output_dir.mkdir(exist_ok=True)

    print("="*70)
    print("UMAP Visualization: Exp #2 Collapse Evidence ONLY")
    print("="*70)
    print("\nThis plot shows:")
    print("  - Exp #2's poor image-text separation")
    print("  - Visual evidence of representation collapse")
    print("  - Explains why R@1 dropped to 0.81%")
    print()
    print("NOTE: We do NOT use UMAP for other experiments.")
    print("      Use cosine similarity + alignment/uniformity instead.")
    print()

    exp2_file = emb_dir / 'exp2_embeddings.npz'

    if not exp2_file.exists():
        print(f"ERROR: {exp2_file} not found!")
        print("Run extract_embeddings_WORKING.py first.")
        return

    output_path = output_dir / 'exp2_collapse_umap.png'
    plot_exp2_collapse(exp2_file, output_path)

    print("\n" + "="*70)
    print("Visualization Complete!")
    print("="*70)
    print("\nUse this plot ONLY to show Exp #2's collapse.")
    print("For other experiments, use:")
    print("  1. Cosine similarity distributions (compute_cosine_similarity.py)")
    print("  2. Alignment & uniformity metrics (compute_alignment_uniformity.py)")

if __name__ == '__main__':
    main()
