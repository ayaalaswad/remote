@echo off
REM ============================================================================
REM BenchX: Run SHARP on all 4 classification datasets
REM ============================================================================
REM
REM This runs SHARP on:
REM   1. SIIM (~1 hour)
REM   2. RSNA (~2 hours)
REM   3. VinDr (~2 hours)
REM   4. NIH (~4-6 hours)
REM
REM Total GPU time: ~8-12 hours
REM Output: D:\experiments\benchx_results\
REM ============================================================================

echo ========================================
echo   BenchX: SHARP Classification Eval
echo ========================================
echo.
echo This will run SHARP on 4 datasets:
echo   1. SIIM-ACR Pneumothorax (12k images)
echo   2. RSNA Pneumonia (30k images)
echo   3. VinDr-CXR (18k images)
echo   4. NIH ChestX-ray14 (112k images)
echo.
echo Total estimated time: 8-12 hours GPU
echo Output: D:\experiments\benchx_results\
echo.
echo Make sure:
echo   - All 4 datasets are downloaded
echo   - SHARP is integrated (benchx_integrate_sharp.bat ran)
echo   - Conda environment 'benchx' is created
echo.
pause

cd C:\Users\aya.alaswad\remote\BenchX

REM Activate conda environment
call conda activate benchx

REM Create output directory
mkdir D:\experiments\benchx_results 2>nul

echo.
echo ========================================
echo   [1/4] Running SIIM-ACR Pneumothorax
echo ========================================
echo.
python bin/train.py configs/classification/siim/sharp.yml
if errorlevel 1 (
    echo [ERROR] SIIM training failed!
    pause
    exit /b 1
)

echo.
echo [1/4] SIIM Complete! Extracting AUROC...
python -c "import pandas as pd; df = pd.read_csv('D:/experiments/benchx_results/siim_sharp/metrics.csv'); print(f'SIIM AUROC: {df[\"val_auroc\"].max():.4f}')"

echo.
echo ========================================
echo   [2/4] Running RSNA Pneumonia
echo ========================================
echo.
python bin/train.py configs/classification/rsna/sharp.yml
if errorlevel 1 (
    echo [ERROR] RSNA training failed!
    pause
    exit /b 1
)

echo.
echo [2/4] RSNA Complete! Extracting AUROC...
python -c "import pandas as pd; df = pd.read_csv('D:/experiments/benchx_results/rsna_sharp/metrics.csv'); print(f'RSNA AUROC: {df[\"val_auroc\"].max():.4f}')"

echo.
echo ========================================
echo   [3/4] Running VinDr-CXR
echo ========================================
echo.
python bin/train.py configs/classification/vindr/sharp.yml
if errorlevel 1 (
    echo [ERROR] VinDr training failed!
    pause
    exit /b 1
)

echo.
echo [3/4] VinDr Complete! Extracting AUROC...
python -c "import pandas as pd; df = pd.read_csv('D:/experiments/benchx_results/vindr_sharp/metrics.csv'); print(f'VinDr AUROC: {df[\"val_auroc\"].max():.4f}')"

echo.
echo ========================================
echo   [4/4] Running NIH ChestX-ray14
echo ========================================
echo.
python bin/train.py configs/classification/nih/sharp.yml
if errorlevel 1 (
    echo [ERROR] NIH training failed!
    pause
    exit /b 1
)

echo.
echo [4/4] NIH Complete! Extracting AUROC...
python -c "import pandas as pd; df = pd.read_csv('D:/experiments/benchx_results/nih_sharp/metrics.csv'); print(f'NIH AUROC: {df[\"val_auroc\"].max():.4f}')"

echo.
echo ========================================
echo   ALL DATASETS COMPLETE!
echo ========================================
echo.
echo Results saved to: D:\experiments\benchx_results\
echo.
echo Summary of AUROC scores:
echo   SIIM:  (see above)
echo   RSNA:  (see above)
echo   VinDr: (see above)
echo   NIH:   (see above)
echo.
echo Next: Compare with baseline numbers from BenchX paper
echo       (Add to experiments.md)
echo.
pause
