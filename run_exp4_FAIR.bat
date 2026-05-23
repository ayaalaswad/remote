@echo off
REM Exp #4: Large Batch (batch_size=512) - FAIR COMPARISON
REM
REM This is the CORRECTED version with proper step count for fair comparison:
REM   Baseline (Exp #1): batch=32  × 100,000 steps = 3,200,000 samples
REM   Exp #4 (fair):     batch=512 × 6,250 steps   = 3,200,000 samples ✓
REM
REM Expected runtime: ~11 hours (vs 170 hours for the incorrect 100k steps!)

echo ============================================================================
echo Exp #4: Large Batch FAIR COMPARISON
echo ============================================================================
echo.
echo Configuration:
echo   - Batch size: 512 (16x larger than baseline)
echo   - Total steps: 6,250 (FAIR - same total samples as baseline)
echo   - Hard negatives: 0.6 max fraction
echo   - Bidirectional loss: YES
echo.
echo Fair comparison calculation:
echo   Baseline: 32 × 100,000 = 3,200,000 samples
echo   Exp #4:   512 × 6,250  = 3,200,000 samples ✓ EQUAL
echo.
echo Expected runtime: ~11 hours
echo Output: D:\experiments\exp4_large_batch_FAIR\
echo.
pause

REM Create output directory
mkdir D:\experiments\exp4_large_batch_FAIR 2>nul

REM Run training with CORRECTED step count
python train_sharp_large_batch.py ^
  --scene_dir D:\datasets\mimic-ext-cxr-qba\scene_graphs\scene_data ^
  --image_dir D:\datasets\mimic-cxr-jpg ^
  --split_csv D:\datasets\mimic-cxr-jpg\mimic-cxr-2.0.0-split.csv.gz ^
  --output_dir D:\experiments\exp4_large_batch_FAIR ^
  --batch_size 512 ^
  --bidirectional ^
  --hard_neg_max_frac 0.6 ^
  --total_steps 6250 ^
  --eval_every 1250 ^
  --save_every 625 ^
  > D:\experiments\exp4_large_batch_FAIR\training.log 2>&1

echo.
echo ============================================================================
echo Training complete!
echo ============================================================================
echo.
echo Results saved to: D:\experiments\exp4_large_batch_FAIR\
echo.
echo Next steps:
echo   1. Check final R@1: python check_exp4_best.py
echo   2. Proceed to Phase 2 (Stage 2 CXRMate fine-tuning)
echo.
pause
