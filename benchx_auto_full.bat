@echo off
REM ============================================================================
REM BenchX Full Automation - Run Everything Unattended
REM ============================================================================
REM
REM This script runs COMPLETELY AUTOMATICALLY:
REM   1. Pull from GitHub
REM   2. Setup BenchX
REM   3. Integrate SHARP
REM   4. Test integration
REM   5. Run all 4 datasets (assumes data already downloaded)
REM   6. Extract results
REM   7. Save summary
REM
REM REQUIREMENTS:
REM   - All 4 datasets already downloaded to D:\datasets\
REM   - If datasets not downloaded, run benchx_download_first.bat
REM
REM Runtime: ~6-8 hours (unattended)
REM ============================================================================

echo ========================================
echo   BenchX Full Automation Started
echo   %date% %time%
echo ========================================
echo.

REM Create log file
set LOGFILE=D:\experiments\benchx_full_run.log
echo Full automation log: %LOGFILE%
echo Starting automation at %date% %time% > %LOGFILE%
echo.

REM ============================================================================
REM Step 1: Pull from GitHub
REM ============================================================================
echo [Step 1/8] Pulling latest files from GitHub...
cd C:\Users\aya.alaswad\remote\MyReasearch
git pull origin main
if errorlevel 1 (
    echo [ERROR] Git pull failed!
    exit /b 1
)
echo [OK] Files pulled
echo.

REM ============================================================================
REM Step 2: Setup BenchX (if not already done)
REM ============================================================================
echo [Step 2/8] Setting up BenchX...
cd C:\Users\aya.alaswad\remote

if not exist "BenchX\" (
    echo Cloning BenchX repository...
    git clone https://github.com/yangzhou12/BenchX.git
    cd BenchX

    echo Creating conda environment...
    call conda create -n benchx python=3.10 -y

    echo Installing dependencies...
    call conda activate benchx
    pip install -r requirements.txt
    echo [OK] BenchX setup complete
) else (
    echo [OK] BenchX already exists
)
echo.

REM ============================================================================
REM Step 3: Integrate SHARP
REM ============================================================================
echo [Step 3/8] Integrating SHARP into BenchX...
cd C:\Users\aya.alaswad\remote

copy /Y MyReasearch\benchx_sharp_model.py BenchX\models\sharp.py
if errorlevel 1 (
    echo [ERROR] Failed to copy SHARP model
    exit /b 1
)

mkdir BenchX\configs\classification\rsna 2>nul
mkdir BenchX\configs\classification\siim 2>nul
mkdir BenchX\configs\classification\nih 2>nul
mkdir BenchX\configs\classification\vindr 2>nul

copy /Y MyReasearch\benchx_config_rsna.yml BenchX\configs\classification\rsna\sharp.yml
copy /Y MyReasearch\benchx_config_siim.yml BenchX\configs\classification\siim\sharp.yml
copy /Y MyReasearch\benchx_config_nih.yml BenchX\configs\classification\nih\sharp.yml
copy /Y MyReasearch\benchx_config_vindr.yml BenchX\configs\classification\vindr\sharp.yml

echo [OK] SHARP integrated
echo.

REM ============================================================================
REM Step 4: Test Integration
REM ============================================================================
echo [Step 4/8] Testing SHARP integration...
cd C:\Users\aya.alaswad\remote\BenchX

call conda activate benchx
python -c "from models.sharp import SHARP; print('[OK] SHARP import works')"
if errorlevel 1 (
    echo [ERROR] SHARP import failed!
    exit /b 1
)

python -c "import torch; from models.sharp import SHARP; model = SHARP('D:/experiments/exp3_hardneg/p3_best.pt', num_classes=2); x = torch.randn(2, 3, 224, 224); y = model(x); print(f'[OK] SHARP forward pass: input={x.shape}, output={y.shape}')"
if errorlevel 1 (
    echo [ERROR] SHARP checkpoint loading failed!
    exit /b 1
)
echo [OK] All tests passed
echo.

REM ============================================================================
REM Step 5: Create output directory
REM ============================================================================
echo [Step 5/8] Creating output directories...
mkdir D:\experiments\benchx_results 2>nul
mkdir D:\experiments\benchx_results\siim_sharp 2>nul
mkdir D:\experiments\benchx_results\rsna_sharp 2>nul
mkdir D:\experiments\benchx_results\vindr_sharp 2>nul
mkdir D:\experiments\benchx_results\nih_sharp 2>nul
echo [OK] Directories created
echo.

REM ============================================================================
REM Step 6: Check datasets exist
REM ============================================================================
echo [Step 6/8] Checking datasets...

if not exist "D:\datasets\siim-pneumothorax\" (
    echo [WARNING] SIIM dataset not found - will skip
    set RUN_SIIM=0
) else (
    echo [OK] SIIM dataset found
    set RUN_SIIM=1
)

if not exist "D:\datasets\rsna-pneumonia\" (
    echo [WARNING] RSNA dataset not found - will skip
    set RUN_RSNA=0
) else (
    echo [OK] RSNA dataset found
    set RUN_RSNA=1
)

if not exist "D:\datasets\vindr-cxr\" (
    echo [WARNING] VinDr dataset not found - will skip
    set RUN_VINDR=0
) else (
    echo [OK] VinDr dataset found
    set RUN_VINDR=1
)

if not exist "D:\datasets\nih-chestxray14\" (
    echo [WARNING] NIH dataset not found - will skip
    set RUN_NIH=0
) else (
    echo [OK] NIH dataset found
    set RUN_NIH=1
)
echo.

REM ============================================================================
REM Step 7: Run Training on All Available Datasets
REM ============================================================================
echo [Step 7/8] Running BenchX evaluation...
echo Start time: %time%
echo.

cd C:\Users\aya.alaswad\remote\BenchX
call conda activate benchx

REM SIIM
if %RUN_SIIM%==1 (
    echo ========================================
    echo [1/4] Running SIIM-ACR Pneumothorax
    echo Start: %time%
    echo ========================================
    python bin/train.py configs/classification/siim/sharp.yml
    if errorlevel 1 (
        echo [WARNING] SIIM training failed - continuing anyway
        set RUN_SIIM=0
    ) else (
        echo [1/4] SIIM Complete at %time%
    )
    echo.
)

REM RSNA
if %RUN_RSNA%==1 (
    echo ========================================
    echo [2/4] Running RSNA Pneumonia
    echo Start: %time%
    echo ========================================
    python bin/train.py configs/classification/rsna/sharp.yml
    if errorlevel 1 (
        echo [WARNING] RSNA training failed - continuing anyway
        set RUN_RSNA=0
    ) else (
        echo [2/4] RSNA Complete at %time%
    )
    echo.
)

REM VinDr
if %RUN_VINDR%==1 (
    echo ========================================
    echo [3/4] Running VinDr-CXR
    echo Start: %time%
    echo ========================================
    python bin/train.py configs/classification/vindr/sharp.yml
    if errorlevel 1 (
        echo [WARNING] VinDr training failed - continuing anyway
        set RUN_VINDR=0
    ) else (
        echo [3/4] VinDr Complete at %time%
    )
    echo.
)

REM NIH
if %RUN_NIH%==1 (
    echo ========================================
    echo [4/4] Running NIH ChestX-ray14
    echo Start: %time%
    echo ========================================
    python bin/train.py configs/classification/nih/sharp.yml
    if errorlevel 1 (
        echo [WARNING] NIH training failed - continuing anyway
        set RUN_NIH=0
    ) else (
        echo [4/4] NIH Complete at %time%
    )
    echo.
)

REM ============================================================================
REM Step 8: Extract Results
REM ============================================================================
echo [Step 8/8] Extracting AUROC results...
echo.
echo ========================================
echo   FINAL RESULTS SUMMARY
echo ========================================
echo.

if %RUN_SIIM%==1 (
    echo SIIM-ACR Pneumothorax:
    python -c "import pandas as pd; import os; f='D:/experiments/benchx_results/siim_sharp/metrics.csv'; print(f'  AUROC: {pd.read_csv(f)[\"val_auroc\"].max():.4f}') if os.path.exists(f) else print('  [ERROR] Results not found')"
    echo.
)

if %RUN_RSNA%==1 (
    echo RSNA Pneumonia:
    python -c "import pandas as pd; import os; f='D:/experiments/benchx_results/rsna_sharp/metrics.csv'; print(f'  AUROC: {pd.read_csv(f)[\"val_auroc\"].max():.4f}') if os.path.exists(f) else print('  [ERROR] Results not found')"
    echo.
)

if %RUN_VINDR%==1 (
    echo VinDr-CXR:
    python -c "import pandas as pd; import os; f='D:/experiments/benchx_results/vindr_sharp/metrics.csv'; print(f'  AUROC: {pd.read_csv(f)[\"val_auroc\"].max():.4f}') if os.path.exists(f) else print('  [ERROR] Results not found')"
    echo.
)

if %RUN_NIH%==1 (
    echo NIH ChestX-ray14:
    python -c "import pandas as pd; import os; f='D:/experiments/benchx_results/nih_sharp/metrics.csv'; print(f'  AUROC: {pd.read_csv(f)[\"val_auroc\"].max():.4f}') if os.path.exists(f) else print('  [ERROR] Results not found')"
    echo.
)

echo ========================================
echo   BenchX Automation Complete!
echo   End time: %date% %time%
echo ========================================
echo.
echo Results saved to: D:\experiments\benchx_results\
echo Log file: %LOGFILE%
echo.

REM Write final summary to log
echo ======================================== >> %LOGFILE%
echo BenchX Automation Complete >> %LOGFILE%
echo End time: %date% %time% >> %LOGFILE%
echo ======================================== >> %LOGFILE%

echo.
echo All done! Results in: D:\experiments\benchx_results\
echo Log saved to: %LOGFILE%
echo.
echo You can close this window.
exit /b 0
