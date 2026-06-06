@echo off
REM ============================================================================
REM BenchX SHARP - Complete Pipeline
REM ============================================================================

echo ========================================
echo   BenchX SHARP Complete Pipeline
echo ========================================
echo.

cd C:\Users\aya.alaswad\remote

REM ============================================================================
REM Step 1: Pull latest code
REM ============================================================================
echo [1/4] Pulling latest code from GitHub...
git pull origin main
echo.

REM ============================================================================
REM Step 2: Convert checkpoint (one-time operation)
REM ============================================================================
echo [2/4] Converting SHARP checkpoint to timm format...
echo   Input:  D:\experiments\exp3_full_sharp\p3_best.pt
echo   Output: D:\experiments\exp3_full_sharp\p3_best_timm.pt
echo.

if exist D:\experiments\exp3_full_sharp\p3_best_timm.pt (
    echo   ✓ Converted checkpoint already exists, skipping...
) else (
    echo   Converting... (this will take ~30 seconds)
    python convert_sharp_to_timm.py

    if errorlevel 1 (
        echo   [ERROR] Conversion failed!
        pause
        exit /b 1
    )
)

echo.

REM ============================================================================
REM Step 3: Copy configs to BenchX
REM ============================================================================
echo [3/4] Copying configs to BenchX...

copy sharp_siim_final.yml BenchX\configs\classification\SIIM\sharp.yml /Y
copy sharp_rsna_final.yml BenchX\configs\classification\RSNA\sharp.yml /Y

if errorlevel 1 (
    echo [ERROR] Failed to copy configs!
    pause
    exit /b 1
)

echo   ✓ Configs copied
echo.

REM ============================================================================
REM Step 4: Run SIIM training
REM ============================================================================
echo [4/4] Running BenchX training on SIIM...
echo   Dataset: 22 samples (train_1 split)
echo   Expected time: ~30-45 minutes
echo.

cd BenchX

python bin/train.py configs/classification/SIIM/sharp.yml

if errorlevel 1 (
    echo.
    echo [ERROR] Training failed!
    echo Check the error above for details.
    pause
    exit /b 1
)

echo.
echo ========================================
echo   Training Complete!
echo ========================================
echo.
echo Check results in:
echo   BenchX\experiments\classification\siim\
echo.

cd ..

pause
