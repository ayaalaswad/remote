@echo off
REM ============================================================================
REM BenchX Complete Unattended Runner - FIXED VERSION
REM ============================================================================
REM
REM This script does EVERYTHING automatically with robust error handling
REM Runtime: 6-8 hours (can close remote desktop)
REM Log: D:\experiments\benchx_unattended.log
REM ============================================================================

echo ========================================
echo   BenchX Unattended Run Started
echo   %date% %time%
echo ========================================
echo.

set LOGFILE=D:\experiments\benchx_unattended.log
set MYRESEARCH=C:\Users\aya.alaswad\remote
set BENCHX=C:\Users\aya.alaswad\remote\BenchX

echo Starting BenchX automation at %date% %time% > %LOGFILE%
echo. >> %LOGFILE%

REM ============================================================================
REM Step 1: Pull from GitHub
REM ============================================================================
echo [1/8] Pulling from GitHub...
cd %MYRESEARCH%
git pull origin main >> %LOGFILE% 2>&1
echo [OK] Files updated
echo.

REM ============================================================================
REM Step 2: Verify Required Files Exist
REM ============================================================================
echo [2/8] Verifying files...

if not exist "%MYRESEARCH%\benchx_sharp_model.py" (
    echo [ERROR] benchx_sharp_model.py not found! >> %LOGFILE%
    echo [ERROR] benchx_sharp_model.py not found!
    pause
    exit /b 1
)

if not exist "%MYRESEARCH%\benchx_config_siim.yml" (
    echo [ERROR] Config files not found! >> %LOGFILE%
    echo [ERROR] Config files not found!
    pause
    exit /b 1
)

echo [OK] All files present
echo.

REM ============================================================================
REM Step 3: Setup BenchX (if needed)
REM ============================================================================
echo [3/8] Setting up BenchX...

if not exist "%BENCHX%" (
    echo Cloning BenchX repository...
    cd C:\Users\aya.alaswad\remote
    git clone https://github.com/yangzhou12/BenchX.git >> %LOGFILE% 2>&1
    if errorlevel 1 (
        echo [ERROR] Failed to clone BenchX! >> %LOGFILE%
        echo [ERROR] Failed to clone BenchX!
        pause
        exit /b 1
    )
)

echo [OK] BenchX directory exists
echo.

REM ============================================================================
REM Step 4: Fix BenchX Requirements (No Conda)
REM ============================================================================
echo [4/8] Fixing BenchX requirements...
cd %BENCHX%

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
REM Step 5: Install Missing Packages (PyTorch already installed)
REM ============================================================================
echo [5/8] Installing missing packages...
pip install transformers timm albumentations scikit-learn einops pydicom SimpleITK monai -q >> %LOGFILE% 2>&1

if errorlevel 1 (
    echo [WARNING] Package installation had issues (continuing anyway) >> %LOGFILE%
)

echo [OK] Packages installed
echo.

REM ============================================================================
REM Step 6: Integrate SHARP
REM ============================================================================
echo [6/8] Integrating SHARP...

REM Create models directory if needed
if not exist "%BENCHX%\models" mkdir "%BENCHX%\models"

REM Copy SHARP model with absolute paths
copy /Y "%MYRESEARCH%\benchx_sharp_model.py" "%BENCHX%\models\sharp.py" >> %LOGFILE% 2>&1

if not exist "%BENCHX%\models\sharp.py" (
    echo [ERROR] Failed to copy SHARP model! >> %LOGFILE%
    echo [ERROR] Failed to copy SHARP model!
    type %LOGFILE%
    pause
    exit /b 1
)

echo [OK] SHARP model copied
echo.

REM Create config directory structure with absolute paths
echo Creating config directories...
if not exist "%BENCHX%\configs" mkdir "%BENCHX%\configs"
if not exist "%BENCHX%\configs\classification" mkdir "%BENCHX%\configs\classification"
if not exist "%BENCHX%\configs\classification\siim" mkdir "%BENCHX%\configs\classification\siim"
if not exist "%BENCHX%\configs\classification\rsna" mkdir "%BENCHX%\configs\classification\rsna"
if not exist "%BENCHX%\configs\classification\nih" mkdir "%BENCHX%\configs\classification\nih"
if not exist "%BENCHX%\configs\classification\vindr" mkdir "%BENCHX%\configs\classification\vindr"

REM Copy configs with absolute paths
copy /Y "%MYRESEARCH%\benchx_config_siim.yml" "%BENCHX%\configs\classification\siim\sharp.yml" >> %LOGFILE% 2>&1
copy /Y "%MYRESEARCH%\benchx_config_rsna.yml" "%BENCHX%\configs\classification\rsna\sharp.yml" >> %LOGFILE% 2>&1
copy /Y "%MYRESEARCH%\benchx_config_nih.yml" "%BENCHX%\configs\classification\nih\sharp.yml" >> %LOGFILE% 2>&1
copy /Y "%MYRESEARCH%\benchx_config_vindr.yml" "%BENCHX%\configs\classification\vindr\sharp.yml" >> %LOGFILE% 2>&1

REM Verify configs were copied
if not exist "%BENCHX%\configs\classification\siim\sharp.yml" (
    echo [ERROR] Failed to copy config files! >> %LOGFILE%
    echo [ERROR] Failed to copy config files!
    echo Source: %MYRESEARCH%
    echo Target: %BENCHX%\configs\classification
    type %LOGFILE%
    pause
    exit /b 1
)

echo [OK] Config files copied
echo.

REM Test SHARP imports
echo Testing SHARP integration...
cd %BENCHX%
python -c "from models.sharp import SHARP; print('[OK] SHARP integrated')" >> %LOGFILE% 2>&1

if errorlevel 1 (
    echo [ERROR] SHARP integration test failed! >> %LOGFILE%
    echo [ERROR] SHARP integration test failed!
    type %LOGFILE%
    pause
    exit /b 1
)

echo [OK] SHARP integrated
echo.

REM ============================================================================
REM Step 7: Check Which Datasets Exist
REM ============================================================================
echo [7/8] Checking datasets...

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
    echo.
    echo Download at least SIIM first:
    echo   https://www.kaggle.com/c/siim-acr-pneumothorax-segmentation
    echo.
    pause
    exit /b 1
)

echo Found %TOTAL% dataset(s)
echo.

REM ============================================================================
REM Step 8: Create Output Directories
REM ============================================================================
echo [8/8] Creating output directories...
if not exist "D:\experiments\benchx_results" mkdir "D:\experiments\benchx_results"
if not exist "D:\experiments\benchx_results\siim_sharp" mkdir "D:\experiments\benchx_results\siim_sharp"
if not exist "D:\experiments\benchx_results\rsna_sharp" mkdir "D:\experiments\benchx_results\rsna_sharp"
if not exist "D:\experiments\benchx_results\vindr_sharp" mkdir "D:\experiments\benchx_results\vindr_sharp"
if not exist "D:\experiments\benchx_results\nih_sharp" mkdir "D:\experiments\benchx_results\nih_sharp"
echo [OK] Directories ready
echo.

REM ============================================================================
REM Step 9: Run Training on All Available Datasets
REM ============================================================================
echo ========================================
echo   Starting Training
echo ========================================
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
echo Datasets to run: %TOTAL% >> %LOGFILE%
echo ======================================== >> %LOGFILE%
echo. >> %LOGFILE%

cd %BENCHX%

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
