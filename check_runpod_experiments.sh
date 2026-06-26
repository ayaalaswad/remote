#!/bin/bash
# Script to verify bidirectional usage in RunPod ablation experiments
# Run this on the RunPod server or wherever /workspace/experiments/ is mounted

echo "======================================================================"
echo "Checking Bidirectional Usage in Ablation Experiments"
echo "======================================================================"
echo ""

check_experiment() {
    local exp_name=$1
    local exp_path=$2

    echo "----------------------------------------------------------------------"
    echo "Checking: $exp_name"
    echo "Path: $exp_path"
    echo "----------------------------------------------------------------------"

    if [ ! -d "$exp_path" ]; then
        echo "❌ Directory not found!"
        echo ""
        return 1
    fi

    # Check experiment_config.json
    if [ -f "$exp_path/experiment_config.json" ]; then
        echo "Config file found: experiment_config.json"

        # Check for bidirectional flag
        if grep -q "bidirectional" "$exp_path/experiment_config.json"; then
            BIDIR=$(grep "bidirectional" "$exp_path/experiment_config.json")
            echo "  $BIDIR"
        else
            echo "  ⚠️  No 'bidirectional' key found (implies unidirectional)"
        fi
    else
        echo "⚠️  No experiment_config.json found"
    fi

    # Check training log
    if [ -f "$exp_path/training.log" ]; then
        echo "Training log found: training.log"

        if grep -q "Loss type" "$exp_path/training.log"; then
            LOSS_TYPE=$(grep "Loss type" "$exp_path/training.log" | head -1)
            echo "  $LOSS_TYPE"
        fi

        if grep -qi "bidirectional" "$exp_path/training.log"; then
            echo "  ✓ 'Bidirectional' mentioned in log"
        fi
    else
        echo "⚠️  No training.log found"
    fi

    # Check checkpoint names for R@1
    echo "Checkpoints found:"
    if ls "$exp_path"/*.pt >/dev/null 2>&1; then
        for ckpt in "$exp_path"/*.pt; do
            CKPT_NAME=$(basename "$ckpt")
            # Try to extract R@1 from filename (format: 0.0702_23_42.pt)
            if [[ $CKPT_NAME =~ ^([0-9]\.[0-9]+) ]]; then
                R1="${BASH_REMATCH[1]}"
                R1_PCT=$(echo "$R1 * 100" | bc)
                echo "  $CKPT_NAME → R@1 ≈ ${R1_PCT}%"
            else
                echo "  $CKPT_NAME"
            fi
        done
    else
        echo "  ⚠️  No .pt checkpoints found"
    fi

    echo ""
}

# Check all ablation experiments
check_experiment "Ablation A (Sym. InfoNCE)" "/workspace/experiments/vit_ablation_A"
check_experiment "Ablation B (MP-InfoNCE)" "/workspace/experiments/vit_ablation_B"
check_experiment "Ablation C (+curriculum)" "/workspace/experiments/vit_ablation_C"
check_experiment "Phase3 / SHARP (full)" "/workspace/experiments/vit_phase3"

echo "======================================================================"
echo "Summary"
echo "======================================================================"
echo ""
echo "EXPECTED if paper is CORRECT:"
echo "  - Ablation B should show bidirectional=false or no key"
echo "  - Ablation B should have checkpoint with R@1 ≈ 7.02%"
echo "  - There should be a SECOND Ablation B directory with bidirectional=true and R@1 ≈ 6.61%"
echo ""
echo "EXPECTED if experiments.md is CORRECT:"
echo "  - All ablations should show bidirectional=true"
echo "  - No experiment should have R@1 ≈ 7.02%"
echo ""
echo "======================================================================"
echo "Alternative Locations to Check (if /workspace/ doesn't exist)"
echo "======================================================================"
echo ""
echo "Try these locations:"
echo "  - D:\\experiments\\vit_ablation_*"
echo "  - C:\\Users\\aya.alaswad\\experiments\\vit_ablation_*"
echo "  - ~/experiments/vit_ablation_*"
echo ""
echo "Or search for them:"
echo "  find / -name 'vit_ablation_B' -type d 2>/dev/null"
echo "  find / -name 'p3_best.pt' 2>/dev/null | grep ablation"
echo ""
