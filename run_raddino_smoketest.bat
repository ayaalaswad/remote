@echo off
REM ============================================================================
REM SHARP RadDINO Smoke Test (100 steps)
REM ============================================================================
REM
REM Purpose: Verify RadDINO integration before full training
REM Duration: ~5-10 minutes
REM
REM Checks:
REM   1. RadDINO model loads from cache
REM   2. Forward pass works (768d output -> 256d embedding)
REM   3. Loss computation succeeds
REM   4. Gradient updates work
REM   5. Checkpoint saving works
REM ============================================================================

echo.
echo ========================================
echo   SHARP RadDINO Smoke Test (100 steps)
echo ========================================
echo.
echo This will run 100 training steps to verify:
echo   - RadDINO loads correctly
echo   - Training loop works
echo   - No dimension mismatches
echo.
echo Duration: ~5-10 minutes
echo.
pause

cd C:\Users\aya.alaswad\remote\MyReasearch

python train_sharp_raddino_v2.py ^
  --encoder_type raddino ^
  --hard_neg_max_frac 0.0 ^
  --batch_size 32 ^
  --grad_accum 1 ^
  --lr 1e-4 ^
  --total_steps 100 ^
  --warmup_steps 50 ^
  --eval_every 100 ^
  --save_every 100 ^
  --patience 10 ^
  --unfreeze_step 999999 ^
  --image_size 224 ^
  --num_workers 2 ^
  --vocab_size 5000 ^
  --val_gallery_size 500 ^
  --scene_dir C:\Users\aya.alaswad\remote\scene_data ^
  --image_dir C:\Users\aya.alaswad\remote\mimic-cxr-jpg ^
  --split_csv C:\Users\aya.alaswad\remote\mimic-cxr-2.0.0-split.csv.gz ^
  --scene_list_path C:\Users\aya.alaswad\remote\scene_files.txt ^
  --crop_cache_dir C:\Users\aya.alaswad\remote\crop_cache ^
  --output_dir D:\experiments\raddino_smoketest

echo.
echo ========================================
echo   Smoke Test Complete
echo ========================================
echo.
if exist D:\experiments\raddino_smoketest\p3_best.pt (
    echo [OK] Checkpoint saved successfully
    echo [OK] RadDINO integration working
    echo.
    echo Ready to run full experiment:
    echo   run_raddino_exp3_hardneg.bat
) else (
    echo [ERROR] Checkpoint not found!
    echo Check error messages above.
)
echo.
pause
