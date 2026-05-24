"""
Phase 1: Extract embeddings - WORKING VERSION

Fixed: Use patient_id + study_id (not dicom_id) and find images in study directory
"""

import os
import json
import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
from pathlib import Path
from tqdm import tqdm
from PIL import Image
import argparse

# ============================================================================
# Model Definitions
# ============================================================================

class ImageEncoderViT(nn.Module):
    def __init__(self, embedding_dim=256):
        super().__init__()
        from transformers import ViTModel

        vit_paths = [
            '/tmp',
            'google/vit-base-patch16-224-in21k',
            'google/vit-base-patch16-224',
        ]
        loaded = False
        for vit_path in vit_paths:
            try:
                if vit_path == '/tmp':
                    self.vit = ViTModel.from_pretrained(vit_path, local_files_only=True)
                else:
                    self.vit = ViTModel.from_pretrained(vit_path)
                loaded = True
                break
            except:
                continue

        if not loaded:
            raise RuntimeError("Could not load ViT weights")

        self.projection = nn.Sequential(
            nn.Linear(768, 512),
            nn.ReLU(),
            nn.Linear(512, embedding_dim),
        )

    def forward(self, x):
        out = self.vit(pixel_values=x)
        return F.normalize(self.projection(out.last_hidden_state[:, 0]), dim=1)


class ImprovedTextEncoder(nn.Module):
    def __init__(self, embedding_dim=256, vocab_size=10000, hidden_dim=256):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, 128, padding_idx=0)
        self.lstm = nn.LSTM(128, hidden_dim, num_layers=2,
                            batch_first=True, bidirectional=True)
        self.projection = nn.Linear(hidden_dim * 2, embedding_dim)

    def forward(self, text_indices):
        x = self.embedding(text_indices)
        _, (h, _) = self.lstm(x)
        h = torch.cat([h[-2], h[-1]], dim=1)
        return F.normalize(self.projection(h), dim=1)


# ============================================================================
# Helper Functions
# ============================================================================

def load_split_csv(csv_path):
    """Load MIMIC-CXR split CSV"""
    import pandas as pd
    if str(csv_path).endswith('.gz'):
        df = pd.read_csv(csv_path, compression='gzip')
    else:
        df = pd.read_csv(csv_path)

    study_to_split = {}
    study_to_subject = {}
    for _, row in df.iterrows():
        study_id = str(row['study_id'])
        if not study_id.startswith('s'):
            study_id = 's' + study_id

        study_to_split[study_id] = row['split']
        study_to_subject[study_id] = str(row['subject_id'])

    return study_to_split, study_to_subject


def get_study_id_from_path(scene_path):
    """Extract study_id from scene file path"""
    stem = Path(scene_path).stem
    if '.scene_graph' in stem:
        stem = stem.split('.scene_graph')[0]
    return stem


def partition_files(scene_files, study_to_split, study_to_subject):
    """Partition scene files by split"""
    train_files, val_files, test_files = [], [], []
    subject_splits = {}

    for scene_file in scene_files:
        study_id = get_study_id_from_path(scene_file)

        if study_id not in study_to_split:
            continue

        subject_id = study_to_subject[study_id]
        split = study_to_split[study_id]

        if subject_id in subject_splits:
            if subject_splits[subject_id] != split:
                continue
        else:
            subject_splits[subject_id] = split

        if split == 'train':
            train_files.append(scene_file)
        elif split == 'validate':
            val_files.append(scene_file)
        elif split == 'test':
            test_files.append(scene_file)

    return train_files, val_files, test_files


def load_vocab(vocab_path):
    """Load vocabulary"""
    with open(vocab_path) as f:
        return json.load(f)


def tokenize_text(text, vocab, max_len=256):
    """Tokenize text using vocabulary"""
    tokens = text.lower().split()
    indices = [vocab.get(t, vocab.get('<unk>', 1)) for t in tokens]

    if len(indices) < max_len:
        indices += [0] * (max_len - len(indices))
    else:
        indices = indices[:max_len]

    return torch.tensor(indices, dtype=torch.long)


def find_study_image(patient_id, study_id, image_dir):
    """Find first image in study directory"""
    # Construct path: p{XX}/{patient_id}/{study_id}/
    p_prefix = f"p{patient_id[1:3]}"  # p10 from p10000032
    study_dir = Path(image_dir) / p_prefix / patient_id / study_id

    if not study_dir.exists():
        return None

    # Find first .jpg in directory
    images = list(study_dir.glob("*.jpg"))
    if not images:
        return None

    return images[0]


def load_image(img_path):
    """Load and preprocess image"""
    from torchvision import transforms

    img = Image.open(img_path).convert('RGB')

    transform = transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])

    return transform(img)


# ============================================================================
# Main Extraction Function
# ============================================================================

def extract_embeddings(checkpoint_path, val_files, image_dir, vocab, device='cuda', max_samples=5000):
    """Extract embeddings from a checkpoint"""

    print(f"\nLoading checkpoint: {checkpoint_path}")
    checkpoint = torch.load(checkpoint_path, map_location=device)
    state_dict = checkpoint.get('state_dict', checkpoint)

    # Initialize encoders
    img_encoder = ImageEncoderViT(embedding_dim=256).to(device)
    txt_encoder = ImprovedTextEncoder(embedding_dim=256, vocab_size=len(vocab)).to(device)

    # Load weights
    img_state = {k.replace('img_encoder.', ''): v for k, v in state_dict.items() if 'img_encoder' in k}
    txt_state = {k.replace('txt_encoder.', ''): v for k, v in state_dict.items() if 'txt_encoder' in k}

    if not img_state:
        img_state = {k.replace('image_encoder.', ''): v for k, v in state_dict.items() if 'image_encoder' in k}
    if not txt_state:
        txt_state = {k.replace('text_encoder.', ''): v for k, v in state_dict.items() if 'text_encoder' in k}

    img_encoder.load_state_dict(img_state, strict=False)
    txt_encoder.load_state_dict(txt_state, strict=False)

    img_encoder.eval()
    txt_encoder.eval()

    # Extract embeddings
    image_embs = []
    text_embs = []
    concept_keys = []

    print(f"Extracting embeddings from {min(max_samples, len(val_files))} validation samples...")

    with torch.no_grad():
        for scene_file in tqdm(val_files[:max_samples]):
            try:
                with open(scene_file) as f:
                    scene = json.load(f)

                # Get patient_id and study_id from scene graph
                patient_id = scene.get('patient_id', '')
                study_id = scene.get('study_id', '')

                if not patient_id or not study_id:
                    continue

                # Find image for this study
                img_path = find_study_image(patient_id, study_id, image_dir)
                if img_path is None:
                    continue

                # Load image
                img = load_image(img_path).unsqueeze(0).to(device)

                # Get observations
                observations = scene.get('observations', {})
                if not observations:
                    continue

                for obs_id, obs in observations.items():
                    entity = obs.get('name', 'finding')
                    polarity = obs.get('positiveness', 'pos')

                    if polarity not in ['pos', 'neg']:
                        continue

                    # Get text
                    text = f"{entity} ({polarity})"
                    text_tokens = tokenize_text(text, vocab).unsqueeze(0).to(device)

                    # Extract embeddings
                    img_emb = img_encoder(img)
                    txt_emb = txt_encoder(text_tokens)

                    image_embs.append(img_emb.cpu().numpy())
                    text_embs.append(txt_emb.cpu().numpy())
                    concept_keys.append((entity, polarity))

            except Exception as e:
                continue

    if not image_embs:
        print("WARNING: No embeddings extracted!")
        return None

    # Stack embeddings
    image_embs = np.vstack(image_embs)
    text_embs = np.vstack(text_embs)

    print(f"Extracted {len(image_embs)} embeddings")

    return {
        'image_embs': image_embs,
        'text_embs': text_embs,
        'concept_keys': concept_keys,
    }


# ============================================================================
# Main
# ============================================================================

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--scene_dir', required=True)
    parser.add_argument('--image_dir', required=True)
    parser.add_argument('--split_csv', required=True)
    parser.add_argument('--output_dir', default='embeddings')
    parser.add_argument('--max_samples', type=int, default=1000)
    parser.add_argument('--device', default='cuda')
    args = parser.parse_args()

    # Create output directory
    Path(args.output_dir).mkdir(parents=True, exist_ok=True)

    # Load split
    print("Loading MIMIC-CXR split...")
    study_to_split, study_to_subject = load_split_csv(args.split_csv)

    # Get scene files
    print("Finding scene files...")
    scene_files = list(Path(args.scene_dir).rglob("*.scene_graph.json"))
    print(f"Found {len(scene_files)} scene files")

    # Partition
    train_files, val_files, test_files = partition_files(scene_files, study_to_split, study_to_subject)
    print(f"Train: {len(train_files)}, Val: {len(val_files)}, Test: {len(test_files)}")

    if not val_files:
        print("\nERROR: No validation files found!")
        return

    # Load vocab from Exp #1
    vocab_path = Path("D:/experiments/exp1_baseline/p3_vocab.json")
    if not vocab_path.exists():
        print(f"ERROR: Vocabulary not found at {vocab_path}")
        return

    vocab = load_vocab(vocab_path)
    print(f"Loaded vocabulary: {len(vocab)} tokens")

    # Extract embeddings for each experiment
    experiments = {
        'exp1': 'D:/experiments/exp1_baseline/p3_best.pt',
        'exp2': 'D:/experiments/exp2_paired/p3_best.pt',
        'exp3': 'D:/experiments/exp3_full_sharp/p3_best.pt',
        'exp4': 'D:/experiments/exp4_large_batch_FAIR/p3_best.pt',
    }

    for exp_name, checkpoint_path in experiments.items():
        if not Path(checkpoint_path).exists():
            print(f"\nSkipping {exp_name}: checkpoint not found")
            continue

        embeddings = extract_embeddings(
            checkpoint_path,
            val_files,
            args.image_dir,
            vocab,
            device=args.device,
            max_samples=args.max_samples
        )

        if embeddings is None:
            print(f"Skipping {exp_name}: no embeddings extracted")
            continue

        # Save
        output_path = Path(args.output_dir) / f"{exp_name}_embeddings.npz"
        np.savez(output_path, **embeddings)
        print(f"Saved: {output_path}")


if __name__ == '__main__':
    main()
