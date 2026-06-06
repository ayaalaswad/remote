@echo off
REM ============================================================================
REM BenchX SHARP - RSNA All Data Regimes (1%, 10%, 100%)
REM ============================================================================

echo ========================================
echo   BenchX SHARP - RSNA All Splits
echo ========================================
echo.
echo This will train SHARP on 3 data regimes:
echo   [1/3] train_1  (1%% - 186 samples)
echo   [2/3] train_10 (10%% - ~1.8k samples)
echo   [3/3] train    (100%% - ~18k samples)
echo.
echo Expected total time: 3-4 hours
echo.
pause

cd C:\Users\aya.alaswad\remote

REM ============================================================================
REM Step 0: Pull latest code
REM ============================================================================
echo [0/4] Pulling latest code from GitHub...
git pull origin main
echo.

REM ============================================================================
REM Step 1: Preprocess RSNA dataset (if not already done)
REM ============================================================================
echo [1/4] Checking RSNA preprocessing...

if not exist "BenchX\datasets\RSNA\rsna_labels.csv" (
    echo [1/4] Preprocessing RSNA dataset...
    echo   - Converting ~30k DICOM to PNG (512x512)
    echo   - Expected time: 10-15 minutes
    echo.
    python run_benchx_rsna_preprocess.py

    if errorlevel 1 (
        echo [ERROR] RSNA preprocessing failed!
        pause
        exit /b 1
    )
    echo.
    echo [OK] RSNA preprocessing complete!
) else (
    echo [OK] RSNA already preprocessed - skipping
)
echo.

REM ============================================================================
REM Step 2: Train on 1% split (186 samples)
REM ============================================================================
echo [2/4] Training SHARP on 1%% split (186 samples)...
echo   - Expected time: 20-30 minutes
echo.

copy sharp_rsna_1pct.yml BenchX\configs\classification\RSNA\sharp.yml /Y
cd BenchX
python bin/train.py configs/classification/RSNA/sharp.yml

if errorlevel 1 (
    echo.
    echo [ERROR] 1%% split training failed!
    pause
    exit /b 1
)

echo.
echo [OK] 1%% split complete!
echo.
cd ..

REM ============================================================================
REM Step 3: Train on 10% split (~1.8k samples)
REM ============================================================================
echo [3/4] Training SHARP on 10%% split (~1,800 samples)...
echo   - Expected time: 1-1.5 hours
echo.

copy sharp_rsna_10pct.yml BenchX\configs\classification\RSNA\sharp.yml /Y
cd BenchX
python bin/train.py configs/classification/RSNA/sharp.yml

if errorlevel 1 (
    echo.
    echo [ERROR] 10%% split training failed!
    pause
    exit /b 1
)

echo.
echo [OK] 10%% split complete!
echo.
cd ..

REM ============================================================================
REM Step 4: Train on 100% split (~18k samples)
REM ============================================================================
echo [4/4] Training SHARP on 100%% split (~18,000 samples)...
echo   - Expected time: 2-3 hours
echo.

copy sharp_rsna_100pct.yml BenchX\configs\classification\RSNA\sharp.yml /Y
cd BenchX
python bin/train.py configs/classification/RSNA/sharp.yml

if errorlevel 1 (
    echo.
    echo [ERROR] 100%% split training failed!
    pause
    exit /b 1
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
echo   All Training Complete!
echo ========================================
echo.
echo Results saved in:
echo   BenchX\experiments\classification\rsna\SHARP_1pct\
echo   BenchX\experiments\classification\rsna\SHARP_10pct\
echo   BenchX\experiments\classification\rsna\SHARP_100pct\
echo.
echo Extract AUROC scores from each folder.
echo.

pause
