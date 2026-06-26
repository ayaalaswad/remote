# Stage 1 Checkpoint Locations - Found!

## ✅ Complete Mapping from lrrg Stage 2 Configs

I found the Stage 2 ablation configs in the **lrrg repository**. Each config specifies which Stage 1 checkpoint it uses.

---

## 📂 Stage 1 Checkpoint Paths

| Paper Name | Stage 2 Config | Stage 1 Checkpoint Path | Location to Check |
|------------|----------------|-------------------------|-------------------|
| **ImageNet-FT** (baseline) | `single_tf_vit_normal.yaml` | `null` (uses ImageNet weights) | N/A - no Stage 1 |
| **Ablation (A)** Sym. InfoNCE | `single_tf_vit_ablation_A.yaml` | `/workspace/experiments/vit_ablation_A/ablA_best.pt` | ✓ Check this |
| **Ablation (B)** MP-InfoNCE | `single_tf_vit_ablation_B.yaml` | `/workspace/experiments/vit_ablation_B/p3_best.pt` | ✓ Check this |
| **Ablation (C)** +curriculum | `single_tf_vit_ablation_C.yaml` | `/workspace/experiments/vit_ablation_C/p3_best.pt` | ✓ Check this |
| **Phase3 / SHARP** (full) | `single_tf_vit_phase3_finetuned.yaml` | `/workspace/experiments/vit_phase3/p3_best.pt` | ✓ Check this |

---

## 🎯 What You Need to Check (On Remote Desktop)

To determine if ablations used bidirectional or unidirectional loss:

### Step 1: Go to Each Stage 1 Checkpoint Directory

```bash
# Ablation A (Sym. InfoNCE)
cd /workspace/experiments/vit_ablation_A
cat experiment_config.json | grep bidirectional
cat training.log | grep "Bidirectional\|Loss type"

# Ablation B (MP-InfoNCE)
cd /workspace/experiments/vit_ablation_B
cat experiment_config.json | grep bidirectional
cat training.log | grep "Bidirectional\|Loss type"

# Ablation C (+curriculum)
cd /workspace/experiments/vit_ablation_C
cat experiment_config.json | grep bidirectional
cat training.log | grep "Bidirectional\|Loss type"

# Phase3 / SHARP (full method)
cd /workspace/experiments/vit_phase3
cat experiment_config.json | grep bidirectional
cat training.log | grep "Bidirectional\|Loss type"
```

---

## 🔍 What to Look For

### In `experiment_config.json`:

**If bidirectional:**
```json
{
  "bidirectional": true,
  ...
}
```

**If unidirectional:**
```json
{
  "bidirectional": false,
  ...
}
```

**Or no key at all** (means unidirectional - from before the flag was added)

### In `training.log`:

**If bidirectional:**
```
Loss type    : Bidirectional (i<->t)
[OK] BIDIRECTIONAL LOSS: Addresses reviewer concern
```

**If unidirectional:**
```
Loss type    : Unidirectional (i->t)
```

**Or no mention** (means unidirectional - from old code)

---

## 📊 Expected Results Based on Paper Claims

Your paper says:

| Ablation | Paper Claim | Expected in Config |
|----------|-------------|-------------------|
| **(A) Sym. InfoNCE** | Bidirectional (by definition) | `"bidirectional": true` |
| **(B) MP-InfoNCE** | Unidirectional | `"bidirectional": false` or no key |
| **(C) +curriculum** | Unidirectional | `"bidirectional": false` or no key |
| **SHARP (full)** | Unidirectional | `"bidirectional": false` or no key |

**But your experiments.md says:** "Bidirectional loss: Yes (all experiments)"

---

## 🚨 Critical Test

**Check Ablation B specifically** - the paper claims you "re-ran" it with bidirectional and got R@1 = 6.61% vs 7.02% unidirectional.

**If you only have ONE Ablation B directory:**
- And it has `"bidirectional": true` → Paper is wrong, it was always bidirectional
- And it has `"bidirectional": false` or no key → Paper might be correct, but where's the bidirectional re-run?

**If you have TWO Ablation B directories:**
- One with `false` (R@1 = 7.02%)
- One with `true` (R@1 = 6.61%)
- → Paper is correct!

---

## 🔧 Quick One-Liner to Check All

```bash
# Check all ablation configs at once
for dir in /workspace/experiments/vit_ablation_{A,B,C} /workspace/experiments/vit_phase3; do
    echo "=== $(basename $dir) ==="
    if [ -f "$dir/experiment_config.json" ]; then
        grep "bidirectional" "$dir/experiment_config.json" || echo "No bidirectional key found"
    else
        echo "No experiment_config.json found"
    fi
    echo ""
done
```

---

## 📁 Alternative Locations (If /workspace/ doesn't exist)

If you're on Windows remote desktop, try:

```batch
REM Check if these directories exist
dir /workspace\experiments\vit_ablation_A
dir D:\experiments\vit_ablation_A
dir C:\Users\aya.alaswad\experiments\vit_ablation_A

REM Or search for them
dir vit_ablation_* /s /b
dir p3_best.pt /s /b
```

---

## 💡 Why This Matters

**This will definitively answer:**

1. ✅ Were ablations (A), (B), (C) run with bidirectional or unidirectional?
2. ✅ Was the "bidirectional re-run" of ablation (B) actually done?
3. ✅ Does SHARP (Phase3) use bidirectional or unidirectional?
4. ✅ Is your paper Section 2.2 ("unidirectional") correct or incorrect?

---

## 🎯 Most Important Check

**Priority 1: Check Ablation B**

```bash
cd /workspace/experiments/vit_ablation_B
cat experiment_config.json
```

**Look for:**
- R@1 value in checkpoint name: Does it match 7.02% or 6.61%?
- Bidirectional flag: `true` or `false`?
- Training date: Before or after May 17, 2026 (when bidirectional was added)?

---

## 📝 What to Report Back

After checking, tell me:

1. **Does `/workspace/experiments/vit_ablation_B/` exist?**
2. **What does `experiment_config.json` say for bidirectional?**
3. **What's the checkpoint filename?** (e.g., `0.0702_23_42.pt` or `0.0661_23_42.pt`)
4. **What does training.log say?** (search for "Loss type" or "Bidirectional")

This will give us the definitive answer!

---

**Last updated:** 2026-06-26
**Source:** lrrg repository Stage 2 configs
**Status:** Ready to verify on remote desktop
