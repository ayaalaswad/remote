@echo off
REM ============================================================================
REM SHARP RadDINO Exp #3 - Hard Negatives with Domain-Specific Encoder
REM ============================================================================
REM
REM Purpose: Workshop robustness check - prove hard negatives work with RadDINO
REM Comparison: RadDINO+hard_neg vs ImageNet ViT+hard_neg (original Exp #3)
REM
REM Expected: Similar improvement pattern (validates method generalization)
REM ============================================================================

echo.
echo ========================================
echo   SHARP RadDINO Exp #3 (Hard Negatives)
echo ========================================
echo.
echo Encoder:       RadDINO (microsoft/rad-dino)
echo Hard neg:      60%% curriculum (0-%%60 over 5k-30k steps)
echo Batch:         256
echo Output:        D:\experiments\exp_raddino_hardneg
echo.
echo Press Ctrl+C to cancel, or
pause

cd C:\Users\aya.alaswad\remote\MyReasearch

python train_sharp_raddino_v2.py ^
  --encoder_type raddino ^
  --hard_neg_max_frac 0.6 ^
  --hard_neg_ramp_end 30000 ^
  --bidirectional ^
  --batch_size 256 ^
  --grad_accum 1 ^
  --lr 1e-4 ^
  --total_steps 100000 ^
  --warmup_steps 5000 ^
  --eval_every 2000 ^
  --save_every 1000 ^
  --patience 10 ^
  --unfreeze_step 5000 ^
  --unfreeze_n_blocks 4 ^
  --unfreeze_ramp_steps 500 ^
  --vit_lr_scale 0.1 ^
  --image_size 224 ^
  --num_workers 4 ^
  --vocab_size 10000 ^
  --val_gallery_size 2000 ^
  --scene_dir D:\datasets\mimic-ext-cxr-qba\scene_graphs\scene_data ^
  --image_dir D:\datasets\mimic-cxr-jpg ^
  --split_csv D:\datasets\mimic-cxr-jpg\mimic-cxr-2.0.0-split.csv.gz ^
  --output_dir D:\experiments\exp_raddino_hardneg

echo.
echo ========================================
echo   RadDINO Exp #3 Training Complete
echo ========================================
echo.
echo Results saved to: D:\experiments\exp_raddino_hardneg
echo Best checkpoint:  D:\experiments\exp_raddino_hardneg\p3_best.pt
echo.
echo Check results with:
echo   cd D:\experiments\exp_raddino_hardneg
echo   type p3_history.json
echo.
pause
