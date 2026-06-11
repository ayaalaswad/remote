@echo off
REM ============================================================================
REM Resume RadDINO Training (Auto-Resume)
REM ============================================================================
REM
REM This script automatically resumes from the last checkpoint (p3_last.pt)
REM No need to specify checkpoint path - the training script finds it!
REM ============================================================================

echo.
echo ========================================
echo   Resume RadDINO Training
echo ========================================
echo.

REM Check which experiment was running
echo Which RadDINO experiment do you want to resume?
echo.
echo 1. Exp #3 (Hard Negatives) - D:\experiments\exp_raddino_hardneg
echo 2. Smoketest - D:\experiments\exp_raddino_smoketest
echo 3. Custom (specify path)
echo.
set /p choice="Enter choice (1-3): "

if "%choice%"=="1" (
    set OUTPUT_DIR=D:\experiments\exp_raddino_hardneg
    set SCRIPT=run_raddino_exp3_hardneg.bat
    echo.
    echo Resuming: Exp #3 (Hard Negatives)
) else if "%choice%"=="2" (
    set OUTPUT_DIR=D:\experiments\exp_raddino_smoketest
    set SCRIPT=run_raddino_smoketest.bat
    echo.
    echo Resuming: Smoketest
) else if "%choice%"=="3" (
    set /p OUTPUT_DIR="Enter output directory path: "
    echo.
    echo Resuming: Custom experiment
) else (
    echo Invalid choice!
    pause
    exit /b 1
)

echo Output directory: %OUTPUT_DIR%
echo.

REM Check if checkpoint exists
if not exist "%OUTPUT_DIR%\p3_last.pt" (
    echo.
    echo [ERROR] No checkpoint found at: %OUTPUT_DIR%\p3_last.pt
    echo.
    echo Make sure the path is correct and training has saved at least one checkpoint.
    echo.
    pause
    exit /b 1
)

echo Found checkpoint: %OUTPUT_DIR%\p3_last.pt
echo.

REM Show checkpoint info
echo Checkpoint info:
python -c "import torch; ckpt = torch.load(r'%OUTPUT_DIR%\p3_last.pt', map_location='cpu'); print(f'  Step: {ckpt[\"step\"]:,}'); print(f'  Best R@1: {ckpt.get(\"best_r1\", \"unknown\")}')" 2>nul

echo.
echo Training will resume from this checkpoint automatically.
echo Press Ctrl+C to cancel, or
pause

REM Resume training by running the original script
REM The script will auto-detect p3_last.pt and resume
if defined SCRIPT (
    echo.
    echo Running: %SCRIPT%
    echo.
    call %SCRIPT%
) else (
    REM For custom path, use the Exp #3 command as template
    echo.
    echo Running training with custom output directory...
    echo.

    cd C:\Users\aya.alaswad\remote

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
      --output_dir %OUTPUT_DIR%
)

echo.
echo ========================================
echo   Training Complete/Interrupted
echo ========================================
echo.
pause
