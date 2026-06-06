@echo off
REM ============================================================================
REM BenchX SHARP - RSNA 10% Split Only (Most Meaningful for Pretraining)
REM ============================================================================

echo ========================================
echo   BenchX SHARP - RSNA 10%% Split
echo ========================================
echo.
echo Training on 10%% data (~1,800 samples)
echo Most meaningful split for pretraining paper
echo Expected time: 1-1.5 hours
echo.

cd C:\Users\aya.alaswad\remote

REM Pull latest code
echo Pulling latest code...
git pull origin main
echo.

REM Preprocess if needed
if not exist "BenchX\datasets\RSNA\rsna_labels.csv" (
    echo Preprocessing RSNA dataset...
    python run_benchx_rsna_preprocess.py
    if errorlevel 1 exit /b 1
    echo.
)

REM Copy config and train
echo Training SHARP on 10%% split...
copy sharp_rsna_10pct.yml BenchX\configs\classification\RSNA\sharp.yml /Y
cd BenchX
python bin/train.py configs/classification/RSNA/sharp.yml

if errorlevel 1 (
    echo [ERROR] Training failed!
    pause
    exit /b 1
)

echo.
echo ========================================
echo   Training Complete!
echo ========================================
echo.
echo Results in: BenchX\experiments\classification\rsna\SHARP_10pct\
echo.

cd ..
pause
