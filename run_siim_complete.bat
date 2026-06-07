@echo off
REM ============================================================================
REM Complete SIIM Pipeline: Fix Preprocessing + Train All 3 Splits
REM ============================================================================

echo ========================================
echo   SIIM Complete Pipeline
echo ========================================
echo.
echo This will:
echo   [1/5] Pull latest code
echo   [2/5] Delete old SIIM preprocessing
echo   [3/5] Run FIXED preprocessing (reads CSV labels)
echo   [4/5] Train on 1%%, 10%%, 100%% splits
echo.
echo Expected total time: 4-5 hours
echo   - Preprocessing: 10-15 min
echo   - Training: 3-4 hours
echo.
pause

cd C:\Users\aya.alaswad\remote

REM ============================================================================
REM Step 1: Pull latest code
REM ============================================================================
echo [1/5] Pulling latest code from GitHub...
git pull origin main
echo.

REM ============================================================================
REM Step 2: Delete old (broken) preprocessing
REM ============================================================================
echo [2/5] Deleting old SIIM preprocessing...

if exist "BenchX\datasets\SIIM" (
    echo   - Found old preprocessing
    rmdir /S /Q "BenchX\datasets\SIIM"
    echo   - Deleted
) else (
    echo   - No old preprocessing found
)
echo.

REM ============================================================================
REM Step 3: Run FIXED preprocessing
REM ============================================================================
echo [3/5] Running FIXED preprocessing...
echo   - Reading labels from CSV (EncodedPixels column)
echo   - Creating stratified splits with BOTH classes
echo   - Expected time: 10-15 minutes
echo.

python preprocess_siim_fixed.py

if errorlevel 1 (
    echo.
    echo [ERROR] Preprocessing failed!
    echo Check the output above for details.
    pause
    exit /b 1
)

echo.
echo [OK] Preprocessing complete!
echo.
echo Verification: Check the output above for class distribution.
echo You should see BOTH positive and negative samples in validation.
echo.
pause

REM ============================================================================
REM Step 4: Train on 1%% split
REM ============================================================================
echo [4/5] Training on all 3 splits...
echo.
echo [4a/5] Training SHARP on 1%% split...
echo   - Expected time: 20-30 minutes
echo.

copy sharp_siim_1pct.yml BenchX\configs\classification\SIIM\sharp.yml /Y
cd BenchX
python bin/train.py configs/classification/SIIM/sharp.yml

if errorlevel 1 (
    echo.
    echo [WARNING] 1%% split training failed - continuing...
)

echo.
echo [OK] 1%% split complete!
echo.
cd ..

REM ============================================================================
REM Step 5: Train on 10%% split
REM ============================================================================
echo [4b/5] Training SHARP on 10%% split...
echo   - Expected time: 1-1.5 hours
echo.

copy sharp_siim_10pct.yml BenchX\configs\classification\SIIM\sharp.yml /Y
cd BenchX
python bin/train.py configs/classification/SIIM/sharp.yml

if errorlevel 1 (
    echo.
    echo [WARNING] 10%% split training failed - continuing...
)

echo.
echo [OK] 10%% split complete!
echo.
cd ..

REM ============================================================================
REM Step 6: Train on 100%% split
REM ============================================================================
echo [4c/5] Training SHARP on 100%% split...
echo   - Expected time: 2-3 hours
echo.

copy sharp_siim_100pct.yml BenchX\configs\classification\SIIM\sharp.yml /Y
cd BenchX
python bin/train.py configs/classification/SIIM/sharp.yml

if errorlevel 1 (
    echo.
    echo [WARNING] 100%% split training failed - continuing...
)

echo.
echo [OK] 100%% split complete!
echo.
cd ..

REM ============================================================================
REM Summary
REM ============================================================================
echo.
echo ========================================
echo   SIIM Pipeline Complete!
echo ========================================
echo.
echo Results saved in:
echo   BenchX\experiments\classification\siim\SHARP_1pct\
echo   BenchX\experiments\classification\siim\SHARP_10pct\
echo   BenchX\experiments\classification\siim\SHARP_100pct\
echo.
echo Next: Calculate F1 scores and compare to BenchX baselines
echo   BenchX baselines:
echo   - MRM: 60.2 / 72.4 / 74.7
echo   - MGCA-ViT: 51.7 / 67.9 / 72.7
echo.

pause
