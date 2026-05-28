@echo off
REM ====================================================================
REM Exp #4 v2a — FAIR matched-epoch large-batch comparison
REM
REM Purpose: Answer reviewer R3's question "does large batch help?" with
REM a comparison that controls for data exposure. This run matches the
REM baseline's 3.2M samples seen (6,250 steps × 512 batch).
REM
REM Linear LR scaling per Goyal et al. 2017 (1e-4 × 16 = 1.6e-3).
REM Warmup = 5%% of total, matching baseline's fraction.
REM Cosine schedule terminates at 6,250 — model gets full decay phase.
REM
REM This is DIFFERENT from Exp #4 v2 (PROPER), which is the scaling-
REM ceiling run (100k steps, 51.2M samples seen). v2a answers the fair
REM matched-epoch question; v2 answers the ceiling question.
REM
REM All other hyperparameters are byte-identical to Exp #1 baseline.
REM ====================================================================

echo ============================================================================
echo Exp #4 v2a: FAIR Matched-Epoch Large-Batch Comparison
echo ============================================================================
echo.
echo Configuration:
echo   - Batch size: 512 (16x larger than baseline)
echo   - Total steps: 6,250 (matches baseline's 3.2M samples seen)
echo   - Learning rate: 1.6e-3 (linear scaling: 1e-4 x 16)
echo   - Warmup: 312 steps (5%% of total, same fraction as baseline)
echo   - LR schedule: cosine decay terminates at step 6,250
echo   - Sampling: SHARP multi-positive with hard negatives (same as v2b)
echo.
echo Why this is FAIR:
echo   - Same data exposure as baseline (3.2M samples)
echo   - Same optimization trajectory length (relative to batch size)
echo   - Linear LR scaling per Goyal et al. 2017
echo   - Tests OUR method at large batch, not vanilla contrastive
echo.
echo Expected runtime: ~45-60 minutes
echo Output: D:\experiments\exp4_v2a_matched_epochs\
echo.
pause

REM Create output directory
mkdir D:\experiments\exp4_v2a_matched_epochs 2>nul

REM Run training with FAIR matched-epoch configuration
python train_sharp_large_batch.py ^
  --scene_dir D:\datasets\mimic-ext-cxr-qba\scene_graphs\scene_data ^
  --image_dir D:\datasets\mimic-cxr-jpg ^
  --split_csv D:\datasets\mimic-cxr-jpg\mimic-cxr-2.0.0-split.csv.gz ^
  --output_dir D:\experiments\exp4_v2a_matched_epochs ^
  --batch_size 512 ^
  --lr 0.0016 ^
  --total_steps 6250 ^
  --warmup_steps 312 ^
  --eval_every 625 ^
  --save_every 625 ^
  --bidirectional ^
  --hard_neg_max_frac 0.6 ^
  --hard_neg_ramp_end 1875 ^
  --unfreeze_step 312 ^
  --unfreeze_ramp_steps 31 ^
  --patience 10 ^
  --num_workers 4 ^
  --vocab_size 10000 ^
  --image_size 224 ^
  --grad_accum 1 ^
  --vit_lr_scale 0.1 ^
  --val_gallery_size 2000 ^
  > D:\experiments\exp4_v2a_matched_epochs\training.log 2>&1

echo.
echo ============================================================================
echo Training complete!
echo ============================================================================
echo.
echo Results saved to: D:\experiments\exp4_v2a_matched_epochs\
echo.
echo Next step: Compare R@1 to baseline (6.61%%) to answer R3's fair-test question
echo.
pause
