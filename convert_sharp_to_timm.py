"""
Convert SHARP checkpoint from HuggingFace ViT format to timm ViT format

Key differences:
1. Simple renames (embeddings.cls_token → cls_token)
2. Structural merge: Q/K/V separate matrices → single QKV concatenated matrix
"""
import torch
import os

# Paths
sharp_checkpoint = r"D:\experiments\exp3_full_sharp\p3_best.pt"
output_checkpoint = r"D:\experiments\exp3_full_sharp\p3_best_timm.pt"

print("="*80)
print("SHARP → timm ViT Converter")
print("="*80)
print()

print(f"Loading: {sharp_checkpoint}")
ckpt = torch.load(sharp_checkpoint, map_location='cpu')
state_dict = ckpt['model_state_dict']

print(f"Loaded {len(state_dict)} keys")
print()

# New timm-compatible state dict
new_state_dict = {}

# Count layers (ViT-B has 12 transformer blocks)
num_layers = 12

print("Converting checkpoint...")
print()

# ============================================================================
# 1. Simple Renames
# ============================================================================

print("[1/3] Simple key renames...")

# Embeddings
if 'image_encoder.vit.embeddings.cls_token' in state_dict:
    new_state_dict['cls_token'] = state_dict['image_encoder.vit.embeddings.cls_token']
    print("  ✓ cls_token")

if 'image_encoder.vit.embeddings.position_embeddings' in state_dict:
    new_state_dict['pos_embed'] = state_dict['image_encoder.vit.embeddings.position_embeddings']
    print("  ✓ pos_embed")

# Patch embeddings
if 'image_encoder.vit.embeddings.patch_embeddings.projection.weight' in state_dict:
    new_state_dict['patch_embed.proj.weight'] = state_dict['image_encoder.vit.embeddings.patch_embeddings.projection.weight']
    print("  ✓ patch_embed.proj.weight")

if 'image_encoder.vit.embeddings.patch_embeddings.projection.bias' in state_dict:
    new_state_dict['patch_embed.proj.bias'] = state_dict['image_encoder.vit.embeddings.patch_embeddings.projection.bias']
    print("  ✓ patch_embed.proj.bias")

print()

# ============================================================================
# 2. Layer Normalization (simple renames)
# ============================================================================

print("[2/3] Layer normalization...")

for i in range(num_layers):
    hf_prefix = f'image_encoder.vit.encoder.layer.{i}'
    timm_prefix = f'blocks.{i}'

    # LayerNorm before attention (norm1)
    if f'{hf_prefix}.layernorm_before.weight' in state_dict:
        new_state_dict[f'{timm_prefix}.norm1.weight'] = state_dict[f'{hf_prefix}.layernorm_before.weight']
        new_state_dict[f'{timm_prefix}.norm1.bias'] = state_dict[f'{hf_prefix}.layernorm_before.bias']

    # LayerNorm after attention (norm2)
    if f'{hf_prefix}.layernorm_after.weight' in state_dict:
        new_state_dict[f'{timm_prefix}.norm2.weight'] = state_dict[f'{hf_prefix}.layernorm_after.weight']
        new_state_dict[f'{timm_prefix}.norm2.bias'] = state_dict[f'{hf_prefix}.layernorm_after.bias']

    # MLP
    if f'{hf_prefix}.intermediate.dense.weight' in state_dict:
        new_state_dict[f'{timm_prefix}.mlp.fc1.weight'] = state_dict[f'{hf_prefix}.intermediate.dense.weight']
        new_state_dict[f'{timm_prefix}.mlp.fc1.bias'] = state_dict[f'{hf_prefix}.intermediate.dense.bias']

    if f'{hf_prefix}.output.dense.weight' in state_dict:
        new_state_dict[f'{timm_prefix}.mlp.fc2.weight'] = state_dict[f'{hf_prefix}.output.dense.weight']
        new_state_dict[f'{timm_prefix}.mlp.fc2.bias'] = state_dict[f'{hf_prefix}.output.dense.bias']

    # Attention projection (output)
    if f'{hf_prefix}.attention.output.dense.weight' in state_dict:
        new_state_dict[f'{timm_prefix}.attn.proj.weight'] = state_dict[f'{hf_prefix}.attention.output.dense.weight']
        new_state_dict[f'{timm_prefix}.attn.proj.bias'] = state_dict[f'{hf_prefix}.attention.output.dense.bias']

print(f"  ✓ Converted {num_layers} layers")
print()

# ============================================================================
# 3. Q/K/V Concatenation (structural merge)
# ============================================================================

print("[3/3] Concatenating Q/K/V matrices...")

for i in range(num_layers):
    hf_attn = f'image_encoder.vit.encoder.layer.{i}.attention.attention'
    timm_attn = f'blocks.{i}.attn'

    # Check if Q/K/V exist
    q_weight_key = f'{hf_attn}.query.weight'
    k_weight_key = f'{hf_attn}.key.weight'
    v_weight_key = f'{hf_attn}.value.weight'

    if all(k in state_dict for k in [q_weight_key, k_weight_key, v_weight_key]):
        # Concatenate weights: [Q; K; V]
        qkv_weight = torch.cat([
            state_dict[q_weight_key],
            state_dict[k_weight_key],
            state_dict[v_weight_key]
        ], dim=0)
        new_state_dict[f'{timm_attn}.qkv.weight'] = qkv_weight

        # Concatenate biases: [Q; K; V]
        qkv_bias = torch.cat([
            state_dict[f'{hf_attn}.query.bias'],
            state_dict[f'{hf_attn}.key.bias'],
            state_dict[f'{hf_attn}.value.bias']
        ], dim=0)
        new_state_dict[f'{timm_attn}.qkv.bias'] = qkv_bias

        print(f"  ✓ Layer {i}: qkv.weight {qkv_weight.shape}, qkv.bias {qkv_bias.shape}")

print()

# ============================================================================
# Final normalization
# ============================================================================

print("[4/4] Final layer normalization...")

if 'image_encoder.vit.layernorm.weight' in state_dict:
    new_state_dict['norm.weight'] = state_dict['image_encoder.vit.layernorm.weight']
    new_state_dict['norm.bias'] = state_dict['image_encoder.vit.layernorm.bias']
    print("  ✓ norm.weight, norm.bias")

print()

# ============================================================================
# Save
# ============================================================================

print("="*80)
print(f"Conversion complete!")
print(f"  Original keys: {len(state_dict)}")
print(f"  Converted keys: {len(new_state_dict)}")
print()

# Verify critical keys exist
critical_keys = ['cls_token', 'pos_embed', 'patch_embed.proj.weight',
                 'blocks.0.attn.qkv.weight', 'blocks.0.norm1.weight',
                 'blocks.11.attn.qkv.weight', 'norm.weight']

print("Verifying critical keys:")
for key in critical_keys:
    if key in new_state_dict:
        print(f"  ✓ {key}: {new_state_dict[key].shape}")
    else:
        print(f"  ✗ {key}: MISSING!")

print()

# Save
print(f"Saving to: {output_checkpoint}")
torch.save(new_state_dict, output_checkpoint)

print()
print("="*80)
print("✅ SUCCESS!")
print("="*80)
print()
print("Update your BenchX config:")
print(f"  cnn:")
print(f"    pretrained: {output_checkpoint}")
print(f"    # No prefix needed!")
print()
