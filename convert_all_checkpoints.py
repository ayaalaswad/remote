"""
Convert all SHARP checkpoints from HuggingFace ViT to timm ViT format
"""
import torch
import os

def convert_hf_to_timm(source_path, target_path):
    """Convert HuggingFace ViT checkpoint to timm format"""
    print(f"Loading checkpoint: {source_path}")
    checkpoint = torch.load(source_path, map_location='cpu')

    # Extract model state dict from checkpoint
    if 'model_state_dict' in checkpoint:
        state_dict = checkpoint['model_state_dict']
        print(f"  ✓ Extracted model_state_dict")
    else:
        state_dict = checkpoint
        print(f"  ⚠ Using checkpoint directly (no model_state_dict key)")

    new_state_dict = {}

    # 1. Embedding layers
    new_state_dict['cls_token'] = state_dict['image_encoder.vit.embeddings.cls_token']
    new_state_dict['pos_embed'] = state_dict['image_encoder.vit.embeddings.position_embeddings']
    new_state_dict['patch_embed.proj.weight'] = state_dict['image_encoder.vit.embeddings.patch_embeddings.projection.weight']
    new_state_dict['patch_embed.proj.bias'] = state_dict['image_encoder.vit.embeddings.patch_embeddings.projection.bias']

    # 2. Transformer blocks (12 layers for ViT-B)
    for i in range(12):
        hf_prefix = f'image_encoder.vit.encoder.layer.{i}'
        timm_prefix = f'blocks.{i}'

        # Layer norm
        new_state_dict[f'{timm_prefix}.norm1.weight'] = state_dict[f'{hf_prefix}.layernorm_before.weight']
        new_state_dict[f'{timm_prefix}.norm1.bias'] = state_dict[f'{hf_prefix}.layernorm_before.bias']
        new_state_dict[f'{timm_prefix}.norm2.weight'] = state_dict[f'{hf_prefix}.layernorm_after.weight']
        new_state_dict[f'{timm_prefix}.norm2.bias'] = state_dict[f'{hf_prefix}.layernorm_after.bias']

        # Attention: Concatenate Q/K/V
        qkv_weight = torch.cat([
            state_dict[f'{hf_prefix}.attention.attention.query.weight'],
            state_dict[f'{hf_prefix}.attention.attention.key.weight'],
            state_dict[f'{hf_prefix}.attention.attention.value.weight']
        ], dim=0)
        qkv_bias = torch.cat([
            state_dict[f'{hf_prefix}.attention.attention.query.bias'],
            state_dict[f'{hf_prefix}.attention.attention.key.bias'],
            state_dict[f'{hf_prefix}.attention.attention.value.bias']
        ], dim=0)
        new_state_dict[f'{timm_prefix}.attn.qkv.weight'] = qkv_weight
        new_state_dict[f'{timm_prefix}.attn.qkv.bias'] = qkv_bias

        # Attention projection
        new_state_dict[f'{timm_prefix}.attn.proj.weight'] = state_dict[f'{hf_prefix}.attention.output.dense.weight']
        new_state_dict[f'{timm_prefix}.attn.proj.bias'] = state_dict[f'{hf_prefix}.attention.output.dense.bias']

        # MLP
        new_state_dict[f'{timm_prefix}.mlp.fc1.weight'] = state_dict[f'{hf_prefix}.intermediate.dense.weight']
        new_state_dict[f'{timm_prefix}.mlp.fc1.bias'] = state_dict[f'{hf_prefix}.intermediate.dense.bias']
        new_state_dict[f'{timm_prefix}.mlp.fc2.weight'] = state_dict[f'{hf_prefix}.output.dense.weight']
        new_state_dict[f'{timm_prefix}.mlp.fc2.bias'] = state_dict[f'{hf_prefix}.output.dense.bias']

    # 3. Final layer norm
    new_state_dict['norm.weight'] = state_dict['image_encoder.vit.layernorm.weight']
    new_state_dict['norm.bias'] = state_dict['image_encoder.vit.layernorm.bias']

    print(f"Saving converted checkpoint: {target_path}")
    torch.save(new_state_dict, target_path)
    print(f"✓ Conversion complete")

    return new_state_dict

# Convert all relevant checkpoints
checkpoints_to_convert = [
    {
        'source': 'D:/experiments/exp1_baseline/p3_best.pt',
        'target': 'D:/experiments/exp1_baseline/p3_best_timm.pt',
        'name': 'Exp #1 Baseline'
    },
    {
        'source': 'D:/experiments/exp3_full_sharp/p3_best.pt',
        'target': 'D:/experiments/exp3_full_sharp/p3_best_timm.pt',
        'name': 'Exp #3 Full SHARP'
    },
    {
        'source': 'D:/experiments/exp4_v2a_matched_epochs/p3_best.pt',
        'target': 'D:/experiments/exp4_v2a_matched_epochs/p3_best_timm.pt',
        'name': 'Exp #4 v2a (Best R@1)'
    }
]

print("="*70)
print("Converting SHARP Checkpoints: HuggingFace → timm")
print("="*70)
print()

for ckpt in checkpoints_to_convert:
    print(f"\n{ckpt['name']}:")
    print("-" * 70)

    if os.path.exists(ckpt['target']):
        print(f"⚠ Target already exists: {ckpt['target']}")
        print("  Skipping conversion...")
        continue

    if not os.path.exists(ckpt['source']):
        print(f"❌ Source not found: {ckpt['source']}")
        continue

    try:
        convert_hf_to_timm(ckpt['source'], ckpt['target'])
    except Exception as e:
        print(f"❌ Conversion failed: {e}")
        continue

print()
print("="*70)
print("All conversions complete!")
print("="*70)
print()
print("Converted checkpoints:")
for ckpt in checkpoints_to_convert:
    if os.path.exists(ckpt['target']):
        size_mb = os.path.getsize(ckpt['target']) / (1024*1024)
        print(f"  ✓ {ckpt['name']}: {size_mb:.1f} MB")
