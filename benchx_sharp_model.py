#!/usr/bin/env python3
"""
SHARP model wrapper for BenchX integration.

This file should be placed in: BenchX/models/sharp.py

Usage in BenchX configs:
    model:
      name: sharp
      checkpoint: D:/experiments/exp3_hardneg/p3_best.pt
      backbone: vit_base
"""

import torch
import torch.nn as nn
import torch.nn.functional as F


class ImageEncoderViT(nn.Module):
    """SHARP's image encoder (ViT-B/16)."""
    def __init__(self, embedding_dim=256):
        super().__init__()
        from transformers import ViTModel

        # Load ViT backbone (will load from SHARP checkpoint later)
        self.vit = ViTModel.from_pretrained('google/vit-base-patch16-224')

        # Projection head
        self.projection = nn.Sequential(
            nn.Linear(768, 512),
            nn.ReLU(),
            nn.Linear(512, embedding_dim),
        )

    def forward(self, x):
        out = self.vit(pixel_values=x)
        return F.normalize(self.projection(out.last_hidden_state[:, 0]), dim=1)


class SHARP(nn.Module):
    """
    SHARP model for BenchX downstream classification.

    Args:
        checkpoint_path: Path to SHARP's pretrained checkpoint (p3_best.pt)
        num_classes: Number of classes for downstream task
        freeze_backbone: Whether to freeze encoder during fine-tuning
    """
    def __init__(self, checkpoint_path, num_classes=1, freeze_backbone=False):
        super().__init__()

        print(f"Loading SHARP checkpoint: {checkpoint_path}")

        # Load SHARP's pretrained encoder
        self.encoder = ImageEncoderViT(embedding_dim=256)

        # Load checkpoint
        ckpt = torch.load(checkpoint_path, map_location='cpu')

        # Extract image encoder state dict
        if 'model_state_dict' in ckpt:
            state_dict = ckpt['model_state_dict']
            # Filter for image_encoder weights only
            encoder_state = {
                k.replace('image_encoder.', ''): v
                for k, v in state_dict.items()
                if k.startswith('image_encoder.')
            }
            self.encoder.load_state_dict(encoder_state, strict=False)
            print(f"   Loaded SHARP encoder from step {ckpt.get('step', 'unknown')}")
        else:
            raise ValueError("Checkpoint missing 'model_state_dict'")

        # Freeze backbone if requested
        if freeze_backbone:
            for param in self.encoder.parameters():
                param.requires_grad = False
            print("   Backbone frozen (linear probe mode)")

        # Classification head (fine-tuning layer)
        self.classifier = nn.Linear(256, num_classes)

        print(f"   Classification head: 256 -> {num_classes}")

    def forward(self, x):
        """
        Args:
            x: Input images (B, 3, 224, 224)

        Returns:
            logits: Classification logits (B, num_classes)
        """
        # Get embeddings from SHARP encoder
        embeddings = self.encoder(x)  # (B, 256)

        # Classification
        logits = self.classifier(embeddings)  # (B, num_classes)

        return logits

    def get_embeddings(self, x):
        """Extract embeddings without classification head."""
        return self.encoder(x)


def build_sharp_model(config):
    """
    Build SHARP model from BenchX config.

    Expected config format:
        model:
          name: sharp
          checkpoint: D:/experiments/exp3_hardneg/p3_best.pt
          num_classes: 2  # or 14 for multi-label
          freeze_backbone: false
    """
    checkpoint_path = config['model']['checkpoint']
    num_classes = config['model'].get('num_classes', 2)
    freeze_backbone = config['model'].get('freeze_backbone', False)

    model = SHARP(
        checkpoint_path=checkpoint_path,
        num_classes=num_classes,
        freeze_backbone=freeze_backbone
    )

    return model


if __name__ == "__main__":
    # Test SHARP model loading
    checkpoint_path = "D:/experiments/exp3_hardneg/p3_best.pt"

    print("Testing SHARP model...")
    model = SHARP(checkpoint_path, num_classes=2)

    # Test forward pass
    dummy_input = torch.randn(2, 3, 224, 224)
    logits = model(dummy_input)

    print(f"Input shape: {dummy_input.shape}")
    print(f"Output shape: {logits.shape}")
    print("✓ SHARP model test passed!")
