@echo off
REM ============================================================================
REM BenchX Complete Unattended Runner - No Conda Required
REM ============================================================================
REM
REM This script does EVERYTHING automatically:
REM   1. Pull from GitHub
REM   2. Fix BenchX requirements (no conda)
REM   3. Install packages
REM   4. Integrate SHARP
REM   5. Run all available datasets
REM   6. Save results
REM
REM Runtime: 6-8 hours (can close remote desktop)
REM Log: D:\experiments\benchx_unattended.log
REM ============================================================================

echo ========================================
echo   BenchX Unattended Run Started
echo   %date% %time%
echo ========================================
echo.

set LOGFILE=D:\experiments\benchx_unattended.log
echo Starting BenchX automation at %date% %time% > %LOGFILE%
echo. >> %LOGFILE%

REM ============================================================================
REM Step 1: Pull from GitHub
REM ============================================================================
echo [1/7] Pulling from GitHub...
cd C:\Users\aya.alaswad\remote
git pull origin main >> %LOGFILE% 2>&1
echo [OK] Files updated
echo.

REM ============================================================================
REM Step 2: Fix BenchX Requirements (No Conda)
REM ============================================================================
echo [2/7] Fixing BenchX requirements...
cd C:\Users\aya.alaswad\remote\BenchX

REM Create fixed requirements
(
echo torch^>=2.0.0
echo torchvision^>=0.15.0
echo transformers^>=4.30.0
echo timm
echo albumentations
echo opencv-python
echo pandas
echo numpy
echo scipy
echo scikit-learn
echo tqdm
echo tensorboard
echo pillow
echo matplotlib
echo pyyaml
) > requirements_fixed.txt

echo [OK] Requirements fixed
echo.

REM ============================================================================
REM Step 3: Install Missing Packages (PyTorch already installed)
REM ============================================================================
echo [3/7] Installing missing packages...
pip install transformers timm albumentations scikit-learn -q >> %LOGFILE% 2>&1

if errorlevel 1 (
    echo [ERROR] Package installation failed! >> %LOGFILE%
    echo [ERROR] Package installation failed!
    echo Check log: %LOGFILE%
    pause
    exit /b 1
)

echo [OK] Packages installed
echo.

REM ============================================================================
REM Step 4: Integrate SHARP
REM ============================================================================
echo [4/7] Integrating SHARP...

REM Copy SHARP model
copy /Y ..\benchx_sharp_model.py models\sharp.py >> %LOGFILE% 2>&1

REM Create config directories
mkdir configs\classification\siim 2>nul
mkdir configs\classification\rsna 2>nul
mkdir configs\classification\nih 2>nul
mkdir configs\classification\vindr 2>nul

REM Copy configs
copy /Y ..\benchx_config_siim.yml configs\classification\siim\sharp.yml >> %LOGFILE% 2>&1
copy /Y ..\benchx_config_rsna.yml configs\classification\rsna\sharp.yml >> %LOGFILE% 2>&1
copy /Y ..\benchx_config_nih.yml configs\classification\nih\sharp.yml >> %LOGFILE% 2>&1
copy /Y ..\benchx_config_vindr.yml configs\classification\vindr\sharp.yml >> %LOGFILE% 2>&1

REM Test SHARP imports
python -c "from models.sharp import SHARP; print('[OK] SHARP integrated')" >> %LOGFILE% 2>&1

if errorlevel 1 (
    echo [ERROR] SHARP integration failed! >> %LOGFILE%
    echo [ERROR] SHARP integration failed!
    echo Check log: %LOGFILE%
    pause
    exit /b 1
)

echo [OK] SHARP integrated
echo.

REM ============================================================================
REM Step 5: Check Which Datasets Exist
REM ============================================================================
echo [5/7] Checking datasets...

set RUN_SIIM=0
set RUN_RSNA=0
set RUN_VINDR=0
set RUN_NIH=0

if exist "D:\datasets\siim-pneumothorax\" (
    echo [OK] SIIM found
    set RUN_SIIM=1
)

if exist "D:\datasets\rsna-pneumonia\" (
    echo [OK] RSNA found
    set RUN_RSNA=1
)

if exist "D:\datasets\vindr-cxr\" (
    echo [OK] VinDr found
    set RUN_VINDR=1
)

if exist "D:\datasets\nih-chestxray14\" (
    echo [OK] NIH found
    set RUN_NIH=1
)

REM Check if at least one dataset exists
set /a TOTAL=%RUN_SIIM%+%RUN_RSNA%+%RUN_VINDR%+%RUN_NIH%
if %TOTAL%==0 (
    echo [ERROR] No datasets found! >> %LOGFILE%
    echo [ERROR] No datasets found!
    echo Download at least SIIM first.
    pause
    exit /b 1
)

echo Found %TOTAL% dataset(s)
echo.

REM ============================================================================
REM Step 6: Create Output Directories
REM ============================================================================
echo [6/7] Creating output directories...
mkdir D:\experiments\benchx_results 2>nul
mkdir D:\experiments\benchx_results\siim_sharp 2>nul
mkdir D:\experiments\benchx_results\rsna_sharp 2>nul
mkdir D:\experiments\benchx_results\vindr_sharp 2>nul
mkdir D:\experiments\benchx_results\nih_sharp 2>nul
echo [OK] Directories ready
echo.

REM ============================================================================
REM Step 7: Run Training on All Available Datasets
REM ============================================================================
echo [7/7] Starting training...
echo Start time: %time%
echo.
echo YOU CAN CLOSE REMOTE DESKTOP NOW
echo Training will continue in background
echo.
echo Check progress later in: %LOGFILE%
echo.

REM Log start time
echo ======================================== >> %LOGFILE%
echo Training started: %date% %time% >> %LOGFILE%
echo ======================================== >> %LOGFILE%
echo. >> %LOGFILE%

REM SIIM
if %RUN_SIIM%==1 (
    echo ======================================== >> %LOGFILE%
    echo [1/%TOTAL%] SIIM-ACR Pneumothorax >> %LOGFILE%
    echo Start: %time% >> %LOGFILE%
    echo ======================================== >> %LOGFILE%

    echo [1/%TOTAL%] Running SIIM... (start: %time%)
    python bin/train.py configs/classification/siim/sharp.yml >> %LOGFILE% 2>&1

    if errorlevel 1 (
        echo [WARNING] SIIM failed - continuing >> %LOGFILE%
        set RUN_SIIM=0
    ) else (
        echo [1/%TOTAL%] SIIM Complete at %time% >> %LOGFILE%
        echo [1/%TOTAL%] SIIM Complete (end: %time%)
    )
    echo. >> %LOGFILE%
)

REM RSNA
if %RUN_RSNA%==1 (
    echo ======================================== >> %LOGFILE%
    echo [2/%TOTAL%] RSNA Pneumonia >> %LOGFILE%
    echo Start: %time% >> %LOGFILE%
    echo ======================================== >> %LOGFILE%

    echo [2/%TOTAL%] Running RSNA... (start: %time%)
    python bin/train.py configs/classification/rsna/sharp.yml >> %LOGFILE% 2>&1

    if errorlevel 1 (
        echo [WARNING] RSNA failed - continuing >> %LOGFILE%
        set RUN_RSNA=0
    ) else (
        echo [2/%TOTAL%] RSNA Complete at %time% >> %LOGFILE%
        echo [2/%TOTAL%] RSNA Complete (end: %time%)
    )
    echo. >> %LOGFILE%
)

REM VinDr
if %RUN_VINDR%==1 (
    echo ======================================== >> %LOGFILE%
    echo [3/%TOTAL%] VinDr-CXR >> %LOGFILE%
    echo Start: %time% >> %LOGFILE%
    echo ======================================== >> %LOGFILE%

    echo [3/%TOTAL%] Running VinDr... (start: %time%)
    python bin/train.py configs/classification/vindr/sharp.yml >> %LOGFILE% 2>&1

    if errorlevel 1 (
        echo [WARNING] VinDr failed - continuing >> %LOGFILE%
        set RUN_VINDR=0
    ) else (
        echo [3/%TOTAL%] VinDr Complete at %time% >> %LOGFILE%
        echo [3/%TOTAL%] VinDr Complete (end: %time%)
    )
    echo. >> %LOGFILE%
)

REM NIH
if %RUN_NIH%==1 (
    echo ======================================== >> %LOGFILE%
    echo [4/%TOTAL%] NIH ChestX-ray14 >> %LOGFILE%
    echo Start: %time% >> %LOGFILE%
    echo ======================================== >> %LOGFILE%

    echo [4/%TOTAL%] Running NIH... (start: %time%)
    python bin/train.py configs/classification/nih/sharp.yml >> %LOGFILE% 2>&1

    if errorlevel 1 (
        echo [WARNING] NIH failed - continuing >> %LOGFILE%
        set RUN_NIH=0
    ) else (
        echo [4/%TOTAL%] NIH Complete at %time% >> %LOGFILE%
        echo [4/%TOTAL%] NIH Complete (end: %time%)
    )
    echo. >> %LOGFILE%
)

REM ============================================================================
REM Extract Final Results
REM ============================================================================
echo. >> %LOGFILE%
echo ======================================== >> %LOGFILE%
echo FINAL RESULTS SUMMARY >> %LOGFILE%
echo End time: %date% %time% >> %LOGFILE%
echo ======================================== >> %LOGFILE%
echo. >> %LOGFILE%

if %RUN_SIIM%==1 (
    echo SIIM-ACR Pneumothorax: >> %LOGFILE%
    python -c "import pandas as pd; import os; f='D:/experiments/benchx_results/siim_sharp/metrics.csv'; print(f'  AUROC: {pd.read_csv(f)[\"val_auroc\"].max():.4f}') if os.path.exists(f) else print('  Results not found')" >> %LOGFILE% 2>&1
)

if %RUN_RSNA%==1 (
    echo RSNA Pneumonia: >> %LOGFILE%
    python -c "import pandas as pd; import os; f='D:/experiments/benchx_results/rsna_sharp/metrics.csv'; print(f'  AUROC: {pd.read_csv(f)[\"val_auroc\"].max():.4f}') if os.path.exists(f) else print('  Results not found')" >> %LOGFILE% 2>&1
)

if %RUN_VINDR%==1 (
    echo VinDr-CXR: >> %LOGFILE%
    python -c "import pandas as pd; import os; f='D:/experiments/benchx_results/vindr_sharp/metrics.csv'; print(f'  AUROC: {pd.read_csv(f)[\"val_auroc\"].max():.4f}') if os.path.exists(f) else print('  Results not found')" >> %LOGFILE% 2>&1
)

if %RUN_NIH%==1 (
    echo NIH ChestX-ray14: >> %LOGFILE%
    python -c "import pandas as pd; import os; f='D:/experiments/benchx_results/nih_sharp/metrics.csv'; print(f'  AUROC: {pd.read_csv(f)[\"val_auroc\"].max():.4f}') if os.path.exists(f) else print('  Results not found')" >> %LOGFILE% 2>&1
)

echo. >> %LOGFILE%
echo ======================================== >> %LOGFILE%
echo BenchX Automation Complete >> %LOGFILE%
echo Results: D:\experiments\benchx_results\ >> %LOGFILE%
echo ======================================== >> %LOGFILE%

echo.
echo ========================================
echo   ALL TRAINING COMPLETE!
echo   End time: %time%
echo ========================================
echo.
echo Results saved to: D:\experiments\benchx_results\
echo Full log: %LOGFILE%
echo.
echo You can close this window now.
exit /b 0
