"""
Custom model loader for SHARP encoder in BenchX

This modifies BenchX to load SHARP's pretrained ViT encoder directly.
"""

import torch
import torch.nn as nn
from transformers import ViTModel


class SHARPEncoder(nn.Module):
    """
    SHARP's ViT-B/16 encoder loaded from checkpoint
    Compatible with BenchX's ImageClassifier
    """
    def __init__(self, sharp_checkpoint_path):
        super().__init__()

        print(f"Loading SHARP encoder from: {sharp_checkpoint_path}")

        # Load ViT-B/16 architecture
        self.vit = ViTModel.from_pretrained('google/vit-base-patch16-224')

        # Load SHARP's pretrained weights
        ckpt = torch.load(sharp_checkpoint_path, map_location='cpu')

        if 'model_state_dict' not in ckpt:
            raise ValueError("Checkpoint missing 'model_state_dict'")

        state_dict = ckpt['model_state_dict']

        # Extract ViT weights (not projection head)
        vit_weights = {}
        for key, value in state_dict.items():
            # Look for image_encoder.vit.* keys
            if 'image_encoder.vit.' in key:
                # Remove prefix: image_encoder.vit.encoder.layer.0.xxx -> encoder.layer.0.xxx
                new_key = key.replace('image_encoder.vit.', '')
                vit_weights[new_key] = value
            elif 'img_encoder.vit.' in key:
                new_key = key.replace('img_encoder.vit.', '')
                vit_weights[new_key] = value

        print(f"Found {len(vit_weights)} ViT parameters in SHARP checkpoint")

        # Load weights into ViT
        missing, unexpected = self.vit.load_state_dict(vit_weights, strict=False)

        if missing:
            print(f"Warning: {len(missing)} missing keys (using pretrained ViT values)")
        if unexpected:
            print(f"Warning: {len(unexpected)} unexpected keys (ignored)")

        print(f"✓ SHARP encoder loaded successfully (step {ckpt.get('step', 'unknown')})")

    def forward(self, x):
        """
        Args:
            x: Images (B, 3, 224, 224)

        Returns:
            features: ViT features (B, 768) - CLS token
        """
        outputs = self.vit(pixel_values=x)
        # Return CLS token (first token)
        return outputs.last_hidden_state[:, 0]  # (B, 768)


def create_sharp_model_for_benchx(sharp_checkpoint_path, num_classes=2):
    """
    Create complete model for BenchX: SHARP encoder + classifier

    Args:
        sharp_checkpoint_path: Path to SHARP's p3_best.pt
        num_classes: Number of output classes

    Returns:
        model: Complete model ready for BenchX training
    """
    from models.classifier import Classifier

    # Create SHARP encoder
    encoder = SHARPEncoder(sharp_checkpoint_path)

    # Create classifier head (768 -> num_classes)
    classifier = Classifier(
        in_features=768,  # ViT-B/16 output dim
        num_classes=num_classes,
        use_fc_norm=True,
        trunc_init=True,
        dropout=0.0
    )

    # Combine into sequential model
    model = nn.Sequential(encoder, classifier)

    return model


if __name__ == "__main__":
    # Test loading
    checkpoint_path = r"D:\experiments\exp3_full_sharp\p3_best.pt"

    print("="*80)
    print("Testing SHARP Encoder Loading")
    print("="*80)
    print()

    # Create encoder
    encoder = SHARPEncoder(checkpoint_path)

    # Test forward pass
    dummy_input = torch.randn(2, 3, 224, 224)
    print()
    print("Testing forward pass...")
    print(f"Input shape: {dummy_input.shape}")

    with torch.no_grad():
        features = encoder(dummy_input)

    print(f"Output shape: {features.shape}")
    print(f"Expected: (2, 768)")
    print()

    if features.shape == (2, 768):
        print("✓ SUCCESS! SHARP encoder working correctly")
    else:
        print("✗ ERROR: Unexpected output shape")

    print("="*80)
