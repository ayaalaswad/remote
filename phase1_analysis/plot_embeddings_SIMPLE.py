"""
Simple script to visualize the 4 embedding files for the rebuttal
Works with exp1/2/3/4_embeddings.npz files
"""

import numpy as np
import matplotlib.pyplot as plt
from sklearn.manifold import TSNE
import umap
from pathlib import Path

print("Loading embeddings...")

# Load all 4 experiments
data = {}
experiments = {
    'exp1': 'Exp #1: Baseline (6.61% R@1)',
    'exp2': 'Exp #2: Paired Sampling (0.81% R@1)',
    'exp3': 'Exp #3: Hard Negatives (6.21% R@1)',
    'exp4': 'Exp #4: Large Batch (6.99% R@1)'
}

for exp_id in ['exp1', 'exp2', 'exp3', 'exp4']:
    npz = np.load(f'embeddings/{exp_id}_embeddings.npz')

    # Subsample to 1000 points for faster visualization
    n = min(1000, len(npz['image_embeddings']))
    idx = np.random.RandomState(42).choice(len(npz['image_embeddings']), n, replace=False)

    data[exp_id] = {
        'image': npz['image_embeddings'][idx],
        'text': npz['text_embeddings'][idx]
    }
    print(f"  {exp_id}: {n} samples")

# Create UMAP visualization
print("\nCreating UMAP plots...")
fig, axes = plt.subplots(2, 2, figsize=(16, 14))
axes = axes.flatten()

for idx, (exp_id, title) in enumerate(experiments.items()):
    print(f"  Processing {exp_id}...")

    # Combine image and text embeddings
    combined = np.vstack([data[exp_id]['image'], data[exp_id]['text']])
    n_img = len(data[exp_id]['image'])

    # Run UMAP
    reducer = umap.UMAP(n_neighbors=15, min_dist=0.1, random_state=42)
    embedded = reducer.fit_transform(combined)

    # Plot
    ax = axes[idx]
    ax.scatter(embedded[:n_img, 0], embedded[:n_img, 1],
              c='blue', alpha=0.4, s=15, label='Image', edgecolors='none')
    ax.scatter(embedded[n_img:, 0], embedded[n_img:, 1],
              c='red', alpha=0.4, s=15, label='Text', edgecolors='none')

    ax.set_title(title, fontsize=13, fontweight='bold')
    ax.legend(fontsize=10)
    ax.set_xlabel('UMAP Dimension 1')
    ax.set_ylabel('UMAP Dimension 2')
    ax.grid(alpha=0.2)

plt.tight_layout()
plt.savefig('plots/umap_all_experiments.png', dpi=300, bbox_inches='tight')
print("\nSaved: plots/umap_all_experiments.png")
plt.close()

# Create comparison: Baseline vs Best
print("\nCreating comparison plot (Baseline vs Large Batch)...")
fig, axes = plt.subplots(1, 2, figsize=(16, 6))

for idx, exp_id in enumerate(['exp1', 'exp4']):
    combined = np.vstack([data[exp_id]['image'], data[exp_id]['text']])
    n_img = len(data[exp_id]['image'])

    reducer = umap.UMAP(n_neighbors=15, min_dist=0.1, random_state=42)
    embedded = reducer.fit_transform(combined)

    ax = axes[idx]
    ax.scatter(embedded[:n_img, 0], embedded[:n_img, 1],
              c='blue', alpha=0.5, s=25, label='Image', edgecolors='none')
    ax.scatter(embedded[n_img:, 0], embedded[n_img:, 1],
              c='red', alpha=0.5, s=25, label='Text', edgecolors='none')

    ax.set_title(experiments[exp_id], fontsize=14, fontweight='bold')
    ax.legend(fontsize=12)
    ax.set_xlabel('UMAP Dimension 1', fontsize=12)
    ax.set_ylabel('UMAP Dimension 2', fontsize=12)
    ax.grid(alpha=0.2)

plt.tight_layout()
plt.savefig('plots/comparison_baseline_vs_best.png', dpi=300, bbox_inches='tight')
print("Saved: plots/comparison_baseline_vs_best.png")
plt.close()

print("\n" + "="*60)
print("DONE! Plots ready for your rebuttal:")
print("  1. umap_all_experiments.png - All 4 experiments")
print("  2. comparison_baseline_vs_best.png - Baseline vs Large Batch")
print("\nKey observations for rebuttal:")
print("  - Exp #2 (paired): Poor image-text alignment (R@1=0.81%)")
print("  - Exp #4 (large batch): Better clustering than baseline")
print("="*60)
