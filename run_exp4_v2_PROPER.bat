@echo off
REM Exp #4 v2: Large Batch - PROPERLY CONFIGURED
REM
REM This fixes BOTH issues with the "FAIR" run:
REM   1. Full 100k training steps (not 6.25k)
REM   2. Scaled LR: 1.6e-3 (not 1e-4)
REM
REM Based on Goyal et al. 2017 "Accurate, Large Minibatch SGD":
REM   - Linear LR scaling: 1e-4 × (512/32) = 1.6e-3
REM   - Warmup: 5k steps (same as baseline)
REM   - Total steps: 100k (same optimization trajectory as baseline)
REM
REM Expected runtime: ~18-20 hours
REM Total samples: 51.2M (16x more than baseline, but proper convergence)

echo ============================================================================
echo Exp #4 v2: Large Batch - PROPERLY CONFIGURED
echo ============================================================================
echo.
echo Configuration:
echo   - Batch size: 512 (16x larger than baseline)
echo   - Total steps: 100,000 (FULL training, not truncated)
echo   - Learning rate: 1.6e-3 (scaled from 1e-4 by batch ratio)
echo   - Warmup: 5,000 steps
echo   - Hard negatives: 0.6 max fraction
echo   - Bidirectional loss: YES
echo.
echo Why this is proper:
echo   - Goyal et al. 2017: Large batches need LR scaling + full schedule
echo   - Previous "FAIR" run had 2 issues: truncated steps AND unscaled LR
echo   - This tests R3's hypothesis correctly
echo.
echo Expected runtime: ~18-20 hours
echo Output: D:\experiments\exp4_v2_large_batch_PROPER\
echo.
pause

REM Create output directory
mkdir D:\experiments\exp4_v2_large_batch_PROPER 2>nul

REM Run training with PROPER configuration
python train_sharp_large_batch.py ^
  --scene_dir D:\datasets\mimic-ext-cxr-qba\scene_graphs\scene_data ^
  --image_dir D:\datasets\mimic-cxr-jpg ^
  --split_csv D:\datasets\mimic-cxr-jpg\mimic-cxr-2.0.0-split.csv.gz ^
  --output_dir D:\experiments\exp4_v2_large_batch_PROPER ^
  --batch_size 512 ^
  --lr 0.0016 ^
  --total_steps 100000 ^
  --warmup_steps 5000 ^
  --eval_every 2000 ^
  --save_every 1000 ^
  --bidirectional ^
  --hard_neg_max_frac 0.6 ^
  > D:\experiments\exp4_v2_large_batch_PROPER\training.log 2>&1

echo.
echo ============================================================================
echo Training complete!
echo ============================================================================
echo.
echo Results saved to: D:\experiments\exp4_v2_large_batch_PROPER\
echo.
echo Next step: Compare R@1 to baseline (6.61%) to answer R3's question
echo.
pause
