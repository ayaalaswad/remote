#!/usr/bin/env python3
"""
SHARP Phase 3 ViT contrastive pretraining - LARGE BATCH EXPERIMENT

Modified for batch size testing to validate multi-positive InfoNCE hypothesis.

Key change: batch_size = 512 (default) vs original 32
Expected result: MP-InfoNCE should now activate properly with more co-positives per batch.

Hypothesis:
  - batch=32  -> |P(i)|=1 most of the time -> MP-InfoNCE = standard InfoNCE -> worse
  - batch=512 -> |P(i)|>1 frequently -> MP-InfoNCE advantage -> better F1

Original improvements over Phase 1/2:
  - Starts from ImageNet ViT-B/16 (clean, reproducible baseline)
  - Official MIMIC-CXR train/val/test split; subject-id disjointness verified
  - Negative observations included: concept key K = (region, entity, polarity)
  - Multi-positive InfoNCE: batch pairs with same K are co-positives
  - Curriculum hard negatives: anatomy-hard + negation-hard, ramp 0->60% steps 5k->30k
  - Step-budget training (100k steps) + val early stopping (patience=10 * eval_every)
  - All ViT blocks frozen; last 4 unfrozen at step 5k with 500-step cosine LR ramp
  - Linear LR warmup over 5k steps, cosine decay after

Usage:
    python train_sharp_large_batch.py                          # batch=512 (test hypothesis)
    python train_sharp_large_batch.py --batch_size 256 --grad_accum 2  # OOM fallback (effective=512)
    python train_sharp_large_batch.py --batch_size 128         # moderate batch test
"""

import sys
import os

import argparse
import gzip
import json
import math
import pickle
import random
from collections import defaultdict
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
import torchvision.transforms as T
from PIL import Image
from torch.cuda.amp import GradScaler, autocast
from torch.optim import AdamW
from torch.utils.data import DataLoader, Dataset
import torch.backends.cudnn as cudnn
from tqdm import tqdm

try:
    import pandas as pd
except ImportError:
    raise ImportError("pandas required: pip install pandas")


class SafeToTensor:
    """PIL->tensor without torch.from_numpy (bypasses NumPy 1.x/2.x clash)."""
    def __call__(self, pic):
        buf = torch.frombuffer(bytearray(pic.tobytes()), dtype=torch.uint8)
        c = len(pic.getbands())
        return buf.reshape(pic.size[1], pic.size[0], c).permute(2, 0, 1).float().div(255.0)


# ─────────────────────────────────────────────────────────────────────────────
# Model  (same architecture as Phase 1/2 — checkpoints are compatible)
# ─────────────────────────────────────────────────────────────────────────────

class ImageEncoderViT(nn.Module):
    def __init__(self, embedding_dim=256):
        super().__init__()
        from transformers import ViTModel
        print("Loading ViT-B/16 ImageNet weights...")
        # Try multiple common locations for ViT weights
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
                print(f"   Loaded from: {vit_path}")
                loaded = True
                break
            except Exception as e:
                continue

        if not loaded:
            raise RuntimeError(
                "Could not load ViT weights. Please either:\n"
                "1. Download weights to /tmp, OR\n"
                "2. Ensure internet connection for HuggingFace download"
            )

        self.projection = nn.Sequential(
            nn.Linear(768, 512),
            nn.ReLU(),
            nn.Linear(512, embedding_dim),
        )

    def forward(self, x):
        out = self.vit(pixel_values=x)
        return F.normalize(self.projection(out.last_hidden_state[:, 0]), dim=1)

    def freeze_all(self):
        for p in self.vit.parameters():
            p.requires_grad_(False)

    def unfreeze_last_n_blocks(self, n=4):
        """Unfreeze last n transformer encoder blocks + final LayerNorm."""
        total = len(self.vit.encoder.layer)
        for i in range(total - n, total):
            for p in self.vit.encoder.layer[i].parameters():
                p.requires_grad_(True)
        for p in self.vit.layernorm.parameters():
            p.requires_grad_(True)
        n_params = sum(p.numel() for p in self.vit.parameters() if p.requires_grad)
        print(f"   Unfrozen {n} ViT blocks + LayerNorm: {n_params:,} params")


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


class GraphTextCLIP(nn.Module):
    def __init__(self, embed_dim=256, temperature=0.07):
        super().__init__()
        self.image_encoder = ImageEncoderViT(embed_dim)
        self.text_encoder = ImprovedTextEncoder(embed_dim)
        self.temperature = temperature


# ─────────────────────────────────────────────────────────────────────────────
# Multi-positive InfoNCE loss  (Khosla et al., NeurIPS 2020 — cross-modal)
# ─────────────────────────────────────────────────────────────────────────────

def multi_positive_infonce(img_embs, txt_embs, concept_keys, temperature, bidirectional=False):
    """
    Cross-modal multi-positive InfoNCE.

    For each image anchor i:
      P(i) = {j : concept_keys[j] == concept_keys[i]}  (includes j=i: diagonal)
      L_i  = -1/|P(i)| * sum_{j in P(i)} sim(i,j)/tau + log sum_k exp(sim(i,k)/tau)

    When |P(i)| = 1 (no batch co-positives), reduces to standard InfoNCE.

    Args:
        bidirectional: If True, computes both i->t and t->i losses (like CLIP).
                      If False, only computes i->t (original SHARP).

    NOTE: "Negated observations are matched positive pairs (same K); hard negatives
    are mismatched confusable pairs (different K but same anatomy or same entity
    with opposite polarity)."

    LARGE BATCH EXPERIMENT: With batch_size=512, we expect many anchors to have
    |P(i)| > 1, activating the multi-positive advantage.
    """
    N = len(img_embs)
    sim = (img_embs @ txt_embs.T) / temperature  # (N, N)

    # Build positive mask — vectorised (can handle N up to ~1024)
    keys = list(concept_keys)
    pos_mask = torch.tensor(
        [[keys[i] == keys[j] for j in range(N)] for i in range(N)],
        dtype=torch.float32, device=img_embs.device,
    )  # (N, N), diagonal always 1

    # IMAGE -> TEXT direction
    n_pos_i2t = pos_mask.sum(dim=1)              # (N,), always >= 1
    sim_pos_avg_i2t = (sim * pos_mask).sum(dim=1) / n_pos_i2t  # (N,)
    log_denom_i2t   = torch.logsumexp(sim, dim=1)           # (N,), includes self
    loss_i2t = (-sim_pos_avg_i2t + log_denom_i2t).mean()

    if bidirectional:
        # TEXT -> IMAGE direction (transpose similarity matrix)
        n_pos_t2i = pos_mask.sum(dim=0)              # (N,), positives per text
        sim_pos_avg_t2i = (sim.T * pos_mask.T).sum(dim=1) / n_pos_t2i  # (N,)
        log_denom_t2i   = torch.logsumexp(sim.T, dim=1)
        loss_t2i = (-sim_pos_avg_t2i + log_denom_t2i).mean()

        # Average both directions (like CLIP)
        loss = (loss_i2t + loss_t2i) / 2
    else:
        # Unidirectional (original SHARP)
        loss = loss_i2t

    # Log co-positive statistics every 100 calls for monitoring
    if not hasattr(multi_positive_infonce, '_call_count'):
        multi_positive_infonce._call_count = 0
    multi_positive_infonce._call_count += 1

    if multi_positive_infonce._call_count % 100 == 0:
        avg_copositives = n_pos_i2t.float().mean().item() - 1  # subtract self
        max_copositives = n_pos_i2t.max().item() - 1
        pct_with_copositives = ((n_pos_i2t > 1).sum().item() / N) * 100
        direction_str = "i<->t (bi)" if bidirectional else "i->t (uni)"
        print(f"\n   [MP-InfoNCE stats] Direction: {direction_str}, Batch size: {N}, "
              f"Avg co-positives: {avg_copositives:.2f}, "
              f"Max: {max_copositives}, "
              f"% with co-pos: {pct_with_copositives:.1f}%")

    return loss


# ─────────────────────────────────────────────────────────────────────────────
# Tokenisation helpers
# ─────────────────────────────────────────────────────────────────────────────

def build_vocab_from_texts(texts, vocab_size=10000):
    from collections import Counter
    counts = Counter(w for t in texts for w in t.lower().split())
    vocab = {'<PAD>': 0, '<UNK>': 1}
    for w, _ in counts.most_common(vocab_size - 2):
        vocab[w] = len(vocab)
    return vocab


def tokenize_text(text, vocab, max_len=30):
    words = text.lower().split()
    idxs  = [vocab.get(w, vocab['<UNK>']) for w in words[:max_len]]
    idxs += [0] * (max_len - len(idxs))
    return torch.tensor(idxs, dtype=torch.long)


# ─────────────────────────────────────────────────────────────────────────────
# Official MIMIC-CXR split + subject-id guard
# ─────────────────────────────────────────────────────────────────────────────

def load_official_split(split_csv_gz):
    """Returns: study_to_split {int -> str}, study_to_subject {int -> int}."""
    with gzip.open(split_csv_gz, 'rt') as f:
        df = pd.read_csv(f)
    return (
        dict(zip(df['study_id'].astype(int), df['split'])),
        dict(zip(df['study_id'].astype(int), df['subject_id'].astype(int))),
    )


def partition_scene_files(scene_files, study_to_split, study_to_subject):
    """
    Partition scene_files into train / validate / test using official split.
    Verifies subject_id disjointness across all three splits.
    """
    buckets  = {'train': [], 'validate': [], 'test': []}
    subj_per = defaultdict(set)
    skipped  = 0

    for sf in scene_files:
        stem = Path(sf).stem.split('.')[0]  # e.g. "s50301465"
        try:
            sid = int(stem[1:])
        except ValueError:
            skipped += 1
            continue

        split = study_to_split.get(sid)
        subj  = study_to_subject.get(sid)
        if split is None or subj is None:
            skipped += 1
            continue

        buckets[split].append(sf)
        subj_per[split].add(subj)

    tr, va, te = subj_per['train'], subj_per['validate'], subj_per['test']

    print(f"\n{'─'*55}")
    print(f"  Official MIMIC-CXR split")
    print(f"  Train     : {len(buckets['train']):>7,} files  "
          f"{len(tr):>6,} subjects")
    print(f"  Validate  : {len(buckets['validate']):>7,} files  "
          f"{len(va):>6,} subjects")
    print(f"  Test      : {len(buckets['test']):>7,} files  "
          f"{len(te):>6,} subjects")
    print(f"  Skipped   : {skipped:>7,} (study_id not in CSV)")

    overlap_tv = tr & va
    overlap_tt = tr & te
    overlap_vt = va & te
    if overlap_tv or overlap_tt or overlap_vt:
        if overlap_tv:
            print(f"  WARNING: {len(overlap_tv)} subjects shared train/val!")
        if overlap_tt:
            print(f"  WARNING: {len(overlap_tt)} subjects shared train/test!")
        if overlap_vt:
            print(f"  WARNING: {len(overlap_vt)} subjects shared val/test!")
    else:
        print(f"  Subject-id disjointness: VERIFIED across all splits")
    print(f"{'─'*55}")

    return buckets['train'], buckets['validate'], buckets['test']


# ─────────────────────────────────────────────────────────────────────────────
# Pair extraction (pos + neg)
# ─────────────────────────────────────────────────────────────────────────────

# Generic neg phrases that carry little discriminative signal
GENERIC_NEG = {
    "no acute cardiopulmonary abnormality",
    "no acute cardiopulmonary disease",
    "no acute cardiopulmonary process",
    "no acute pulmonary disease",
    "no acute disease",
    "lungs clear",
    "clear lungs",
}


def extract_pairs(scene, image_dir, rng=None, generic_neg_cap=0.10,
                  no_polarity=False):
    """
    Extract (image_path, bbox, phrase, concept_key) from a scene-graph JSON.

    concept_key = (region, entity, polarity)  [or (region, entity, "any") if no_polarity]
      region   = first localization_reference_id (or "unknown")
      entity   = obs["name"]
      polarity = "pos" or "neg"

    generic_neg_cap: if not None, caps generic neg phrases to at most
    this fraction of total neg pairs in the file (applied when rng is set).
    """
    pairs  = []
    image_dir = Path(image_dir)

    patient_id = scene.get("patient_id", "")
    study_id   = scene.get("study_id", "")
    if not patient_id or not study_id:
        return pairs

    p_num    = patient_id[1:] if patient_id.startswith("p") else patient_id
    p_prefix = f"p{p_num[:2]}"

    pos_pairs, neg_specific, neg_generic = [], [], []

    for obs in scene.get("observations", {}).values():
        polarity = obs.get("positiveness", "")
        if polarity not in ("pos", "neg"):
            continue

        entity   = obs.get("name", "finding")
        severity = obs.get("severity", [])
        if isinstance(severity, list):
            severity = severity[0] if severity else ""

        for image_id, loc_data in obs.get("localization", {}).items():
            bboxes  = loc_data.get("bboxes", [])
            regions = loc_data.get("localization_reference_ids", [])
            if not bboxes:
                continue

            region      = regions[0] if regions else "unknown"
            concept_key = (region, entity, "any" if no_polarity else polarity)

            attrs  = [] if no_polarity else [polarity]
            if severity:
                attrs.append(severity)
            phrase = (f"[{region}] {entity} ({', '.join(attrs)})"
                      if attrs else f"[{region}] {entity}")

            img_path = (image_dir / "files" / p_prefix /
                        patient_id / study_id / f"{image_id}.jpg")
            if not img_path.exists():
                continue

            for bbox in bboxes:
                if not bbox or len(bbox) < 4:
                    continue
                if (bbox[2] - bbox[0]) * (bbox[3] - bbox[1]) < 100:
                    continue
                pair = {
                    'image_path': str(img_path),
                    'bbox': bbox[:4],
                    'phrase': phrase,
                    'concept_key': concept_key,
                }
                if polarity == "pos":
                    pos_pairs.append(pair)
                elif entity.lower() in GENERIC_NEG or phrase.lower() in GENERIC_NEG:
                    neg_generic.append(pair)
                else:
                    neg_specific.append(pair)

    # Apply generic-neg cap
    if generic_neg_cap is not None and rng is not None and neg_specific:
        max_g = max(1, int(len(neg_specific) * generic_neg_cap /
                           max(1e-9, 1.0 - generic_neg_cap)))
        if len(neg_generic) > max_g:
            neg_generic = rng.sample(neg_generic, max_g)

    pairs = pos_pairs + neg_specific + neg_generic
    return pairs


# ─────────────────────────────────────────────────────────────────────────────
# Hard-negative index
# ─────────────────────────────────────────────────────────────────────────────

class HardNegIndex:
    """
    Lightweight index for hard-negative sampling.

      anatomy_hard : same region, different entity
      negation_hard: same (region, entity), opposite polarity

    Built from a sample of train pairs at startup.
    """
    def __init__(self, pairs, rng_seed=42):
        self.rng = random.Random(rng_seed)
        self._by_region = defaultdict(list)          # region -> [pairs]
        self._by_re     = defaultdict(                # (region, entity) -> {pol: [pairs]}
            lambda: defaultdict(list)
        )
        for p in pairs:
            r, e, pol = p['concept_key']
            self._by_region[r].append(p)
            self._by_re[(r, e)][pol].append(p)

        self._regions = list(self._by_region.keys())
        print(f"   HN index: {len(pairs):,} pairs  |  "
              f"{len(self._regions):,} regions  |  "
              f"{len(self._by_re):,} (region,entity) groups")

    def sample_anatomy_hard(self, concept_key):
        """Same region, DIFFERENT entity."""
        region, entity, _ = concept_key
        cands = [p for p in self._by_region.get(region, [])
                 if p['concept_key'][1] != entity]
        return self.rng.choice(cands) if cands else None

    def sample_negation_hard(self, concept_key):
        """Same (region, entity), OPPOSITE polarity."""
        region, entity, polarity = concept_key
        opposite = 'neg' if polarity == 'pos' else 'pos'
        cands = self._by_re.get((region, entity), {}).get(opposite, [])
        return self.rng.choice(cands) if cands else None

    def sample(self, concept_key):
        """Alternate between anatomy-hard and negation-hard."""
        if self.rng.random() < 0.5:
            p = self.sample_anatomy_hard(concept_key)
            return p if p is not None else self.sample_negation_hard(concept_key)
        else:
            p = self.sample_negation_hard(concept_key)
            return p if p is not None else self.sample_anatomy_hard(concept_key)


# ─────────────────────────────────────────────────────────────────────────────
# Dataset
# ─────────────────────────────────────────────────────────────────────────────

class Phase3Dataset(Dataset):
    """
    Streaming dataset. Returns one (image_crop, phrase, concept_key) per item.
    Hard-negative injection is handled in the training loop (main process).
    """
    def __init__(self, scene_files, image_dir, image_size=224,
                 augment=True, seed=42, crop_manifest=None, no_polarity=False):
        self.scene_files    = list(scene_files)
        self.image_dir      = Path(image_dir)
        self.augment        = augment
        self._base_seed     = seed
        self._epoch_seed    = seed
        self.crop_manifest  = crop_manifest
        self.no_polarity    = no_polarity
        if crop_manifest is not None:
            self._virtual_len = len(crop_manifest)
        else:
            self._virtual_len = len(self.scene_files) * 5  # ~5 pairs per file

        if augment:
            self.transform = T.Compose([
                T.RandomResizedCrop(image_size, scale=(0.7, 1.0)),
                T.RandomHorizontalFlip(),
                T.ColorJitter(brightness=0.3, contrast=0.3),
                SafeToTensor(),
                T.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
            ])
        else:
            self.transform = T.Compose([
                T.Resize((image_size, image_size)),
                SafeToTensor(),
                T.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
            ])

    def set_epoch(self, epoch):
        self._epoch_seed = self._base_seed + epoch * 1000

    def __len__(self):
        return self._virtual_len

    def __getitem__(self, idx):
        # ── fast path: pre-cropped cache ──────────────────────────────────────
        if self.crop_manifest is not None:
            entry = self.crop_manifest[idx % len(self.crop_manifest)]
            try:
                img   = Image.open(entry['crop']).convert('RGB')
                img_t = self.transform(img)
            except Exception:
                return None
            ck = entry['concept_key']
            ph = entry['phrase']
            if self.no_polarity:
                ck = (ck[0], ck[1], 'any')
                # strip "(pos)" / "(neg)" / "(pos, severity)" / "(neg, severity)"
                import re as _re
                ph = _re.sub(r'\((?:pos|neg)(?:,\s*[^)]+)?\)', '', ph).strip()
                ph = _re.sub(r'\s{2,}', ' ', ph).rstrip('( ).').strip()
            return {
                'image':       img_t,
                'phrase':      ph,
                'concept_key': ck,
            }
        # ── slow path: load from disk ─────────────────────────────────────────
        rng = random.Random(self._epoch_seed + idx)
        sf  = rng.choice(self.scene_files)
        try:
            with open(sf) as fh:
                scene = json.load(fh)
        except Exception:
            return None

        pairs = extract_pairs(scene, self.image_dir, rng=rng,
                              no_polarity=self.no_polarity)
        if not pairs:
            return None

        pair = rng.choice(pairs)
        try:
            img  = Image.open(pair['image_path']).convert('RGB')
            bbox = pair['bbox']
            img  = img.crop((bbox[0], bbox[1], bbox[2], bbox[3]))
            img_t = self.transform(img)
        except Exception:
            return None

        return {
            'image':       img_t,
            'phrase':      pair['phrase'],
            'concept_key': pair['concept_key'],
        }


def collate_fn(batch):
    batch = [b for b in batch if b is not None]
    if len(batch) < 2:
        return None
    return {
        'images':       torch.stack([b['image'] for b in batch]),
        'phrases':      [b['phrase'] for b in batch],
        'concept_keys': [b['concept_key'] for b in batch],
    }


def paired_collate_fn(batch):
    """
    Collate function with guaranteed same-concept pairs.

    Ensures every batch has at least 1 co-positive pair per concept key.
    Batch size N -> N/2 concept keys, 2 instances each.
    """
    batch = [b for b in batch if b is not None]
    if len(batch) < 4:
        # Fallback to regular if batch too small
        return collate_fn(batch)

    # Group by concept key
    key_to_samples = defaultdict(list)
    for sample in batch:
        key_to_samples[sample['concept_key']].append(sample)

    # Sample pairs: batch_size/2 keys, 2 samples each
    target_size = len(batch)
    num_keys = target_size // 2

    # Select keys that have at least 2 samples
    valid_keys = [k for k, v in key_to_samples.items() if len(v) >= 2]
    if len(valid_keys) < num_keys:
        # Not enough keys with pairs, fall back to regular
        return collate_fn(batch)

    # Sample keys and create paired batch
    selected_keys = random.sample(valid_keys, num_keys)
    paired_batch = []
    for key in selected_keys:
        # Sample 2 instances of this concept key
        pair = random.sample(key_to_samples[key], 2)
        paired_batch.extend(pair)

    return {
        'images':       torch.stack([b['image'] for b in paired_batch]),
        'phrases':      [b['phrase'] for b in paired_batch],
        'concept_keys': [b['concept_key'] for b in paired_batch],
    }


# ─────────────────────────────────────────────────────────────────────────────
# Validation gallery
# ─────────────────────────────────────────────────────────────────────────────

def build_val_gallery(val_files, image_dir, vocab, max_pairs=2000,
                      image_size=224, seed=42, cache_dir=None):
    if cache_dir is not None:
        ci = Path(cache_dir) / 'p3_gallery_imgs.pt'
        ct = Path(cache_dir) / 'p3_gallery_txts.pt'
        if ci.exists() and ct.exists():
            gi = torch.load(ci, weights_only=True)
            gt = torch.load(ct, weights_only=True)
            print(f"   Loaded cached gallery: {len(gi)} pairs")
            return gi, gt

    transform = T.Compose([
        T.Resize((image_size, image_size)),
        SafeToTensor(),
        T.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
    ])
    rng   = random.Random(seed)
    files = list(val_files)
    rng.shuffle(files)

    images, texts = [], []
    subj_count = defaultdict(int)

    for sf in tqdm(files, desc="Building val gallery", leave=False):
        if len(images) >= max_pairs:
            break
        subj = Path(sf).parent.name
        if subj_count[subj] >= 2:
            continue
        try:
            with open(sf) as fh:
                scene = json.load(fh)
        except Exception:
            continue

        pairs = extract_pairs(scene, image_dir, rng=rng)
        pos = [p for p in pairs if p['concept_key'][2] == 'pos']
        pool = pos if pos else pairs
        if not pool:
            continue

        pair = rng.choice(pool)
        try:
            img  = Image.open(pair['image_path']).convert('RGB')
            bbox = pair['bbox']
            img  = img.crop((bbox[0], bbox[1], bbox[2], bbox[3]))
            img_t = transform(img)
        except Exception:
            continue

        images.append(img_t)
        texts.append(tokenize_text(pair['phrase'], vocab))
        subj_count[subj] += 1

    if not images:
        return None, None

    gi = torch.stack(images)
    gt = torch.stack(texts)
    print(f"   Gallery: {len(gi)} pairs from {len(subj_count)} subjects")

    if cache_dir is not None:
        Path(cache_dir).mkdir(parents=True, exist_ok=True)
        torch.save(gi, ci)
        torch.save(gt, ct)
        print(f"   Gallery cached -> {cache_dir}")

    return gi, gt


# ─────────────────────────────────────────────────────────────────────────────
# Recall@K
# ─────────────────────────────────────────────────────────────────────────────

@torch.no_grad()
def compute_recall(model, gallery_imgs, gallery_txts, device='cuda', batch_size=128):
    model.eval()
    img_embs, txt_embs = [], []
    for i in range(0, len(gallery_imgs), batch_size):
        imgs = gallery_imgs[i:i+batch_size].to(device)
        txts = gallery_txts[i:i+batch_size].to(device)
        img_embs.append(model.image_encoder(imgs).cpu())
        txt_embs.append(model.text_encoder(txts).cpu())

    img_embs = torch.cat(img_embs)
    txt_embs = torch.cat(txt_embs)
    sim = img_embs @ txt_embs.T
    N   = len(img_embs)
    gt  = torch.arange(N)

    i2t = (sim.argsort(dim=1, descending=True) == gt.unsqueeze(1)).nonzero()[:, 1]
    t2i = (sim.T.argsort(dim=1, descending=True) == gt.unsqueeze(1)).nonzero()[:, 1]

    return (
        (i2t < 1).sum().item() / N,
        (i2t < 5).sum().item() / N,
        (i2t < 10).sum().item() / N,
        (t2i < 1).sum().item() / N,
        (t2i < 5).sum().item() / N,
        (t2i < 10).sum().item() / N,
    )


# ─────────────────────────────────────────────────────────────────────────────
# LR schedule helpers
# ─────────────────────────────────────────────────────────────────────────────

def lr_at_step(step, warmup_steps, total_steps, base_lr, min_ratio=0.05):
    """Linear warmup + cosine decay."""
    if step < warmup_steps:
        return base_lr * step / max(1, warmup_steps)
    progress = (step - warmup_steps) / max(1, total_steps - warmup_steps)
    cosine   = 0.5 * (1 + math.cos(math.pi * progress))
    return max(base_lr * min_ratio, base_lr * cosine)


def unfreeze_lr_scale(step, unfreeze_step, ramp_steps=500):
    """Cosine ramp for newly unfrozen ViT blocks: 0 -> 1 over ramp_steps."""
    if step < unfreeze_step:
        return 0.0
    delta = step - unfreeze_step
    if delta >= ramp_steps:
        return 1.0
    return 0.5 * (1 - math.cos(math.pi * delta / ramp_steps))


def hard_neg_frac(step, warmup_steps, ramp_end, max_frac):
    """Hard-negative fraction: 0 during warmup, linear ramp to max_frac."""
    if step < warmup_steps:
        return 0.0
    return min(max_frac, max_frac * (step - warmup_steps) /
               max(1, ramp_end - warmup_steps))


# ─────────────────────────────────────────────────────────────────────────────
# Module-level worker init (must be at module scope for spawn multiprocessing)
# ─────────────────────────────────────────────────────────────────────────────

def seed_worker(wid):
    s = torch.initial_seed() % 2**32
    np.random.seed(s); random.seed(s)


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────

def main(args):
    cudnn.benchmark = True
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    print(f"\n{'='*80}")
    print(f"  SHARP LARGE BATCH EXPERIMENT")
    print(f"  Testing multi-positive InfoNCE hypothesis")
    print(f"{'='*80}")
    print(f"Device       : {device}")
    print(f"Batch size   : {args.batch_size}  |  Grad accum: {args.grad_accum}"
          f"  |  Effective batch: {args.batch_size * args.grad_accum}")
    print(f"Loss type    : {'Bidirectional (i<->t)' if args.bidirectional else 'Unidirectional (i->t)'}")
    print(f"Sampling     : {'Paired (guaranteed co-pos)' if args.paired_sampling else 'Random'}")
    print(f"Total steps  : {args.total_steps:,}")
    print(f"Warmup steps : {args.warmup_steps:,}")
    print(f"Eval every   : {args.eval_every:,} steps  (patience={args.patience})")

    if args.bidirectional:
        print(f"\n[OK] BIDIRECTIONAL LOSS: Addresses reviewer concern (fair comparison to symmetric baseline)")
    if args.paired_sampling:
        print(f"\n[*] PAIRED SAMPLING: Tests MP-InfoNCE directly (100% guaranteed co-positives)")
    if args.batch_size >= 256:
        print(f"\n[LARGE BATCH]: {args.batch_size} should provide ~60-70% natural co-positive rate")

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Save experiment config
    with open(output_dir / 'experiment_config.json', 'w') as f:
        json.dump({
            'batch_size': args.batch_size,
            'effective_batch': args.batch_size * args.grad_accum,
            'hypothesis': 'Large batch activates multi-positive InfoNCE',
            'expected_copositives': f'>{args.batch_size // 20} per batch',
            'args': vars(args),
        }, f, indent=2)

    # ── 1. Official split
    print("\nLoading official MIMIC-CXR split...")
    study_to_split, study_to_subject = load_official_split(args.split_csv)

    # ── 2. Scene file list
    print("Loading scene file list...")
    if args.scene_list_path and Path(args.scene_list_path).exists():
        with open(args.scene_list_path) as f:
            scene_files = [l.strip() for l in f if l.strip()]
    else:
        # MIMIC-Ext has both .scene_graph.json and .metadata.json - we only want scene_graph
        scene_files = [str(p) for p in Path(args.scene_dir).rglob("*.scene_graph.json")]
    print(f"   Total: {len(scene_files):,} scene files")

    # ── 3. Partition + subject-id guard
    train_files, val_files, test_files = partition_scene_files(
        scene_files, study_to_split, study_to_subject
    )

    # ── 4. Vocabulary (from train files only, includes neg phrases)
    vocab_path = output_dir / 'p3_vocab.json'
    if vocab_path.exists():
        with open(vocab_path) as f:
            vocab = json.load(f)
        print(f"\nLoaded existing vocab: {len(vocab):,} tokens")
    else:
        print("\nBuilding vocabulary from train files...")
        rng_v   = random.Random(42)
        sample  = rng_v.sample(train_files, min(5000, len(train_files)))
        texts   = []
        for sf in tqdm(sample, desc="Vocab sampling", leave=False):
            try:
                with open(sf) as fh:
                    scene = json.load(fh)
            except Exception:
                continue
            for obs in scene.get("observations", {}).values():
                pol = obs.get("positiveness", "")
                if pol not in ("pos", "neg"):
                    continue
                ent = obs.get("name", "finding")
                sev = obs.get("severity", [])
                if isinstance(sev, list):
                    sev = sev[0] if sev else ""
                attrs = [pol] + ([sev] if sev else [])
                for _, loc in obs.get("localization", {}).items():
                    for r in loc.get("localization_reference_ids", []):
                        texts.append(f"[{r}] {ent} ({', '.join(attrs)})")
        vocab = build_vocab_from_texts(texts, args.vocab_size)
        with open(vocab_path, 'w') as f:
            json.dump(vocab, f, indent=2)
        print(f"   Vocab size: {len(vocab):,}  -> {vocab_path}")

    # ── 5. Hard-negative index
    hn_index = None
    if args.hard_neg_max_frac > 0:
        print("\nBuilding hard-negative index (20k train files sample)...")
        rng_hn  = random.Random(42)
        sample  = rng_hn.sample(train_files, min(20000, len(train_files)))
        hn_pairs = []
        for sf in tqdm(sample, desc="Indexing", leave=False):
            try:
                with open(sf) as fh:
                    scene = json.load(fh)
            except Exception:
                continue
            hn_pairs.extend(extract_pairs(scene, args.image_dir))
        hn_index  = HardNegIndex(hn_pairs, rng_seed=42)
        hn_transform = T.Compose([
            T.RandomResizedCrop(args.image_size, scale=(0.7, 1.0)),
            T.RandomHorizontalFlip(),
            T.ColorJitter(brightness=0.3, contrast=0.3),
            SafeToTensor(),
            T.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
        ])

    # ── 6. Dataset + DataLoader
    crop_manifest = None
    if args.crop_cache_dir:
        mpath = Path(args.crop_cache_dir) / "manifest.pkl"
        if mpath.exists():
            print(f"\nLoading crop cache manifest: {mpath} ...")
            with open(str(mpath), 'rb') as fh:
                crop_manifest = pickle.load(fh)
            print(f"  {len(crop_manifest):,} pre-cropped pairs (fast path)")
        else:
            print(f"WARNING: Crop cache not found at {mpath}, using on-the-fly cropping (slow)")

    # Build concept_key -> crop_paths lookup for fast HN injection
    hn_crop_lookup = defaultdict(list)
    if crop_manifest is not None:
        for entry in crop_manifest:
            ck = entry['concept_key']
            if args.no_polarity:
                ck = (ck[0], ck[1], 'any')
            hn_crop_lookup[ck].append(entry['crop'])
        print(f"  HN crop lookup: {len(hn_crop_lookup):,} concept keys cached")

    train_ds = Phase3Dataset(
        train_files, args.image_dir,
        image_size=args.image_size, augment=True, seed=42,
        crop_manifest=crop_manifest,
        no_polarity=args.no_polarity,
    )
    if crop_manifest is None:
        train_ds._virtual_len = len(train_files) * 5

    # Choose collate function based on paired_sampling flag
    collate_function = paired_collate_fn if args.paired_sampling else collate_fn
    if args.paired_sampling:
        print(f"\n[*] Using PAIRED SAMPLING - guaranteed co-positives!")
        print(f"   Each batch will have {args.batch_size // 2} concept keys, 2 instances each")

    g = torch.Generator(); g.manual_seed(42)
    loader = DataLoader(
        train_ds, batch_size=args.batch_size, shuffle=True,
        num_workers=args.num_workers, collate_fn=collate_function,
        persistent_workers=(args.num_workers > 0),
        prefetch_factor=2 if args.num_workers > 0 else None,
        pin_memory=True, drop_last=True,
        worker_init_fn=seed_worker, generator=g,
    )
    print(f"\nTrain: {len(train_files):,} files  |  "
          f"{len(loader):,} batches/epoch  |  "
          f"Val: {len(val_files):,} files  |  Test: {len(test_files):,} files")

    # ── 7. Model — start from ImageNet weights
    print("\nCreating model (ImageNet ViT-B/16)...")
    model = GraphTextCLIP(embed_dim=256, temperature=0.07).to(device)
    model.image_encoder.freeze_all()
    frozen_n = sum(p.numel() for p in model.image_encoder.vit.parameters()
                   if not p.requires_grad)
    trainable_n = sum(p.numel() for p in model.parameters() if p.requires_grad)
    print(f"   ViT frozen: {frozen_n:,} params")
    print(f"   Trainable (proj + text encoder): {trainable_n:,} params")

    # ── 8. Optimizer
    head_params = (list(model.image_encoder.projection.parameters()) +
                   list(model.text_encoder.parameters()))
    optimizer = AdamW(
        [{'params': head_params, 'lr': args.lr, 'name': 'heads'}],
        weight_decay=0.01,
    )
    scaler = GradScaler()
    vit_unfrozen = False
    resume_step  = 0

    # ── 8b. Resume from checkpoint (optional or auto-resume)
    resume_from = getattr(args, 'resume_from', None)

    # Auto-resume: if no explicit checkpoint given, check for p3_last.pt
    if resume_from is None:
        auto_ckpt = output_dir / 'p3_last.pt'
        if auto_ckpt.exists():
            resume_from = auto_ckpt
            print(f"\n⚡ Auto-resuming from: {auto_ckpt}")

    if resume_from:
        if not resume_from == output_dir / 'p3_last.pt':
            print(f"\nResuming from: {resume_from}")
        ckpt_r = torch.load(resume_from, map_location=device)
        resume_step = ckpt_r['step']
        if resume_step >= args.unfreeze_step:
            model.image_encoder.unfreeze_last_n_blocks(args.unfreeze_n_blocks)
            vit_params = [p for p in model.image_encoder.vit.parameters()
                          if p.requires_grad]
            optimizer.add_param_group(
                {'params': vit_params, 'lr': 0.0, 'name': 'vit_blocks'})
            vit_unfrozen = True
        model.load_state_dict(ckpt_r['model_state_dict'])
        optimizer.load_state_dict(ckpt_r['optimizer_state_dict'])

        # Load scaler state if available (for mixed precision training)
        if 'scaler_state_dict' in ckpt_r:
            scaler.load_state_dict(ckpt_r['scaler_state_dict'])
            print(f"   [OK] Restored GradScaler state")

        del ckpt_r
        print(f"   Resumed at step {resume_step:,}  "
              f"(will train to {args.total_steps:,})")

    # ── 9. Val gallery
    print("\nBuilding validation gallery...")
    gallery_imgs, gallery_txts = build_val_gallery(
        val_files, args.image_dir, vocab,
        max_pairs=args.val_gallery_size,
        image_size=args.image_size,
        cache_dir=output_dir,
    )
    if gallery_imgs is None:
        raise RuntimeError("Could not build val gallery — check val_files / image_dir")
    print(f"   Gallery: {len(gallery_imgs)} pairs")

    # ── 10. Training loop
    best_r1        = -1.0
    patience_ctr   = 0
    global_step    = resume_step
    accum_steps    = 0
    window_loss    = 0.0
    window_count   = 0
    history        = []
    epoch_num      = 0

    # If resuming, restore history
    if resume_step > 0:
        hist_path = output_dir / 'p3_history.json'
        if hist_path.exists():
            with open(hist_path) as fh:
                history = json.load(fh)
            history = [e for e in history if e['step'] <= resume_step]
        best_r1 = max((e['i2t_r1'] for e in history), default=-1.0)
        print(f"   Restored history: {len(history)} evals, "
              f"best R@1={best_r1*100:.2f}%")

    print(f"\nStarting Phase 3 training...")
    print(f"  {args.total_steps:,} steps  |  eval every {args.eval_every:,}  |  "
          f"patience {args.patience}")

    optimizer.zero_grad()
    data_iter = iter(loader)
    pbar = tqdm(total=args.total_steps, initial=global_step,
                desc="SHARP-LargeBatch", unit="step")

    while global_step < args.total_steps:

        # Get next batch
        try:
            batch = next(data_iter)
        except StopIteration:
            epoch_num += 1
            train_ds.set_epoch(epoch_num)
            data_iter = iter(loader)
            batch = next(data_iter)

        if batch is None:
            continue

        # ── Unfreeze last 4 ViT blocks at step 5k
        if not vit_unfrozen and global_step >= args.unfreeze_step:
            print(f"\n[step {global_step}] Unfreezing last "
                  f"{args.unfreeze_n_blocks} ViT blocks...")
            model.image_encoder.unfreeze_last_n_blocks(args.unfreeze_n_blocks)
            vit_params = [p for p in model.image_encoder.vit.parameters()
                          if p.requires_grad]
            optimizer.add_param_group({
                'params': vit_params,
                'lr': 0.0,
                'name': 'vit_blocks',
            })
            vit_unfrozen = True

        # ── Hard-negative injection (curriculum)
        hn_frac = hard_neg_frac(
            global_step, args.warmup_steps,
            args.hard_neg_ramp_end, args.hard_neg_max_frac,
        )
        if hn_index is not None and hn_frac > 0 and random.random() < hn_frac:
            n_inject = max(1, int(args.batch_size * 0.25))
            inj_imgs, inj_phrases, inj_keys = [], [], []
            for key in batch['concept_keys'][:n_inject]:
                hn = hn_index.sample(key)
                if hn is None:
                    continue
                try:
                    cached = hn_crop_lookup.get(hn['concept_key'])
                    if not cached:
                        continue
                    img = Image.open(random.choice(cached)).convert('RGB')
                    inj_imgs.append(hn_transform(img))
                    inj_phrases.append(hn['phrase'])
                    inj_keys.append(hn['concept_key'])
                except Exception:
                    continue
            if inj_imgs:
                batch['images']  = torch.cat(
                    [batch['images'], torch.stack(inj_imgs)], dim=0)
                batch['phrases'].extend(inj_phrases)
                batch['concept_keys'].extend(inj_keys)

        # ── Forward + loss
        images = batch['images'].to(device)
        txt_t  = torch.stack(
            [tokenize_text(p, vocab) for p in batch['phrases']]
        ).to(device)

        with autocast():
            img_embs = model.image_encoder(images)
            txt_embs = model.text_encoder(txt_t)
            loss     = multi_positive_infonce(
                img_embs, txt_embs, batch['concept_keys'], model.temperature,
                bidirectional=args.bidirectional
            )
            loss_scaled = loss / args.grad_accum

        scaler.scale(loss_scaled).backward()
        window_loss  += loss.item()
        window_count += 1
        accum_steps  += 1

        if accum_steps < args.grad_accum:
            continue

        # ── Gradient step
        scaler.unscale_(optimizer)
        torch.nn.utils.clip_grad_norm_(
            [p for g in optimizer.param_groups for p in g['params']], 1.0
        )
        scaler.step(optimizer)
        scaler.update()
        optimizer.zero_grad()
        accum_steps  = 0
        global_step += 1

        # ── Update LR
        base_lr = lr_at_step(global_step, args.warmup_steps,
                             args.total_steps, args.lr)
        scale   = unfreeze_lr_scale(global_step, args.unfreeze_step,
                                    args.unfreeze_ramp_steps)
        for pg in optimizer.param_groups:
            if pg.get('name') == 'vit_blocks':
                pg['lr'] = base_lr * args.vit_lr_scale * scale
            else:
                pg['lr'] = base_lr

        # ── Periodic checkpoint (every save_every steps, for crash recovery)
        if global_step % args.save_every == 0 and global_step > 0:
            periodic_ckpt = {
                'step':              global_step,
                'model_state_dict':  model.state_dict(),
                'optimizer_state_dict': optimizer.state_dict(),
                'scaler_state_dict': scaler.state_dict(),
                'vocab_path':        str(vocab_path),
                'batch_size':        args.batch_size,
                'effective_batch':   args.batch_size * args.grad_accum,
                'args':              vars(args),
            }
            torch.save(periodic_ckpt, output_dir / 'p3_last.pt')
            if args.save_every != args.eval_every:
                print(f"   💾 Checkpoint saved (step {global_step:,})")

        # ── Eval
        if global_step % args.eval_every == 0 or global_step == args.total_steps:
            avg_loss = window_loss / max(1, window_count)
            window_loss = window_count = 0

            i2t_r1, i2t_r5, i2t_r10, t2i_r1, t2i_r5, t2i_r10 = compute_recall(
                model, gallery_imgs, gallery_txts, device=device,
            )
            model.train()

            print(f"\n[step {global_step:>6}]  loss={avg_loss:.4f}  "
                  f"I->T R@1={i2t_r1*100:.2f}%  R@5={i2t_r5*100:.2f}%  "
                  f"T->I R@1={t2i_r1*100:.2f}%  "
                  f"hard_frac={hn_frac:.2f}  lr={base_lr:.2e}")

            ckpt = {
                'step':              global_step,
                'model_state_dict':  model.state_dict(),
                'optimizer_state_dict': optimizer.state_dict(),
                'scaler_state_dict': scaler.state_dict(),  # For mixed precision resume
                'avg_loss':          avg_loss,
                'i2t_r1': i2t_r1, 'i2t_r5': i2t_r5,  'i2t_r10': i2t_r10,
                't2i_r1': t2i_r1, 't2i_r5': t2i_r5,  't2i_r10': t2i_r10,
                'vocab_path':        str(vocab_path),
                'batch_size':        args.batch_size,
                'effective_batch':   args.batch_size * args.grad_accum,
                'args':              vars(args),
            }
            torch.save(ckpt, output_dir / 'p3_last.pt')

            history.append({'step': global_step, 'loss': avg_loss,
                            'i2t_r1': i2t_r1, 'i2t_r5': i2t_r5,
                            't2i_r1': t2i_r1, 't2i_r5': t2i_r5})
            with open(output_dir / 'p3_history.json', 'w') as fh:
                json.dump(history, fh, indent=2)

            if i2t_r1 > best_r1:
                best_r1      = i2t_r1
                patience_ctr = 0
                torch.save(ckpt, output_dir / 'p3_best.pt')
                print(f"   [NEW BEST] New best  I->T R@1={i2t_r1*100:.2f}%  "
                      f"-> {output_dir}/p3_best.pt")
            else:
                patience_ctr += 1
                print(f"   No improvement  ({patience_ctr}/{args.patience})")
                if patience_ctr >= args.patience:
                    print(f"\nEarly stopping at step {global_step} "
                          f"(no R@1 gain for {args.patience} evals = "
                          f"{args.patience * args.eval_every:,} steps)")
                    break

        pbar.update(1)
        pbar.set_postfix({
            'loss': f'{window_loss/max(1,window_count):.3f}',
            'R@1':  f'{best_r1*100:.1f}%',
            'hn':   f'{hn_frac:.2f}',
        })

    pbar.close()

    # ── Final summary
    print(f"\n{'='*80}")
    print(f"SHARP LARGE BATCH EXPERIMENT COMPLETE")
    print(f"Batch size: {args.batch_size} (effective: {args.batch_size * args.grad_accum})")
    print(f"Best I->T R@1: {best_r1*100:.2f}%")
    print(f"Best checkpoint: {output_dir}/p3_best.pt")
    print(f"{'='*80}")

    if history:
        print(f"\n{'Step':>8}  {'Loss':>7}  {'I->T R@1':>8}  "
              f"{'I->T R@5':>8}  {'T->I R@1':>8}  {'T->I R@5':>8}")
        for row in history:
            mark = " *" if row['i2t_r1'] == best_r1 else ""
            print(f"{row['step']:>8}  {row['loss']:>7.4f}  "
                  f"{row['i2t_r1']*100:>7.2f}%  {row['i2t_r5']*100:>7.2f}%  "
                  f"{row['t2i_r1']*100:>7.2f}%  {row['t2i_r5']*100:>7.2f}%{mark}")


# ─────────────────────────────────────────────────────────────────────────────
# Args
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    p = argparse.ArgumentParser(description="SHARP Phase 3 - Large Batch Experiment")

    # Paths (configurable for local/remote setup)
    p.add_argument("--scene_dir",      default="./scene_data",
                   help="Path to MIMIC-Ext scene_data directory")
    p.add_argument("--image_dir",      default="./mimic-cxr-jpg",
                   help="Path to MIMIC-CXR image directory")
    p.add_argument("--split_csv",      default="./mimic-cxr-2.0.0-split.csv.gz",
                   help="Path to official MIMIC-CXR split CSV")
    p.add_argument("--scene_list_path",default="./scene_files.txt",
                   help="Optional: pre-built list of scene file paths")
    p.add_argument("--output_dir",     default="./sharp_experiments/batch_512",
                   help="Output directory for checkpoints and logs")

    # Training
    p.add_argument("--total_steps",    type=int,   default=100_000)
    p.add_argument("--warmup_steps",   type=int,   default=5_000)
    p.add_argument("--eval_every",     type=int,   default=2_000)
    p.add_argument("--save_every",     type=int,   default=1_000,
                   help="Save checkpoint every N steps (for crash recovery)")
    p.add_argument("--patience",       type=int,   default=10,
                   help="Early stop after patience×eval_every steps without R@1 gain")
    p.add_argument("--batch_size",     type=int,   default=512,
                   help="LARGE BATCH EXPERIMENT: default 512 (vs original 32)")
    p.add_argument("--grad_accum",     type=int,   default=1,
                   help="Effective batch = batch_size × grad_accum")
    p.add_argument("--lr",             type=float, default=1e-4)
    p.add_argument("--image_size",     type=int,   default=224)
    p.add_argument("--num_workers",    type=int,   default=4)
    p.add_argument("--vocab_size",     type=int,   default=10000)
    p.add_argument("--val_gallery_size", type=int, default=2000)

    # NEW: Bidirectional loss and paired sampling
    p.add_argument("--bidirectional",  action="store_true",
                   help="Use bidirectional InfoNCE (i<->t, like CLIP). Addresses reviewer concern.")
    p.add_argument("--paired_sampling", action="store_true",
                   help="Guarantee same-concept pairs in each batch (tests MP-InfoNCE directly)")

    # Unfreeze schedule
    p.add_argument("--unfreeze_step",      type=int,   default=5_000)
    p.add_argument("--unfreeze_n_blocks",  type=int,   default=4)
    p.add_argument("--unfreeze_ramp_steps",type=int,   default=500)
    p.add_argument("--vit_lr_scale",       type=float, default=0.1)

    # Resume
    p.add_argument("--resume_from", default=None,
                   help="Path to checkpoint to resume from")

    # Crop cache
    p.add_argument("--crop_cache_dir", default="",
                   help="Dir with manifest.pkl for pre-cropped images (optional)")

    # Hard negatives
    p.add_argument("--hard_neg_max_frac",  type=float, default=0.6)
    p.add_argument("--hard_neg_ramp_end",  type=int,   default=30_000)
    p.add_argument("--no_polarity",        action="store_true",
                   help="Ablation: strip polarity from concept key")

    args = p.parse_args()
    main(args)
