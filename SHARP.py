"""
SHARP model for BenchX framework.
Place this file at: BenchX/unifier/models/vilmedic/SHARP.py
"""

import torch
import torch.nn as nn
from transformers import ViTModel


class SHARP(nn.Module):
    """
    SHARP Vision-Language Model wrapper for BenchX.

    Returns 768-dim CLS token features from pretrained ViT-B/16 encoder.
    Compatible with BenchX's ImageClassifier downstream model.
    """

    def __init__(self, checkpoint_path: str):
        super().__init__()
        self.feature_dim = 768

        # Load ViT-B/16 architecture
        self.vit = ViTModel.from_pretrained(
            "google/vit-base-patch16-224-in21k",
            add_pooling_layer=False,
        )

        # Load SHARP's pretrained weights
        self._load_sharp_checkpoint(checkpoint_path)

    def _load_sharp_checkpoint(self, checkpoint_path: str):
        """Load SHARP checkpoint and extract image encoder weights."""
        raw = torch.load(checkpoint_path, map_location="cpu")
        state_dict = raw.get("model_state_dict", raw.get("state_dict", raw))

        # Extract and remap image_encoder.vit.* keys to match HuggingFace ViTModel
        PREFIX = "image_encoder.vit."
        remapped = {}

        for k, v in state_dict.items():
            if not k.startswith(PREFIX):
                continue
            stripped = k[len(PREFIX):]

            # Pattern A: already has vit. prefix
            if stripped.startswith("vit.") or stripped.startswith("pooler."):
                remapped[stripped] = v
            # Pattern B: needs vit. prefix
            else:
                remapped["vit." + stripped] = v

        if not remapped:
            raise ValueError(f"No keys matched prefix '{PREFIX}' in checkpoint")

        # Load into ViT model
        missing, unexpected = self.vit.load_state_dict(remapped, strict=False)
        print(f"SHARP loaded: {len(remapped)} keys, {len(missing)} missing (OK if < 5)")

    def forward(self, pixel_values: torch.Tensor) -> torch.Tensor:
        """
        Args:
            pixel_values: [B, 3, 224, 224]
        Returns:
            features: [B, 768] CLS token
        """
        out = self.vit(pixel_values=pixel_values)
        return out.last_hidden_state[:, 0, :]  # [B, 768] CLS token
