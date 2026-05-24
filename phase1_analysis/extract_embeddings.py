"""
Phase 1: Extract Stage 1 encoder embeddings for t-SNE/UMAP analysis

Loads all 4 Stage 1 checkpoints and extracts embeddings on validation set.
Saves embeddings + metadata (concept keys, regions, entities, polarities) for visualization.
"""

import sys
import json
import torch
import numpy as np
from pathlib import Path
from tqdm import tqdm
from collections import defaultdict
import argparse

# Add parent directory to path to import from training script
sys.path.insert(0, str(Path(__file__).parent.parent))

from train_sharp_large_batch import (
    ImageEncoderViT,
    ImprovedTextEncoder,
    load_scene_graph,
    partition_scene_files,
)


def extract_embeddings_for_experiment(
    checkpoint_path,
    val_files,
    image_dir,
    vocab,
    device="cuda",
    max_samples=5000,
    batch_size=64
):
    """
    Extract image and text embeddings from a trained checkpoint.

    Returns:
        embeddings: dict with keys:
            - image_embs: (N, 128) numpy array
            - text_embs: (N, 128) numpy array
            - concept_keys: list of (region, entity, polarity) tuples
            - regions: list of region strings
            - entities: list of entity strings
            - polarities: list of polarity strings
            - dicom_ids: list of DICOM IDs
    """
    print(f"\n{'='*80}")
    print(f"Extracting embeddings: {checkpoint_path}")
    print(f"{'='*80}")

    # Load checkpoint
    checkpoint = torch.load(checkpoint_path, map_location=device)
    state_dict = checkpoint.get("state_dict", checkpoint)

    # Initialize encoders
    img_encoder = ImageEncoderViT(d_model=128).to(device)
    txt_encoder = ImprovedTextEncoder(len(vocab), d_model=128, max_len=256).to(device)

    # Load weights (handle lightning prefixes)
    img_state = {k.replace("img_encoder.", ""): v for k, v in state_dict.items() if "img_encoder" in k}
    txt_state = {k.replace("txt_encoder.", ""): v for k, v in state_dict.items() if "txt_encoder" in k}

    img_encoder.load_state_dict(img_state, strict=False)
    txt_encoder.load_state_dict(txt_state, strict=False)

    img_encoder.eval()
    txt_encoder.eval()

    print(f"Loaded encoders from checkpoint")
    print(f"Processing {min(max_samples, len(val_files)):,} validation samples...")

    # Sample validation files
    import random
    rng = random.Random(42)
    sampled_files = rng.sample(val_files, min(max_samples, len(val_files)))

    image_embs = []
    text_embs = []
    concept_keys = []
    regions = []
    entities = []
    polarities = []
    dicom_ids = []

    with torch.no_grad():
        for scene_file in tqdm(sampled_files, desc="Extracting embeddings"):
            try:
                # Load scene graph
                scene = load_scene_graph(scene_file)
                if scene is None:
                    continue

                dicom_id = scene.get("dicom_id", "")
                observations = scene.get("observations", {})

                if not observations:
                    continue

                # Get image path
                img_path = Path(image_dir) / f"{dicom_id}.jpg"
                if not img_path.exists():
                    continue

                # Load image (simple grayscale -> RGB)
                from PIL import Image
                img = Image.open(img_path).convert("RGB")
                img_array = np.array(img.resize((224, 224))) / 255.0
                img_tensor = torch.from_numpy(img_array).permute(2, 0, 1).float().unsqueeze(0).to(device)

                # Extract image embedding
                img_emb = img_encoder(img_tensor).cpu().numpy()[0]  # (128,)

                # Process each observation
                for obs_id, obs in observations.items():
                    region_str = obs.get("region", "")
                    entity_str = obs.get("entity", "")
                    polarity_str = obs.get("polarity", "")

                    # Get phrases
                    phrases = obs.get("pos_phrases", []) + obs.get("neg_phrases", [])
                    if not phrases:
                        continue

                    # Use first phrase
                    phrase = phrases[0]

                    # Tokenize
                    tokens = phrase.lower().split()
                    token_ids = [vocab.get(t, vocab.get("<UNK>", 0)) for t in tokens]
                    token_ids = token_ids[:256]  # Truncate

                    # Pad
                    padded = token_ids + [vocab.get("<PAD>", 1)] * (256 - len(token_ids))
                    txt_tensor = torch.tensor([padded], dtype=torch.long).to(device)

                    # Extract text embedding
                    txt_emb = txt_encoder(txt_tensor).cpu().numpy()[0]  # (128,)

                    # Store
                    image_embs.append(img_emb)
                    text_embs.append(txt_emb)
                    concept_keys.append((region_str, entity_str, polarity_str))
                    regions.append(region_str)
                    entities.append(entity_str)
                    polarities.append(polarity_str)
                    dicom_ids.append(dicom_id)

            except Exception as e:
                continue

    print(f"Extracted {len(image_embs):,} image-text pairs")

    return {
        "image_embs": np.array(image_embs),
        "text_embs": np.array(text_embs),
        "concept_keys": concept_keys,
        "regions": regions,
        "entities": entities,
        "polarities": polarities,
        "dicom_ids": dicom_ids,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--scene_dir", type=str, required=True)
    parser.add_argument("--image_dir", type=str, required=True)
    parser.add_argument("--split_csv", type=str, required=True)
    parser.add_argument("--output_dir", type=str, default="phase1_analysis/embeddings")
    parser.add_argument("--max_samples", type=int, default=5000)
    parser.add_argument("--device", type=str, default="cuda")
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Load vocab from exp1 (all experiments use same vocab)
    exp1_vocab_path = Path("D:/experiments/exp1_baseline/p3_vocab.json")
    print(f"\nLoading vocabulary from {exp1_vocab_path}")
    with open(exp1_vocab_path) as f:
        vocab = json.load(f)
    print(f"Loaded {len(vocab):,} tokens")

    # Load split
    import pandas as pd
    import gzip
    print(f"\nLoading split from {args.split_csv}")
    if args.split_csv.endswith(".gz"):
        with gzip.open(args.split_csv, "rt") as f:
            df = pd.read_csv(f)
    else:
        df = pd.read_csv(args.split_csv)

    study_to_split = dict(zip(df["study_id"], df["split"]))
    study_to_subject = dict(zip(df["study_id"], df["subject_id"]))

    # Get scene files
    print(f"\nScanning scene files from {args.scene_dir}")
    scene_files = [str(p) for p in Path(args.scene_dir).rglob("*.scene_graph.json")]
    print(f"Found {len(scene_files):,} scene files")

    # Partition
    train_files, val_files, test_files = partition_scene_files(
        scene_files, study_to_split, study_to_subject
    )
    print(f"Val files: {len(val_files):,}")

    # Experiment checkpoints
    experiments = {
        "exp1_baseline": "D:/experiments/exp1_baseline/checkpoints/best_model.ckpt",
        "exp2_paired": "D:/experiments/exp2_paired_sampling/checkpoints/best_model.ckpt",
        "exp3_full_sharp": "D:/experiments/exp3_full_sharp/checkpoints/best_model.ckpt",
        "exp4_large_batch": "D:/experiments/exp4_large_batch/checkpoints/best_model.ckpt",
    }

    # Extract embeddings for each experiment
    for exp_name, ckpt_path in experiments.items():
        ckpt_path = Path(ckpt_path)
        if not ckpt_path.exists():
            print(f"\n⚠️  Checkpoint not found: {ckpt_path}")
            print(f"   Skipping {exp_name}")
            continue

        embeddings = extract_embeddings_for_experiment(
            checkpoint_path=ckpt_path,
            val_files=val_files,
            image_dir=args.image_dir,
            vocab=vocab,
            device=args.device,
            max_samples=args.max_samples,
        )

        # Save
        output_path = output_dir / f"{exp_name}_embeddings.npz"
        np.savez_compressed(
            output_path,
            image_embs=embeddings["image_embs"],
            text_embs=embeddings["text_embs"],
            concept_keys=np.array(embeddings["concept_keys"], dtype=object),
            regions=np.array(embeddings["regions"], dtype=object),
            entities=np.array(embeddings["entities"], dtype=object),
            polarities=np.array(embeddings["polarities"], dtype=object),
            dicom_ids=np.array(embeddings["dicom_ids"], dtype=object),
        )
        print(f"\n✓ Saved embeddings to {output_path}")
        print(f"  Shape: {embeddings['image_embs'].shape}")

    print("\n" + "="*80)
    print("Phase 1 Step 1: Embedding extraction complete!")
    print("="*80)


if __name__ == "__main__":
    main()
