@echo off
REM ============================================================================
REM BenchX SHARP Training - SIIM and RSNA
REM ============================================================================

echo ========================================
echo   BenchX SHARP Training Pipeline
echo ========================================
echo.
echo This will:
echo   1. Setup configs
echo   2. Fix SIIM CSV (add has_pneumo column)
echo   3. Train SHARP on SIIM (30-45 min)
echo   4. Preprocess RSNA dataset (10-15 min)
echo   5. Train SHARP on RSNA (1-1.5 hours)
echo.
echo Total time: ~2 hours
echo ========================================
echo.

REM ============================================================================
REM Step 0: Setup - Copy configs and sync from GitHub
REM ============================================================================
echo [0/4] Setting up configs...
echo.

cd C:\Users\aya.alaswad\remote
git pull origin main

echo Copying SHARP configs to BenchX...
copy sharp_siim.yml BenchX\configs\classification\SIIM\sharp.yml /Y
copy sharp_rsna.yml BenchX\configs\classification\RSNA\sharp.yml /Y

if errorlevel 1 (
    echo [ERROR] Config copy failed!
    pause
    exit /b 1
)

echo [OK] Configs ready
echo.

REM ============================================================================
REM Step 1: Rebuild SIIM CSV (match actual image filenames)
REM ============================================================================
echo [1/5] Rebuilding SIIM CSV to match actual image files...
echo.

cd C:\Users\aya.alaswad\remote

python rebuild_siim_csv.py

if errorlevel 1 (
    echo [ERROR] SIIM CSV fix failed!
    pause
    exit /b 1
)

echo [OK] SIIM CSV fixed
echo.

REM ============================================================================
REM Step 2: SIIM Training
REM ============================================================================
echo [2/5] Training SHARP on SIIM dataset...
echo   - Using preprocessed data (3,205 images)
echo   - Training on train_1.txt (1%% subset)
echo   - Expected time: 30-45 minutes
echo.

cd C:\Users\aya.alaswad\remote\BenchX

python bin/train.py configs/classification/SIIM/sharp.yml

if errorlevel 1 (
    echo [ERROR] SIIM training failed!
    echo Check the error above for details.
    pause
    exit /b 1
)

echo.
echo [OK] SIIM training complete!
echo.

REM ============================================================================
REM Step 3: RSNA Preprocessing
REM ============================================================================
echo [3/5] Preprocessing RSNA dataset...
echo   - Converting ~30k DICOM to PNG (512x512)
echo   - Generating pneumonia masks
echo   - Creating train/val/test splits
echo   - Expected time: 10-15 minutes
echo.

cd C:\Users\aya.alaswad\remote

python preprocess_rsna_adapted.py

if errorlevel 1 (
    echo [ERROR] RSNA preprocessing failed!
    pause
    exit /b 1
)

echo.
echo [OK] RSNA preprocessing complete!
echo.

REM ============================================================================
REM Step 4: RSNA Training
REM ============================================================================
echo [4/5] Training SHARP on RSNA dataset...
echo   - Using preprocessed data (~30k images)
echo   - Training on train_1.txt (1%% subset)
echo   - Expected time: 1-1.5 hours
echo.

cd C:\Users\aya.alaswad\remote\BenchX

python bin/train.py configs/classification/RSNA/sharp.yml

if errorlevel 1 (
    echo [ERROR] RSNA training failed!
    echo Check the error above for details.
    pause
    exit /b 1
)

echo.
echo [OK] RSNA training complete!
echo.

REM ============================================================================
REM Step 5: Extract Results
REM ============================================================================
echo [5/5] Extracting results...
echo ========================================
echo   Training Complete! Results Summary
echo ========================================
echo.

cd C:\Users\aya.alaswad\remote\BenchX

echo Looking for SIIM results...
dir /s /b results\*SIIM*sharp*\val_metrics.pt 2>nul
echo.

echo Looking for RSNA results...
dir /s /b results\*RSNA*sharp*\val_metrics.pt 2>nul
echo.

echo ========================================
echo   All Done!
echo ========================================
echo.
echo Results saved in BenchX/results/
echo.
echo To view AUROC scores, check:
echo   - results/[SIIM experiment folder]/val_metrics.pt
echo   - results/[RSNA experiment folder]/val_metrics.pt
echo.
echo Use this command to extract AUROC:
echo   python -c "import torch; print(torch.load('results/[folder]/val_metrics.pt'))"
echo.
pause
