"""
SHARP model wrapper for BenchX integration.

Usage:
    model = SHARPForBenchX(checkpoint_path='/path/to/sharp_checkpoint.pth')
    features = model(pixel_values)   # [B, 768] — ready for BenchX's classification head

Integration into BenchX:
    1. Place this file in BenchX's models/ directory.
    2. Mirror how an existing model (e.g. MGCA) is registered in BenchX's
       model factory / __init__.py, and do the same for SHARPForBenchX.
    3. Create configs/classification/<dataset>/sharp.yml by copying
       an existing ViT-B config (e.g. mgca.yml) and setting model: sharp
       (or whatever key you register below).
    4. Run: python bin/train.py configs/classification/<dataset>/sharp.yml
"""

import torch
import torch.nn as nn
from transformers import ViTModel


class SHARPForBenchX(nn.Module):
    """
    Loads SHARP's pretrained image encoder (ViT-B/16) and returns the
    768-dim CLS token (pre-projection) for BenchX downstream fine-tuning.

    Checkpoint structure expected:
        image_encoder.vit.*    — the ViT weights  (loaded here)
        image_encoder.projection.*  — dropped (not needed for classification)
        text_encoder.*         — dropped (not needed for classification)

    FEATURE DIM: 768  (ViT-B/16 CLS token, before the 768→256 projection)
    """

    FEATURE_DIM = 768

    def __init__(self, checkpoint_path: str, inspect_keys: bool = True):
        """
        Args:
            checkpoint_path: path to SHARP .pth / .ckpt file
            inspect_keys:    print a sample of checkpoint keys on first run
                             (set False once confirmed working)
        """
        super().__init__()
        self.feature_dim = self.FEATURE_DIM

        # ── ViT-B/16 architecture (weights will be overridden below) ──────
        self.vit = ViTModel.from_pretrained(
            "google/vit-base-patch16-224-in21k",
            add_pooling_layer=False,  # we extract CLS manually
        )

        self._load_checkpoint(checkpoint_path, inspect_keys)

    # ──────────────────────────────────────────────────────────────────────
    def _load_checkpoint(self, checkpoint_path: str, inspect_keys: bool):
        # ── 1. load raw checkpoint ────────────────────────────────────────
        raw = torch.load(checkpoint_path, map_location="cpu")
        if isinstance(raw, dict):
            state_dict = raw.get("state_dict", raw.get("model", raw))
        else:
            raise ValueError("Unexpected checkpoint format.")

        # ── 2. INSPECT KEYS — run once, then set inspect_keys=False ───────
        if inspect_keys:
            img_keys = [k for k in state_dict if k.startswith("image_encoder")]
            print("=" * 60)
            print(f"Found {len(img_keys)} image_encoder.* keys. Sample (first 8):")
            for k in img_keys[:8]:
                print(f"  {k}  →  {tuple(state_dict[k].shape)}")
            print()
            print("Expected patterns:")
            print("  Pattern A: image_encoder.vit.vit.embeddings.*  (ViTModel wrapper)")
            print("  Pattern B: image_encoder.vit.embeddings.*      (bare ViT encoder)")
            print("See comments in _build_vit_state_dict() to select the right one.")
            print("=" * 60)

        # ── 3. remap keys so they match HuggingFace ViTModel ──────────────
        vit_sd = self._build_vit_state_dict(state_dict)

        missing, unexpected = self.vit.load_state_dict(vit_sd, strict=False)

        loaded = len(vit_sd)
        print(f"\nSHARP → ViTModel: loaded {loaded} keys.")
        if missing:
            print(f"  Missing  ({len(missing)}): {missing[:4]}")
        if unexpected:
            print(f"  Unexpected ({len(unexpected)}): {unexpected[:4]}")
        # A few missing/unexpected keys (pooler, position_ids) is normal.
        print("Done. If missing count is small (< 5) this is fine.\n")

    def _build_vit_state_dict(self, state_dict: dict) -> dict:
        """
        Remap SHARP's image_encoder.vit.* keys → HuggingFace ViTModel keys.

        HuggingFace ViTModel state-dict keys look like:
            vit.embeddings.cls_token
            vit.encoder.layer.0.attention.attention.query.weight
            pooler.dense.weight      ← we can ignore this one

        ── HOW TO CHOOSE THE RIGHT PATTERN ──────────────────────────────
        Run with inspect_keys=True first and look at the printed keys.

        Pattern A  →  your keys start with  image_encoder.vit.vit.
            (SHARP stores the full ViTModel as image_encoder.vit,
             so there is an inner 'vit.' prefix)
            → strip 'image_encoder.vit.'  →  gives 'vit.embeddings.*'  ✓

        Pattern B  →  your keys start with  image_encoder.vit.embeddings.
            (SHARP stores only the ViT encoder, no ViTModel wrapper)
            → strip 'image_encoder.vit.'  →  gives 'embeddings.*'
            → need to prepend 'vit.' to match ViTModel
        ─────────────────────────────────────────────────────────────────
        """
        PREFIX = "image_encoder.vit."          # prefix to strip from SHARP keys
        remapped = {}

        for k, v in state_dict.items():
            if not k.startswith(PREFIX):
                continue
            stripped = k[len(PREFIX):]         # remove PREFIX

            # ── Pattern A: stripped is already 'vit.embeddings.*' ────────
            if stripped.startswith("vit.") or stripped.startswith("pooler."):
                remapped[stripped] = v

            # ── Pattern B: stripped is 'embeddings.*' — prepend 'vit.' ───
            else:
                remapped["vit." + stripped] = v

        if not remapped:
            raise ValueError(
                f"No keys matched prefix '{PREFIX}'. "
                "Check checkpoint key names with inspect_keys=True."
            )
        return remapped

    # ──────────────────────────────────────────────────────────────────────
    def forward(self, pixel_values: torch.Tensor) -> torch.Tensor:
        """
        Args:
            pixel_values: FloatTensor  [B, 3, 224, 224]
        Returns:
            features:     FloatTensor  [B, 768]  — CLS token, pre-projection
        """
        out = self.vit(pixel_values=pixel_values)
        cls_token = out.last_hidden_state[:, 0, :]   # [B, 768]
        return cls_token


# ── Quick sanity check ────────────────────────────────────────────────────
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python sharp_benchx_model.py /path/to/sharp.pth")
        sys.exit(1)

    ckpt = sys.argv[1]
    print(f"Loading checkpoint: {ckpt}")
    model = SHARPForBenchX(ckpt, inspect_keys=True)
    model.eval()

    dummy = torch.randn(2, 3, 224, 224)
    with torch.no_grad():
        feats = model(dummy)
    print(f"\nOutput shape: {feats.shape}")   # expect [2, 768]
    assert feats.shape == (2, 768), "Unexpected output shape!"
    print("Sanity check passed — output is [B, 768] ✓")
