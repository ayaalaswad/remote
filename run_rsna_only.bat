@echo off
REM ============================================================================
REM BenchX SHARP - RSNA Only
REM ============================================================================

echo ========================================
echo   BenchX SHARP - RSNA Training
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
REM Step 2: Preprocess RSNA dataset
REM ============================================================================
echo [2/4] Preprocessing RSNA dataset...
echo   - Converting ~30k DICOM to PNG (512x512)
echo   - Generating pneumonia masks
echo   - Creating train/val/test splits
echo   - Expected time: 10-15 minutes
echo.

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
REM Step 3: Copy config to BenchX
REM ============================================================================
echo [3/4] Copying RSNA config to BenchX...

copy sharp_rsna_final.yml BenchX\configs\classification\RSNA\sharp.yml /Y

if errorlevel 1 (
    echo [ERROR] Config copy failed!
    pause
    exit /b 1
)

echo [OK] Config copied
echo.

REM ============================================================================
REM Step 4: Run RSNA training
REM ============================================================================
echo [4/4] Training SHARP on RSNA dataset...
echo   - Using preprocessed data (~30k images)
echo   - Training on train_1.txt (1%% subset)
echo   - Expected time: 1-1.5 hours
echo.

cd BenchX

python bin/train.py configs/classification/RSNA/sharp.yml

if errorlevel 1 (
    echo.
    echo [ERROR] RSNA training failed!
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
echo   BenchX\experiments\classification\rsna\
echo.

cd ..

pause
